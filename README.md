# EchoStep AI: AI-Powered Carbon Footprint Tracker & Reduction Advisor

**EchoStep AI** is a personalized, interactive web application built with **Streamlit** and the **Gemini API** that acts as an eco-coach and carbon accountant to address **UN SDG 13: Climate Action**. 

Users log daily activities (transportation, dietary habits, utility usage) and receive carbon footprint metrics, interactive visualizations, and natural language recommendations powered by the Gemini API to systematically offset emissions.

---

## Key Features

1. **Interactive Carbon Dashboard**: Renders a breakdown of weekly and monthly carbon footprints in kg CO2e, split by category (Food, Transport, Utilities) using Plotly charts. Classifies footprints into Scope 1, Scope 2, and Scope 3 emissions.
2. **AI Eco-Coach Chatbot**: A chat window powered by Gemini to ask questions about sustainable habits, commutes, and eco-friendly practices.
3. **Smart Recommendation Engine**: Evaluates your highest carbon emission sectors and drafts a prioritized, structured carbon reduction plan.
4. **Gamified Achievements**: Allows setting carbon targets and awards virtual achievements (e.g. *Plant-Powered*, *Green Commuter*) to incentivize and reward climate-positive behaviors.
5. **Downloadable PDF Report**: Compiles logged metrics and the AI action plan into a downloadable PDF report.

---

## File Structure

```
EchoStep/
├── app.py                # Main Streamlit application and layout logic
├── ai_engine.py          # Gemini API integrations and recommendation system
├── db_helper.py          # SQLite database connection and activity logging helpers
├── requirements.txt      # Python dependencies list
└── README.md             # Project setup and guide (this file)
```

---

## Setup & Running Locally

Follow these instructions to run EchoStep on your local machine.

### Prerequisites
- Python 3.10 or higher (Python 3.13.13 tested)
- A Gemini API Key (EchoStep comes with a preconfigured key but accepts overrides in the sidebar settings)

### Step 1: Clone or Open the Workspace
Ensure you are in the project folder directory:
```bash
cd EchoStep
```

### Step 2: Set Up Virtual Environment & Install Dependencies
Create a virtual environment:
```bash
python -m venv venv
```

Activate the virtual environment:
- **Windows (Command Prompt)**:
  ```cmd
  venv\Scripts\activate.bat
  ```
- **Windows (PowerShell)**:
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
- **Linux/macOS**:
  ```bash
  source venv/bin/activate
  ```

Install dependencies:
```bash
pip install -r requirements.txt
```

### Step 3: Run the Streamlit Application
Start the local server:
```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## Scientific Emission Factors

EchoStep calculates carbon footprints based on the following standard coefficients (in kg CO2e):

*   **Transportation**:
    *   Petrol Car: `0.18` per km
    *   Diesel Car: `0.17` per km
    *   Electric Vehicle: `0.05` per km
    *   Bus: `0.04` per passenger-km
    *   Train: `0.03` per passenger-km
    *   Flight: `0.12` per passenger-km
    *   Walk/Cycle: `0.00`
*   **Dietary Choices**:
    *   High Meat: `7.2` per day
    *   Flexitarian: `3.8` per day
    *   Vegetarian: `2.5` per day
    *   Vegan: `1.5` per day
*   **Home Utilities**:
    *   Electricity: `0.40` per kWh
    *   Natural Gas: `2.00` per m³
    *   Water: `0.30` per m³
