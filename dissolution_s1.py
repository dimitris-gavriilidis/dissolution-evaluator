import tkinter as tk
from tkinter import ttk, messagebox


def evaluate_s1(results, q):
    threshold = q + 5
    failures = [(i + 1, v) for i, v in enumerate(results) if v < threshold]
    if not failures:
        return True, f"All 6 units ≥ Q+5% ({threshold}%). Batch PASSES at S1."
    lines = ", ".join(f"Unit {i}: {v}%" for i, v in failures)
    return False, (
        f"{len(failures)} unit(s) below Q+5% ({threshold}%): {lines}.\n"
        "S1 criteria NOT met — proceed to S2 testing per USP <711>."
    )


def on_evaluate():
    try:
        q = float(q_entry.get())
        results = [float(e.get()) for e in vessel_entries]
    except ValueError:
        messagebox.showerror("Input error", "Please enter valid numeric values for Q and all 6 vessels.")
        return

    if not (0 <= q <= 100):
        messagebox.showerror("Input error", "Q must be between 0 and 100.")
        return
    if any(v < 0 or v > 120 for v in results):
        messagebox.showerror("Input error", "Vessel results must be between 0 and 120.")
        return

    passed, reason = evaluate_s1(results, q)
    verdict_label.config(
        text="PASS" if passed else "FAIL",
        foreground="#1b8a3a" if passed else "#c0392b",
    )
    reason_label.config(text=reason)


def on_clear():
    q_entry.delete(0, tk.END)
    for e in vessel_entries:
        e.delete(0, tk.END)
    verdict_label.config(text="")
    reason_label.config(text="")


root = tk.Tk()
root.title("USP <711> Dissolution — S1 Evaluator")
root.resizable(False, False)

style = ttk.Style()
try:
    style.theme_use("vista")
except tk.TclError:
    pass

main = ttk.Frame(root, padding=20)
main.grid(row=0, column=0)

ttk.Label(main, text="USP <711> Dissolution Stage 1 (S1)", font=("Segoe UI", 13, "bold")).grid(
    row=0, column=0, columnspan=4, pady=(0, 12)
)

ttk.Label(main, text="Q value (%):").grid(row=1, column=0, sticky="e", padx=(0, 8), pady=4)
q_entry = ttk.Entry(main, width=10)
q_entry.grid(row=1, column=1, sticky="w", pady=4)

ttk.Separator(main, orient="horizontal").grid(row=2, column=0, columnspan=4, sticky="ew", pady=10)

ttk.Label(main, text="Vessel results (% dissolved):").grid(
    row=3, column=0, columnspan=4, sticky="w", pady=(0, 6)
)

vessel_entries = []
for i in range(6):
    r, c = divmod(i, 2)
    ttk.Label(main, text=f"Vessel {i + 1}:").grid(row=4 + r, column=c * 2, sticky="e", padx=(0, 8), pady=3)
    e = ttk.Entry(main, width=10)
    e.grid(row=4 + r, column=c * 2 + 1, sticky="w", padx=(0, 16), pady=3)
    vessel_entries.append(e)

btn_frame = ttk.Frame(main)
btn_frame.grid(row=8, column=0, columnspan=4, pady=(14, 6))
ttk.Button(btn_frame, text="Evaluate", command=on_evaluate).grid(row=0, column=0, padx=5)
ttk.Button(btn_frame, text="Clear", command=on_clear).grid(row=0, column=1, padx=5)

ttk.Separator(main, orient="horizontal").grid(row=9, column=0, columnspan=4, sticky="ew", pady=10)

verdict_label = ttk.Label(main, text="", font=("Segoe UI", 18, "bold"))
verdict_label.grid(row=10, column=0, columnspan=4)

reason_label = ttk.Label(main, text="", wraplength=360, justify="center", font=("Segoe UI", 9))
reason_label.grid(row=11, column=0, columnspan=4, pady=(6, 0))

root.mainloop()
