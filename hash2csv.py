import hashlib
import hmac
import tkinter as tk
from tkinter import messagebox
import csv
from datetime import datetime
import numpy as np
from collections import defaultdict
import os

# Block hashes
BLOCK_HASH = '0000000000000000001b34dc6a1e86083f95500b096231436e9b25cbdd0075c4'
US_BLOCK_HASH = '000000000000000000066448f2f56069750fc40c718322766b6bdf63fdcf45b8'

# Crypto and multiplier calculation
def sha256_hex(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()

def get_multiplier(server_seed: str, use_us_block=False) -> float:
    key = US_BLOCK_HASH if use_us_block else BLOCK_HASH
    hmac_hash = hmac.new(server_seed.encode(), key.encode(), hashlib.sha256).hexdigest()
    hex_part = hmac_hash[:8]
    dec = int(hex_part, 16)
    multiplier = ((4294967296 / (dec + 1)) * (1 - 0.01))
    return int(multiplier * 100) / 100

def generate_chain_and_multipliers(initial_seed: str, count: int, use_us_block=False):
    seeds = [initial_seed]
    for _ in range(count - 1):
        seeds.append(sha256_hex(seeds[-1]))
    return [get_multiplier(seed, use_us_block) for seed in seeds]

# Streak detection
def find_sub2x_streaks(multipliers, threshold=2.0):
    streaks = []
    current_streak = 0
    start_index = 0
    for i, m in enumerate(multipliers):
        if m < threshold:
            if current_streak == 0:
                start_index = i
            current_streak += 1
        else:
            if current_streak > 0:
                streaks.append((current_streak, start_index))
                current_streak = 0
    if current_streak > 0:
        streaks.append((current_streak, start_index))
    return streaks

def find_top_streaks(streaks, top_n=100):
    top = sorted(streaks, key=lambda x: x[0], reverse=True)[:top_n]
    return sorted(top, key=lambda x: x[1])

def streak_statistics(streaks):
    if not streaks:
        return {}
    lengths = [s[0] for s in streaks]
    return {
        "Total Sub-2X Streaks": len(streaks),
        "Longest Sub-2X Streak": max(lengths),
        "Average Streak Length": round(np.mean(lengths), 2),
        "Streak Length Std Dev": round(np.std(lengths), 2),
    }

def multiplier_statistics(data):
    return {
        "Average Multiplier": round(np.mean(data), 4),
        "Median Multiplier": round(np.median(data), 4),
        "Max Multiplier": round(np.max(data), 2),
        "Min Multiplier": round(np.min(data), 2),
        "25th Percentile": round(np.percentile(data, 25), 2),
        "50th Percentile": round(np.percentile(data, 50), 2),
        "75th Percentile": round(np.percentile(data, 75), 2),
        "Standard Deviation": round(np.std(data), 4)
    }

def gap_statistics(top_streaks):
    gaps = [j[1] - i[1] for i, j in zip(top_streaks[:-1], top_streaks[1:])]
    if not gaps:
        return {"Average Gap Between Top Streaks": 0, "Std Dev of Gaps": 0, "Minimum Gap": 0, "Maximum Gap": 0, "Min Gap Between": "N/A", "Max Gap Between": "N/A"}
    min_gap = min(gaps)
    max_gap = max(gaps)
    min_index = gaps.index(min_gap)
    max_index = gaps.index(max_gap)
    return {
        "Average Gap Between Top Streaks": round(np.mean(gaps), 2),
        "Std Dev of Gaps": round(np.std(gaps), 2),
        "Minimum Gap": min_gap,
        "Maximum Gap": max_gap,
        "Min Gap Between": f"{top_streaks[min_index][0]} @ {top_streaks[min_index][1]} → {top_streaks[min_index+1][0]} @ {top_streaks[min_index+1][1]} (gap = {min_gap})",
        "Max Gap Between": f"{top_streaks[max_index][0]} @ {top_streaks[max_index][1]} → {top_streaks[max_index+1][0]} @ {top_streaks[max_index+1][1]} (gap = {max_gap})"
    }

def analyze_streak_gaps_by_length_from_all(all_streaks):
    streak_groups = defaultdict(list)
    for length, index in all_streaks:
        streak_groups[length].append(index)

    result = {}
    for length, indices in streak_groups.items():
        if len(indices) < 2:
            continue
        indices.sort()
        gaps = [j - i for i, j in zip(indices[:-1], indices[1:])]
        result[length] = {
            "Min Gap": min(gaps),
            "Max Gap": max(gaps),
            "Avg Gap": round(np.mean(gaps), 2),
            "Count": len(indices)
        }
    return result

def save_crash_history_only(data, filename):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Index", "Crash Multiplier"])
        for i, val in enumerate(data):
            writer.writerow([i, val])

def show_summary_window(stats_all, stats_streaks, stats_gap, top_streaks, count, detailed_gaps, multipliers):
    text = f"Top 100 Sub-2X Streaks (from {count} games):\n"
    text += ", ".join(f"{length} @ {index}" for length, index in top_streaks)
    text += "\n\n--- Multiplier Stats ---\n"
    for k, v in stats_all.items():
        text += f"{k}: {v}\n"
    text += "\n--- Streak Stats ---\n"
    for k, v in stats_streaks.items():
        text += f"{k}: {v}\n"
    text += "\n--- Gap Stats ---\n"
    for k, v in stats_gap.items():
        text += f"{k}: {v}\n"
    text += "\n--- Gap Per Streak Length ---\n"
    for s_len in sorted(detailed_gaps):
        s = detailed_gaps[s_len]
        text += f"Streak {s_len}: Min = {s['Min Gap']}, Max = {s['Max Gap']}, Avg = {s['Avg Gap']}, Count = {s['Count']}\n"

    text += "\n--- Full Crash Multiplier History ---\n"
    for i, val in enumerate(multipliers):
        text += f"{i}: {val}\n"

    popup = tk.Toplevel()
    popup.title("Crash Analysis Summary")
    popup.geometry("700x600")

    text_widget = tk.Text(popup, wrap="word")
    text_widget.insert("1.0", text)
    text_widget.config(state="disabled")
    text_widget.pack(expand=True, fill="both")

    scrollbar = tk.Scrollbar(popup, command=text_widget.yview)
    scrollbar.pack(side="right", fill="y")
    text_widget.config(yscrollcommand=scrollbar.set)

def run_simulation():
    seed = entry_seed.get().strip()
    if len(seed) < 64:
        messagebox.showerror("Error", "Invalid server seed hash.")
        return

    try:
        count = int(entry_count.get().strip())
    except ValueError:
        messagebox.showerror("Error", "Enter a valid number of samples.")
        return

    use_us_block = var_us.get()
    multipliers = generate_chain_and_multipliers(seed, count, use_us_block)
    all_streaks = find_sub2x_streaks(multipliers)
    top_streaks = find_top_streaks(all_streaks)
    stats_all = multiplier_statistics(multipliers)
    stats_streaks = streak_statistics(all_streaks)
    stats_gap = gap_statistics(top_streaks)
    detailed_gaps = analyze_streak_gaps_by_length_from_all(all_streaks)

    show_summary_window(stats_all, stats_streaks, stats_gap, top_streaks, count, detailed_gaps, multipliers)

    # Automatically save to folder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    short_hash = seed[:6]
    filename = f"crash_only_{short_hash}_{timestamp}.csv"

    save_dir = r"C:\Users\admin\Desktop\crash\crashLogs"
    os.makedirs(save_dir, exist_ok=True)

    path = os.path.join(save_dir, filename)
    save_crash_history_only(multipliers, path)

    messagebox.showinfo("Success", f"✅ Crash history automatically saved to:\n{path}")

# GUI Setup
root = tk.Tk()
root.title("Stake Crash History Viewer")
root.geometry("360x240")

tk.Label(root, text="Enter server seed hash:").pack(pady=5)
entry_seed = tk.Entry(root, width=66)
entry_seed.pack(pady=5)

tk.Label(root, text="Enter number of samples to simulate:").pack(pady=5)
entry_count = tk.Entry(root, width=20)
entry_count.insert(0, "10000")
entry_count.pack(pady=5)

var_us = tk.BooleanVar()
tk.Checkbutton(root, text="Use stake.us block hash", variable=var_us).pack(pady=5)

tk.Button(root, text="Run Simulation", command=run_simulation).pack(pady=20)
tk.Label(root, text="Generates crash multipliers only in CSV, full summary in popup.", fg="gray").pack()

root.mainloop()
