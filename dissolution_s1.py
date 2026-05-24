# USP <711> Dissolution Stage 1 / Stage 2 evaluator.
# Simple tkinter desktop GUI: user enters Q and 6 vessel results, app evaluates S1.
# If S1 fails, an additional 6-vessel input panel is revealed for S2 evaluation.

import tkinter as tk
from tkinter import ttk, messagebox


# ---------------------------------------------------------------------------
# Evaluation logic (pure functions — no GUI references, easy to reason about)
# ---------------------------------------------------------------------------

def evaluate_s1(results, q):
    """USP <711> Stage 1: all 6 units must be >= Q + 5%.

    Returns (passed: bool, reason: str).
    """
    threshold = q + 5  # S1 acceptance threshold per USP <711>
    # Collect any units that fall below the threshold for a useful failure message.
    failures = [(i + 1, v) for i, v in enumerate(results) if v < threshold]
    if not failures:
        return True, f"All 6 units ≥ Q+5% ({threshold}%). Batch PASSES at S1."
    lines = ", ".join(f"Unit {i}: {v}%" for i, v in failures)
    return False, (
        f"{len(failures)} unit(s) below Q+5% ({threshold}%): {lines}.\n"
        "S1 criteria NOT met — proceed to S2 testing per USP <711>."
    )


def evaluate_s2(results_12, q):
    """USP <711> Stage 2: evaluated on the pooled 12 units (S1 + S2).

    Pass requires BOTH:
      * mean of all 12 units >= Q
      * no individual unit below Q - 15%

    Returns (passed: bool, reason: str).
    """
    lower_bound = q - 15  # individual-unit floor for S2
    mean_val = sum(results_12) / len(results_12)  # average across all 12 vessels
    # Identify any single unit that falls below the Q-15% floor.
    below = [(i + 1, v) for i, v in enumerate(results_12) if v < lower_bound]

    # Both criteria must be satisfied; report which one(s) failed.
    mean_ok = mean_val >= q
    individuals_ok = not below

    if mean_ok and individuals_ok:
        return True, (
            f"Mean of 12 units = {mean_val:.2f}% (≥ Q={q}%), "
            f"no unit below Q−15% ({lower_bound}%). Batch PASSES at S2."
        )

    # Build a clear, multi-part failure message.
    parts = []
    if not mean_ok:
        parts.append(f"Mean = {mean_val:.2f}% is below Q ({q}%).")
    if not individuals_ok:
        listed = ", ".join(f"Unit {i}: {v}%" for i, v in below)
        parts.append(f"Unit(s) below Q−15% ({lower_bound}%): {listed}.")
    parts.append("S2 criteria NOT met — proceed to S3 testing per USP <711>.")
    return False, " ".join(parts)


# ---------------------------------------------------------------------------
# Input parsing / validation helpers
# ---------------------------------------------------------------------------

def parse_vessels(entries):
    """Convert a list of Entry widgets into floats; raises ValueError on bad input."""
    return [float(e.get()) for e in entries]


def vessels_in_range(values, lo=0, hi=120):
    """Reasonable physical range for % dissolved (allow slight over-recovery up to 120%)."""
    return all(lo <= v <= hi for v in values)


# ---------------------------------------------------------------------------
# GUI event handlers
# ---------------------------------------------------------------------------

def on_evaluate():
    """Triggered by the Evaluate button. Runs S1 first; if S1 fails, reveal S2 panel."""
    # --- Parse Q ---
    try:
        q = float(q_entry.get())
    except ValueError:
        messagebox.showerror("Input error", "Please enter a valid numeric Q value.")
        return
    if not (0 <= q <= 100):
        messagebox.showerror("Input error", "Q must be between 0 and 100.")
        return

    # --- Parse S1 vessels ---
    try:
        s1_results = parse_vessels(s1_entries)
    except ValueError:
        messagebox.showerror("Input error", "Please enter valid numeric values for all 6 S1 vessels.")
        return
    if not vessels_in_range(s1_results):
        messagebox.showerror("Input error", "S1 vessel results must be between 0 and 120.")
        return

    # --- Run S1 evaluation ---
    s1_passed, s1_reason = evaluate_s1(s1_results, q)

    if s1_passed:
        # S1 passed: show verdict, make sure S2 panel is hidden.
        show_verdict(True, s1_reason)
        hide_s2_panel()
        return

    # S1 failed.
    # If user has not yet filled S2 vessels, reveal the S2 panel and prompt them.
    s2_raw = [e.get().strip() for e in s2_entries]
    if not all(s2_raw):
        # Show S1 failure result and unlock S2 inputs for the user to complete.
        show_verdict(False, s1_reason + "\nEnter 6 additional vessel results below for S2.")
        show_s2_panel()
        return

    # S2 inputs are present — parse and evaluate Stage 2.
    try:
        s2_results = parse_vessels(s2_entries)
    except ValueError:
        messagebox.showerror("Input error", "Please enter valid numeric values for all 6 S2 vessels.")
        return
    if not vessels_in_range(s2_results):
        messagebox.showerror("Input error", "S2 vessel results must be between 0 and 120.")
        return

    # Pool S1 + S2 (12 vessels total) and evaluate per USP <711> S2.
    all_12 = s1_results + s2_results
    s2_passed, s2_reason = evaluate_s2(all_12, q)
    # Always prefix with the S1 outcome for transparency.
    combined_reason = f"S1: {s1_reason}\n\nS2: {s2_reason}"
    show_verdict(s2_passed, combined_reason)


