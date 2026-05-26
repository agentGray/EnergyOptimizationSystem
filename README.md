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
- **Database:** PostgreSQL + TimescaleDB
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

## Quick Start

```bash
# 1. Clone the repository
git clone <repo-url>
cd EnergyOptimizationSystem

# 2. Copy environment file
cp .env.example .env

# 3. Start with Docker Compose
docker-compose up -d

# 4. Run database migrations
docker-compose exec backend alembic upgrade head

# 5. Access the application
# Backend API: http://localhost:8000/docs
# Dashboard: http://localhost:8501
```

## Features

- **Real-time Monitoring:** Live sensor data from factory machines
- **Anomaly Detection:** AI-powered detection of energy waste patterns
- **Load Optimization:** Intelligent load dispatch and scheduling
- **Asset Health:** Predictive maintenance and health scoring
- **ESG Reporting:** ISO 50001 compliance and sustainability metrics
- **SCADA Integration:** Bi-directional communication with factory systems
- **Operator Approval:** Human-in-the-loop for critical decisions

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
