# UM Hackathon 2026 – Team Bakkutteh  
## 💡 Crypto-Integrated Financial Intelligence Advisor  

An AI-powered wealth management assistant that balances **financial security** (FDs, EPF) with **high-risk investment strategies**, built for the **Z.AI Hackathon**.

---

## 🎥 Demo Video  
> _Coming soon_

---

## 📄 Documentation  
### Product Requirement Documentation (PRD)
[Product Requirement Documentation (PRD)](https://drive.google.com/file/d/1GiCiEnwAKrbZuhnHU6FVOM9-A7nPGtQq/view?usp=drive_link)

### System Analysis Documentation
[System Analysis Documentation](https://drive.google.com/file/d/159IaUnQ4VpCEYtGcHWzPpK5iSv1IRXdD/view?usp=drive_link)

### Sample Testing Analysis (Preliminary)
[Sample Testing Analysis (Preliminary)](https://drive.google.com/file/d/1S8udVotqi3N2ueJG4FTpvbPBiVjJIOMz/view?usp=drive_link)

---

## ⚙️ Environment Setup Guide  

To ensure our AI models and live data feeds run consistently across all machines, follow the steps below to set up your local environment.

---
## To run live_data.py outside of program
### 🚀 Setup Instructions  

To ensure our AI models and live data feeds run consistently across all our laptops, please follow these steps to set up your local environment.
#### Prerequisites
Ensure you have **Python 3.11** (or at least 3.10+) installed on your machine.

### Setup the Environment
1. Pull the latest code: `git pull origin main`
2. Open your terminal in the project root folder and run:
- **Mac/Linux:** `python3.11 -m venv venv`
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
python -m uvicorn app:app --reload
```
<img width="462" height="136" alt="Untitled" src="https://github.com/user-attachments/assets/98636cbe-63fd-4a40-b5c3-98d08c2a5582" />
