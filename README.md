# CropVerse 🌱

> **Smart Environment Monitoring for Precision Agriculture**




## 🎯 Key Features

### 🔌 Secure Device Integration
- **Authenticated device onboarding** with unique credentials for each sensor node
- **Resilient data ingestion** tolerating intermittent connectivity and network issues
- **Compact JSON protocol** optimized for low-bandwidth IoT environments
- **Batch and real-time submission** support for flexible deployment scenarios

### 📊 Real-Time Monitoring & Analytics
- **Live dashboard updates** via Firebase real-time listeners
- **Time-series trend analysis** with configurable aggregation windows (minute/hour/day)
- **Statistical anomaly detection** using moving averages and z-score analysis
- **Cross-sensor correlation matrices** to identify environmental relationships
- **Pre-computed aggregations** for instant historical query performance

### 🚨 Intelligent Alerting System
- **Multi-tier threshold configuration** (info/warning/critical severity levels)
- **Dynamic thresholding with hysteresis** to prevent alert flapping
- **Complete alert lifecycle management** (acknowledgement, escalation, auto-closure)
- **Multi-channel notifications** via email, SMS, and push notifications
- **Smart grouping and throttling** to reduce operator alert fatigue

### 🤖 AI-Powered Operational Assistant
- **Context-aware chatbot** seeded with current system state and recent events
- **Guided troubleshooting workflows** for rapid issue resolution
- **Natural language queries** for system data and historical trends
- **Proactive recommendations** based on detected patterns and anomalies

### 🔐 Enterprise Security & Access Control
- **Firebase Authentication integration** for secure user identity management
- **Role-based access control** (operator/admin) with granular permissions
- **Firestore security rules** enforcing data access policies
- **Comprehensive audit logging** for compliance and traceability

### 📈 Advanced Data Management
- **Schema validation** ensuring data consistency and quality
- **Sanity checks** filtering malformed or spurious readings
- **UTC timestamp normalization** with timezone-aware reporting
- **Optimized indexing strategy** balancing performance and cost
- **Configurable retention policies** for long-term data archival

---

## 🏗️ System Architecture

```
┌─────────────────┐
│  IoT Sensors    │  (Arduino-based nodes)
│  Temperature    │
│  Humidity       │
│  Gas Detection  │
└────────┬────────┘
         │ HTTPS/JSON
         ▼
┌─────────────────────────────────────────────────────┐
│           Firebase Cloud Functions                  │
│  ┌──────────────┐  ┌─────────────┐  ┌───────────┐ │
│  │  Ingestion   │  │ Analytics   │  │  Alerts   │ │
│  │  Service     │  │ Service     │  │  Service  │ │
│  └──────┬───────┘  └──────┬──────┘  └─────┬─────┘ │
│         │                  │                │       │
│         └──────────────────┼────────────────┘       │
│                            ▼                        │
│                    ┌──────────────┐                 │
│                    │   Firestore  │                 │
│                    │   Database   │                 │
│                    └──────┬───────┘                 │
└───────────────────────────┼─────────────────────────┘
                            │ Real-time Sync
                            ▼
                ┌─────────────────────┐
                │   Web Dashboard     │
                │  - Live Monitoring  │
                │  - Analytics Views  │
                │  - AI Chatbot       │
                │  - Alert Management │
                └─────────────────────┘
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9 or higher
- Node.js 16+ (for frontend development)
- Firebase CLI
- Arduino IDE (for device firmware)

### Backend Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/cropverse-firebase.git
cd cropverse-firebase
```

2. **Install dependencies**
```bash
cd functions
pip install -r requirements.txt
```

3. **Configure Firebase**
```bash
firebase login
firebase init
```

4. **Set environment variables**
```bash
cp .env.example .env.yaml
# Edit .env.yaml with your Firebase credentials and API keys
```

5. **Deploy to Firebase**
```bash
firebase deploy --only functions
```

### Frontend Setup

1. **Navigate to public directory**
```bash
cd public
```

2. **Configure Firebase**
Edit `js/firebase-config.js` with your Firebase project credentials:
```javascript
const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_AUTH_DOMAIN",
  projectId: "YOUR_PROJECT_ID",
  // ...
};
```

