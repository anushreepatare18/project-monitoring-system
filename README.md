# PRAGYA AI — AI-Powered Infrastructure Project Monitoring System

PRAGYA AI is a comprehensive, predictive project-monitoring intelligence platform built for government ministries, monitoring officers, and implementing agencies. It aims to reduce delays, minimize cost overruns, and improve accountability in infrastructure projects through real-time tracking, AI-driven risk triage, anomaly detection, and transparent public reporting.

## Technology Stack
- **Frontend:** Next.js (React), Tailwind CSS, Recharts (Data Visualization), Lucide React (Icons)
- **Backend:** FastAPI (Python), SQLite (via SQLAlchemy)
- **AI/ML:** SHAP (Explainable AI), Pandas, Scikit-learn (Risk Inference Engine), Google Gemini (Grounded Chatbot Assistant)

## Prerequisites
- Node.js v18+ 
- Python 3.9+ 
- npm or yarn

## Installation

1. **Clone the repository and install frontend dependencies:**
   ```bash
   npm install
   ```

2. **Set up the backend environment:**
   Ensure you have Python installed. Navigate to the project root and create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r backend/requirements.txt
   ```
   *(Note: Ensure requirements like fastapi, uvicorn, sqlalchemy, pandas, shap are installed.)*

## Environment Setup
Create a `.env` file in the root directory (you can use `.env.example` if available) and configure the following variables:
```
# .env
GEMINI_API_KEY=your_google_gemini_api_key_here
```
*Note: Do not commit `.env` containing your actual API keys. The Gemini API key is required only for the PRAGYA Assistant Chatbot functionality.*

## How to Run

1. **Start the Backend API Server:**
   From the project root, start the FastAPI server on port 8000:
   ```bash
   uvicorn backend.main:app --reload
   ```

2. **Start the Frontend Development Server:**
   In a new terminal window, start the Next.js server:
   ```bash
   npm run dev
   ```

3. **Access the application:**
   Open your browser and navigate to `http://localhost:3000`.

## Demo Login Instructions
The prototype includes mock role-based authentication. Use the following credentials to explore different workflows:

- **System Admin:**
  - Username: `admin`
  - Password: `admin`
- **Monitoring Officer:**
  - Username: `officer_1` (or any starting with "officer")
  - Password: `any_password`
- **Implementing Agency:**
  - Username: `agency_nhai` (or any starting with "agency")
  - Password: `any_password`
- **Public Visitor:** No login required. Click "Public Dashboard" from the login screen or navigate to `/dashboard/public`.

## Available Features
- **Role-Based Dashboards:** Distinct workflows for Agencies, Ministry Officials, Monitoring Officers, and Public Citizens.
- **Explainable AI (XAI):** Predictive risk scoring (delay/cost) with SHAP value visual explanations indicating *why* a project is flagged.
- **Anomaly Detection:** Rule-based and predictive cross-checking (e.g., Financial vs. Physical progress anomalies).
- **Public Transparency Portal:** A highly restricted, read-only view of approved datasets.
- **PRAGYA Assistant:** A grounded NLP chatbot capable of answering dataset-specific questions securely.
- **Alert Triage Workflow:** End-to-end alert handling for monitoring officers and agencies.

## Data and AI Limitations
- **Data Source:** The system currently utilizes a synthetic, localized dataset (`dataset.csv` and `pragya.db`) strictly for prototype demonstration. It is not currently connected to live government systems (e.g., PAIMANA).
- **AI Models:** The ML risk model and explanations are driven by an offline-trained Random Forest model and SHAP. The predictions are intended for demonstrative triage and *do not replace human judgment*. "AI assists. Humans decide."
- **Authorization:** While the backend restricts public data via scoped endpoints, some role-based visibility rules are primarily enforced client-side for rapid prototyping.

## Known Issues
- Sector distribution charts cap at the top 10/14 sectors; long-tail sectors may not be visible in some overview visualisations.
- If the Gemini API key is not provided, the PRAGYA Assistant Chatbot will return an error notice instead of functioning.

## Future Integration Requirements
- **Live Authentication:** Integration with SSO / e-Pramaan or NIC identity services.
- **Database Scaling:** Migration from SQLite to an enterprise relational database (e.g., PostgreSQL).
- **GIS Integration:** Integration of live satellite / mapping systems (e.g., Leaflet/Mapbox/Bhuvan).
- **PWA / Offline Sync:** Implementation of service workers for offline update submissions.
