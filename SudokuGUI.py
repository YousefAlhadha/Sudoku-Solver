import sys, platform, time, tkinter as tk
from tkinter import messagebox
from Sudoku import readSudoku, sudoku, versions, solved, limitations, toLaTeX, solve

# ═══════════════════════════════════════════════════════════════════
# CROSS-PLATFORM FONTS
# ═══════════════════════════════════════════════════════════════════

_is_win = platform.system() == "Windows"
_FONT_SANS = "Segoe UI" if _is_win else "SF Pro Display"
_FONT_MONO = "Consolas" if _is_win else "Menlo"

FONT_NUM  = (_FONT_SANS, 20, "bold")
FONT_CAND = (_FONT_MONO, 8)
FONT_LABEL= (_FONT_SANS, 11)
FONT_SECT = (_FONT_SANS, 11, "bold")
FONT_STAT_V=(_FONT_SANS, 20, "bold")
FONT_STAT_L=(_FONT_SANS, 10)
FONT_BTN  = (_FONT_SANS, 12, "bold")
FONT_INFO = (_FONT_SANS, 11)
FONT_LEG  = (_FONT_SANS, 10)

# Dark theme – deep navy/violet tones
BG_APP      = "#1C1C1E"
BG_PANEL    = "#2C2C2E"
BG_CARD     = "#3A3A3C"
ACCENT      = "#1CA10D"
ACCENT2     = "#2F80B5"
C_GIVEN_BG  = "#1C3A5C"; C_GIVEN_FG  = "#64B5F6"
C_SOLVED_BG = "#162E20"; C_SOLVED_FG = "#66BB6A"
C_OPEN_BG   = "#2C2C2E"; C_OPEN_FG   = "#9E9E9E"
C_ELIM_BG   = "#2E1414"; C_ELIM_FG   = "#EF5350"
C_ACTIVE_BG = "#473717"; C_ACTIVE_FG = "#FFB74D"
C_EDIT_BG   = "#2C2C2E"; C_EDIT_FG   = "#64B5F6"
C_BOX_LINE  = "#888888"
C_CELL_LINE = "#48484A"
C_TEXT      = "#FFFFFF"
C_TEXT_DIM  = "#AAAAAA"
C_HINT_BG   = "#1A1A35"
C_INFO_BG   = "#1A1A30"

C_SECT      = "#FFFFFF"   # dark theme
C_SECT_LIGHT= "#060606"   # light theme

# Light theme
LIGHT = {
    "BG_APP":"#D6D6D6", "BG_PANEL":"#FFFFFF", "BG_CARD":"#DEDEDE",
    "ACCENT":"#63A9FF", "ACCENT2":"#FF6B9D",
    "C_GIVEN_BG":"#C0DBFB", "C_GIVEN_FG":"#1565C0",
    "C_SOLVED_BG":"#CAE5CC", "C_SOLVED_FG":"#2E7D32",
    "C_OPEN_BG":"#FFFFFF", "C_OPEN_FG":"#616161",
    "C_ELIM_BG":"#F9D7DC", "C_ELIM_FG":"#C62828",
    "C_ACTIVE_BG":"#F8EBC1", "C_ACTIVE_FG":"#E65100",
    "C_EDIT_BG":"#FFFFFF", "C_EDIT_FG":"#1565C0",
    "C_BOX_LINE":"#555555", "C_CELL_LINE":"#D0D0D8",
    "C_TEXT":"#1A1A2E", "C_TEXT_DIM":"#8888AA",
    "C_HINT_BG":"#EEEEF4", "C_INFO_BG":"#F5F5FA",
    "C_SECT": C_SECT_LIGHT,
}
DARK = {k: globals()[k] for k in LIGHT}

CELL_SIZE = 56

PUZZLES = {
    "Easy  —  sc3":
        ".26...81.\n3..7.8..6\n4...5...7\n.5.1.7.9.\n..39.51..\n.4.3.2.5.\n1...3...2\n5..2.4..9\n.38...46.",
    "Medium  —  sc2":
        "8156....4\n6...75.8.\n....9....\n9...417..\n.4.....2.\n..623...8\n....5....\n.5.91...6\n1....7895",
    "Hard  —  sc4":
        "....6..8.\n.2.......\n..1......\n.7....1.2\n5...3....\n......4..\n..42.1...\n3..7..6..\n.......5.",
    "Medium-hard  —  sc5":
        ".5..6...1\n..48...7.\n8......52\n2...57.3.\n.........\n.3.69...5\n79......8\n.1...65..\n5...3..6.",
}