3. **Serve locally**
```bash
firebase serve
```

4. **Deploy**
```bash
firebase deploy --only hosting
```

### Device Setup

1. **Flash Arduino firmware**
- Open `arduino/sensor_node/sensor_node.ino` in Arduino IDE
- Configure WiFi credentials and API endpoint
- Upload to your Arduino board

2. **Register device**
- Use the admin dashboard to register new devices
- Note the device credentials for configuration

---

## 📚 API Documentation

### Core Endpoints

#### Analytics
- `GET /api/analytics/correlations` - Correlation matrix across sensors
- `GET /api/analytics/summary` - Daily summaries and aggregations
- `POST /api/analytics/summary/<date>/calculate` - Trigger recalculation
- `GET /api/analytics/trends` - Time-series data for trends

#### Device Integration
- `POST /api/arduino/data` - Receive sensor telemetry
- `GET /api/arduino/health` - Device connectivity check
- `POST /api/arduino/test` - Verify device authentication

#### Dashboard
- `GET /api/dashboard` - Complete dashboard payload
- `GET /api/dashboard/alerts` - Alert list with filters
- `GET /api/dashboard/readings` - Latest sensor readings

#### AI Chatbot
- `POST /api/chatbot/message` - Send message and receive AI response
- `GET /api/chatbot/context` - Current system context
- `GET /api/chatbot/suggestions` - Suggested prompts

#### Settings & Thresholds
- `GET /api/settings/thresholds` - Retrieve alert thresholds
- `PUT /api/settings/thresholds` - Update threshold configuration
- `POST /api/settings/reset` - Reset to default settings

For complete API documentation, see [BACKEND_API_DOCS.md](docs/BACKEND_API_DOCS.md)

---

## 🧪 Testing & Development

### Simulate Sensor Data
```bash
python scripts/simulate_arduino.py --count 100 --interval 5
```

### Analyze Backend Health
```bash
python scripts/analyze_backend.py
```

### Seed Test Data
```bash
python scripts/seed_firestore.py --dataset sample_farm
```

### Run Tests
```bash
pytest tests/ --cov=functions
```

---

## 👥 Team

CropVerse is developed by a dedicated cross-functional team:

| Role | Name | Responsibilities |
|------|------|------------------|
| 🎯 **Project Lead & Backend** | **Priya Sharma** | System architecture, core backend services, analytics orchestration |
| 📊 **Data & Analytics** | **Rahul Kulkarni** | Aggregation pipelines, trend analysis, anomaly detection |
| 🎨 **Frontend Lead** | **Meera Desai** | Dashboard UX, data visualization, real-time client integration |
| 🔧 **Embedded Systems** | **Arjun Patil** | Device firmware, telemetry protocols, hardware diagnostics |
| 🤖 **AI & Chatbot** | **Sneha Rao** | AI assistant integration, prompt engineering, conversational flows |
| 🔐 **DevOps & Security** | **Karan Verma** | Deployment automation, security rules, operational best practices |

---

## 🏆 Achievements

**Smart India Hackathon 2025 Finalist** - Selected among thousands of submissions nationwide for innovative approach to agricultural technology and sustainability.

---

## 📖 Documentation

- [Frontend Integration Guide](docs/FRONTEND_INTEGRATION_GUIDE.md)
- [Backend API Reference](docs/BACKEND_API_DOCS.md)
- [Device Integration Manual](docs/DEVICE_INTEGRATION.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Security Best Practices](docs/SECURITY.md)

---

## 🤝 Contributing

We welcome contributions from the community! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Contact & Support

For questions, feature requests, or partnership opportunities:

- **GitHub Issues**: [Create an issue](https://github.com/yourusername/cropverse-firebase/issues)
- **Email**: cropverse.team@example.com
- **Documentation**: [Read the docs](https://cropverse.example.com/docs)

---

## 🙏 Acknowledgments

- Smart India Hackathon 2025 organizing committee
- Firebase and Google Cloud Platform teams
- Open-source community for invaluable tools and libraries
- Agricultural experts who provided domain guidance

