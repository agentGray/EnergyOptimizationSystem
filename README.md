# Industrial AI Energy Optimization Platform

An AI-powered industrial energy optimization system that monitors factory machines, detects electricity waste, reduces energy costs, and improves machine efficiency.

## Architecture

```
Factory Machines
→ Sensors + Smart Meters
→ PLC Controllers
→ SCADA System
→ OPC-UA / MQTT Gateway
→ AWS IoT Core
→ AWS SQS Queue
→ FastAPI Backend (AWS ECS Fargate)
→ PostgreSQL + TimescaleDB
→ AI Analytics Engine
→ Streamlit Dashboard
→ Operator Approval Layer
→ SCADA Write-back
→ Machine Control
```

## Tech Stack

- **Backend:** FastAPI (Python)
- **Database:** SQLite (local dev) / PostgreSQL + TimescaleDB (production)
- **AI Engine:** scikit-learn, numpy, pandas
- **Dashboard:** Streamlit
- **IoT:** MQTT, OPC-UA, AWS IoT Core
- **Queue:** AWS SQS
- **Deployment:** Docker, AWS ECS Fargate
- **Monitoring:** AWS CloudWatch

## Project Structure

```
├── app/                    # FastAPI backend application
│   ├── api/               # API route handlers
│   ├── models/            # SQLAlchemy database models
│   ├── schemas/           # Pydantic request/response schemas
│   ├── services/          # Business logic services
│   ├── core/              # Configuration and utilities
│   └── main.py            # FastAPI app entry point
├── ai_engine/             # AI/ML analytics engine
│   ├── anomaly_detection.py
│   ├── energy_optimizer.py
│   ├── load_forecasting.py
│   └── recommendations.py
├── iot/                   # IoT integration layer
│   ├── mqtt_subscriber.py
│   ├── aws_iot_core.py
│   ├── sqs_consumer.py
│   └── opcua_client.py
├── scada/                 # SCADA integration
│   ├── writeback.py
│   └── approval.py
├── dashboard/             # Streamlit dashboard
│   ├── app.py
│   ├── pages/
│   └── components/
├── alembic/               # Database migrations
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Quick Start (Local Development — No Docker Required)

### Prerequisites

- Python 3.10 or higher
- pip (comes with Python)
- Git

### Step-by-Step Setup

```bash
# 1. Clone the repository
git clone <repo-url>
cd EnergyOptimizationSystem

# 2. Create a virtual environment
python -m venv .venv

# 3. Activate the virtual environment
# On Windows (CMD):
.venv\Scripts\activate
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On Linux/Mac:
source .venv/bin/activate

# 4. Install all dependencies
pip install -r requirements.txt

# 5. Copy environment file
cp .env.example .env        # Linux/Mac
copy .env.example .env      # Windows CMD

# 6. Start the FastAPI Backend (Terminal 1)
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 7. Start the Streamlit Dashboard (Terminal 2 — open a new terminal)
# Activate venv first, then:
streamlit run dashboard/app.py
```

### Access the Application

| Service | URL |
|---------|-----|
| Backend API (Swagger Docs) | http://localhost:8000/docs |
| Backend API (ReDoc) | http://localhost:8000/redoc |
| Health Check | http://localhost:8000/health |
| Streamlit Dashboard | http://localhost:8501 |

### Database

By default, the project uses **SQLite** for local development — no database installation needed. The database file (`energy_optimization.db`) is created automatically when the backend starts.

For production, switch to PostgreSQL + TimescaleDB by changing `.env`:
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/energy_optimization
```

---

## Running with Docker (Production/Full Stack)

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Start all services
docker compose up -d --build

# 3. Run database migrations
docker compose exec backend alembic upgrade head

