import os
import traceback
from collections import deque
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import pandas as pd

BASE_DIR = r"C:\Users\Pc1\Desktop\AI Project\Datasets"
SIZES    = ["Small", "Large"]

names = {}
people = {}
papers = {}
data_loaded = False

def load_data(size, log):
    log.insert("end", f"[DEBUG] Loading “{size}” dataset...\n", "debug")
    sci_file  = f"{size.lower()}_scientists.csv"
    pap_file  = f"{size.lower()}_papers.csv"
    auth_file = f"{size.lower()}_authors.csv"

    for fn in (sci_file, pap_file, auth_file):
        p = os.path.join(BASE_DIR, fn)
        ok = os.path.isfile(p)
        tag = "ok" if ok else "error"
        log.insert("end", f" • {fn}: {'FOUND' if ok else 'MISSING'}\n", tag)

    names.clear()
    people.clear()
    papers.clear()

    df = pd.read_csv(os.path.join(BASE_DIR, sci_file), encoding="utf-8")
    for _, r in df.iterrows():
        sid, nm = str(r["scientist_id"]), r["name"]
        people[sid] = {"name": nm, "papers": set()}
        names.setdefault(nm.lower(), set()).add(sid)
    log.insert("end", f"[DEBUG] → {len(df)} scientists loaded\n", "debug")

    df = pd.read_csv(os.path.join(BASE_DIR, pap_file), encoding="utf-8")
    for _, r in df.iterrows():
        pid = str(r["paper_id"])
        papers[pid] = {"title": r["title"], "year": r["year"], "authors": set()}
    log.insert("end", f"[DEBUG] → {len(df)} papers loaded\n", "debug")

    df = pd.read_csv(os.path.join(BASE_DIR, auth_file), encoding="utf-8")
    count = 0
    for _, r in df.iterrows():
        sid, pid = str(r["scientist_id"]), str(r["paper_id"])
        if sid in people and pid in papers:
            people[sid]["papers"].add(pid)
            papers[pid]["authors"].add(sid)
            count += 1
    log.insert("end", f"[DEBUG] → {count} author links\n", "debug")

def neighbors_for_person(sid):
    res = set()
    for pid in people[sid]["papers"]:
        for co in papers[pid]["authors"]:
            if co != sid:
                res.add((pid, co))
    return res

def shortest_path(src, tgt):
    if src == tgt:
        return []
    frontier = deque([(src, [])])
    explored = {src}
    while frontier:
        cur, path = frontier.popleft()
        for pid, nei in neighbors_for_person(cur):
            if nei in explored:
                continue
            new_path = path + [(pid, nei)]
            if nei == tgt:
                return new_path
            explored.add(nei)
            frontier.append((nei, new_path))
    return None

