import tkinter as tk
from tkinter import ttk, Toplevel
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from data_manager import DataManager

class CryptoFinancialApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Financial Intelligence Advisor")
        self.geometry("1200x800")
        self.configure(bg="white")
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.container = tk.Frame(self, bg="white")
        self.container.grid(row=0, column=0, sticky="nsew")
        
        self.frames = {}
        for F in (StartPage, DashboardPage, ConclusionPage):
            page = F(parent=self.container, controller=self)
            self.frames[F.__name__] = page
            page.grid(row=0, column=0, sticky="nsew")
        self.show_frame("StartPage")

    def show_frame(self, name): self.frames[name].tkraise()

class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        tk.Label(self, text="Financial Profile Setup", font=("Arial", 32, "bold"), bg="white").pack(pady=50)
        self.inputs = {}
        for field in ["Age", "EPF Balance", "Monthly Expenses", "Monthly Income"]:
            row = tk.Frame(self, bg="white")
            row.pack(pady=15)
            tk.Label(row, text=field, font=("Arial", 16), bg="white", width=20).pack(side=tk.LEFT)
            ent = tk.Entry(row, font=("Arial", 16), width=25)
            ent.pack(side=tk.LEFT)
            self.inputs[field] = ent
        self.tier = ttk.Combobox(self, values=["Basic", "Adequate", "Enhanced"], font=("Arial", 16), state="readonly")
        self.tier.set("Basic")
        self.tier.pack(pady=20)
        tk.Button(self, text="ANALYZE FINANCES", font=("Arial", 18, "bold"), bg="#28a745", fg="white",
                  command=lambda: controller.show_frame("DashboardPage")).pack(pady=40, ipadx=40, ipady=15)

class DashboardPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        tk.Label(self, text="Financial Overview", font=("Arial", 32, "bold"), bg="white").pack(pady=40)
        cols = tk.Frame(self, bg="white")
        cols.pack(fill=tk.BOTH, expand=True, padx=50, pady=20)
        cols.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.create_card(cols, 0, "FD RATES", self.show_fd)
        self.create_card(cols, 1, "EPF / SAVINGS", self.show_epf)
        self.create_card(cols, 2, "BITCOIN SIGNAL", self.show_btc)
        
        tk.Button(self, text="NEXT: VIEW RECOMMENDATION", font=("Arial", 14), bg="#ffc107",
                  command=lambda: controller.show_frame("ConclusionPage")).pack(pady=40, ipadx=20)

    def create_card(self, parent, col, title, cmd):
        card = tk.LabelFrame(parent, text="", bg="white", padx=50, pady=50)
        card.grid(row=0, column=col, sticky="nsew", padx=20, pady=20)
        tk.Label(card, text=title, font=("Arial", 20, "bold"), bg="white").pack(pady=20)
        tk.Button(card, text="VIEW DETAILS", font=("Arial", 12), command=cmd).pack(pady=20)

    def show_fd(self):
        top = Toplevel(self); top.geometry("500x500"); top.focus_force()
        tree = ttk.Treeview(top, columns=("Bank", "Rate", "Period"), show='headings')
        for col in ["Bank", "Rate", "Period"]: tree.heading(col, text=col)
        for row in DataManager.get_fd_rates(): tree.insert("", "end", values=row)
        tree.pack(fill=tk.BOTH, expand=True)

    def show_epf(self):
        top = Toplevel(self); top.geometry("300x200"); top.focus_force()
        tk.Label(top, text="EPF Status: Optimal", font=("Arial", 14)).pack(pady=50)

    def show_btc(self):
        top = Toplevel(self); top.geometry("500x400"); top.focus_force()
        fig = Figure(figsize=(4, 2), dpi=100); ax = fig.add_subplot(111)
        ax.plot(DataManager.get_bitcoin_chart_data(), color='green', marker='o')
        canvas = FigureCanvasTkAgg(fig, master=top); canvas.draw(); canvas.get_tk_widget().pack()
        sig, col = DataManager.get_bitcoin_signal()
        tk.Label(top, text=f"Market Signal: {sig}", font=("Arial", 16, "bold"), bg=col, fg="white", width=20).pack(pady=20)

class ConclusionPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        tk.Label(self, text="AI Allocation Strategy", font=("Arial", 32, "bold"), bg="white").pack(pady=80)
        advice = DataManager.get_ai_advice(3000, 2000, 10000, "Basic")
        tk.Label(self, text=advice, font=("Arial", 18), bg="white", wraplength=800, justify="center").pack(pady=30)
        tk.Button(self, text="RESTART", command=lambda: controller.show_frame("StartPage")).pack()

if __name__ == "__main__":
    app = CryptoFinancialApp(); app.mainloop()