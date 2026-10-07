# Frontend — build from repo root: docker build -f frontend/Dockerfile --build-arg VITE_API_URL=... .
FROM node:20-alpine AS build

WORKDIR /app

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ .

# Vite inlines this at build time
ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}
RUN npx vite build

FROM nginx:1.27-alpine
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 8080
