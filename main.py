import tkinter as tk
from tkinter import ttk, Toplevel
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from data_manager import DataManager

class CryptoFinancialApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Crypto-Integrated Financial Intelligence Advisor")
        self.geometry("1200x800")
        self.configure(bg="white")
        
        # Configure Grid to expand
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.container = tk.Frame(self, bg="white")
        self.container.grid(row=0, column=0, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        for F in (StartPage, DashboardPage, ConclusionPage):
            frame = F(parent=self.container, controller=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame("StartPage")

    def show_frame(self, name):
        self.frames[name].tkraise()

# --- PAGE 1: INPUT ---
class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        tk.Label(self, text="Financial Profile Setup", font=("Arial", 32, "bold"), bg="white").pack(pady=80)
        
        for field in ["Age", "EPF Balance", "Monthly Expenses", "Monthly Income"]:
            row = tk.Frame(self, bg="white")
            row.pack(pady=20)
            tk.Label(row, text=field, font=("Arial", 18), bg="white").pack(side=tk.LEFT, padx=30)
            ent = tk.Entry(row, font=("Arial", 18), width=30)
            ent.pack(side=tk.LEFT)
            
        tk.Button(self, text="ANALYZE FINANCES", font=("Arial", 18, "bold"), bg="#28a745", fg="white",
                  command=lambda: controller.show_frame("DashboardPage")).pack(pady=80, ipadx=40, ipady=20)

# --- PAGE 2: DASHBOARD ---
class DashboardPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        tk.Label(self, text="Financial Overview", font=("Arial", 32, "bold"), bg="white").pack(pady=40)
        
        cols = tk.Frame(self, bg="white")
        cols.pack(fill=tk.BOTH, expand=True, padx=50, pady=20)
        cols.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.create_card(cols, 0, "FD RATES\n(Best ROI)", self.show_fd)
        self.create_card(cols, 1, "EPF STATUS\n(Retirement)", None)
        self.create_card(cols, 2, "BITCOIN\n(AI Prediction)", self.show_btc)

        tk.Button(self, text="NEXT: VIEW RECOMMENDATION", font=("Arial", 16), bg="#ffc107",
                  command=lambda: controller.show_frame("ConclusionPage")).pack(pady=40, ipadx=20, ipady=15)

    def create_card(self, parent, col, title, command):
        card = tk.LabelFrame(parent, text="", font=("Arial", 18, "bold"), padx=40, pady=40, bg="white")
        card.grid(row=0, column=col, sticky="nsew", padx=20, pady=20)
        tk.Label(card, text=title, font=("Arial", 22, "bold"), bg="white").pack(pady=40)
        if command:
            tk.Button(card, text="VIEW DETAILS", font=("Arial", 14), bg="white", command=command).pack(pady=40, ipadx=20)

    def show_fd(self):
        top = Toplevel(self)
        tree = ttk.Treeview(top, columns=("B", "R", "P"), show='headings')
        for c in ("B", "R", "P"): tree.heading(c, text=c)
        for r in DataManager.get_fd_rates(): tree.insert("", "end", values=r)
        tree.pack(fill=tk.BOTH, expand=True)

    def show_btc(self):
        top = Toplevel(self)
        fig = Figure(figsize=(5, 3))
        ax = fig.add_subplot(111)
        ax.plot(DataManager.get_bitcoin_data(), color='#2e7d32', marker='o')
        canvas = FigureCanvasTkAgg(fig, master=top)
        canvas.draw()
        canvas.get_tk_widget().pack()

# --- PAGE 3: CONCLUSION ---
class ConclusionPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        tk.Label(self, text="AI Allocation Strategy", font=("Arial", 32, "bold"), bg="white").pack(pady=80)
        # Explainability Layer: Clear language
        msg = DataManager.get_ai_advice()
        tk.Label(self, text=msg, font=("Arial", 18), bg="white", justify="center").pack(pady=30)
        tk.Button(self, text="RESTART", font=("Arial", 16), command=lambda: controller.show_frame("StartPage")).pack(pady=50, ipadx=30)

if __name__ == "__main__":
    app = CryptoFinancialApp()
    app.mainloop()