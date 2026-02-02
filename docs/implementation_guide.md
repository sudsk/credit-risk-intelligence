# Complete MVP Implementation Guide

## 📁 Project Structure

```
foresight-ai-demo/
├── data/                           # CSV data files (already created)
│   ├── smes.csv                    # 100 SMEs with risk scores
│   ├── employees.csv               # Employee counts & trends
│   ├── departures.csv              # Employee departures
│   ├── web_traffic.csv             # Website analytics
│   ├── company_info.csv            # Companies House data
│   ├── news_events.csv             # News & events
│   └── financial_data.csv          # Financial metrics
│
├── mcp-servers/                    # MCP servers (CSV-backed)
│   ├── linkedin_server.py          # ✅ Created
│   ├── web_traffic_server.py       # ✅ Created
│   ├── companies_house_server.py   # TODO
│   ├── news_server.py              # TODO
│   ├── financial_server.py         # TODO
│   └── payment_data_server.py      # TODO
│
├── backend/                        # FastAPI backend
│   ├── main.py                     # FastAPI app
│   ├── services/
│   │   ├── portfolio_service.py    # Portfolio analytics
│   │   ├── risk_engine.py          # Risk calculation (✅ Methodology documented)
│   │   ├── scenario_service.py     # Scenario analysis
│   │   └── chat_service.py         # AI chat integration
│   ├── routes/
│   │   ├── portfolio.py            # Portfolio endpoints
│   │   ├── scenarios.py            # Scenario endpoints
│   │   └── chat.py                 # Chat endpoints
│   └── models/
│       ├── sme.py                  # SME data models
│       └── scenario.py             # Scenario models
│
├── frontend/                       # React/Next.js frontend
│   ├── pages/
│   │   ├── index.tsx               # Landing page
│   │   ├── dashboard.tsx           # Main dashboard
│   │   └── scenarios.tsx           # Scenario analysis
│   ├── components/
│   │   ├── PortfolioMetrics.tsx    # Metrics cards
│   │   ├── SMEList.tsx             # SME table
│   │   ├── SMEDetail.tsx           # SME detail panel
│   │   ├── Chat.tsx                # Chat interface
│   │   └── ScenarioBuilder.tsx     # Scenario builder
│   └── lib/
│       └── api.ts                  # API client
│
├── docs/
│   └── CREDIT_RISK_METHODOLOGY.md  # ✅ Created - Comprehensive risk model
│
├── requirements.txt                # Python dependencies
├── package.json                    # Node dependencies
└── README.md                       # Project README
```

---

## 🎯 Implementation Phases

### **Phase 1: Data & MCP Servers** (Week 1)
**Status:** 70% Complete

#### ✅ Completed:
1. All 7 CSV files with comprehensive data
2. LinkedIn MCP server (employees + departures)
3. Web Traffic MCP server (analytics)
4. Credit Risk Methodology document

#### 🔨 TODO:
1. Companies House MCP server
2. News Intelligence MCP server
3. Financial Data MCP server
4. Payment Data MCP server

---

### **Phase 2: Backend Services** (Week 1-2)
#### Core Services to Build:

**1. Risk Engine (`backend/services/risk_engine.py`)**
```python
class RiskEngine:
    """
    Implements the credit risk calculation from CREDIT_RISK_METHODOLOGY.md
    """
    
    def calculate_risk_score(self, sme_id: str) -> dict:
        # Step 1: Gather data from all MCP servers
        financial_data = await financial_mcp.get_metrics(sme_id)
        employee_data = await linkedin_mcp.get_employee_trend(sme_id)
        traffic_data = await web_traffic_mcp.get_traffic_trend(sme_id)
        news_data = await news_mcp.get_recent_events(sme_id)
        
        # Step 2: Calculate component scores
        financial_score = self._calc_financial_score(financial_data)
        operational_score = self._calc_operational_score(financial_data)
        market_score = self._calc_market_score(sme_id)
        alt_data_score = self._calc_alt_data_score(
            employee_data, traffic_data, news_data
        )
        
        # Step 3: Weighted composite
        risk_score = (
            financial_score * 0.40 +
            operational_score * 0.25 +
            market_score * 0.20 +
            alt_data_score * 0.15
        )
        
        # Step 4: Calculate default probability
        pd_12m = self._calc_default_probability(risk_score, financial_data)
        
        return {
            "risk_score": round(risk_score),
            "risk_category": self._get_category(risk_score),
            "default_probability_12m": pd_12m,
            "components": {
                "financial": financial_score,
                "operational": operational_score,
                "market": market_score,
                "alternative_data": alt_data_score
            }
        }
```

