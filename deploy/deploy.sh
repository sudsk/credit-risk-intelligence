#!/usr/bin/env bash
# Deploy the SME Credit Intelligence Platform to Cloud Run behind an HTTPS load
# balancer with IAP.
#
#   source deploy/deploy.env && bash deploy/deploy.sh      # setup + all services + LB
#   bash deploy/deploy.sh backend frontend                 # rebuild/redeploy only these
#   bash deploy/deploy.sh lb                               # (re)apply LB + IAP only
#
# Traffic:
#   browser ──HTTPS──▶ LB + IAP ──▶ frontend   (everything except /api/*)
#                                └─▶ backend    (/api/*)
#   backend ──ID token──▶ agents  (IAM-private)
#   agents  ──VPC──▶ mcp-server, backend (internal ingress), Vertex AI (Private Google Access)
#
# frontend/backend only accept traffic from the LB, so the run.app URLs can't bypass IAP.
set -euo pipefail

# Required (set in your shell, never committed): PROJECT_ID, NETWORK, SUBNET, IAP_MEMBERS
PROJECT_ID="${PROJECT_ID:-}"
REGION="${REGION:-europe-west2}"
REPO="${REPO:-credit-risk}"
GEMINI_MODEL="${GEMINI_MODEL:-gemini-3.7-flash}"
# Vertex AI location for the model; may differ from REGION (e.g. "global" for newer models)
GEMINI_LOCATION="${GEMINI_LOCATION:-$REGION}"
# Existing VPC network + subnet (in REGION) used for the agents' egress
NETWORK="${NETWORK:-}"
SUBNET="${SUBNET:-}"
# DOMAIN: optional hostname. Unset = <ip>.nip.io (HTTPS without owning a domain; IAP needs HTTPS)
DOMAIN="${DOMAIN:-}"
# IAP_MEMBERS: who can open the app, comma-separated IAM members (e.g. "domain:example.com")
IAP_MEMBERS="${IAP_MEMBERS:-}"

