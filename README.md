# 📊 PricingIQ — Pricing Strategy Analysis Tool

A full-stack web application that helps e-commerce businesses make data-driven pricing decisions using machine learning and statistical analysis.

![PricingIQ](https://img.shields.io/badge/PricingIQ-Pricing%20Strategy%20Tool-blue)
![Python](https://img.shields.io/badge/Python-3.12-green)
![React](https://img.shields.io/badge/React-18-blue)
![Flask](https://img.shields.io/badge/Flask-3.x-lightgrey)
![XGBoost](https://img.shields.io/badge/XGBoost-ML-orange)

---

## 🚀 Live Demo

- **Frontend:** [https://pricing-strategy-tool.vercel.app](https://pricing-strategy-tool.vercel.app)
- **Backend API:** [https://pricing-strategy-tool.onrender.com](https://pricing-strategy-tool-api.onrender.com/)

---

## 💡 Problem Statement

Small e-commerce business owners often price their products based on gut feeling rather than data. This leads to:
- Lost revenue from underpricing
- Lost customers from overpricing
- No visibility into competitor pricing
- No way to simulate discount or bundling impact

**PricingIQ solves this** by letting businesses upload their sales data and instantly get AI-powered pricing recommendations.

---

## ✨ Features

### 📁 Smart Data Upload
- Upload any CSV or Excel file
- Auto-detects column names using keyword matching
- Auto-detects currency (₹, $, €, £, ¥) from data
- Manual column mapping override if needed

### 📉 Demand Elasticity Analysis
- Calculates Price Elasticity of Demand
- Tells you if customers are price sensitive or not
- Interactive Price vs Units Sold chart

### 💰 Optimal Price Finder
- Uses Linear Regression to find revenue-maximizing price
- Compares current price vs optimal price
- Shows potential revenue increase

### 🏪 Competitor Price Comparison
- Compares your average price vs competitor average
- Shows price difference percentage
- Gives actionable suggestions

### 🤖 ML-Powered Predictions
- **XGBoost** — Predicts optimal price with feature importance
- **Random Forest** — Forecasts demand at different price points
- **Facebook Prophet** — Forecasts future revenue for next 30 days
- Shows model accuracy (R² score, RMSE)

### 🎯 Revenue Simulator
- Discount simulator with elasticity slider
- Bundling simulator for 2-product bundles
- Real-time revenue impact calculation

### 🗄️ SQLite Database
- Stores all uploaded files and analysis results
- Upload history tracking
- Persistent analysis results

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| Python 3.12 | Core language |
| Flask | REST API framework |
| Flask-CORS | Cross-origin requests |
| Pandas | Data cleaning and analysis |
| NumPy | Numerical computations |
| Scikit-learn | Linear Regression, Random Forest |
| XGBoost | Price prediction ML model |
| Prophet | Time series revenue forecasting |
| SQLite | Database |
| Statsmodels | Statistical analysis |

### Frontend
| Technology | Purpose |
|---|---|
| React 18 | UI framework |
| Vite | Build tool |
| Tailwind CSS | Styling |
| Recharts | Data visualization |
| Axios | API calls |
| React Router | Navigation |

### Deployment
| Service | Purpose |
|---|---|
| Vercel | Frontend hosting |
| Render | Backend hosting |
| GitHub | Version control |

---

## 📁 Project Structure

```
pricing-strategy-tool/
│
├── backend/
│   ├── app.py                      ← Main Flask app, all routes
│   ├── config.py                   ← App settings
│   ├── requirements.txt            ← Python dependencies
│   ├── analysis/
│   │   ├── elasticity.py           ← Demand elasticity calculation
│   │   ├── optimal_price.py        ← Linear regression price finder
│   │   ├── competitor.py           ← Competitor comparison
│   │   ├── simulator.py            ← Discount & bundling simulation
│   │   ├── price_predictor.py      ← XGBoost price prediction
│   │   ├── demand_forecaster.py    ← Random Forest demand forecast
│   │   └── revenue_forecaster.py   ← Prophet revenue forecast
│   ├── models/
│   │   └── db.py                   ← SQLite setup and queries
│   ├── utils/
│   │   └── helpers.py              ← File reading, cleaning, auto-detection
│   └── data/
│       └── uploads/                ← Uploaded CSV files
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Home.jsx            ← Upload + column mapping
│   │   │   ├── Dashboard.jsx       ← Overview metrics
│   │   │   ├── Elasticity.jsx      ← Elasticity analysis
│   │   │   ├── Competitor.jsx      ← Competitor comparison
│   │   │   └── Simulator.jsx       ← Revenue simulator
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   ├── FileUpload.jsx
│   │   │   └── RecommendationCard.jsx
│   │   └── services/
│   │       └── api.js              ← All API calls
│   └── package.json
│
└── README.md
```

---

## 🔌 API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Health check |
| `/upload` | POST | Upload CSV/Excel file |
| `/analyze` | POST | Run analysis with column mapping |
| `/elasticity` | GET | Get elasticity analysis |
| `/optimal-price` | GET | Get optimal price |
| `/competitor` | GET | Get competitor comparison |
| `/simulate` | POST | Run discount/bundling simulation |
| `/ml/price-predictor` | GET | XGBoost price prediction |
| `/ml/demand-forecaster` | GET | Random Forest demand forecast |
| `/ml/revenue-forecaster` | GET | Prophet revenue forecast |
| `/history` | GET | Get upload history |
| `/history/<id>` | GET | Get analysis for specific upload |

---

## 🚦 Getting Started

### Prerequisites
- Python 3.12+
- Node.js 18+
- Git

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/adityapatil2/pricing-strategy-tool.git
cd pricing-strategy-tool/backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Run Flask server
python app.py
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run React app
npm run dev
```

### Open in Browser
```
http://localhost:5173
```

---

## 📊 Sample Data Format

Your CSV file should have at least these columns (any name works — tool auto-detects):

| Column | Description | Example |
|---|---|---|
| date | Date of sale | 2024-01-01 |
| price | Your selling price | 499.00 |
| units_sold | Units sold that day | 150 |
| competitor_price | Competitor's price | 450.00 |

Extra columns are automatically ignored.

---

## 🤖 ML Models

### XGBoost Price Predictor
- **Input:** Historical price, units sold, competitor price, time features
- **Output:** Optimal price that maximizes revenue
- **Metrics:** R² score, RMSE, feature importance

### Random Forest Demand Forecaster
- **Input:** Price, competitor price, time features, lag features
- **Output:** Predicted units sold at 20 different price points
- **Metrics:** R² score, RMSE, feature importance

### Facebook Prophet Revenue Forecaster
- **Input:** Date, revenue time series
- **Output:** 30-day revenue forecast with confidence intervals
- **Metrics:** Growth percentage, trend analysis

---

## 👨‍💻 Author

**Aditya Patil**
- GitHub: [@adityapatil2](https://github.com/adityapatil2)
- LinkedIn: [Aditya Patil](https://www.linkedin.com/in/adityasanjivpatil/)

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