**2. Portfolio Service (`backend/services/portfolio_service.py`)**
```python
class PortfolioService:
    def get_portfolio_summary(self) -> dict:
        # Read from smes.csv
        smes_df = pd.read_csv('data/smes.csv')
        
        return {
            "total_exposure": smes_df['exposure'].sum(),
            "total_smes": len(smes_df),
            "risk_distribution": {
                "critical": len(smes_df[smes_df['risk_category'] == 'critical']),
                "medium": len(smes_df[smes_df['risk_category'] == 'medium']),
                "stable": len(smes_df[smes_df['risk_category'] == 'stable'])
            },
            "avg_risk_score": smes_df['risk_score'].mean()
        }
    
    def get_sme_detail(self, sme_id: str) -> dict:
        # Aggregate data from all sources
        # Call MCP servers to enrich data
        pass
```

**3. Scenario Service (`backend/services/scenario_service.py`)**
```python
class ScenarioService:
    def run_scenario(self, scenario_type: str, parameters: dict) -> dict:
        """
        Run stress test scenarios:
        - Interest rate changes
        - Sector-specific shocks
        - Economic downturn
        - Regulatory changes
        """
        if scenario_type == "interest_rate":
            return self._simulate_interest_rate_shock(parameters)
        elif scenario_type == "sector_shock":
            return self._simulate_sector_shock(parameters)
        elif scenario_type == "recession":
            return self._simulate_recession(parameters)
```

---

### **Phase 3: Frontend** (Week 2)
#### Key Components:

**Dashboard Layout:**
```
┌─────────────────────────────────────────────────────┐
│  Portfolio Metrics Cards                            │
│  [Total Exposure] [Risk Distribution] [Avg Score]   │
├─────────────────────────────────────────────────────┤
│  SME List (Table)                   │ SME Detail    │
│  - Risk Score                       │ Panel         │
│  - Exposure                         │               │
│  - Trend                            │ • Financials  │
│  - Sector                           │ • Alt Data    │
│                                     │ • News        │
│                                     │ • Chart       │
├─────────────────────────────────────┴───────────────┤
│  Chat Interface                                     │
│  "Show me SMEs with declining web traffic"         │
└─────────────────────────────────────────────────────┘
```

---

## 🔧 Quick Start Commands

### 1. **Setup CSV Data**
```bash
# Data already created in /mnt/user-data/outputs/data/
cp -r /mnt/user-data/outputs/data ./
```

### 2. **Run MCP Servers**
```bash
# Install dependencies
pip install mcp pandas

# Run servers
python mcp-servers/linkedin_server.py
python mcp-servers/web_traffic_server.py
# ... etc
```

### 3. **Run Backend**
```bash
cd backend
pip install fastapi uvicorn pandas
uvicorn main:app --reload
```

### 4. **Run Frontend**
```bash
cd frontend
npm install
npm run dev
```

---

## 📊 Credit Risk Calculation - Quick Reference

### Risk Score Formula:
```
Risk Score = Financial(40%) + Operational(25%) + Market(20%) + AltData(15%)
```

### Risk Categories:
- **0-35**: Stable (Green)
- **35-60**: Medium (Yellow)
- **60-100**: Critical (Red)

