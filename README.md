# Crypto-Integrated Financial Intelligence Advisor
An AI-powered wealth-management assistant that balances essential financial security (FDs, EPF) with high-risk investment guidance, built for the Z.AI Hackathon.

## Tech Stack
* **Frontend:** 
* **Backend & Data Pipeline:** 
* **AI/Decision Engine:** Z.AI GLM

## What is the requirement.txt for?
To ensure our AI models and live data feeds run consistently across all our laptops, please follow these steps to set up your local environment.
#### Prerequisites
Ensure you have **Python 3.14** (or at least 3.10+) installed on your machine.

### Setup the Environment
1. Pull the latest code: `git pull origin main`
2. Open your terminal in the project root folder and run:
- **Mac/Linux:** `python3 -m venv venv`
- **Windows:** `python -m venv venv`

3. Activate :
- **Mac/Linux:** `source venv/bin/activate`
- **Windows:** `venv\Scripts\activate`
> **Note:** You should see `(venv)` appear at the start of your terminal line.

4. Install Dependencies:
This command reads the `requirements.txt` file and installs the exact versions we need.
```bash
pip install -r requirements.txt
```

5. Run the following script to ensure you can fetch live market data:
```bash
python live_data.py
```
<img width="462" height="136" alt="Untitled" src="https://github.com/user-attachments/assets/98636cbe-63fd-4a40-b5c3-98d08c2a5582" />
