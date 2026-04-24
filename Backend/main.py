"""
AI Financial Intelligence Advisor - Main Application
Desktop GUI application for personal financial recommendation
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
from Backend.models import UserProfile, MarketData
from Backend.optimizer import RecommendationEngine
from Backend.config import RISK_PROFILES, FD_RATES
import threading


class FinancialAdvisorApp:
    """Main application window, to be replaced with frontend in future iterations"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("AI Financial Intelligence Advisor")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f0f0")
        
        # Style
        self.setup_styles()
        
        # Create main frames
        self.create_widgets()
        
        self.recommendation = None
    
    def setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colors
        style.configure("Title.TLabel", font=("Arial", 16, "bold"), background="#f0f0f0")
        style.configure("Header.TLabel", font=("Arial", 12, "bold"), background="#f0f0f0")
        style.configure("Normal.TLabel", font=("Arial", 10), background="#f0f0f0")
        style.configure("TButton", font=("Arial", 10))
        style.configure("TEntry", font=("Arial", 10))
        style.configure("Result.TFrame", relief="ridge", borderwidth=2)
    
    def create_widgets(self):
        """Create all UI widgets"""
        
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_container, text="AI Financial Intelligence Advisor", style="Title.TLabel")
        title_label.pack(pady=10)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_container)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Input Form
        self.input_frame = ttk.Frame(notebook, padding=20)
        notebook.add(self.input_frame, text="User Profile & Market Data")
        self.create_input_tab()
        
        # Tab 2: Results
        self.results_frame = ttk.Frame(notebook, padding=20)
        notebook.add(self.results_frame, text="Recommendation Results")
        self.create_results_tab()
    
    def create_input_tab(self):
        """Create input form tab"""
        
        # Left side: User Profile
        left_frame = ttk.LabelFrame(self.input_frame, text="User Profile", padding=15)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Age
        ttk.Label(left_frame, text="Age:", style="Normal.TLabel").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.age_var = tk.StringVar(value="30")
        ttk.Entry(left_frame, textvariable=self.age_var, width=20).grid(row=0, column=1, padx=10, pady=5)
        
        # Monthly Salary
        ttk.Label(left_frame, text="Monthly Salary (MYR):", style="Normal.TLabel").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.salary_var = tk.StringVar(value="5000")
        ttk.Entry(left_frame, textvariable=self.salary_var, width=20).grid(row=1, column=1, padx=10, pady=5)
        
        # Monthly Expenditure
        ttk.Label(left_frame, text="Monthly Expenditure (MYR):", style="Normal.TLabel").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.expenditure_var = tk.StringVar(value="2000")
        ttk.Entry(left_frame, textvariable=self.expenditure_var, width=20).grid(row=2, column=1, padx=10, pady=5)
        
        # Fixed Liabilities
        ttk.Label(left_frame, text="Fixed Liabilities (MYR):", style="Normal.TLabel").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.liabilities_var = tk.StringVar(value="500")
        ttk.Entry(left_frame, textvariable=self.liabilities_var, width=20).grid(row=3, column=1, padx=10, pady=5)
        
        # Current EPF Balance
        ttk.Label(left_frame, text="Current EPF Balance (MYR):", style="Normal.TLabel").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.epf_balance_var = tk.StringVar(value="80000")
        ttk.Entry(left_frame, textvariable=self.epf_balance_var, width=20).grid(row=4, column=1, padx=10, pady=5)
        
        # Risk Appetite
        ttk.Label(left_frame, text="Risk Appetite:", style="Normal.TLabel").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.risk_var = tk.StringVar(value="Moderate")
        risk_combo = ttk.Combobox(left_frame, textvariable=self.risk_var, 
                                   values=list(RISK_PROFILES.keys()), state="readonly", width=17)
        risk_combo.grid(row=5, column=1, padx=10, pady=5)
        
        # Right side: Market Data
        right_frame = ttk.LabelFrame(self.input_frame, text="Market Data", padding=15)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Bitcoin Price
        ttk.Label(right_frame, text="Bitcoin Price (USD):", style="Normal.TLabel").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.btc_price_var = tk.StringVar(value="45000")
        ttk.Entry(right_frame, textvariable=self.btc_price_var, width=20).grid(row=0, column=1, padx=10, pady=5)
        
        # Bitcoin Daily Change
        ttk.Label(right_frame, text="Bitcoin Daily Change (%):", style="Normal.TLabel").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.btc_change_var = tk.StringVar(value="2.5")
        ttk.Entry(right_frame, textvariable=self.btc_change_var, width=20).grid(row=1, column=1, padx=10, pady=5)
        
        # Bitcoin 7-day Average
        ttk.Label(right_frame, text="Bitcoin 7-Day Avg (USD):", style="Normal.TLabel").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.btc_7day_var = tk.StringVar(value="44000")
        ttk.Entry(right_frame, textvariable=self.btc_7day_var, width=20).grid(row=2, column=1, padx=10, pady=5)
        
        # Bitcoin 30-day Average
        ttk.Label(right_frame, text="Bitcoin 30-Day Avg (USD):", style="Normal.TLabel").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.btc_30day_var = tk.StringVar(value="42000")
        ttk.Entry(right_frame, textvariable=self.btc_30day_var, width=20).grid(row=3, column=1, padx=10, pady=5)
        
        # Button frame
        button_frame = ttk.Frame(self.input_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(button_frame, text="Generate Recommendation", command=self.generate_recommendation).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset", command=self.reset_form).pack(side=tk.LEFT, padx=5)
    
    def create_results_tab(self):
        """Create results display tab"""
        
        # Create scrolled text widget
        self.results_text = scrolledtext.ScrolledText(
            self.results_frame, 
            wrap=tk.WORD, 
            height=30, 
            width=100,
            font=("Courier", 10)
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for formatting
        self.results_text.tag_configure("header", font=("Courier", 12, "bold"), foreground="#0066cc")
        self.results_text.tag_configure("subheader", font=("Courier", 11, "bold"), foreground="#333333")
        self.results_text.tag_configure("success", foreground="#009900")
        self.results_text.tag_configure("warning", foreground="#cc6600")
        self.results_text.tag_configure("error", foreground="#cc0000")
        self.results_text.tag_configure("normal", foreground="#000000")
    
    def generate_recommendation(self):
        """Generate recommendation based on form inputs"""
        try:
            # Validate and get inputs
            age = int(self.age_var.get())
            monthly_salary = float(self.salary_var.get())
            monthly_expenditure = float(self.expenditure_var.get())
            fixed_liabilities = float(self.liabilities_var.get())
            current_epf = float(self.epf_balance_var.get())
            risk_appetite = self.risk_var.get()
            
            # Validate Bitcoin market data
            btc_price = float(self.btc_price_var.get())
            btc_daily_change = float(self.btc_change_var.get())
            btc_7day = float(self.btc_7day_var.get())
            btc_30day = float(self.btc_30day_var.get())
            
            # Validate inputs
            if age < 18 or age > 65:
                messagebox.showerror("Invalid Input", "Age must be between 18 and 65")
                return
            
            if monthly_salary <= 0:
                messagebox.showerror("Invalid Input", "Monthly salary must be positive")
                return
            
            # Create user profile
            user_profile = UserProfile(
                age=age,
                monthly_salary=monthly_salary,
                monthly_expenditure=monthly_expenditure,
                current_epf_balance=current_epf,
                fixed_liabilities=fixed_liabilities,
                risk_appetite=risk_appetite
            )
            
            # Create market data
            market_data = MarketData(
                bitcoin_price=btc_price,
                bitcoin_daily_change=btc_daily_change,
                bitcoin_7day_avg=btc_7day,
                bitcoin_30day_avg=btc_30day,
                fd_rates=FD_RATES,
                epf_interest_rate=3.5,
                timestamp=datetime.now()
            )
            
            # Run analysis in separate thread to keep UI responsive
            threading.Thread(
                target=self._run_analysis,
                args=(user_profile, market_data),
                daemon=True
            ).start()
            
        except ValueError as e:
            messagebox.showerror("Input Error", f"Please enter valid numbers: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
    
    def _run_analysis(self, user_profile: UserProfile, market_data: MarketData):
        """Run the recommendation engine and display results"""
        try:
            # Generate recommendation
            recommendation = RecommendationEngine.generate_recommendation(
                user_profile, 
                market_data
            )
            self.recommendation = recommendation
            
            # Display results
            self.display_results(recommendation)
            
        except Exception as e:
            messagebox.showerror("Analysis Error", f"Error during analysis: {e}")
    
    def display_results(self, rec):
        """Display recommendation results in results tab"""
        
        # Clear previous results
        self.results_text.delete(1.0, tk.END)
        
        # Prepare output
        output = []
        
        # Header
        output.append("=" * 100)
        output.append("AI FINANCIAL INTELLIGENCE ADVISOR - RECOMMENDATION REPORT")
        output.append("=" * 100)
        output.append("")
        
        # User Summary
        output.append("USER PROFILE SUMMARY")
        output.append("-" * 100)
        output.append(f"Age: {rec.user_profile.age} years old")
        output.append(f"Monthly Salary: MYR {rec.user_profile.monthly_salary:,.2f}")
        output.append(f"Monthly Expenditure: MYR {rec.user_profile.monthly_expenditure:,.2f}")
        output.append(f"Monthly Surplus: MYR {rec.user_profile.monthly_surplus:,.2f}")
        output.append(f"Annual Surplus: MYR {rec.user_profile.annual_surplus:,.2f}")
        output.append(f"Current EPF Balance: MYR {rec.user_profile.current_epf_balance:,.2f}")
        output.append(f"Risk Appetite: {rec.user_profile.risk_appetite}")
        output.append("")
        
        # EPF Analysis
        output.append("EPF STATUS ANALYSIS")
        output.append("-" * 100)
        status_str = "✓ ON TRACK" if rec.epf_status.value == "ON_TRACK" else "⚠ BEHIND"
        output.append(f"EPF Status: {status_str}")
        output.append(f"Target Balance for Age {rec.user_profile.age}: MYR {rec.epf_target:,.2f}")
        output.append(f"Current Gap: MYR {rec.epf_gap:,.2f} ({rec.epf_gap_percentage:+.1f}%)")
        
        if rec.epf_status.value != "ON_TRACK":
            output.append(f"⚠  WARNING: Your EPF is behind target. Prioritize EPF contributions.")
        output.append("")
        
        # Bitcoin Analysis
        output.append("BITCOIN MARKET ANALYSIS")
        output.append("-" * 100)
        output.append(f"Signal: {rec.bitcoin_analysis.signal.value}")
        output.append(f"Trend: {rec.bitcoin_analysis.trend}")
        output.append(f"Confidence Level: {rec.bitcoin_analysis.confidence_score:.0%}")
        output.append(f"Analysis: {rec.bitcoin_analysis.reasoning}")
        output.append("")
        
        # Allocation Strategy
        output.append("RECOMMENDED ALLOCATION STRATEGY")
        output.append("-" * 100)
        output.append(f"Fixed Deposit (FD):  {rec.allocation_strategy.fd_percentage*100:5.1f}% → MYR {rec.allocation_monthly_amount['FD']:>10,.2f}/month (MYR {rec.allocation_annual_amount['FD']:>10,.2f}/year)")
        output.append(f"EPF Contribution:   {rec.allocation_strategy.epf_percentage*100:5.1f}% → MYR {rec.allocation_monthly_amount['EPF']:>10,.2f}/month (MYR {rec.allocation_annual_amount['EPF']:>10,.2f}/year)")
        output.append(f"Crypto/Bitcoin:     {rec.allocation_strategy.crypto_percentage*100:5.1f}% → MYR {rec.allocation_monthly_amount['Crypto']:>10,.2f}/month (MYR {rec.allocation_annual_amount['Crypto']:>10,.2f}/year)")
        output.append("")
        
        # Best FD Option
        output.append("BEST FD OPTION")
        output.append("-" * 100)
        if rec.top_fd_option:
            output.append(f"Bank: {rec.top_fd_option.bank_name.replace('_', ' ')}")
            output.append(f"Interest Rate: {rec.top_fd_option.rate:.2f}% p.a.")
            output.append(f"Period: {rec.top_fd_option.period.replace('_', '-')}")
        output.append("")
        
        # Portfolio Projections
        output.append("12-MONTH PORTFOLIO PROJECTION")
        output.append("-" * 100)
        output.append(f"Initial Monthly Investment: MYR {rec.user_profile.monthly_surplus:,.2f}")
        output.append(f"Projected Value (1 month):  MYR {rec.projected_portfolio_1month:>12,.2f}")
        output.append(f"Projected Value (6 months): MYR {rec.projected_portfolio_6months:>12,.2f}")
        output.append(f"Projected Value (12 months): MYR {rec.projected_portfolio_12months:>12,.2f}")
        output.append("")
        
        # Quantifiable Impact
        total_annual = rec.allocation_annual_amount['FD'] + rec.allocation_annual_amount['EPF'] + rec.allocation_annual_amount['Crypto']
        output.append("QUANTIFIABLE IMPACT")
        output.append("-" * 100)
        output.append(f"Annual Investment: MYR {total_annual:,.2f}")
        output.append(f"Projected Portfolio Growth: MYR {rec.projected_portfolio_12months - total_annual:,.2f}")
        output.append(f"Estimated ROI: {((rec.projected_portfolio_12months - total_annual) / total_annual * 100) if total_annual > 0 else 0:.1f}%")
        output.append("")
        
        # Reasoning
        output.append("DETAILED REASONING")
        output.append("=" * 100)
        output.append(rec.reasoning)
        output.append("")
        output.append("=" * 100)
        output.append(f"Report Generated: {rec.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        output.append("=" * 100)
        
        # Display in text widget
        full_text = "\n".join(output)
        self.results_text.insert(tk.END, full_text, "normal")
        
        # Switch to results tab
        self.root.nametowidget(self.root.children['!notebook']).select(1)
    
    def reset_form(self):
        """Reset form to default values"""
        self.age_var.set("30")
        self.salary_var.set("5000")
        self.expenditure_var.set("2000")
        self.liabilities_var.set("500")
        self.epf_balance_var.set("80000")
        self.risk_var.set("Moderate")
        self.btc_price_var.set("45000")
        self.btc_change_var.set("2.5")
        self.btc_7day_var.set("44000")
        self.btc_30day_var.set("42000")


def main():
    """Main entry point"""
    root = tk.Tk()
    app = FinancialAdvisorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