# 4. Access the application
# Backend API: http://localhost:8000/docs
# Dashboard: http://localhost:8501
```

### Docker Services

| Service | Container | Port | Description |
|---------|-----------|------|-------------|
| Database | energy_db | 5432 | PostgreSQL + TimescaleDB |
| MQTT Broker | energy_mqtt | 1883, 9001 | Eclipse Mosquitto |
| Backend | energy_backend | 8000 | FastAPI server |
| Dashboard | energy_dashboard | 8501 | Streamlit UI |
| IoT Worker | energy_iot_worker | — | Data pipeline consumer |

## Features

- **Real-time Monitoring:** Live sensor data from factory machines
- **Anomaly Detection:** AI-powered detection of energy waste patterns
- **Load Optimization:** Intelligent load dispatch and scheduling
- **Asset Health:** Predictive maintenance and health scoring
- **ESG Reporting:** ISO 50001 compliance and sustainability metrics
- **SCADA Integration:** Bi-directional communication with factory systems
- **Operator Approval:** Human-in-the-loop for critical decisions

## Dashboard Screenshots (Light Theme)

### 1. Live Dashboard
![Live Dashboard](screenshots/01_live_dashboard.svg)

**Main control center** — Shows real-time factory energy status at a glance:
- **KPI Cards:** Total Power (2,450 kW), Energy Today (18,200 kWh), Active Anomalies (3), Savings ($245.30)
- **Energy Chart:** 24-hour consumption curve vs baseline with time-axis
- **Asset Status:** Bar chart showing Running/Idle/Maintenance/Offline counts
- **Alerts Panel:** Color-coded warnings (red=critical, orange=warning, blue=info)
- **Recommendations:** Top 3 AI suggestions with estimated dollar savings
- **Energy Mix:** Grid/Solar/Battery percentage breakdown

---

### 2. Anomaly Detection
![Anomaly Detection](screenshots/02_anomaly_detection.svg)

**AI-powered waste detection** — Identifies energy anomalies in real-time:
- **Filters:** Severity, Anomaly Type, Time Range dropdowns
- **KPI Summary:** Active anomalies (7), Critical (1), Energy Waste (342 kWh/day), Cost Impact ($41.04/day)
- **Timeline Chart:** Blue anomaly score line with red threshold (0.85) and red dot markers for detected anomalies
- **Anomalies Table:** 5 active issues with Asset, Type, Severity badge (pill-shaped), Confidence %, Energy Waste, Cost, Time detected
- **Detail Panel:** Expandable view with root cause analysis, baseline vs actual comparison, and Approve/Dismiss action buttons

---

### 3. Load Dispatch & Optimization
![Load Dispatch](screenshots/03_load_dispatch.svg)

**Intelligent load management** — Optimizes when and how machines consume power:
- **KPI Cards:** Current Demand (2,450 kW), Demand Limit (3,000 kW), Peak Today (2,890 kW), Load Factor (78%)
- **Load Profile Chart:** Blue=actual consumption, Green dashed=optimized target, Red dashed=demand limit line
- **Load Shifting Table:** Assets that can move to off-peak hours (Compressor-02→$45/day, Pump-04→$22/day, Chiller-02→$58/day)
- **Savings Summary:** Daily ($312.50), Monthly ($9,375), CO₂ reduction (156 kg/day)
- **Demand Response:** Green status bar showing 92.5% achievement of 200 kW target

---

### 4. Asset Health & Monitoring
![Asset Health](screenshots/04_asset_health.svg)

**Equipment health tracking** — Predictive maintenance and status monitoring:
- **KPI Cards:** Total Assets (18), Avg Health (87.3%), Maintenance Due (2), Faults (1)
- **Asset Table:** Name, Type, Status badge (green=Running, red=Fault, yellow=Idle), Power, Health %, Efficiency, Last Maintenance
- **Fault Highlight:** Compressor-01 row highlighted in red (Health: 45%, 60 days since maintenance)
- **Maintenance Schedule:** 3 upcoming jobs with priority badges (Urgent/High/Medium) and due dates
- **Health Distribution:** Horizontal bar chart showing asset counts by health range (90-100%, 80-89%, 70-79%, <70%)

---

### 5. ESG & ISO 50001 Reporting
![ESG Reporting](screenshots/05_esg_reporting.svg)

**Sustainability & compliance** — Carbon tracking and regulatory reporting:
- **KPI Cards:** CO₂ Emissions (4,250 kg ▼-320), Energy Intensity (0.42 kWh/unit), Renewable % (25%), ISO 50001 Score (78.5%)
- **Carbon Trend Chart:** 12-month declining emissions line (green) with orange target line
- **ISO 50001 Checklist:** 7 requirements with status (✅ Complete, ⚠️ In Progress, ❌ Pending) and percentage scores
- **Year-over-Year:** Three progress bars — Energy Reduction (12.3%/15%), CO₂ Reduction (18.5%/20%), Cost Savings ($142K/$150K)
- **Energy Sources:** Horizontal bars — Grid 60%, Solar 25%, Battery 10%, Gas 5%

## Workflow

### 1. Data Ingestion Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FACTORY FLOOR                                 │
│                                                                     │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐       │
│  │ Chiller  │   │  HVAC    │   │Compressor│   │  Pump    │       │
│  │          │   │          │   │          │   │          │       │
│  └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘       │
│       │               │               │               │             │
│  ┌────▼─────────────────────────────────────────────▼────┐         │
│  │              Sensors + Smart Meters                     │         │
│  │  (Temperature, Pressure, Voltage, Current, Power)      │         │
│  └────────────────────────┬───────────────────────────────┘         │
│                           │                                         │
│  ┌────────────────────────▼───────────────────────────────┐         │
│  │                PLC Controllers                          │         │
│  └────────────────────────┬───────────────────────────────┘         │
│                           │                                         │
│  ┌────────────────────────▼───────────────────────────────┐         │
│  │                 SCADA System                            │         │
│  └────────────────────────┬───────────────────────────────┘         │
└───────────────────────────┼─────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     IoT GATEWAY LAYER                                │
│                                                                     │
│  ┌─────────────────┐              ┌─────────────────┐              │
│  │   MQTT Gateway  │              │  OPC-UA Gateway  │              │
│  │   (Port 1883)   │              │   (Port 4840)    │              │
│  └────────┬────────┘              └────────┬─────────┘              │
└───────────┼────────────────────────────────┼────────────────────────┘
            │                                │
            ▼                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        AWS CLOUD                                     │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │                  AWS IoT Core                            │       │
│  │           (MQTT Broker + TLS Auth)                       │       │
│  └────────────────────────┬────────────────────────────────┘       │
│                           │                                         │
│  ┌────────────────────────▼───────────────────────────────┐         │
│  │               AWS SQS Queue                             │         │
│  │        (Reliable message buffering)                     │         │
│  └────────────────────────┬───────────────────────────────┘         │
│                           │                                         │
│  ┌────────────────────────▼───────────────────────────────┐         │
│  │            FastAPI Backend (ECS Fargate)                 │         │
│  │                                                         │         │
│  │  ┌──────────┐  ┌───────────┐  ┌──────────────────┐    │         │
│  │  │ API Layer│  │ Services  │  │  Data Pipeline   │    │         │
│  │  └──────────┘  └───────────┘  └──────────────────┘    │         │
│  └────────────────────────┬───────────────────────────────┘         │
│                           │                                         │
│  ┌────────────────────────▼───────────────────────────────┐         │
│  │         PostgreSQL + TimescaleDB                        │         │
│  │    (Operational data + Time-series hypertables)         │         │
│  └────────────────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────────────┘
```