if [[ $# -gt 0 ]]; then
  STEPS=("$@"); FULL_DEPLOY=false
else
  STEPS=(mcp-server agents backend frontend lb); FULL_DEPLOY=true
fi

cd "$(dirname "$0")/.."

if [[ -z "$PROJECT_ID" ]]; then
  echo "Set PROJECT_ID (see deploy/deploy.env.example)" >&2; exit 1
fi
if [[ " ${STEPS[*]} " == *" lb "* && -z "$IAP_MEMBERS" ]]; then
  echo "Set IAP_MEMBERS, e.g. IAP_MEMBERS=domain:example.com (see deploy/deploy.env.example)" >&2; exit 1
fi
# Only setup and the agents step use the network
needs_network=$FULL_DEPLOY
[[ " ${STEPS[*]} " == *" agents "* ]] && needs_network=true
if $needs_network && [[ -z "$NETWORK" || -z "$SUBNET" ]]; then
  echo "Set NETWORK and SUBNET to an existing VPC network/subnet in ${REGION}. Available:" >&2
  gcloud compute networks subnets list --project "$PROJECT_ID" --filter "region:${REGION}" \
    --format "table(name, network.basename(), ipCidrRange, privateIpGoogleAccess)" >&2
  exit 1
fi
echo "Project: ${PROJECT_ID}  Region: ${REGION}  Model: ${GEMINI_MODEL} (${GEMINI_LOCATION})"

PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')
# Cloud Run deterministic URLs: https://<service>-<project-number>.<region>.run.app
url() { echo "https://$1-${PROJECT_NUMBER}.${REGION}.run.app"; }
MCP_URL=$(url mcp-server)
AGENTS_URL=$(url agents)
BACKEND_URL=$(url backend)

AR="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}"
TAG=$(git rev-parse --short HEAD 2>/dev/null || date +%s)

SA_RUNTIME="cr-runtime@${PROJECT_ID}.iam.gserviceaccount.com"   # mcp-server, frontend (no roles)
SA_AGENTS="cr-agents@${PROJECT_ID}.iam.gserviceaccount.com"     # Vertex AI
SA_BACKEND="cr-backend@${PROJECT_ID}.iam.gserviceaccount.com"   # invokes agents

gc() { gcloud --project "$PROJECT_ID" --quiet "$@"; }
exists() { "$@" >/dev/null 2>&1; }

setup() {
  echo "==> Enabling APIs"
  gc services enable run.googleapis.com artifactregistry.googleapis.com \
    cloudbuild.googleapis.com aiplatform.googleapis.com iamcredentials.googleapis.com \
    compute.googleapis.com iap.googleapis.com

  echo "==> Artifact Registry repo"
  exists gc artifacts repositories describe "$REPO" --location "$REGION" ||
    gc artifacts repositories create "$REPO" --location "$REGION" --repository-format docker

  echo "==> Service accounts"
  for sa in cr-runtime cr-agents cr-backend; do
    exists gc iam service-accounts describe "${sa}@${PROJECT_ID}.iam.gserviceaccount.com" ||
      gc iam service-accounts create "$sa" --display-name "Credit risk ${sa#cr-}"
  done
  gc projects add-iam-policy-binding "$PROJECT_ID" \
    --member "serviceAccount:${SA_AGENTS}" --role roles/aiplatform.user --condition None >/dev/null

  echo "==> Subnet ${SUBNET} (agents egress)"
  # Agents send all egress through the VPC, so the subnet needs Private Google
  # Access to reach Vertex AI
  pga=$(gc compute networks subnets describe "$SUBNET" --region "$REGION" \
    --format 'value(privateIpGoogleAccess)')
  if [[ "$pga" != "True" ]]; then
    echo "    Enabling Private Google Access on ${SUBNET}"
    gc compute networks subnets update "$SUBNET" --region "$REGION" \
      --enable-private-ip-google-access
  fi

  # One reserved IP shared by the HTTPS and HTTP-redirect rules; also keeps the
  # <ip>.nip.io hostname (and its cert) stable across redeploys
  echo "==> Static IP"
  exists gc compute addresses describe cr-ip --global ||
    gc compute addresses create cr-ip --global --ip-version IPV4
}

check_model() {
  echo "==> Checking ${GEMINI_MODEL} is available in ${GEMINI_LOCATION}"
  local host="${GEMINI_LOCATION}-aiplatform.googleapis.com"
  [[ "$GEMINI_LOCATION" == "global" ]] && host="aiplatform.googleapis.com"
  local status
  status=$(curl -s -o /tmp/gemini-check.json -w '%{http_code}' -X POST \
    -H "Authorization: Bearer $(gcloud auth print-access-token)" \
    -H "Content-Type: application/json" \
    "https://${host}/v1/projects/${PROJECT_ID}/locations/${GEMINI_LOCATION}/publishers/google/models/${GEMINI_MODEL}:generateContent" \
    -d '{"contents":[{"role":"user","parts":[{"text":"ping"}]}]}')
  if [[ "$status" != "200" ]]; then
    echo "Model ${GEMINI_MODEL} not usable in ${GEMINI_LOCATION} (HTTP ${status}):" >&2
    head -c 500 /tmp/gemini-check.json >&2; echo >&2
    echo "Try GEMINI_LOCATION=global or a different GEMINI_MODEL." >&2
    exit 1
  fi
}

lb_ip() { gc compute addresses describe cr-ip --global --format='value(address)'; }

build() {  # build <service> <dockerfile> [vite_api_url]
  echo "==> Building $1"
  gc builds submit . --region "$REGION" --config deploy/cloudbuild.yaml \
    --substitutions "_DOCKERFILE=$2,_IMAGE=${AR}/$1:${TAG},_VITE_API_URL=${3:-}"
}

deploy_mcp() {
  build mcp-server mcp-servers/Dockerfile
  # internal ingress: only reachable from the VPC (agents)
  gc run deploy mcp-server --image "${AR}/mcp-server:${TAG}" --region "$REGION" \
    --service-account "$SA_RUNTIME" --ingress internal --no-invoker-iam-check \
    --memory 512Mi --max-instances 3
}

deploy_agents() {
  check_model
  build agents agents/Dockerfile
  # max-instances 1: chat sessions live in memory (InMemorySessionService)
  # all-traffic VPC egress so calls to mcp-server/backend count as internal
  gc run deploy agents --image "${AR}/agents:${TAG}" --region "$REGION" \
    --service-account "$SA_AGENTS" --no-allow-unauthenticated \
    --network "$NETWORK" --subnet "$SUBNET" --vpc-egress all-traffic \
    --memory 1Gi --max-instances 1 --timeout 300 \
    --set-env-vars "GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_LOCATION=${GEMINI_LOCATION},GOOGLE_GENAI_USE_VERTEXAI=TRUE,GEMINI_MODEL=${GEMINI_MODEL},MCP_SERVER_URL=${MCP_URL},BACKEND_API_URL=${BACKEND_URL}"
  gc run services add-iam-policy-binding agents --region "$REGION" \
    --member "serviceAccount:${SA_BACKEND}" --role roles/run.invoker >/dev/null
}

deploy_backend() {
  build backend backend/Dockerfile
  # max-instances 1 + no CPU throttling: scenario jobs and alerts are in memory
  # and run as background tasks after the request returns
  gc run deploy backend --image "${AR}/backend:${TAG}" --region "$REGION" \
    --service-account "$SA_BACKEND" \
    --ingress internal-and-cloud-load-balancing --no-invoker-iam-check \
    --memory 1Gi --max-instances 1 --no-cpu-throttling --timeout 300 \
    --set-env-vars "AGENTS_URL=${AGENTS_URL},CORS_ORIGINS=https://${DOMAIN}"
}

deploy_frontend() {
  # Empty API URL: the frontend calls /api/* on its own origin (the LB)
  build frontend frontend/Dockerfile ""
  gc run deploy frontend --image "${AR}/frontend:${TAG}" --region "$REGION" \
    --service-account "$SA_RUNTIME" \
    --ingress internal-and-cloud-load-balancing --no-invoker-iam-check \
    --memory 256Mi --max-instances 3
}

deploy_lb() {
  echo "==> Load balancer for ${DOMAIN}"
  for svc in frontend backend; do
    exists gc compute network-endpoint-groups describe "cr-${svc}-neg" --region "$REGION" ||
      gc compute network-endpoint-groups create "cr-${svc}-neg" --region "$REGION" \
        --network-endpoint-type serverless --cloud-run-service "$svc"
    if ! exists gc compute backend-services describe "cr-${svc}-bs" --global; then
      gc compute backend-services create "cr-${svc}-bs" --global \
        --load-balancing-scheme EXTERNAL_MANAGED
      gc compute backend-services add-backend "cr-${svc}-bs" --global \
        --network-endpoint-group "cr-${svc}-neg" --network-endpoint-group-region "$REGION"
    fi
    gc compute backend-services update "cr-${svc}-bs" --global --iap enabled
    IFS=',' read -r -a members <<< "$IAP_MEMBERS"
    for m in "${members[@]}"; do
      gc iap web add-iam-policy-binding --resource-type backend-services \
        --service "cr-${svc}-bs" --member "$m" --role roles/iap.httpsResourceAccessor >/dev/null
    done
  done

  if ! exists gc compute url-maps describe cr-urlmap --global; then
    gc compute url-maps create cr-urlmap --global --default-service cr-frontend-bs
    gc compute url-maps add-path-matcher cr-urlmap --global --path-matcher-name api \
      --default-service cr-frontend-bs --path-rules "/api/*=cr-backend-bs" \
      --new-hosts "*"
  fi

  # Managed certs can't change domains in place — name the cert after the domain
  CERT="cr-cert-$(echo "$DOMAIN" | tr '.' '-' | cut -c1-50)"
  exists gc compute ssl-certificates describe "$CERT" --global ||
    gc compute ssl-certificates create "$CERT" --global --domains "$DOMAIN"

  if exists gc compute target-https-proxies describe cr-https-proxy --global; then
    gc compute target-https-proxies update cr-https-proxy --global --ssl-certificates "$CERT"
  else
    gc compute target-https-proxies create cr-https-proxy --global \
      --url-map cr-urlmap --ssl-certificates "$CERT"
  fi
  exists gc compute forwarding-rules describe cr-https-fr --global ||
    gc compute forwarding-rules create cr-https-fr --global \
      --load-balancing-scheme EXTERNAL_MANAGED --address cr-ip \
      --target-https-proxy cr-https-proxy --ports 443

  # HTTP → HTTPS redirect
  if ! exists gc compute url-maps describe cr-http-redirect --global; then
    gc compute url-maps import cr-http-redirect --global --source /dev/stdin <<EOF
name: cr-http-redirect
defaultUrlRedirect:
  redirectResponseCode: MOVED_PERMANENTLY_DEFAULT
  httpsRedirect: true
EOF
  fi
  exists gc compute target-http-proxies describe cr-http-proxy --global ||
    gc compute target-http-proxies create cr-http-proxy --global --url-map cr-http-redirect
  exists gc compute forwarding-rules describe cr-http-fr --global ||
    gc compute forwarding-rules create cr-http-fr --global \
      --load-balancing-scheme EXTERNAL_MANAGED --address cr-ip \
      --target-http-proxy cr-http-proxy --ports 80
}

$FULL_DEPLOY && setup

LB_IP=$(lb_ip)
DOMAIN="${DOMAIN:-${LB_IP}.nip.io}"

for step in "${STEPS[@]}"; do
  case "$step" in
    mcp-server) deploy_mcp ;;
    agents)     deploy_agents ;;
    backend)    deploy_backend ;;
    frontend)   deploy_frontend ;;
    lb)         deploy_lb ;;
    *) echo "Unknown step: $step" >&2; exit 1 ;;
  esac
done

cat <<EOF

Done. App: https://${DOMAIN}   (LB IP ${LB_IP})
  - Custom DOMAIN? Point its DNS A record at ${LB_IP} first.
  - The managed TLS cert takes 15-60 min to become ACTIVE after DNS resolves:
      gcloud compute ssl-certificates list --project ${PROJECT_ID}
  - IAP access granted to: ${IAP_MEMBERS}
EOF
