
# ModelChain - AI Model Trust Layer

A blockchain-based trust layer for AI model routing that provides transparency and accountability in AI model selection and performance tracking.

## 🎯 Project Overview

ModelChain addresses trust challenges in AI model routing by:
- Verifying model capabilities through a decentralized registry
- Ensuring fair model selection with transparent routing decisions
- Holding models accountable for performance promises through staking and slashing
- Maintaining dynamic trust scores based on real performance metrics

## 🏗️ Architecture

### Backend (FastAPI)
- **Model Registry**: Decentralized registry for AI model registration
- **Routing Audit Trail**: Transparent routing decision tracking
- **Performance Tracking**: Monitor model performance vs promises
- **Trust Score System**: Dynamic reputation based on performance
- **Blockchain Integration**: Simulated blockchain for transparency

### Frontend (React + TypeScript)
- **Dashboard**: Real-time overview of system metrics
- **Model Registry**: Register and verify AI models
- **Routing Audit**: Test and monitor routing decisions
- **Performance Tracking**: Report and view model performance
- **Trust Scores**: Visualize model reputation scores

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the FastAPI server:
```bash
python main.py
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 📊 Key Features

### 1. Model Registry
- Register AI models with capability declarations
- Stake tokens as quality guarantee
- Get verified status after testing
- View all registered models and their status

### 2. Routing Audit Trail
- Test routing with sample queries
- View routing statistics
- Commit routing batches to blockchain
- Transparent routing decisions with blockchain proof

### 3. Performance Tracking
- Report model performance metrics
- Track latency, success rate, and uptime
- Monitor violations
- Historical performance data

### 4. Trust Score System
- Dynamic reputation scores (0-100)
- Based on:
  - Performance (40%): Meets latency/quality promises
  - Reliability (30%): Uptime and success rate
  - Usage (20%): How often selected by router
  - Age (10%): How long in the system
- Visual score breakdown and trends

## 🔌 API Endpoints

### Model Registry
- `POST /api/models/register` - Register a new model
- `GET /api/models` - Get all registered models
- `GET /api/models/{model_id}` - Get specific model info
- `POST /api/models/{model_id}/verify` - Verify a model

### Routing
- `POST /api/route` - Route a query to the best model
- `GET /api/routing/stats` - Get routing statistics
- `POST /api/routing/commit-batch` - Commit routing batch to blockchain

### Performance
- `POST /api/performance/report` - Report model performance
- `GET /api/performance/{model_id}` - Get model performance records

### Trust Scores
- `GET /api/trust-scores` - Get all trust scores
- `GET /api/trust-scores/{model_id}` - Get specific model trust score

## 📝 Project Structure

```
project/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic models
│   ├── database.py          # Database configuration
│   ├── blockchain_service.py # Blockchain simulation
│   ├── router_service.py    # Routing logic
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   ├── App.tsx         # Main app component
│   │   └── main.tsx        # Entry point
│   ├── package.json        # Node dependencies
│   └── vite.config.ts      # Vite configuration
└── README.md              # This file
```

## 🎓 Learning Outcomes

Students working on this project will learn:
- Blockchain + AI Integration
- Decentralized Registries
- Cryptographic Commitments (Merkle trees)
- Economic Incentives (Staking and Slashing)
- Oracle Design (Bridging on-chain/off-chain worlds)

## 🔐 Security Considerations

In production, this system would need:
- Real blockchain integration (Ethereum, Polygon, etc.)
- Secure key management
- Proper authentication and authorization
- Rate limiting and DDoS protection
- Input validation and sanitization

## 📄 License

This project is for educational purposes.
