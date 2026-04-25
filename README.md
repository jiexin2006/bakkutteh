# UM Hackathon 2026 – Team Bakkutteh  
## 💡 Crypto-Integrated Financial Intelligence Advisor  
**Your AI Financial Guardian. Not Your Broker.**
* **Demo Video:** [Coming Soon]

The **Crypto-Integrated Financial Intelligence Advisor** is a sophisticated wealth management platform that bridges the gap between high-yield crypto speculation and long-term financial security (EPF, Fixed Deposits). By utilizing a **"Broker-Neutral"** logic, it acts as a fiduciary guardrail, preventing retail investors from over-leveraging based on hype.

---
## 📄 Documentation  
### Product Requirement Documentation (PRD)
[Product Requirement Documentation (PRD)](https://drive.google.com/file/d/1GiCiEnwAKrbZuhnHU6FVOM9-A7nPGtQq/view?usp=drive_link)

### System Analysis Documentation
[System Analysis Documentation](https://drive.google.com/file/d/159IaUnQ4VpCEYtGcHWzPpK5iSv1IRXdD/view?usp=drive_link)

### Sample Testing Analysis (Preliminary)
[Sample Testing Analysis (Preliminary)](https://drive.google.com/file/d/1S8udVotqi3N2ueJG4FTpvbPBiVjJIOMz/view?usp=drive_link)

---

## 🚩 The Problem
Retail investors in the current economy face three primary hurdles:
* **Data Fragmentation:** Financial health is scattered across EPF statements, bank FD rates, and volatile crypto exchanges. There is no "Big Picture."
* **The Analytical Gap:** Most investors rely on "gut feelings" or social media hype rather than objective data-driven trade-offs.
* **Lack of Guardrails:** Platforms are designed to encourage trading volume (revenue) rather than user survival. No AI currently tells a user "No" when their safety net is at risk.

## 🛠️ The Solution: The "Fiduciary" Pipeline
We implemented a multi-layered safety logic powered by the **Z.AI Engine** and **Gemini 1.5 Flash**:

1.  **Automated Safety Audit:** Real-time cross-referencing of user EPF/FD balances against **KWSP Age-Based Savings** benchmarks.
2.  **Broker-Neutral Logic Veto:** If a "Strong Bullish" crypto trend is detected but the user's financial health is "Red," the AI overrides the market signal and enforces a **0%–5% Crypto Cap**.
3.  **Context-Aware XAI (Explainable AI):** Instead of blind numbers, the system provides natural language justifications (e.g., *"Crypto capped because your liabilities exceed 50% of your income"*).
4.  **Resilience Fallback:** A fail-safe integrity system that switches to pre-programmed logic if the primary AI API experiences downtime.

---

## 🏗️ System Architecture
The platform is built on a 5-layer intelligence stack:


* **Layer 1 (Presentation):** React (Vite) SPA for real-time dashboards.
* **Layer 2 (Orchestration):** FastAPI Backend with Pydantic input validation.
* **Layer 3 (Services):** * **Bitcoin Analyzer:** TensorFlow (JS) for price trend inference.
    * **EPF Calculator:** Malaysian retirement benchmarks via local datasets.
    * **Market Data:** yFinance real-time feeds.
* **Layer 4 (Intelligence):** Primary Z.AI (lmu-glm-5.1) with Gemini 1.5 Flash as a robust fallback.
* **Layer 5 (Infrastructure):** Google Secret Manager & Cloud Storage.
 <img width="717" height="522" alt="image" src="https://github.com/user-attachments/assets/81f21aad-9f4d-4b4a-859a-4f9f05196e44" />


---

## 🏗️ Data Flow Diagram
<img width="940" height="645" alt="image" src="https://github.com/user-attachments/assets/b315fd4e-2311-40d9-8dd5-97e445987a2e" />

---

## 🧰 Tech Stack
| Component | Technology |
| :--- | :--- |
| **Frontend** | React (Vite) |
| **Backend** | FastAPI (Python 3.11+) |
| **Primary AI** | Z.AI (Reasoning & Strategy) |
| **Secondary AI** | Gemini 1.5 Flash (Validation & Fallback) |
| **ML Engine** | TensorFlow / yFinance API |
| **Deployment** | Uvicorn / Cloud Run |

---

## 👥 Target Audience
* **The Yield-Chasers:** Young investors needing structure before taking upside.
* **Income Unstable:** Gig workers needing liquidity-first stability.
* **Safe-But-Stuck:** Conservative savers needing guided exposure to grow wealth.
* **Future Builders:** Early-career professionals seeking goal-based consistency.

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

---

## 🚀 Future Improvements

### 1. Seamless Automation & Open Finance
To move from a manual "advice" platform to an "execution" powerhouse, we plan to leverage emerging banking standards:
* **Direct EPF (i-Akaun) Integration:** Replace manual balance entry with a direct API connection to sync real-time retirement savings, ensuring the "Safety Audit" is always based on live data.
* **Auto-Execution Layer:** Implement user-approved **Micro-Investments**. If the AI detects a surplus in a low-interest savings account, it can automatically trigger EPF top-ups or Fixed Deposit placements via Open Banking rails.

### 2. Broader Asset Coverage
Closing the "Missing Middle" between low-risk savings and high-risk crypto:
* **Bursa Malaysia Layer:** Introduce Malaysian blue-chip equities and REITs as a "Medium-Risk" bucket, providing users with a balanced path to growth.
* **ASB & PRS Integration:** Full inclusion of Amanah Saham Bumiputera and Private Retirement Schemes (PRS) to provide a 360° view of a Malaysian investor’s net worth.

### 3. Trust & Security Layer
Enhancing the "Guardian" aspect of the AI through advanced cryptography:
* **Zero-Knowledge Verification (ZKP):** Allow the system to validate that a user has met their financial "safety threshold" (e.g., 6 months of emergency funds) without the platform ever seeing the raw bank balance numbers.
* **Biometric Authorization:** Integrate hardware-level authentication (FaceID/Passkeys) for all fund movements and high-stakes allocation changes.

### 4. Scalable & Transparent Architecture
Ensuring the system remains resilient and accountable:
* **Microservices Architecture:** Decouple the "Crypto Forecasting" module from the "Safety Logic" module. This allows the safety guardrails to scale independently and remain active even if market data providers experience downtime.
* **On-Chain Audit Logs:** Use a lightweight blockchain ledger to create an immutable record of all AI advisory outputs. This ensures transparency—users can prove what the AI recommended at any specific point in time.

---
**Team Bakkutteh:** Lim Jie Xin, Kan Hoi Yeng, Chew Jee Syuen, Chong Wah Yun, Ho Hann Yi.