### Default Probability:
```python
PD = 1 / (1 + e^(-z))
where z = -5.2 + 0.12(Risk_Score) + sector_adj + size_adj

# Then apply alternative data multipliers
if critical_news: PD *= 1.5
if c_level_departure: PD *= 1.3
if traffic_decline_40%: PD *= 1.4
```

### Key Alternative Data Signals:
1. **Employee Departures** (6-8 week lead)
   - C-level departure = +25 risk points
   - VP departures (2+) = +15 risk points

2. **Web Traffic Decline** (4-6 week lead)
   - -40% QoQ = +65 risk points (critical)
   - -25% QoQ = +45 risk points (high)

3. **Payment Delays** (2-4 week lead)
   - 45+ days average = +55 risk points
   - Trend increasing = +20 risk points

4. **News Sentiment**
   - Litigation/compliance = +20 risk points
   - Multiple critical events = +40 risk points

---

## 🚀 Next Steps

1. **Finish remaining MCP servers** (4 more)
2. **Build FastAPI backend** with 3 core services
3. **Create React frontend** with dashboard + chat
4. **Test end-to-end** workflow
5. **Deploy** (optional: Vercel + Railway)

---

## 📦 Dependencies

### Python (backend + MCP servers):
```txt
fastapi==0.104.1
uvicorn==0.24.0
pandas==2.1.3
numpy==1.26.2
mcp==0.1.0
pydantic==2.5.0
python-multipart==0.0.6
websockets==12.0
```

### Node (frontend):
```json
{
  "dependencies": {
    "next": "14.0.3",
    "react": "18.2.0",
    "react-dom": "18.2.0",
    "recharts": "2.10.0",
    "lucide-react": "0.294.0",
    "tailwindcss": "3.3.5"
  }
}
```

---

## 💡 Demo Flow

### User Journey:
1. **Land on dashboard** → See portfolio overview
2. **Click SME** → View detailed risk profile with alt data
3. **Ask chatbot** → "Which SMEs had recent C-level departures?"
4. **Run scenario** → "What if interest rates rise 2%?"
5. **Export report** → Generate PDF with findings

### Key Value Props to Demonstrate:
- ✅ **6-8 week early warning** from alternative data
- ✅ **Real-time risk monitoring** vs quarterly reviews
- ✅ **Comprehensive data integration** (6 sources)
- ✅ **AI-powered insights** via chat
- ✅ **Scenario analysis** for proactive planning

---

## 📄 Files Already Created

✅ `/mnt/user-data/outputs/data/smes.csv` (100 SMEs)
✅ `/mnt/user-data/outputs/data/employees.csv` (Employee trends)
✅ `/mnt/user-data/outputs/data/departures.csv` (Leadership exits)
✅ `/mnt/user-data/outputs/data/web_traffic.csv` (Analytics)
✅ `/mnt/user-data/outputs/data/company_info.csv` (Companies House)
✅ `/mnt/user-data/outputs/data/news_events.csv` (News intelligence)
✅ `/mnt/user-data/outputs/data/financial_data.csv` (Financial metrics)
✅ `/mnt/user-data/outputs/CREDIT_RISK_METHODOLOGY.md` (Risk model)
✅ `/mnt/user-data/outputs/mcp-servers/linkedin_server.py`
✅ `/mnt/user-data/outputs/mcp-servers/web_traffic_server.py`

---

## 🎯 Success Metrics

The demo should showcase:
1. **Accuracy**: 87% prediction accuracy (from methodology)
2. **Speed**: 6-8 week earlier detection than traditional methods
3. **Coverage**: 6 data sources integrated
4. **Actionability**: Clear risk scores + recommended actions
5. **Usability**: Intuitive dashboard + natural language chat

---

**Ready to implement! Next step: Complete remaining 4 MCP servers and FastAPI backend.**