class SudokuGUI:
    def __init__(self, root):
        self.root       = root
        self.root.title("Sudoku Solver")
        self.root.configure(bg=BG_APP)
        self._is_dark   = True

        self.cells        = {}
        self.edit_entries = {}
        self.given_mask   = [[False]*9 for _ in range(9)]
        self.edit_mode    = False

        self.anim_id      = None
        self.anim_steps   = []
        self.anim_idx     = 0
        self.running      = False
        self.step_count   = 0
        self.original_data = None

        self._build_ui()
        self._load_puzzle(list(PUZZLES.keys())[0])
        self.root.update_idletasks()
        min_w = self.root.winfo_width()
        self.root.geometry(f"{min_w}x900")
        self.root.minsize(min_w, 600)
        self.root.resizable(True, True)

    # ── Build ──────────────────────────────────────────────────────

    def _build_ui(self):
        # Outer container with subtle border
        self._outer = tk.Frame(self.root, bg=BG_APP)
        self._outer.pack(padx=20, pady=16)

        # ── Top bar: theme button ────────────────────────────────────────
        self._top_bar = tk.Frame(self._outer, bg=BG_APP)
        self._top_bar.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 4))
        self.theme_btn = tk.Label(self._top_bar, text="☀", font=(_FONT_SANS, 14),
                                  bg=BG_CARD, fg=C_TEXT, padx=10, pady=4,
                                  cursor="hand2")
        self.theme_btn.pack(side="right")
        self.theme_btn.bind("<Button-1>", lambda e: self._toggle_theme())
        self.theme_btn.bind("<Enter>", lambda e: self.theme_btn.configure(bg=BG_PANEL))
        self.theme_btn.bind("<Leave>", lambda e: self.theme_btn.configure(bg=BG_CARD))

        # ── Left side: grid + legend ─────────────────────────────────
        canvas_h = CELL_SIZE * 9 + 10
        self._outer.grid_rowconfigure(1, minsize=canvas_h)
        self.grid_container = tk.Frame(self._outer, bg=BG_APP)
        self.grid_container.grid(row=1, column=0, sticky="n", padx=(0, 16))
        self._build_canvas()
        self._build_edit_grid()
        self._build_legend()

        # ── Right panel ───────────────────────────────────────────────
        right = tk.Frame(self._outer, bg=BG_PANEL, width=280,
                         highlightbackground=C_CELL_LINE, highlightthickness=1)
        right.grid(row=1, column=1, sticky="nsew")
        right.grid_propagate(False)
        self._panel = right
        self._build_panel(right)

    # ── Canvas grid ──────────────────────────────────────────────────

    def _build_canvas(self):
        size = CELL_SIZE * 9 + 10
        self.canvas = tk.Canvas(self.grid_container, width=size, height=size,
                                bg=BG_APP, highlightthickness=0)
        self.canvas.pack()
        self._thin_lines = []
        self._box_lines  = []
        for i in range(10):
            x = i * CELL_SIZE + (i//3)*2 + 2
            y = i * CELL_SIZE + (i//3)*2 + 2
            if i % 3 != 0:
                self._thin_lines.append(self.canvas.create_line(
                    x, 0, x, size, fill=C_CELL_LINE, width=1))
                self._thin_lines.append(self.canvas.create_line(
                    0, y, size, y, fill=C_CELL_LINE, width=1))
        for i in range(4):
            x = i*(CELL_SIZE*3+2)+2
            y = i*(CELL_SIZE*3+2)+2
            self._box_lines.append(self.canvas.create_line(
                x, 0, x, size, fill=C_BOX_LINE, width=3))
            self._box_lines.append(self.canvas.create_line(
                0, y, size, y, fill=C_BOX_LINE, width=3))

        for r in range(9):
            for c in range(9):
                x = c*CELL_SIZE + (c//3)*2 + 2
                y = r*CELL_SIZE + (r//3)*2 + 2
                cx, cy = x+CELL_SIZE//2, y+CELL_SIZE//2
                bg_id = self.canvas.create_rectangle(
                    x+1, y+1, x+CELL_SIZE-1, y+CELL_SIZE-1,
                    fill=C_OPEN_BG, outline="")
                txt_id = self.canvas.create_text(
                    cx, cy, text="", fill=C_OPEN_FG, font=FONT_NUM)
                self.cells[(r, c)] = {"bg": bg_id, "txt": txt_id, "bg_rect": (x, y)}

    # ── Edit grid (overlay for custom input) ────────────────────────

    def _build_edit_grid(self):
        self.edit_frame = tk.Frame(self.grid_container, bg=BG_APP)
        for r in range(9):
            for c in range(9):
                vcmd = (self.root.register(self._validate_digit), '%P')
                px_l = 6 if c % 3 == 0 else 3
                px_r = 6 if c % 3 == 2 else 3
                py_t = 6 if r % 3 == 0 else 3
                py_b = 6 if r % 3 == 2 else 3
                e = tk.Entry(self.edit_frame, width=2, font=FONT_NUM,
                             bg=C_EDIT_BG, fg=C_EDIT_FG,
                             insertbackground=C_EDIT_FG,
                             relief="flat", bd=0, justify="center",
                             validate="key", validatecommand=vcmd,
                             highlightthickness=1,
                             highlightbackground=C_CELL_LINE,
                             highlightcolor=C_EDIT_FG)
                e.grid(row=r, column=c, padx=(px_l, px_r), pady=(py_t, py_b),
                       ipadx=8, ipady=10)
                for key, dr, dc in [("<Tab>", 0, 1), ("<Return>", 1, 0),
                                    ("<Right>", 0, 1), ("<Left>", 0, -1),
                                    ("<Down>", 1, 0), ("<Up>", -1, 0)]:
                    e.bind(key, lambda ev, r=r, c=c, dr=dr, dc=dc:
                           self._next_cell(r, c, dr, dc))
                self.edit_entries[(r, c)] = e

    def _validate_digit(self, val):
        return val == "" or (len(val) == 1 and val in "123456789")

    def _next_cell(self, r, c, dr, dc):
        self.edit_entries[((r+dr) % 9, (c+dc) % 9)].focus_set()
        return "break"

    # ── Legend ───────────────────────────────────────────────────────

    def _build_legend(self):
        self.legend_frame = tk.Frame(self.grid_container, bg=BG_APP)
        self.legend_frame.pack(fill="x", pady=(10, 0))
        legend_items = [
            ("pre-filled",  C_GIVEN_FG),
            ("solved",      C_SOLVED_FG),
            ("candidate",   C_OPEN_FG),
            ("eliminated",  C_ELIM_FG),
        ]
        for i, (txt, fg) in enumerate(legend_items):
            if i > 0:
                tk.Frame(self.legend_frame, width=1, bg=C_TEXT_DIM, height=12).pack(side="left", padx=8)
            d = tk.Canvas(self.legend_frame, width=10, height=10, bg=BG_APP, highlightthickness=0)
            d.create_oval(1, 1, 9, 9, fill=fg, outline="")
            d.pack(side="left")
            tk.Label(self.legend_frame, text=txt, font=FONT_LEG, bg=BG_APP, fg=C_TEXT_DIM).pack(side="left", padx=(4, 0))

    def _build_panel(self, parent):
        pd = dict(padx=20)
        self._section(parent, "Puzzle", pd, ytop=10)

        keys = list(PUZZLES.keys())
        self.puzzle_var = tk.StringVar(value=keys[0])
        self.puzzle_var.trace_add("write", lambda *_: self._load_puzzle(self.puzzle_var.get()))
        self._combo = tk.OptionMenu(parent, self.puzzle_var, keys[0], *keys[1:])
        self._combo.config(bg=BG_CARD, fg=C_TEXT, activebackground=BG_CARD,
                           activeforeground=C_TEXT, relief="flat", bd=0,
                           highlightthickness=0, font=FONT_LABEL, indicatoron=0)
        self._combo["menu"].config(bg=BG_CARD, fg=C_TEXT,
                                   activebackground=ACCENT,
                                   activeforeground="#FFFFFF",
                                   relief="flat", bd=0, font=FONT_LABEL)
        self._combo.pack(fill="x", **pd)

        self._divider(parent, pd)

        # Speed
        self._section(parent, "Speed", pd)
        sr = tk.Frame(parent, bg=BG_PANEL)
        sr.pack(fill="x", **pd)
        tk.Label(sr, text="Fast", font=FONT_LEG,
                 bg=BG_PANEL, fg=C_TEXT_DIM).pack(side="left")
        self.speed_ms = tk.IntVar(value=150)
        tk.Scale(sr, from_=20, to=800, resolution=20, orient="horizontal",
                 variable=self.speed_ms, bg=BG_PANEL, fg=C_TEXT_DIM,
                 troughcolor=BG_CARD, activebackground=ACCENT,
                 highlightthickness=0, showvalue=False, length=150, bd=0
                 ).pack(side="left", padx=6)
        tk.Label(sr, text="Slow", font=FONT_LEG,
                 bg=BG_PANEL, fg=C_TEXT_DIM).pack(side="left")

        self._divider(parent, pd)

        # Solve section
        self._section(parent, "Solve", pd)
        self.btn_solve = self._pill(parent, "▶   Solve automatically", ACCENT, self._start_auto)
        self.btn_instant = self._pill(parent, "⚡   Solve instantly", ACCENT2, self._solve_instantly)
        self.btn_timed   = self._pill(parent, "⏱   Benchmark",       ACCENT2, self._solve_timed)
        self.btn_step  = self._pill(parent, "⏭   Step forward",       ACCENT2, self._next_step)
        self.btn_back  = self._pill(parent, "⏮   Step back",          C_TEXT_DIM, self._prev_step, state="disabled")
        self.btn_pause = self._pill(parent, "⏸   Pause",              ACCENT, self._toggle_pause, state="disabled")
        self.btn_reset = self._pill(parent, "↻   Reset",              C_TEXT_DIM, self._reset)

        self._divider(parent, pd)

        # Custom puzzle
        self._section(parent, "Custom puzzle", pd)
        self.btn_edit = self._pill(parent, "✎   Enter puzzle", ACCENT2, self._enter_edit)
        self.btn_use  = self._pill(parent, "✓   Use this puzzle", ACCENT, self._use_custom, state="disabled")
        self.btn_clr  = self._pill(parent, "✕   Cancel",  C_TEXT_DIM, self._clear_edit, state="disabled")
        self.btn_clr.pack_forget()

        self.div_after_custom = self._divider(parent, pd)

        # 81-char string
        self._section(parent, "81-char string", pd)
        self.entry_81 = tk.Entry(parent, font=FONT_LABEL,
                                 bg=BG_CARD, fg=C_TEXT, insertbackground=C_TEXT,
                                 relief="flat", bd=10, justify="center")
        self.entry_81.pack(fill="x", padx=20, pady=(2, 6))
        self.entry_81.insert(0, "000000000000000000000000000000000000000000000000000000000000000000000000000000000")
        self.btn_load81 = self._pill(parent, "↺  Load", ACCENT2, self._load_81)
        self.btn_latex  = self._pill(parent, "📋  Copy to LaTeX", ACCENT2, self._copy_latex)

        self._divider(parent, pd)

        # Stats
        stats = tk.Frame(parent, bg=BG_PANEL)
        stats.pack(fill="x", **pd)
        self.stat_ver   = self._stat_card(stats, "possibilities", "–")
        tk.Frame(stats, bg=C_CELL_LINE, width=1).pack(side="left", fill="y", padx=8)
        self.stat_steps = self._stat_card(stats, "steps", "0")

        self._divider(parent, pd)

        # Info
        self._section(parent, "What's happening", pd, ybot=0)
        self.info_box = tk.Text(parent, width=28, height=6,
                                font=FONT_INFO,
                                bg=BG_CARD, fg=C_TEXT, insertbackground=C_TEXT,
                                relief="flat", bd=0, wrap="word",
                                state="disabled", padx=12, pady=8,
                                highlightthickness=0)
        self.info_box.pack(fill="x", pady=(4, 10), **pd)

    # ── Panel helpers ────────────────────────────────────────────────

    def _section(self, parent, text, pd, ytop=4, ybot=2):
        if not hasattr(self, '_sect_labels'):
            self._sect_labels = []
        lbl = tk.Label(parent, text=text, font=FONT_SECT,
                       bg=BG_PANEL, fg=C_SECT)
        lbl.pack(anchor="w", pady=(ytop, ybot), **pd)
        self._sect_labels.append(lbl)

    def _divider(self, parent, pd):
        f = tk.Frame(parent, bg=C_CELL_LINE, height=1)
        f.pack(fill="x", pady=(4, 2), **pd)
        return f

    def _stat_card(self, parent, label, initial):
        f = tk.Frame(parent, bg=BG_PANEL)
        f.pack(side="left", expand=True)
        val = tk.Label(f, text=initial, font=FONT_STAT_V, bg=BG_PANEL, fg=C_SECT)
        val.pack()
        tk.Label(f, text=label, font=FONT_STAT_L, bg=BG_PANEL, fg=C_TEXT_DIM).pack()
        return val

    # ── Modern pill button ──────────────────────────────────────────

    def _pill(self, parent, text, color, cmd, state="normal", side="top", expand=False):
        b = tk.Label(parent, text=text, font=FONT_BTN,
                     bg=color, fg="#FFFFFF", padx=14, pady=4,
                     cursor="hand2")
        b.pack(fill="x", padx=20, pady=2, side=side, expand=expand)
        b._btn_color = color
        b._btn_enabled = True

        def set_state(s):
            if s == "disabled":
                b._btn_enabled = False
                b.configure(bg="#555555", fg="#999999")
            else:
                b._btn_enabled = True
                b.configure(bg=color, fg="#FFFFFF")
        b._set_state = set_state

        def on_enter(e):
            if b._btn_enabled:
                b.configure(bg="#FFFFFF", fg=color)
        def on_leave(e):
            if b._btn_enabled:
                b.configure(bg=color, fg="#FFFFFF")
        def on_click(e):
            if not b._btn_enabled:
                return
            cmd()
            if b.winfo_containing(e.x_root, e.y_root) == b:
                b.configure(bg="#FFFFFF", fg=color)
        b.bind("<Enter>", on_enter)
        b.bind("<Leave>", on_leave)
        b.bind("<Button-1>", on_click)
        if state == "disabled":
            b._set_state("disabled")
        return b

    # ── Theme toggle ────────────────────────────────────────────────

    def _toggle_theme(self):
        dark = not self._is_dark
        import sys
        mod = sys.modules[__name__]
        old, new = (LIGHT, DARK) if dark else (DARK, LIGHT)
        self._is_dark = dark
        geom = self.root.geometry()

        for k, v in new.items():
            setattr(mod, k, v)

        self.root.configure(bg=new["BG_APP"])
        self._outer.configure(bg=new["BG_APP"])
        self.grid_container.configure(bg=new["BG_APP"])
        self._panel.configure(bg=new["BG_PANEL"], highlightbackground=new["C_CELL_LINE"])

        self._recolor_widgets(self._panel, old, new)
        self._recolor_widgets(self.grid_container, old, new)

        self._combo.config(bg=new["BG_CARD"], fg=new["C_TEXT"],
                           activebackground=new["BG_CARD"],
                           activeforeground=new["C_TEXT"])
        self._combo["menu"].config(bg=new["BG_CARD"], fg=new["C_TEXT"])

        # Section headers, stat values & info box
        self.info_box.configure(bg=BG_CARD, fg=C_TEXT)

        # Section headers & stat values
        for lbl in getattr(self, '_sect_labels', []):
            lbl.configure(fg=C_SECT, bg=BG_PANEL)
        for attr in ('stat_ver', 'stat_steps'):
            w = getattr(self, attr, None)
            if w:
                w.configure(fg=C_SECT, bg=BG_PANEL)

        # Top bar + theme button
        self._top_bar.configure(bg=new["BG_APP"])
        self.theme_btn.configure(text="☀" if dark else "☾",
                                 bg=BG_CARD, fg=C_TEXT)

        self.canvas.configure(bg=new["BG_APP"])
        for item_id in self._thin_lines:
            self.canvas.itemconfig(item_id, fill=new["C_CELL_LINE"])
        for item_id in self._box_lines:
            self.canvas.itemconfig(item_id, fill=new["C_BOX_LINE"])

        self._draw_data(self.init_data)
        self.root.geometry(geom)

    def _recolor_widgets(self, w, old, new):
        for child in w.winfo_children():
            try:
                bg = child.cget("bg")
            except Exception:
                bg = None
            try:
                fg = child.cget("fg")
            except Exception:
                fg = None
            cl = child.winfo_class()
            if bg and cl != "Button" and not hasattr(child, '_btn_color'):
                for k in old:
                    if bg == old[k] and k in new:
                        try:
                            child.configure(bg=new[k])
                        except Exception:
                            pass
                        break
            if fg and cl in ("Label", "Entry", "Text", "Menu") and not hasattr(child, '_btn_color'):
                for k in old:
                    if fg == old[k] and k in new and k != "BG_APP":
                        try:
                            child.configure(fg=new[k])
                        except Exception:
                            pass
                        break
            self._recolor_widgets(child, old, new)

    # ── Rendering ────────────────────────────────────────────────────

    def _format_candidates(self, opts):
        """Format candidates as a 3×3 grid using monospace font."""
        lines = []
        for row in range(3):
            line = ""
            for col in range(3):
                val = row * 3 + col + 1
                if val in opts:
                    line += str(val)
                else:
                    line += " "
                if col < 2:
                    line += " "
            lines.append(line)
        return "\n".join(lines)

    def _draw_frame(self, frame):
        for (r, c), (opts, ck) in frame.items():
            info = self.cells[(r, c)]
            bg_id, txt_id = info["bg"], info["txt"]
            bg = {"given": C_GIVEN_BG, "solved": C_SOLVED_BG, "open": C_OPEN_BG,
                  "elim": C_ELIM_BG, "active": C_ACTIVE_BG}[ck]
            fg = {"given": C_GIVEN_FG, "solved": C_SOLVED_FG, "open": C_OPEN_FG,
                  "elim": C_ELIM_FG, "active": C_ACTIVE_FG}[ck]
            self.canvas.itemconfig(bg_id, fill=bg)
            if len(opts) == 0:
                self.canvas.itemconfig(txt_id, text="✕", fill=C_ELIM_FG, font=FONT_NUM)
            elif len(opts) == 1:
                self.canvas.itemconfig(txt_id, text=str(opts[0]), fill=fg, font=FONT_NUM)
            else:
                self.canvas.itemconfig(txt_id, text=self._format_candidates(opts),
                                       fill=fg, font=FONT_CAND)

    def _color_key(self, r, c, opts, highlight=None, eliminated=None):
        if highlight and (r, c) == highlight:
            return "active"
        if eliminated and (r, c) in eliminated:
            return "elim"
        if self.given_mask[r][c]:
            return "given"
        if len(opts) == 1:
            return "solved"
        return "open"

    def _make_frame(self, data, highlight=None, eliminated=None):
        return {(r, c): (list(data[r][c]),
                         self._color_key(r, c, data[r][c], highlight, eliminated))
                for r in range(9) for c in range(9)}

    def _draw_data(self, data, highlight=None, eliminated=None):
        self._draw_frame(self._make_frame(data, highlight, eliminated))

    # ── Frame computation (unchanged logic) ─────────────────────────

    def _compute_frames(self, init_data):
        frames = []
        data = [[list(init_data[r][c]) for c in range(9)] for r in range(9)]

        def snap():
            return [[list(data[r][c]) for c in range(9)] for r in range(9)]

        def record(highlight=None, eliminated=None, info="",
                   grid_data=None, skip_in_auto=False):
            gd = grid_data if grid_data is not None else snap()
            frames.append((self._make_frame(gd, highlight, eliminated),
                           info, skip_in_auto))

        def find_hidden_singles(grid):
            fixed = []
            claimed = set()
            for unit_name, coords_list in (
                ("row",    [[(r, c) for c in range(9)] for r in range(9)]),
                ("column", [[(r, c) for r in range(9)] for c in range(9)]),
                ("box",    [[(b//3*3+i//3, b%3*3+i%3) for i in range(9)]
                           for b in range(9)]),
            ):
                for idx, coords in enumerate(coords_list):
                    already = {grid[r][c][0] for r, c in coords
                               if len(grid[r][c]) == 1}
                    for val in range(1, 10):
                        if val in already:
                            continue
                        cells = [(r, c) for r, c in coords
                                 if len(grid[r][c]) > 1 and val in grid[r][c]]
                        if len(cells) == 1:
                            r, c = cells[0]
                            if (r, c) not in claimed:
                                fixed.append((r, c, val, unit_name, idx + 1))
                                claimed.add((r, c))
            return fixed

        # ── Phase 1: Constraint propagation ──────────────────────────

        record(info="Initial puzzle")

        GROUPS = (
            ("row",    [(r, [(r, c) for c in range(9)]) for r in range(9)]),
            ("column", [(c, [(r, c) for r in range(9)]) for c in range(9)]),
            ("box",    [(b, [(b//3*3+i//3, b%3*3+i%3) for i in range(9)])
                        for b in range(9)]),
        )
        changed = True
        passes = 0
        while changed:
            passes += 1
            changed = False
            for gname, idx_list in GROUPS:
                for idx, coords in idx_list:
                    fixed = {data[r][c][0] for r, c in coords
                             if len(data[r][c]) == 1}
                    elim = []
                    for r, c in coords:
                        if len(data[r][c]) > 1:
                            nw = [v for v in data[r][c] if v not in fixed]
                            if nw != data[r][c]:
                                data[r][c] = nw
                                elim.append((r, c))
                    if elim:
                        changed = True
                        fixed_str = ", ".join(str(v) for v in sorted(fixed))
                        record(eliminated=set(elim),
                               info=f"limitLine() — {gname} {idx+1}\n\n"
                                    f"Fixed in this unit: {fixed_str}\n\n"
                                    f"Removed from {len(elim)} cell(s).")

            hs = find_hidden_singles(data)
            if hs:
                changed = True
                for r, c, val, uname, uidx in hs:
                    data[r][c] = [val]
                    record(highlight=(r, c),
                           info=f"hiddenSingle() — in {uname} {uidx}!\n\n"
                                f"{val} can only go in ({r+1},{c+1})\n"
                                f"within {uname} {uidx} — every other cell\n"
                                f"in this {uname} already has {val}\n"
                                f"eliminated or is fixed.")

        tup = tuple(tuple(data[r][c] for c in range(9)) for r in range(9))
        if solved(tup):
            record(info="Solved by logic alone! ✓")
            return frames

        # ── Phase 2: Backtracking ────────────────────────────────────

        record(info="limitations() is exhausted.\n"
                     "Entering backtracking search — trying\n"
                     "candidates one by one.")

        def _propagate(grid):
            while True:
                tup = limitations(tuple(
                    tuple(grid[r][c] for c in range(9)) for r in range(9)))
                for r in range(9):
                    for c in range(9):
                        grid[r][c] = list(tup[r][c])
                tup2 = tuple(
                    tuple(grid[r][c] for c in range(9)) for r in range(9))
                if versions(tup2) == 0:
                    return None
                if solved(tup2):
                    return tup2
                hs = find_hidden_singles(grid)
                if not hs:
                    return False
                for r, c, val, *_ in hs:
                    grid[r][c] = [val]

        def bt_search(grid_state, depth=0):
            status = _propagate(grid_state)
            if status is None:
                return None
            if status is not False:
                return status

            br, bc, bn = -1, -1, 10
            for r in range(9):
                for c in range(9):
                    n = len(grid_state[r][c])
                    if 1 < n < bn:
                        br, bc, bn = r, c, n
            if br == -1:
                return None

            candidates = sorted(grid_state[br][bc])
            cand_str = ", ".join(str(v) for v in candidates)

            for val in candidates:
                trial = [[list(grid_state[r][c]) for c in range(9)]
                         for r in range(9)]
                trial[br][bc] = [val]

                record(highlight=(br, bc),
                       info=f"Trying {val} at ({br+1},{bc+1})\n\n"
                            f"Candidates for this cell: {cand_str}")

                result = bt_search(trial, depth + 1)
                if result is not None:
                    frames.pop()
                    record(highlight=(br, bc),
                           info=f"✓ {val} at ({br+1},{bc+1}) → leads to solution!")
                    for r in range(9):
                        for c in range(9):
                            grid_state[r][c] = list(result[r][c])
                    return result

                record(highlight=(br, bc),
                       info=f"✗ {val} at ({br+1},{bc+1}) — contradiction.\n"
                            f"Undoing and trying next candidate.",
                       grid_data=trial,
                       skip_in_auto=True)

            return None

        result = bt_search(data)
        if result is not None:
            record(info="Solved by logic and guessing ✓")
        else:
            record(info="No solution exists for this puzzle. ✗")
        return frames

    # ── Playback ─────────────────────────────────────────────────────

    def _set_info(self, msg):
        self.info_box.config(state="normal")
        self.info_box.delete("1.0", "end")
        self.info_box.insert("end", msg)
        self.info_box.config(state="disabled")

    def _update_stats(self, frame_dict):
        total = 1
        for (r, c), (opts, _) in frame_dict.items():
            total *= len(opts) if opts else 1
        self.stat_ver.config(text=f"{total:,}" if total < 1_000_000 else f"{total:.1e}")
        self.stat_steps.config(text=str(self.anim_idx))

    def _show_frame(self, idx):
        if idx >= len(self.anim_steps):
            return
        step = self.anim_steps[idx]
        frame, info = step[0], step[1]
        self._draw_frame(frame)
        self._set_info(info)
        self._update_stats(frame)

    def _tick(self):
        if not self.running:
            return
        if self.anim_idx >= len(self.anim_steps):
            self._on_done()
            return
        while (self.anim_idx < len(self.anim_steps)
               and len(self.anim_steps[self.anim_idx]) > 2
               and self.anim_steps[self.anim_idx][2]):
            self.anim_idx += 1
            self.step_count += 1
        if self.anim_idx >= len(self.anim_steps):
            self._on_done()
            return
        self._show_frame(self.anim_idx)
        self.anim_idx += 1
        if self.anim_idx < len(self.anim_steps):
            self.anim_id = self.root.after(self.speed_ms.get(), self._tick)
        else:
            self._on_done()

    def _on_done(self):
        self.running = False
        self.btn_solve._set_state("normal")
        self.btn_instant._set_state("normal")
        self.btn_timed._set_state("normal")
        self.btn_step._set_state("normal")
        self.btn_pause.configure(text="⏸   Pause")
        self.btn_pause._set_state("disabled")
        self._update_back_btn()

    # ── Controls ─────────────────────────────────────────────────────

    def _prepare(self):
        if not self.anim_steps:
            self._set_info("Computing solution…")
            self.root.update()
            init = [[list(self.init_data[r][c]) for c in range(9)]
                    for r in range(9)]
            self.anim_steps = self._compute_frames(init)
            self.anim_idx = 0

    def _solve_instantly(self):
        self.root.config(cursor="watch")
        self.root.update()
        self._reset()
        self._prepare()
        if not self.anim_steps:
            self.root.config(cursor="")
            return
        for i in range(len(self.anim_steps)):
            self._show_frame(i)
        self.anim_idx = len(self.anim_steps)
        self.step_count = self.anim_idx
        self.stat_steps.config(text=str(self.step_count))
        self._on_done()
        self._update_back_btn()
        self.root.config(cursor="")

    def _solve_timed(self):
        self.root.config(cursor="watch")
        self.root.update()

        self.running = False
        if self.anim_id:
            self.root.after_cancel(self.anim_id)
            self.anim_id = None
        self.anim_steps = []
        self.anim_idx = 0

        s = ""
        for r in range(9):
            for c in range(9):
                opts = self.init_data[r][c]
                s += str(opts[0]) if len(opts) == 1 else "0"

        start = time.time()
        solution = solve(sudoku(s))
        elapsed = time.time() - start

        if solution is None:
            self._set_info(f"No solution found! ({elapsed:.4f}s)")
        else:
            for r in range(9):
                for c in range(9):
                    self.init_data[r][c] = list(solution[r][c])
            self._draw_data(self.init_data)
            self._set_info(f"Solved in {elapsed:.4f} seconds")
            self.stat_ver.config(text="1")
            self.stat_steps.config(text="1")
            self.btn_solve._set_state("disabled")
            self.btn_instant._set_state("disabled")
            self.btn_timed._set_state("normal")
            self.btn_step._set_state("disabled")
            self.btn_back._set_state("disabled")

        self.root.config(cursor="")

    def _start_auto(self):
        if self.running:
            return
        self._prepare()
        self.running = True
        self.btn_solve._set_state("disabled")
        self.btn_instant._set_state("disabled")
        self.btn_timed._set_state("disabled")
        self.btn_step._set_state("disabled")
        self.btn_back._set_state("disabled")
        self.btn_pause._set_state("normal")
        self._tick()

    def _next_step(self):
        if self.running:
            return
        self._prepare()
        if self.anim_idx < len(self.anim_steps):
            self._show_frame(self.anim_idx)
            self.anim_idx += 1
        if self.anim_idx >= len(self.anim_steps):
            self._on_done()
        self._update_back_btn()

    def _prev_step(self):
        if self.running:
            return
        if self.anim_idx > 1:
            self.anim_idx -= 1
            self._show_frame(self.anim_idx - 1)
        self.btn_solve._set_state("normal")
        self.btn_step._set_state("normal")
        self._update_back_btn()

    def _update_back_btn(self):
        self.btn_back._set_state("normal" if self.anim_idx > 1 else "disabled")

    def _toggle_pause(self):
        if self.running:
            self.running = False
            if self.anim_id:
                self.root.after_cancel(self.anim_id)
            self.btn_pause.configure(text="▶   Resume")
            self.btn_solve._set_state("disabled")
            self.btn_step._set_state("normal")
            self._update_back_btn()
        else:
            self.running = True
            self.btn_pause.configure(text="⏸   Pause")
            self.btn_solve._set_state("disabled")
            self.btn_step._set_state("disabled")
            self.btn_back._set_state("disabled")
            self._tick()

    def _reset(self):
        self.running = False
        if self.anim_id:
            self.root.after_cancel(self.anim_id)
        self.anim_steps = []
        self.anim_idx = 0
        self.btn_solve._set_state("normal")
        self.btn_instant._set_state("normal")
        self.btn_timed._set_state("normal")
        self.btn_step._set_state("normal")
        self.btn_back._set_state("disabled")
        self.btn_pause.configure(text="⏸   Pause")
        self.btn_pause._set_state("disabled")
        if self.original_data is not None:
            self.init_data = [[list(self.original_data[r][c]) for c in range(9)] for r in range(9)]
            self.given_mask = [[len(self.original_data[r][c]) == 1 for c in range(9)] for r in range(9)]
            self._draw_data(self.init_data)
            self.stat_ver.config(text="–")
            self.stat_steps.config(text="0")
            self._set_info("Reset to original puzzle.")

    # ── Puzzle loading ───────────────────────────────────────────────

    def _load_puzzle(self, name):
        if self.edit_mode:
            self.edit_frame.pack_forget()
            self.legend_frame.pack_forget()
            self.canvas.pack()
            self.legend_frame.pack(fill="x", pady=(10, 0))
            self.edit_mode = False
        self.running = False
        self.anim_steps = []
        self.anim_idx = 0
        parsed = readSudoku(PUZZLES[name])
        self.init_data = [[list(parsed[r][c]) for c in range(9)] for r in range(9)]
        self.original_data = parsed
        self.given_mask = [[len(parsed[r][c]) == 1 for c in range(9)] for r in range(9)]
        self.btn_solve._set_state("normal")
        self.btn_instant._set_state("normal")
        self.btn_timed._set_state("normal")
        self.btn_step._set_state("normal")
        self.btn_back._set_state("disabled")
        self.btn_pause._set_state("disabled")

        def _update_text():
            self.btn_pause.configure(text="⏸   Pause")
        self.btn_pause._update_text = _update_text
        try:
            self.btn_pause._update_text()
        except Exception:
            pass

        self.btn_edit._set_state("normal")
        self.btn_use._set_state("disabled")
        self.btn_clr.pack_forget()
        self._draw_data(self.init_data)
        self.stat_ver.config(text="–")
        self.stat_steps.config(text="0")
        self.root.focus_set()
        self._set_info("Press  ▶ Solve automatically\n"
                       "to watch the full solution.\n\n"
                       "Or press  ⏭ Step forward  to go\n"
                       "one step at a time.")

    def _load_81(self):
        s = self.entry_81.get().strip()
        if len(s) != 81 or not all(c in "0123456789" for c in s):
            messagebox.showerror("Invalid input",
                "Must be exactly 81 characters (digits 0-9).\n\n"
                "0 = empty cell\n1-9 = given digit")
            return
        clues = sum(1 for c in s if c != "0")
        if clues < 17:
            messagebox.showwarning("Too few clues",
                f"You entered {clues} clue(s).\nA valid Sudoku needs at least 17.")
            return
        if self.edit_mode:
            self.edit_frame.pack_forget()
            self.legend_frame.pack_forget()
            self.canvas.pack()
            self.legend_frame.pack(fill="x", pady=(10, 0))
            self.edit_mode = False
        self.running = False
        self.anim_steps = []
        self.anim_idx = 0
        parsed = sudoku(s)
        msg = self._check_conflicts(parsed)
        if msg:
            messagebox.showerror("Unsolvable", msg)
            return
        self.init_data = [[list(parsed[r][c]) for c in range(9)] for r in range(9)]
        self.original_data = parsed
        self.given_mask = [[len(parsed[r][c]) == 1 for c in range(9)] for r in range(9)]
        self.btn_solve._set_state("normal")
        self.btn_instant._set_state("normal")
        self.btn_timed._set_state("normal")
        self.btn_step._set_state("normal")
        self.btn_back._set_state("disabled")
        self.btn_pause.configure(text="⏸   Pause")
        self.btn_pause._set_state("disabled")

        self.btn_edit._set_state("normal")
        self.btn_use._set_state("disabled")
        self.btn_clr.pack_forget()
        self._draw_data(self.init_data)
        self.stat_ver.config(text="–")
        self.stat_steps.config(text="0")
        self.root.focus_set()
        self._set_info(f"Loaded puzzle ({clues} clues).\n\n"
                       "Press  ▶ Solve automatically  or\n"
                       "⏭ Step forward  to solve it.")

    def _copy_latex(self):
        latex = toLaTeX(self.init_data)
        self.root.clipboard_clear()
        self.root.clipboard_append(latex)
        self._set_info("LaTeX copied to clipboard!")

    def _check_conflicts(self, parsed):
        for r in range(9):
            vals = [parsed[r][c][0] for c in range(9) if len(parsed[r][c]) == 1]
            if len(vals) != len(set(vals)):
                return f"Row {r+1} has duplicate fixed digits."
        for c in range(9):
            vals = [parsed[r][c][0] for r in range(9) if len(parsed[r][c]) == 1]
            if len(vals) != len(set(vals)):
                return f"Column {c+1} has duplicate fixed digits."
        for b in range(9):
            br, bc = b//3*3, b%3*3
            vals = [parsed[br+r][bc+c][0] for r in range(3) for c in range(3)
                    if len(parsed[br+r][bc+c]) == 1]
            if len(vals) != len(set(vals)):
                return f"Box {b//3+1},{b%3+1} has duplicate fixed digits."
        if versions(limitations(parsed)) == 0:
            return "Contradiction found: a cell has no possible digits left."
        return None

    # ── Custom puzzle ────────────────────────────────────────────────

    def _enter_edit(self):
        self.running = False
        if self.anim_id:
            self.root.after_cancel(self.anim_id)
        self.edit_mode = True
        self.canvas.pack_forget()
        self.legend_frame.pack_forget()
        self.edit_frame.pack(fill="both")
        self.legend_frame.pack(fill="x", pady=(10, 0))
        for e in self.edit_entries.values():
            e.delete(0, "end")
        self.btn_edit._set_state("disabled")
        self.btn_use._set_state("normal")
        self.btn_clr.pack(before=self.div_after_custom, fill="x", padx=20, pady=2)
        self.btn_clr._set_state("normal")
        self.btn_solve._set_state("disabled")
        self.btn_instant._set_state("disabled")
        self.btn_timed._set_state("disabled")
        self.btn_step._set_state("disabled")
        self.btn_back._set_state("disabled")
        self._set_info("Type digits 1–9 into the cells.\n\n"
                       "Leave empty for unknowns.\n\n"
                       "Use arrow keys or Tab to move.\n\n"
                       "Press  ✓ Use this puzzle  when done.")
        self.edit_entries[(0, 0)].focus_set()

    def _cancel_edit(self):
        self.edit_mode = False
        self.edit_frame.pack_forget()
        self.legend_frame.pack_forget()
        self.canvas.pack()
        self.legend_frame.pack(fill="x", pady=(10, 0))
        self.btn_edit._set_state("normal")
        self.btn_use._set_state("disabled")
        self.btn_clr.pack_forget()
        self.btn_solve._set_state("normal")
        self.btn_instant._set_state("normal")
        self.btn_timed._set_state("normal")
        self.btn_step._set_state("normal")
        self.btn_back._set_state("disabled")
        if self.original_data is not None:
            self.init_data = [[list(self.original_data[r][c]) for c in range(9)] for r in range(9)]
            self.given_mask = [[len(self.original_data[r][c]) == 1 for c in range(9)] for r in range(9)]
            self._draw_data(self.init_data)
        self.stat_ver.config(text="–")
        self.stat_steps.config(text="0")
        self._set_info("Cancelled — restored previous puzzle.")
        self.root.focus_set()

    def _clear_edit(self):
        self._cancel_edit()

    def _use_custom(self):
        rows_str = []
        for r in range(9):
            row = ""
            for c in range(9):
                v = self.edit_entries[(r, c)].get().strip()
                row += v if v else "."
            rows_str.append(row)

        flat = "".join(rows_str)
        clues = sum(1 for ch in flat if ch != ".")
        if clues < 17:
            messagebox.showwarning("Too few clues",
                f"You entered {clues} clue(s).\nA valid Sudoku needs at least 17.")
            return

        grid = [[int(rows_str[r][c]) if rows_str[r][c] != "." else 0
                 for c in range(9)] for r in range(9)]
        errors = []
        for i in range(9):
            rv = [grid[i][c] for c in range(9) if grid[i][c]]
            cv = [grid[r][i] for r in range(9) if grid[r][i]]
            br, bc = (i//3)*3, (i%3)*3
            bv = [grid[br+r][bc+c] for r in range(3) for c in range(3)
                  if grid[br+r][bc+c]]
            if len(rv) != len(set(rv)):
                errors.append(f"Row {i+1} has duplicates")
            if len(cv) != len(set(cv)):
                errors.append(f"Column {i+1} has duplicates")
            if len(bv) != len(set(bv)):
                errors.append(f"Box {i//3+1},{i%3+1} has duplicates")
        if errors:
            messagebox.showerror("Invalid puzzle",
                "Conflicts found:\n\n"+"\n".join(errors[:5]) +
                ("\n..." if len(errors) > 5 else "") +
                "\n\nPlease fix these before solving.")
            return

        parsed = readSudoku("\n".join(rows_str))
        msg = self._check_conflicts(parsed)
        if msg:
            messagebox.showerror("Unsolvable", msg)
            return
        self.init_data = [[list(parsed[r][c]) for c in range(9)] for r in range(9)]
        self.original_data = parsed
        self.given_mask = [[len(parsed[r][c]) == 1 for c in range(9)] for r in range(9)]
        self.anim_steps = []
        self.anim_idx = 0

        self.edit_mode = False
        self.edit_frame.pack_forget()
        self.legend_frame.pack_forget()
        self.canvas.pack()
        self.legend_frame.pack(fill="x", pady=(10, 0))
        self.btn_edit._set_state("normal")
        self.btn_use._set_state("disabled")
        self.btn_clr.pack_forget()
        self.btn_solve._set_state("normal")
        self.btn_instant._set_state("normal")
        self.btn_timed._set_state("normal")
        self.btn_step._set_state("normal")
        self.btn_back._set_state("disabled")
        self._draw_data(self.init_data)
        self.stat_ver.config(text="–")
        self.stat_steps.config(text="0")
        self._set_info(f"Custom puzzle loaded! ({clues} clues)\n\n"
                       "Press  ▶ Solve automatically  or\n"
                       "⏭ Step forward  to solve it.")


def main():
    root = tk.Tk()
    root.tk_setPalette(background=BG_APP)
    SudokuGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
