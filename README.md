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