def on_clear():
    """Reset every input and hide the S2 panel so the form is fresh."""
    q_entry.delete(0, tk.END)
    for e in s1_entries + s2_entries:
        e.delete(0, tk.END)
    verdict_label.config(text="")
    reason_label.config(text="")
    hide_s2_panel()


# ---------------------------------------------------------------------------
# GUI display helpers
# ---------------------------------------------------------------------------

def show_verdict(passed, reason):
    """Update the big PASS/FAIL label and the detailed reason text."""
    verdict_label.config(
        text="PASS" if passed else "FAIL",
        foreground="#1b8a3a" if passed else "#c0392b",
    )
    reason_label.config(text=reason)


def show_s2_panel():
    """Reveal the S2 input frame (only used after S1 fails)."""
    s2_frame.grid()


def hide_s2_panel():
    """Hide the S2 input frame (default state, or after a successful S1)."""
    s2_frame.grid_remove()


# ---------------------------------------------------------------------------
# Build the GUI
# ---------------------------------------------------------------------------

root = tk.Tk()
root.title("USP <711> Dissolution — S1 / S2 Evaluator")
root.resizable(False, False)

# Use the Vista theme on Windows for a cleaner look; fall back silently elsewhere.
style = ttk.Style()
try:
    style.theme_use("vista")
except tk.TclError:
    pass

# Root container with consistent padding.
main = ttk.Frame(root, padding=20)
main.grid(row=0, column=0)

# --- Title ---
ttk.Label(
    main,
    text="USP <711> Dissolution Stage Evaluator",
    font=("Segoe UI", 13, "bold"),
).grid(row=0, column=0, columnspan=4, pady=(0, 12))

# --- Q-value input ---
ttk.Label(main, text="Q value (%):").grid(row=1, column=0, sticky="e", padx=(0, 8), pady=4)
q_entry = ttk.Entry(main, width=10)
q_entry.grid(row=1, column=1, sticky="w", pady=4)

ttk.Separator(main, orient="horizontal").grid(row=2, column=0, columnspan=4, sticky="ew", pady=10)

# --- S1 vessel inputs (always visible) ---
s1_frame = ttk.LabelFrame(main, text="Stage 1 — 6 vessels", padding=10)
s1_frame.grid(row=3, column=0, columnspan=4, sticky="ew")

s1_entries = []  # references to S1 Entry widgets, indexed 0..5
for i in range(6):
    # Arrange vessels in a 3-row × 2-column grid inside the S1 frame.
    r, c = divmod(i, 2)
    ttk.Label(s1_frame, text=f"Vessel {i + 1}:").grid(
        row=r, column=c * 2, sticky="e", padx=(0, 8), pady=3
    )
    e = ttk.Entry(s1_frame, width=10)
    e.grid(row=r, column=c * 2 + 1, sticky="w", padx=(0, 16), pady=3)
    s1_entries.append(e)

# --- S2 vessel inputs (hidden until S1 fails) ---
s2_frame = ttk.LabelFrame(main, text="Stage 2 — 6 additional vessels", padding=10)
s2_frame.grid(row=4, column=0, columnspan=4, sticky="ew", pady=(10, 0))

s2_entries = []  # references to S2 Entry widgets, indexed 0..5 (vessels 7..12)
for i in range(6):
    r, c = divmod(i, 2)
    ttk.Label(s2_frame, text=f"Vessel {i + 7}:").grid(
        row=r, column=c * 2, sticky="e", padx=(0, 8), pady=3
    )
    e = ttk.Entry(s2_frame, width=10)
    e.grid(row=r, column=c * 2 + 1, sticky="w", padx=(0, 16), pady=3)
    s2_entries.append(e)

# Start with the S2 panel hidden — it only appears after an S1 failure.
s2_frame.grid_remove()

# --- Action buttons ---
btn_frame = ttk.Frame(main)
btn_frame.grid(row=5, column=0, columnspan=4, pady=(14, 6))
ttk.Button(btn_frame, text="Evaluate", command=on_evaluate).grid(row=0, column=0, padx=5)
ttk.Button(btn_frame, text="Clear", command=on_clear).grid(row=0, column=1, padx=5)

ttk.Separator(main, orient="horizontal").grid(row=6, column=0, columnspan=4, sticky="ew", pady=10)

# --- Verdict + reason output ---
verdict_label = ttk.Label(main, text="", font=("Segoe UI", 18, "bold"))
verdict_label.grid(row=7, column=0, columnspan=4)

reason_label = ttk.Label(main, text="", wraplength=380, justify="center", font=("Segoe UI", 9))
reason_label.grid(row=8, column=0, columnspan=4, pady=(6, 0))

# Hand control to tkinter's event loop.
root.mainloop()
