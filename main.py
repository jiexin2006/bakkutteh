import tkinter as tk
from tkinter import ttk, Toplevel
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from data_manager import DataManager

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Financial Intelligence Advisor")
        self.state('zoomed') # Forces full-screen opening
        self.user_data = {}
        
        self.container = tk.Frame(self, bg="white")
        self.container.pack(fill="both", expand=True)
        
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
            row = tk.Frame(self, bg="white"); row.pack(pady=10)
            tk.Label(row, text=field, width=20, bg="white", font=("Arial", 16)).pack(side=tk.LEFT)
            self.inputs[field] = tk.Entry(row, width=25, font=("Arial", 16)); self.inputs[field].pack(side=tk.LEFT)
        
        self.tier = ttk.Combobox(self, values=["Basic", "Adequate", "Enhanced"], state="readonly", font=("Arial", 16))
        self.tier.set("Basic"); self.tier.pack(pady=20)
        tk.Button(self, text="ANALYZE", font=("Arial", 18), bg="#28a745", fg="white", 
                  command=lambda: self.save(controller)).pack(pady=30)

    def save(self, controller):
        for field, entry in self.inputs.items(): controller.user_data[field] = entry.get()
        controller.user_data["tier"] = self.tier.get()
        controller.show_frame("DashboardPage")

class DashboardPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        tk.Label(self, text="Financial Overview", font=("Arial", 32, "bold"), bg="white").pack(pady=40)
        cols = tk.Frame(self, bg="white"); cols.pack(fill=tk.BOTH, expand=True, padx=50, pady=20)
        cols.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.create_card(cols, 0, "FD RATES", self.show_fd)
        self.create_card(cols, 1, "EPF STATUS", self.show_epf)
        self.create_card(cols, 2, "BITCOIN", self.show_btc)
        tk.Button(self, text="NEXT: VIEW RECOMMENDATION", bg="#ffc107", 
                  command=lambda: controller.show_frame("ConclusionPage")).pack(pady=40)

    def create_card(self, p, col, title, cmd):
        card = tk.LabelFrame(p, text="", bg="white", padx=50, pady=50)
        card.grid(row=0, column=col, sticky="nsew", padx=20); tk.Label(card, text=title, font=("Arial", 20, "bold"), bg="white").pack(pady=20); tk.Button(card, text="VIEW DETAILS", command=cmd).pack()

    def show_fd(self):
        top = Toplevel(self); top.geometry("600x600"); top.focus_force()
        tree = ttk.Treeview(top, columns=("Bank", "Rate", "Period"), show='headings')
        for col in ["Bank", "Rate", "Period"]: tree.heading(col, text=col)
        for r in DataManager.get_ranked_fd_rates(): tree.insert("", "end", values=(r[0], f"{r[1]}%", r[2]))
        tree.pack(fill=tk.BOTH, expand=True)

    def show_btc(self):
        top = Toplevel(self); top.geometry("500x400"); top.focus_force()
        fig = Figure(figsize=(4, 2), dpi=100); ax = fig.add_subplot(111)
        ax.plot(DataManager.get_bitcoin_chart_data(), marker='o', color='green')
        canvas = FigureCanvasTkAgg(fig, master=top); canvas.draw(); canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        sig, col = DataManager.get_bitcoin_signal()
        tk.Label(top, text=f"SIGNAL: {sig}", font=("Arial", 20), bg=col, fg="white", width=20).pack(pady=20)

    def show_epf(self):
        top = Toplevel(self); top.geometry("300x200"); top.focus_force()
        tk.Label(top, text="EPF Status: Optimal", font=("Arial", 16)).pack(pady=50)

class ConclusionPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller
        tk.Label(self, text="AI Allocation Strategy", font=("Arial", 32, "bold"), bg="white").pack(pady=80)
        self.advice = tk.Label(self, text="", font=("Arial", 18), bg="white", wraplength=800, justify="center")
        self.advice.pack(pady=30)
        tk.Button(self, text="RESTART", command=lambda: controller.show_frame("StartPage")).pack()
        self.bind("<Visibility>", self.update_text)

    def update_text(self, event):
        self.advice.config(text=DataManager.calculate_advice(self.controller.user_data))

if __name__ == "__main__":
    app = App(); app.mainloop()