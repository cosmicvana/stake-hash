import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import sys
import os
import glob

def analyze_streaks(file_path):
    df = pd.read_csv(file_path, header=None, names=["Multiplier"])
    df = df[df["Multiplier"] != "Crash Multiplier"]
    df["Multiplier"] = df["Multiplier"].astype(float)

    streak_info = {length: [] for length in range(1, 100)}
    idx = 0
    while idx < len(df):
        if df.iloc[idx]["Multiplier"] < 2.00:
            start_idx = idx
            count = 0
            while idx < len(df) and df.iloc[idx]["Multiplier"] < 2.00:
                count += 1
                idx += 1
            if count in streak_info:
                streak_info[count].append((start_idx, df["Multiplier"].iloc[start_idx:start_idx+count].tolist()))
        else:
            idx += 1

    summary = {k: len(v) for k, v in streak_info.items() if len(v) > 0}
    total_streaks = sum(summary.values())
    summary_table = [
        f"Streak Length: {k:<3} | Count: {v:<4} | Frequency: {v / total_streaks * 100:.2f}%"
        for k, v in sorted(summary.items()) if k >= 3
    ]

    results = {}
    for streak_len, entries in streak_info.items():
        if streak_len >= 3 and entries:
            indices = [e[0] for e in entries]
            mult_strs = [f"[{', '.join(f'{x:.2f}' for x in e[1])}]" for e in entries]
            results[streak_len] = {
                "Start Indices": indices,
                "Multiplier Sequences": mult_strs
            }

    return results, summary_table

def browse_file(file_path=None):
    if not file_path:
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if file_path:
        global results
        results, summary = analyze_streaks(file_path)

        listbox.delete(0, tk.END)
        summary_box.delete("1.0", tk.END)
        text_display.delete("1.0", tk.END)

        for key in sorted(results.keys()):
            listbox.insert(tk.END, f"Streak Length {key}")

        summary_box.insert(tk.END, "=== Frequency Summary ===\n")
        summary_box.insert(tk.END, "\n".join(summary))

def on_select(event):
    selection = listbox.curselection()
    if selection:
        streak_len = int(listbox.get(selection[0]).split()[-1])
        data = results[streak_len]
        text_display.delete("1.0", tk.END)
        text_display.insert(tk.END, f"Streak Length: {streak_len}\n\n")
        text_display.insert(tk.END, "Start Indices:\n")
        text_display.insert(tk.END, f"{data['Start Indices']}\n\n")
        text_display.insert(tk.END, "Multiplier Sequences:\n")
        text_display.insert(tk.END, "\n".join(data["Multiplier Sequences"]))

def get_latest_csv_from_logs():
    log_dir = r"C:\Users\admin\Desktop\crash\crashLogs"
    csv_files = glob.glob(os.path.join(log_dir, "*.csv"))
    if not csv_files:
        return None
    latest = max(csv_files, key=os.path.getmtime)
    return latest

# GUI Setup
root = tk.Tk()
root.title("Crash Sub-2.00 Streak Analyzer")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

load_button = tk.Button(frame, text="Load CSV File", command=browse_file)
load_button.pack()

main_pane = tk.PanedWindow(root, sashrelief=tk.RAISED, sashwidth=4, orient=tk.HORIZONTAL)
main_pane.pack(fill=tk.BOTH, expand=True)

listbox = tk.Listbox(main_pane, width=25)
listbox.bind("<<ListboxSelect>>", on_select)
main_pane.add(listbox)

right_pane = tk.PanedWindow(main_pane, orient=tk.VERTICAL, sashwidth=3)
main_pane.add(right_pane)

text_display = tk.Text(right_pane, wrap=tk.WORD, height=20)
right_pane.add(text_display)

summary_box = tk.Text(right_pane, wrap=tk.WORD, height=10, bg="#f0f0f0")
summary_box.config(state=tk.NORMAL)
right_pane.add(summary_box)

# Auto-load from command-line OR latest file
if len(sys.argv) > 1:
    browse_file(sys.argv[1])
else:
    latest_csv = get_latest_csv_from_logs()
    if latest_csv:
        browse_file(latest_csv)
    else:
        messagebox.showinfo("No CSV Found", "No CSV files found in crashLogs folder.")

root.mainloop()