### 2. AI Analysis & Optimization Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                      AI ENGINE                                       │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │              Anomaly Detection                           │       │
│  │                                                         │       │
│  │  ┌──────────┐  ┌───────────────┐  ┌───────────────┐   │       │
│  │  │ Z-Score  │  │Isolation Forest│  │Pattern Rules  │   │       │
│  │  │Detection │  │  (ML-based)   │  │(Domain Logic) │   │       │
│  │  └──────────┘  └───────────────┘  └───────────────┘   │       │
│  └──────────────────────────┬──────────────────────────────┘       │
│                             │                                       │
│  Detected Anomalies:        │                                       │
│  • Phantom Loads            │                                       │
│  • HVAC Overcooling         │                                       │
│  • Air Leaks                │                                       │
│  • Voltage Imbalance        │                                       │
│  • Furnace Cycling          │                                       │
│  • Power Spikes             │                                       │
│                             ▼                                       │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │             Energy Optimizer                             │       │
│  │                                                         │       │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │       │
│  │  │Load Shifting │  │Peak Shaving  │  │ Setpoint    │  │       │
│  │  │(Off-peak)    │  │(Demand Limit)│  │ Adjustment  │  │       │
│  │  └──────────────┘  └──────────────┘  └─────────────┘  │       │
│  │  ┌──────────────┐  ┌──────────────┐                    │       │
│  │  │Equipment     │  │Efficiency    │                    │       │
│  │  │Scheduling    │  │Optimization  │                    │       │
│  │  └──────────────┘  └──────────────┘                    │       │
│  └──────────────────────────┬──────────────────────────────┘       │
│                             │                                       │
│                             ▼                                       │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │            Load Forecasting                             │       │
│  │  (Predict future demand using historical patterns)      │       │
│  └──────────────────────────┬──────────────────────────────┘       │
│                             │                                       │
│                             ▼                                       │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │          Recommendation Engine                          │       │
│  │  (Generate actionable SCADA commands with savings)      │       │
│  └──────────────────────────┬──────────────────────────────┘       │
└─────────────────────────────┼───────────────────────────────────────┘
                              │
                              ▼
