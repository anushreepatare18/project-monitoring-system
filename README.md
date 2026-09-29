# PRAGYA AI — Prototype

**PRAGYA AI** is an AI-powered Infrastructure Project Monitoring System developed for the Smart India Hackathon (SIH 2026). It provides a unified, role-based platform for monitoring national infrastructure projects, triaging risk, and exposing approved data to the public.

## Overview
This repository contains the frontend React prototype for PRAGYA AI. 

> **Important Prototype Notice:** 
> - The data shown in this application is **illustrative sample data**. 
> - Feature contributions (SHAP values), risk scores, and anomaly detections are simulated to demonstrate the UI workflow and do not represent a live, connected AI backend.
> - "AI Assists. Humans Decide." The system is designed to support, not replace, human monitoring officers.
> - Authorization is currently handled via client-side Context for demo purposes.

## Key Features by Role
- **Implementing Agency:** Track assigned projects, submit physical/financial progress updates, and respond to clarification requests.
- **Ministry / Department:** View a high-level portfolio overview of all assigned projects with beautiful descriptive analytics.
- **Monitoring Officer:** A powerful triage dashboard to review AI risk alerts, inspect progress anomalies, and log official reviews.
- **Public:** A sanitized transparency portal providing published execution data to citizens, strictly shielding all internal AI scores and officer notes.
- **PRAGYA AI Assistant:** A role-aware, read-only chat interface for querying project details and summarizing portfolios naturally.

## Technology Stack
- **Framework:** Next.js 14 (App Router)
- **Styling:** Tailwind CSS v4
- **Icons:** Lucide React
- **Charts:** Recharts
- **State Management:** React Context API

## Prerequisites
- Node.js (v18 or higher)
- npm or yarn

## Installation & Setup

1. Clone the repository.
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Demo Instructions for Judges

To quickly evaluate the system without setting up accounts, use the **1-Click Demo Login** on the home page.

### Recommended Demo Sequence

1. **Log in as Implementing Agency**
   - Click "Implementing Agency" on the login screen.
   - Navigate to **Update Forms** and submit a progress update.
   - Check the **Priority Queue** to see an open clarification request.
2. **Switch to Monitoring Officer**
   - Use the bottom-left sidebar menu to **Log Out**, then log in as **Monitoring Officer**.
   - Note the comprehensive KPIs (Critical Risk, Overdue Follow-ups).
   - Go to **Alert Queue**, click "Review" on an alert, and observe the AI Explanation (SHAP) and internal action workflow.
   - Try out the floating **PRAGYA AI Assistant** (bottom right) and ask "What projects require my attention?"
3. **Switch to Ministry / Department**
   - Log out, log in as **Ministry**.
   - Navigate to **Portfolio Analytics** to see portfolio-wide Recharts visualizations.
   - Verify that the Ministry can see Alerts but cannot close them (enforcing the read-only oversight boundary).
4. **Switch to Public**
   - Log out, log in as **Public**.
   - Go to **Browse Projects** and verify that no internal risk scores, SHAP values, or alerts are visible.
   - Try asking the Chatbot about "risk scores" and verify the security rejection.

## Known Limitations & Future Work
- **Backend Integration:** Currently relies on `src/context/ProjectContext.tsx` and `src/data/mockProjects.ts`. Future phases require integrating a PostgreSQL/FastAPI backend.
- **Authentication:** Security boundaries are enforced via client-side routing and data filtering. A robust JWT/OAuth integration is required for production.
- **Live AI Models:** The SHAP values and risk scores are static. Integration with the PAIMANA prediction pipeline is pending.
- **Exporting:** PDF export capabilities are mocked for Phase 4. CSV exporting works via local Blob generation.

## License
Created for Smart India Hackathon. All rights reserved.