def main():
    global data_loaded

    app = tk.Tk()
    app.title("Co-Authorship Explorer")
    app.configure(bg="#f5f5f5")

    style = ttk.Style(app)
    style.theme_use("clam")

    ACCENT = "#4a90e2"
    style.configure("TFrame", background="#f5f5f5")
    style.configure("TLabel",
                    background="#f5f5f5",
                    foreground="#333333",
                    font=("Segoe UI", 11))
    style.configure("TButton",
                    background=ACCENT,
                    foreground="white",
                    font=("Segoe UI", 10, "bold"),
                    padding=8)
    style.map("TButton",
              background=[("active", "#357ab8")])
    style.configure("TCombobox",
                    fieldbackground="white",
                    background="white",
                    foreground="#333333",
                    font=("Segoe UI", 10))
    style.map("TCombobox",
              fieldbackground=[("readonly", "white")])

    frm = ttk.Frame(app, padding=12)
    frm.pack(fill="both", expand=True)

    ttk.Label(frm, text="Dataset:").grid(row=0, column=0, sticky="w", padx=4, pady=4)
    size_var = tk.StringVar(value="Small")
    ds_box = ttk.Combobox(frm, textvariable=size_var,
                          values=SIZES, state="readonly", width=12)
    ds_box.grid(row=0, column=1, sticky="w", padx=4, pady=4)
    load_btn = ttk.Button(frm, text="Load Data", command=lambda: on_load())
    load_btn.grid(row=0, column=2, sticky="w", padx=4, pady=4)

    ttk.Label(frm, text="From:").grid(row=1, column=0, sticky="w", padx=4, pady=4)
    from_cb = ttk.Combobox(frm, values=[], width=32)
    from_cb.grid(row=1, column=1, columnspan=2, sticky="ew", padx=4, pady=4)

    ttk.Label(frm, text="To:").grid(row=2, column=0, sticky="w", padx=4, pady=4)
    to_cb = ttk.Combobox(frm, values=[], width=32)
    to_cb.grid(row=2, column=1, columnspan=2, sticky="ew", padx=4, pady=4)

    search_btn = ttk.Button(frm, text="🔍 Find Path", command=lambda: on_search())
    search_btn.grid(row=3, column=0, columnspan=3, sticky="ew", padx=4, pady=8)

    log = scrolledtext.ScrolledText(frm,
                                    bg="white", fg="#333333",
                                    insertbackground="#333333",
                                    font=("Consolas", 10),
                                    wrap="word", height=16)
    log.grid(row=4, column=0, columnspan=3, sticky="nsew", padx=4, pady=4)
    frm.rowconfigure(4, weight=1)
    frm.columnconfigure(2, weight=1)

    log.tag_config("debug", foreground="#888888")
    log.tag_config("ok",    foreground="#27ae60")
    log.tag_config("error", foreground="#e74c3c")
    log.tag_config("info",  foreground=ACCENT)

    def on_load():
        global data_loaded
        data_loaded = False
        log.delete("1.0", "end")
        log.insert("end", "[INFO] Loading data…\n", "info")
        try:
            load_data(size_var.get(), log)
            names_list = sorted(p["name"] for p in people.values())
            from_cb["values"] = names_list
            to_cb["values"]   = names_list
            data_loaded = True
            log.insert("end", "[INFO] Data loaded successfully 👍\n", "info")
        except Exception:
            messagebox.showerror("Load Error",
                                 "Failed to load data—see log for details.")
            log.insert("end", traceback.format_exc(), "error")

    def filter_cb(evt):
        txt = evt.widget.get().lower()
        base = sorted(p["name"] for p in people.values())
        evt.widget["values"] = [n for n in base if txt in n.lower()] if txt else base

    def on_search():
        log.delete("1.0", "end")
        if not data_loaded:
            messagebox.showwarning("No Data", "Please click “Load Data” first.")
            return
        n1, n2 = from_cb.get().strip(), to_cb.get().strip()
        ids1, ids2 = names.get(n1.lower()), names.get(n2.lower())
        if not ids1 or not ids2:
            messagebox.showerror("Name Error",
                                 "One or both names not found.")
            return
        src, tgt = next(iter(ids1)), next(iter(ids2))
        path = shortest_path(src, tgt)
        if path is None:
            messagebox.showinfo("No Path",
                                f"No connection between {n1} and {n2}.")
            return

        log.insert("end", f"{len(path)} degrees of separation:\n\n", "info")
        prev = src
        for i, (pid, sid) in enumerate(path, 1):
            p1, p2 = people[prev]["name"], people[sid]["name"]
            title  = papers[pid]["title"]
            log.insert("end",
                       f"{i}. {p1} → {p2}  (\"{title}\")\n")
            prev = sid

    load_btn.configure(command=on_load)
    search_btn.configure(command=on_search)
    from_cb.bind("<KeyRelease>", filter_cb)
    to_cb.bind("<KeyRelease>", filter_cb)

    app.mainloop()

if __name__ == "__main__":
    main()