```

### 3. Approval & Execution Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                OPERATOR APPROVAL WORKFLOW                            │
│                                                                     │
│        ┌──────────────────────────────────────┐                    │
│        │    AI Recommendation Generated       │                    │
│        └───────────────────┬──────────────────┘                    │
│                            │                                        │
│                            ▼                                        │
│        ┌──────────────────────────────────────┐                    │
│        │     Risk Assessment                  │                    │
│        │  (Low / Medium / High / Critical)    │                    │
│        └───────────┬──────────────┬───────────┘                    │
│                    │              │                                  │
│          Low Risk  │              │  Medium/High Risk                │
│          + High    │              │                                  │
│          Confidence│              │                                  │
│                    ▼              ▼                                  │
│        ┌────────────────┐  ┌──────────────────────────┐            │
│        │ Auto-Approve   │  │ Operator Dashboard       │            │
│        │ (Non-critical  │  │                          │            │
│        │  assets only)  │  │  ┌────────┐ ┌────────┐  │            │
│        └───────┬────────┘  │  │Approve │ │Reject  │  │            │
│                │           │  └───┬────┘ └───┬────┘  │            │
│                │           └──────┼──────────┼───────┘            │
│                │                  │          │                      │
│                ▼                  ▼          ▼                      │
│        ┌────────────────────────────┐  ┌──────────┐               │
│        │    Safety Checks           │  │ Logged & │               │
│        │  • Command validation      │  │ Archived │               │
│        │  • Parameter limits        │  └──────────┘               │
│        │  • Rate limiting           │                              │
│        │  • Asset type rules        │                              │
│        └───────────────┬────────────┘                              │
│                        │                                            │
│                        ▼                                            │
│        ┌──────────────────────────────────────┐                    │
│        │       SCADA Write-back               │                    │
│        │                                      │                    │
│        │  ┌────────────┐  ┌────────────┐     │                    │
│        │  │  OPC-UA    │  │   MQTT     │     │                    │
│        │  │  Protocol  │  │  Protocol  │     │                    │
│        │  └─────┬──────┘  └─────┬──────┘     │                    │
│        └────────┼───────────────┼─────────────┘                    │
│                 │               │                                    │
└─────────────────┼───────────────┼────────────────────────────────────┘
                  │               │
                  ▼               ▼
┌─────────────────────────────────────────────────────────────────────┐
│              FACTORY EQUIPMENT CONTROL                               │
│                                                                     │
│  • Adjust HVAC setpoints        • Start/Stop equipment              │
│  • Reduce compressor load       • Shift loads to off-peak           │
│  • Dim lighting systems         • Adjust motor speeds               │
│  • Optimize furnace cycles      • Control pump flow rates           │
└─────────────────────────────────────────────────────────────────────┘
```

### 4. Dashboard & Monitoring Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                   STREAMLIT DASHBOARD                                │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │  🏠 Live Dashboard                                      │       │
│  │  Real-time power consumption, alerts, KPIs              │       │
│  └─────────────────────────────────────────────────────────┘       │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │  🔍 Anomaly Detection                                   │       │
│  │  Active anomalies, timeline, severity, root causes      │       │
│  └─────────────────────────────────────────────────────────┘       │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │  ⚖️ Load Dispatch                                       │       │
│  │  Load profile, optimization strategies, demand response │       │
│  └─────────────────────────────────────────────────────────┘       │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │  🏭 Asset Health                                        │       │
│  │  Health scores, maintenance schedule, status overview   │       │
│  └─────────────────────────────────────────────────────────┘       │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │  🌱 ESG & ISO 50001                                     │       │
│  │  Carbon emissions, compliance, year-over-year progress  │       │
│  └─────────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────────┘
```

### 5. End-to-End Data Flow Summary

```
Step 1: Machine sensors generate readings (every 5 seconds)
         ↓
Step 2: PLC collects sensor data from multiple sensors
         ↓
Step 3: SCADA aggregates PLC data and provides supervisory view
         ↓
Step 4: IoT Gateway converts data to MQTT/OPC-UA messages
         ↓
Step 5: AWS IoT Core receives messages (TLS encrypted, cert auth)
         ↓
Step 6: IoT Rules forward messages to AWS SQS queue
         ↓
Step 7: FastAPI backend consumes SQS messages (batch processing)
         ↓
Step 8: Data validated, enriched, and stored in TimescaleDB
         ↓
Step 9: AI Engine runs periodic analysis:
         • Anomaly detection (every 5 minutes)
         • Optimization analysis (every 15 minutes)
         • Load forecasting (every hour)
         ↓
Step 10: Recommendations generated with estimated savings
         ↓
Step 11: Operator reviews on Streamlit dashboard
         ↓
Step 12: Approved commands sent to SCADA via write-back
         ↓
Step 13: Equipment adjusts operation (setpoints, scheduling)
         ↓
Step 14: Savings tracked and reported in ESG dashboard
```
