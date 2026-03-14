"""
MathCode Art Monitor
════════════════════
A non-blocking floating window that shows live generative art
produced from MathCore calculation results.

Usage (from MathCoreApp):
    from MathCodeMonitor import ArtMonitor
    monitor = ArtMonitor(root_tk_window, engine)
    monitor.show()   # open / raise
    monitor.hide()   # minimise to tray
"""

import tkinter as tk
import tkinter.ttk as ttk
import os
import sys
import math
import random
import threading
from functools import partial
from typing import Optional

# Ensure MathCodeEngine (sibling file) is always importable
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

# ── Shared theme constants (duplicated so this file is self-contained) ────────
C = {
    'bg':          '#080b0f',
    'bg2':         '#0d1117',
    'bg3':         '#111820',
    'panel':       '#0a0e14',
    'border':      '#1a2535',
    'border_hi':   '#00ff9f',
    'accent':      '#00ff9f',
    'accent2':     '#00d4ff',
    'accent3':     '#ff006e',
    'accent4':     '#ffe600',
    'text':        '#c9d1d9',
    'text_dim':    '#6e7681',
    'text_bright': '#f0f6fc',
    'text_code':   '#79c0ff',
    'result':      '#00ff9f',
    'error':       '#ff4444',
    'warn':        '#ffe600',
    'step_bg':     '#0d1f0d',
    'btn':         '#0f2a1f',
    'btn_hover':   '#1a4030',
    'btn_text':    '#00ff9f',
}
FONTS = {
    'mono':    ('Consolas', 10),
    'mono_sm': ('Consolas', 9),
    'mono_lg': ('Consolas', 12, 'bold'),
    'ui':      ('Segoe UI', 10),
    'ui_sm':   ('Segoe UI', 9),
    'title':   ('Consolas', 13, 'bold'),
    'huge':    ('Consolas', 20, 'bold'),
}
RARITY_COLOR = {
    'Common':     '#6e7681',
    'Uncommon':   '#00FF9F',
    'Rare':       '#00D4FF',
    'Ultra Rare': '#7B61FF',
    'Legendary':  '#FFE600',
}

# ══════════════════════════════════════════════════════════════════════════════
# HISTORY THUMBNAIL STRIP
# ══════════════════════════════════════════════════════════════════════════════

class HistoryStrip(tk.Frame):
    """Horizontal row of small clickable art thumbnails."""
    THUMB = 52

    def __init__(self, master, on_select, **kw):
        super().__init__(master, bg=C['bg2'], height=self.THUMB+16, **kw)
        self.pack_propagate(False)
        self.on_select = on_select
        self._canvases = []
        self._pieces   = []
        self._build()

    def _build(self):
        inner = tk.Frame(self, bg=C['bg2'])
        inner.pack(fill='both', expand=True, padx=4, pady=4)
        self._scrollable = tk.Frame(inner, bg=C['bg2'])
        self._scrollable.pack(fill='x', side='left')
        lbl = tk.Label(inner, text='HISTORY →', font=FONTS['mono_sm'],
                       fg=C['text_dim'], bg=C['bg2'])
        lbl.pack(side='left', padx=4)

    def push(self, piece):
        """Add a new piece thumbnail at the left."""
        self._pieces.insert(0, piece)
        if len(self._pieces) > 16:
            self._pieces.pop()
        self._redraw()

    def _redraw(self):
        for w in self._scrollable.winfo_children():
            w.destroy()
        self._canvases = []
        for i, piece in enumerate(self._pieces[:12]):
            frame = tk.Frame(self._scrollable, bg=C['bg2'], cursor='hand2')
            frame.pack(side='left', padx=2)
            T = self.THUMB
            c = tk.Canvas(frame, width=T, height=T, bg=C['bg'],
                          highlightthickness=1,
                          highlightbackground=RARITY_COLOR.get(piece.rarity, C['border']))
            c.pack()
            # Rarity dot
            rc = RARITY_COLOR.get(piece.rarity, C['text_dim'])
            c.create_rectangle(0, 0, T, T, fill=C['bg'], outline='')
            # Mini art render
            self._mini_render(c, piece, T)
            c.create_text(T//2, T-7, text=piece.rarity[0],
                          font=FONTS['mono_sm'], fill=rc)
            c.bind('<Button-1>', lambda e, p=piece: self.on_select(p))
            frame.bind('<Button-1>', lambda e, p=piece: self.on_select(p))
            self._canvases.append(c)

    def _mini_render(self, canvas, piece, size):
        """Draw a micro preview onto a small thumbnail canvas.

        PIL fast path: resizes piece.image (whatever resolution — 512 or 3000)
        down to `size` px using LANCZOS.  Stores photo ref on canvas to avoid GC.
        Falls back to stroke-based drawing if PIL unavailable.
        """
        # PIL fast path
        if piece.image is not None:
            try:
                from PIL import ImageTk, Image as _PILImage
                resample = (_PILImage.Resampling.LANCZOS
                            if hasattr(_PILImage, 'Resampling')
                            else _PILImage.LANCZOS)
                thumb  = piece.image.resize((size, size), resample)
                photo  = ImageTk.PhotoImage(thumb)
                canvas._thumb_photo = photo   # prevent GC
                canvas.create_image(0, 0, anchor='nw', image=photo, tags='mini')
                return
            except Exception:
                pass

        # Stroke fallback (positions are already in engine-pixel space)
        from MathCodeEngine import SIZE
        scale = size / SIZE
        for rule in piece.strokes[:30]:
            cx  = rule.get('cx', SIZE//2) * scale
            cy  = rule.get('cy', SIZE//2) * scale
            s   = max(1, rule['size'] * scale)
            col = rule.get('color', '#00FF9F')
            try:
                if rule['stroke'] in ('dot', 'orbit', 'scatter'):
                    r = max(1, s/3)
                    canvas.create_oval(cx-r, cy-r, cx+r, cy+r,
                                       fill=col, outline='', tags='mini')
                elif rule['stroke'] == 'arc':
                    canvas.create_arc(cx-s, cy-s, cx+s, cy+s,
                                      start=rule.get('angle', 0), extent=120,
                                      outline=col, style='arc', width=1, tags='mini')
                else:
                    rad = math.radians(rule.get('angle', 0))
                    canvas.create_line(cx, cy,
                                       cx+s*math.cos(rad), cy+s*math.sin(rad),
                                       fill=col, width=1, tags='mini')
            except Exception:
                pass

# ══════════════════════════════════════════════════════════════════════════════
# MAIN ART MONITOR WINDOW
# ══════════════════════════════════════════════════════════════════════════════

class ArtMonitor(tk.Toplevel):
    """
    Floating, always-on-top-optional art monitor.
    Receives ArtPieces from MathCodeEngine and renders them live.
    """
    CANVAS_SIZE = 400   # display size in the monitor window — always 400px
                        # regardless of generation resolution.
                        # PIL resizes from whatever SIZE the engine produced
                        # (512 for preview, 3000 for production) down to this.

    def __init__(self, parent, engine):
        super().__init__(parent)
        self.engine         = engine
        self._current_piece = None
        self._photo         = None
        self._pulse_job     = None
        self._on_top        = tk.BooleanVar(value=False)

        # Window setup
        self.title('MathCode Art Monitor')
        self.geometry('500x860')
        self.minsize(460, 600)
        self.resizable(True, True)
        self.configure(bg=C['bg'])
        self.protocol('WM_DELETE_WINDOW', self.hide)

        # Connect engine — polling loop replaces the fragile callback
        # Do NOT set engine.on_new_piece here; we poll instead
        self._last_seen_count = 0   # tracks engine.total_generated

        self._build()
        self._start_pulse()
        self._start_poll()          # reliable 200ms polling loop
        self.withdraw()   # start hidden; caller calls show()

    # ── Public ────────────────────────────────────────────────────────────────

    def show(self):
        self.deiconify()
        self.lift()
        self._refresh_profile_menu()   # always sync profiles on open
        self._sync_from_engine()
        if self._current_piece:
            self._render_to_canvas(self._current_piece)
            self._update_meta(self._current_piece)

    def hide(self):
        self.withdraw()

    def _sync_from_engine(self):
        """Load current engine state into the monitor — called on open."""
        # Populate history strip from engine's history list
        history = list(self.engine.history)
        if history:
            # Push oldest → newest so newest ends up at front
            for piece in history:
                self.history_strip.push(piece)

        # Display the most recent piece
        if self.engine.latest:
            self.display_piece(self.engine.latest)
            self._update_stats()

    def display_piece(self, piece):
        """Render a specific piece (from history click or new generation)."""
        self._current_piece = piece
        self._render_to_canvas(piece)
        self._update_meta(piece)

    # ── Build UI ──────────────────────────────────────────────────────────────

    def _build(self):
        # ── Title bar (fixed, outside scroll) ────────────────────────────────
        title_bar = tk.Frame(self, bg=C['bg2'], height=40)
        title_bar.pack(fill='x')
        title_bar.pack_propagate(False)

        tk.Label(title_bar, text='  ◈  MATHCODE', font=FONTS['title'],
                 fg=C['accent'], bg=C['bg2']).pack(side='left', fill='y')
        tk.Label(title_bar, text='Art Monitor', font=FONTS['mono'],
                 fg=C['text_dim'], bg=C['bg2']).pack(side='left', fill='y', padx=4)

        # Controls
        tk.Button(title_bar, text='✕', font=FONTS['mono_sm'],
                  bg=C['bg2'], fg=C['text_dim'], relief='flat',
                  cursor='hand2', command=self.hide,
                  padx=8).pack(side='right', fill='y')
        self._pin_btn = tk.Button(title_bar, text='📌', font=FONTS['mono_sm'],
                                  bg=C['bg2'], fg=C['text_dim'], relief='flat',
                                  cursor='hand2', command=self._toggle_ontop,
                                  padx=6)
        self._pin_btn.pack(side='right', fill='y')

        tk.Frame(self, height=1, bg=C['border_hi']).pack(fill='x')

        # ── Scrollable body — all content below title goes here ───────────────
        _scroll_canvas = tk.Canvas(self, bg=C['bg'], highlightthickness=0)
        _scrollbar     = tk.Scrollbar(self, orient='vertical',
                                       command=_scroll_canvas.yview,
                                       bg=C['bg'], troughcolor=C['bg2'])
        _scroll_canvas.configure(yscrollcommand=_scrollbar.set)
        _scrollbar.pack(side='right', fill='y')
        _scroll_canvas.pack(side='left', fill='both', expand=True)

        # _b is the inner frame — every widget below packs into _b, not self
        _b = tk.Frame(_scroll_canvas, bg=C['bg'])
        _win_id = _scroll_canvas.create_window((0, 0), window=_b, anchor='nw')

        def _on_frame_configure(e):
            _scroll_canvas.configure(scrollregion=_scroll_canvas.bbox('all'))
        def _on_canvas_configure(e):
            _scroll_canvas.itemconfig(_win_id, width=e.width)

        _b.bind('<Configure>', _on_frame_configure)
        _scroll_canvas.bind('<Configure>', _on_canvas_configure)

        # Mouse-wheel scrolling
        def _on_mousewheel(e):
            _scroll_canvas.yview_scroll(int(-1*(e.delta/120)), 'units')
        _scroll_canvas.bind_all('<MouseWheel>', _on_mousewheel)

        # ── Canvas ────────────────────────────────────────────────────────────
        canvas_frame = tk.Frame(_b, bg=C['bg'])
        canvas_frame.pack(fill='x', padx=8, pady=(8,4))

        self.art_canvas = tk.Canvas(canvas_frame,
                                    width=self.CANVAS_SIZE,
                                    height=self.CANVAS_SIZE,
                                    bg=C['bg'], highlightthickness=2,
                                    highlightbackground=C['border'])
        self.art_canvas.pack()
        self._draw_placeholder()

        # ── Status pulse bar ──────────────────────────────────────────────────
        self._pulse_bar = tk.Canvas(_b, height=3, bg=C['bg'],
                                    highlightthickness=0)
        self._pulse_bar.pack(fill='x', padx=8)
        self._pulse_pos = 0

        # ── Metadata panel ────────────────────────────────────────────────────
        meta = tk.Frame(_b, bg=C['bg2'])
        meta.pack(fill='x', padx=8, pady=4)
        tk.Frame(_b, height=1, bg=C['border']).pack(fill='x')

        # Rarity badge
        badge_row = tk.Frame(meta, bg=C['bg2'])
        badge_row.pack(fill='x', padx=8, pady=(6,2))
        self.rarity_lbl = tk.Label(badge_row, text='——', font=FONTS['mono_lg'],
                                    fg=C['text_dim'], bg=C['bg2'])
        self.rarity_lbl.pack(side='left')
        self.price_lbl  = tk.Label(badge_row, text='ℳ 0.00', font=FONTS['mono_lg'],
                                    fg=C['accent4'], bg=C['bg2'])
        self.price_lbl.pack(side='right')

        # Info grid
        info_grid = tk.Frame(meta, bg=C['bg2'])
        info_grid.pack(fill='x', padx=8, pady=(2,6))
        self._meta_vars = {}
        for i, key in enumerate(['Domain', 'Function', 'Complexity', 'Seed', 'Time']):
            tk.Label(info_grid, text=f'{key}:', font=FONTS['mono_sm'],
                     fg=C['text_dim'], bg=C['bg2'],
                     width=10, anchor='e').grid(row=i, column=0, sticky='e', pady=1)
            v = tk.StringVar(value='—')
            self._meta_vars[key] = v
            tk.Label(info_grid, textvariable=v, font=FONTS['mono_sm'],
                     fg=C['text_code'], bg=C['bg2'],
                     anchor='w').grid(row=i, column=1, sticky='w', padx=6, pady=1)

        tk.Frame(_b, height=1, bg=C['border']).pack(fill='x')

        # ── Stats bar ─────────────────────────────────────────────────────────
        stats_frame = tk.Frame(_b, bg=C['bg'])
        stats_frame.pack(fill='x', padx=8, pady=4)
        from MathCodeEngine import PIL_AVAILABLE
        default_status = ('Waiting for first calculation…' if PIL_AVAILABLE
                          else '⚠ Pillow not installed — exports will be EPS not PNG'
                               '  |  pip install Pillow')
        self.stats_lbl = tk.Label(stats_frame,
                                   text=default_status,
                                   font=FONTS['mono_sm'],
                                   fg=C['text_dim'] if PIL_AVAILABLE else C['warn'],
                                   bg=C['bg'], anchor='w')
        self.stats_lbl.pack(side='left', fill='x', expand=True)
        q_frame = tk.Frame(stats_frame, bg=C['bg'])
        q_frame.pack(side='right')
        tk.Label(q_frame, text='queue:', font=FONTS['mono_sm'],
                 fg=C['text_dim'], bg=C['bg']).pack(side='left')
        self.queue_lbl = tk.Label(q_frame, text='0', font=FONTS['mono_sm'],
                                   fg=C['accent'], bg=C['bg'])
        self.queue_lbl.pack(side='left', padx=4)

        tk.Frame(_b, height=1, bg=C['border']).pack(fill='x')

        # ── History strip ─────────────────────────────────────────────────────
        self.history_strip = HistoryStrip(_b, on_select=self.display_piece)
        self.history_strip.pack(fill='x', padx=8, pady=4)

        tk.Frame(_b, height=1, bg=C['border']).pack(fill='x')

        # ── Action buttons ────────────────────────────────────────────────────
        btn_row = tk.Frame(_b, bg=C['bg'])
        btn_row.pack(fill='x', padx=8, pady=6)

        tk.Button(btn_row, text='↓ Export PNG + JSON',
                  font=FONTS['mono_sm'], bg=C['btn'], fg=C['btn_text'],
                  relief='flat', padx=10, pady=5, cursor='hand2',
                  command=self._export).pack(side='left')

        # Randomize style on each calculation
        self._rand_style_var = tk.BooleanVar(value=False)
        self._rand_style_chk = tk.Checkbutton(btn_row, text='🎲 Style',
                                               variable=self._rand_style_var,
                                               font=FONTS['mono_sm'],
                                               fg=C['text_dim'], bg=C['bg'],
                                               selectcolor=C['bg3'],
                                               activebackground=C['bg'],
                                               relief='flat', cursor='hand2',
                                               command=self._toggle_rand_style)
        self._rand_style_chk.pack(side='left')

        # Stack mode toggle
        self._stack_var = tk.BooleanVar(value=False)
        self._stack_chk = tk.Checkbutton(btn_row, text='⊕ Stack',
                                          variable=self._stack_var,
                                          font=FONTS['mono_sm'],
                                          fg=C['text_dim'], bg=C['bg'],
                                          selectcolor=C['bg3'],
                                          activebackground=C['bg'],
                                          relief='flat', cursor='hand2',
                                          command=self._toggle_stack)
        self._stack_chk.pack(side='left', padx=(6,0))

        tk.Button(btn_row, text='✕ Clear stack',
                  font=FONTS['mono_sm'], bg=C['bg2'], fg=C['text_dim'],
                  relief='flat', padx=8, pady=5, cursor='hand2',
                  command=self._clear_stack).pack(side='left', padx=4)

        tk.Button(btn_row, text='⟳ Regen',
                  font=FONTS['mono_sm'], bg=C['bg2'], fg=C['accent2'],
                  relief='flat', padx=10, pady=5, cursor='hand2',
                  command=self._regen).pack(side='right')

        # ── Session folder label ───────────────────────────────────────────────
        try:
            from MathCodeEngine import SESSION_DIR
            session_path = SESSION_DIR
        except Exception:
            session_path = 'mathcode_art/...'
        self._session_path = session_path
        session_frame = tk.Frame(_b, bg=C['step_bg'])
        session_frame.pack(fill='x', padx=8, pady=(0,4))
        tk.Frame(session_frame, height=1, bg=C['border']).pack(fill='x')
        inner_sf = tk.Frame(session_frame, bg=C['step_bg'])
        inner_sf.pack(fill='x', padx=6, pady=3)
        tk.Label(inner_sf, text='Session folder:',
                 font=FONTS['mono_sm'], fg=C['text_dim'],
                 bg=C['step_bg']).pack(side='left')
        path_lbl = tk.Label(inner_sf, text=os.path.abspath(session_path),
                            font=FONTS['mono_sm'], fg=C['accent4'],
                            bg=C['step_bg'], cursor='hand2')
        path_lbl.pack(side='left', padx=4)
        path_lbl.bind('<Button-1>', lambda e: self._open_folder())
        tk.Button(inner_sf, text='📂 Open', font=FONTS['mono_sm'],
                  bg=C['btn'], fg=C['accent4'], relief='flat',
                  padx=8, pady=2, cursor='hand2',
                  command=self._open_folder).pack(side='right')

        # ── Profile selector ──────────────────────────────────────────────────
        prof_frame = tk.Frame(_b, bg=C['bg2'])
        prof_frame.pack(fill='x', padx=8, pady=(4,0))
        tk.Frame(prof_frame, height=1, bg=C['border']).pack(fill='x')

        # ── Row 1: dropdown + randomize ───────────────────────────────────────
        row1 = tk.Frame(prof_frame, bg=C['bg2'])
        row1.pack(fill='x', padx=8, pady=(4,2))
        tk.Label(row1, text='Profile:', font=FONTS['mono_sm'],
                 fg=C['text_dim'], bg=C['bg2']).pack(side='left')
        self._profile_var = tk.StringVar(value='default')
        try:
            from MathCodeEngine import PROFILES, ACTIVE_PROFILE
            prof_names = list(PROFILES.keys())
            current    = ACTIVE_PROFILE.name
        except Exception as e:
            prof_names = ['default']
            current    = 'default'
        self._prof_menu = ttk.Combobox(row1, textvariable=self._profile_var,
                                        values=prof_names, state='readonly',
                                        font=FONTS['mono_sm'], width=14)
        self._profile_var.set(current)
        self._prof_menu.pack(side='left', padx=6)
        self._prof_menu.bind('<<ComboboxSelected>>', self._on_profile_change)

        tk.Button(row1, text='🎲 Random', font=FONTS['mono_sm'],
                  bg=C['btn'], fg=C['accent4'], relief='flat',
                  padx=8, pady=3, cursor='hand2',
                  command=self._randomize_profile).pack(side='left', padx=2)

        # Instant save — saves active profile to disk right now
        tk.Button(row1, text='💾', font=FONTS['mono_sm'],
                  bg=C['btn'], fg=C['btn_text'], relief='flat',
                  padx=6, pady=3, cursor='hand2',
                  command=self._quick_save_profile).pack(side='left', padx=2)

        # Toggle inline editor
        self._editor_open = False
        self._edit_toggle_btn = tk.Button(
            row1, text='▶ Edit', font=FONTS['mono_sm'],
            bg=C['btn'], fg=C['accent2'], relief='flat',
            padx=8, pady=3, cursor='hand2',
            command=self._toggle_inline_editor)
        self._edit_toggle_btn.pack(side='left', padx=2)

        # ── Row 2: save-as / load ─────────────────────────────────────────────
        row2 = tk.Frame(prof_frame, bg=C['bg2'])
        row2.pack(fill='x', padx=8, pady=(0,2))
        tk.Label(row2, text='Save as:', font=FONTS['mono_sm'],
                 fg=C['text_dim'], bg=C['bg2']).pack(side='left')
        self._save_name_var = tk.StringVar()
        tk.Entry(row2, textvariable=self._save_name_var,
                 font=FONTS['mono_sm'], bg=C['bg3'], fg=C['accent'],
                 insertbackground=C['accent'], relief='flat',
                 highlightthickness=1, highlightcolor=C['border_hi'],
                 highlightbackground=C['border'],
                 width=14).pack(side='left', padx=4, ipady=2)
        tk.Button(row2, text='💾 Save', font=FONTS['mono_sm'],
                  bg=C['btn'], fg=C['btn_text'], relief='flat',
                  padx=8, pady=3, cursor='hand2',
                  command=self._save_profile).pack(side='left', padx=2)
        tk.Button(row2, text='📂 Load', font=FONTS['mono_sm'],
                  bg=C['btn'], fg=C['accent2'], relief='flat',
                  padx=8, pady=3, cursor='hand2',
                  command=self._load_profile_file).pack(side='left', padx=2)
        tk.Button(row2, text='⚙ Advanced', font=FONTS['mono_sm'],
                  bg=C['bg2'], fg=C['text_dim'], relief='flat',
                  padx=6, pady=3, cursor='hand2',
                  command=self._open_advanced_editor).pack(side='right', padx=2)

        # ── Inline editor panel (hidden by default) ───────────────────────────
        self._inline_editor_frame = tk.Frame(_b, bg=C['bg3'])
        # Does NOT pack yet — toggled by _toggle_inline_editor

        # ── Colour palette strip ───────────────────────────────────────────────
        self._palette_canvas = tk.Canvas(_b, height=10, bg=C['bg'],
                                          highlightthickness=0)
        self._palette_canvas.pack(fill='x', padx=8, pady=(0,6))

    # ── Rendering ─────────────────────────────────────────────────────────────

    def _draw_placeholder(self):
        """Draw the 'waiting' animation on the canvas."""
        C2 = self.CANVAS_SIZE
        self.art_canvas.delete('all')
        self.art_canvas.create_rectangle(0, 0, C2, C2, fill=C['bg'], outline='')
        # Animated grid
        for gx in range(0, C2, 32):
            self.art_canvas.create_line(gx, 0, gx, C2, fill='#0d1520')
        for gy in range(0, C2, 32):
            self.art_canvas.create_line(0, gy, C2, gy, fill='#0d1520')
        # Centre text
        self.art_canvas.create_text(C2//2, C2//2 - 16,
                                     text='◈', font=('Consolas', 40),
                                     fill=C['border'])
        self.art_canvas.create_text(C2//2, C2//2 + 28,
                                     text='Run a calculation to\ngenerate art',
                                     font=FONTS['mono_sm'],
                                     fill=C['text_dim'], justify='center')

    def _render_to_canvas(self, piece):
        """Display a piece on the art canvas (PIL or tkinter fallback).

        The engine now generates at 3000×3000 by default for print quality.
        This method downscales to CANVAS_SIZE (400px) for display using
        LANCZOS resampling — preserves detail far better than the default
        NEAREST filter when reducing from 3000→400.
        """
        C2 = self.CANVAS_SIZE
        self.art_canvas.delete('all')
        self.art_canvas.create_rectangle(0, 0, C2, C2, fill=C['bg'], outline='')

        try:
            from PIL import ImageTk, Image as _PILImage
            if piece.image is not None:
                # Downscale with LANCZOS (high quality, handles 3000→400 well)
                resized     = piece.image.resize((C2, C2),
                                                  _PILImage.Resampling.LANCZOS
                                                  if hasattr(_PILImage, 'Resampling')
                                                  else _PILImage.LANCZOS)
                self._photo = ImageTk.PhotoImage(resized)
                self.art_canvas.create_image(0, 0, anchor='nw', image=self._photo)
                piece.tk_photo = self._photo
                return
        except ImportError:
            pass

        # Tkinter Canvas fallback
        from MathCodeEngine import draw_piece_on_canvas
        draw_piece_on_canvas(self.art_canvas, piece, C2, C2)

        # Rarity border glow
        rc = RARITY_COLOR.get(piece.rarity, C['border'])
        self.art_canvas.configure(highlightbackground=rc, highlightthickness=2)

    def _update_meta(self, piece):
        """Update all metadata labels for a piece."""
        rc = RARITY_COLOR.get(piece.rarity, C['text_dim'])
        self.rarity_lbl.configure(text=f'◆ {piece.rarity}', fg=rc)
        self.price_lbl.configure(text=f'ℳ {piece.price:.2f}')

        self._meta_vars['Domain'].set(piece.domain[:30] if piece.domain else '—')
        self._meta_vars['Function'].set(piece.fn_name[:28] if piece.fn_name else '—')
        self._meta_vars['Complexity'].set(str(piece.complexity))
        self._meta_vars['Seed'].set(str(piece.seed))

        # Show layer count if stacked
        layers = piece.metadata.get('stack_layers', 1)
        time_str = piece.timestamp
        if layers > 1:
            time_str = f'{piece.timestamp}  ·  {layers} layers'
        self._meta_vars['Time'].set(time_str)

        # Colour palette strip
        colors = list(set(s['color'] for s in piece.strokes))
        self._draw_palette(colors)

        # Update canvas rarity border
        self.art_canvas.configure(highlightbackground=RARITY_COLOR.get(piece.rarity, C['border']))

    def _draw_palette(self, colors):
        w  = self._palette_canvas.winfo_width() or 464
        pw = max(8, w // max(1, len(colors)))
        self._palette_canvas.delete('all')
        for i, col in enumerate(colors):
            self._palette_canvas.create_rectangle(
                i*pw, 0, (i+1)*pw, 10, fill=col, outline='')

    # ── Polling loop (replaces thread callbacks — 100% thread-safe) ──────────

    def _start_poll(self):
        """Start the 200ms polling loop that checks for new pieces."""
        self._poll_engine()

    def _poll_engine(self):
        """Called every 200ms on the main thread — check if engine has new art."""
        piece = None
        try:
            current_count = self.engine.total_generated
            if current_count > self._last_seen_count:
                self._last_seen_count = current_count
                piece = self.engine.latest
                if piece is not None:
                    self._current_piece = piece
                    self.history_strip.push(piece)
                    self._update_stats()
                    if self.winfo_viewable():
                        self._render_to_canvas(piece)
                        self._update_meta(piece)
                    if piece.rarity == 'Legendary':
                        self._flash_border()
        except Exception:
            pass

        # Reschedule
        try:
            self.after(200, self._poll_engine)
        except Exception:
            pass

    # ── Pulse bar animation ───────────────────────────────────────────────────

    def _start_pulse(self):
        self._animate_pulse()

    def _animate_pulse(self):
        try:
            W = self._pulse_bar.winfo_width() or 464
            self._pulse_bar.delete('all')
            status = self.engine.current_status()
            if status['queue_depth'] > 0 or status['generated'] == 0:
                # Scanning animation
                pos  = self._pulse_pos % W
                grad = 60
                for dx in range(grad):
                    alpha = int(255 * (1 - dx/grad))
                    col   = f'#{alpha:02x}ff{min(255,alpha+80):02x}'
                    x     = (pos - dx) % W
                    self._pulse_bar.create_line(x, 0, x, 3, fill=col)
                self._pulse_pos = (self._pulse_pos + 8) % W
            else:
                # Idle — solid accent line
                rc = RARITY_COLOR.get(
                    self.engine.latest.rarity if self.engine.latest else 'Common',
                    C['border'])
                self._pulse_bar.create_rectangle(0, 0, W, 3, fill=rc, outline='')
            # Update queue count
            self.queue_lbl.configure(text=str(status['queue_depth']))
            self._pulse_job = self.after(80, self._animate_pulse)
        except Exception:
            pass

    # ── Stats ─────────────────────────────────────────────────────────────────

    def _update_stats(self):
        s = self.engine.current_status()
        self.stats_lbl.configure(
            text=f'Generated: {s["generated"]}  |  Legendary: {s["legendary"]}  |  '
                 f'Latest: {s["latest_rarity"]}  ℳ {s["latest_price"]:.2f}')

    # ── Actions ───────────────────────────────────────────────────────────────

    def _toggle_rand_style(self):
        """Toggle randomize-style-on-generation mode."""
        on = self._rand_style_var.get()
        col = C['accent4'] if on else C['text_dim']
        self._rand_style_chk.configure(fg=col)
        if on:
            self.stats_lbl.configure(
                text='🎲 Style ON — a new random profile is applied before each calculation')
        else:
            self.stats_lbl.configure(
                text='🎲 Style OFF — profile stays fixed between calculations')

    def _toggle_stack(self):
        """Sync the checkbox state to the engine's stack_mode flag."""
        on = self._stack_var.get()
        self.engine.stack_mode = on
        col = C['accent'] if on else C['text_dim']
        self._stack_chk.configure(fg=col)
        if on:
            self.stats_lbl.configure(
                text='⊕ Stack ON — calculations will layer on the same canvas')
        else:
            self.stats_lbl.configure(
                text='⊕ Stack OFF — each calculation starts a fresh canvas')

    def _clear_stack(self):
        """Discard the accumulated canvas so the next calculation starts fresh."""
        self.engine.clear_stack()
        self.stats_lbl.configure(text='Stack cleared — next calculation starts fresh')

    def _open_folder(self):
        """Open the session export folder in the system file explorer."""
        try:
            from MathCodeEngine import SESSION_DIR
            path = os.path.abspath(SESSION_DIR)
            os.makedirs(path, exist_ok=True)   # create it if nothing exported yet
            import subprocess, sys
            if sys.platform == 'win32':
                subprocess.Popen(['explorer', path])
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', path])
            else:
                subprocess.Popen(['xdg-open', path])
        except Exception as e:
            self.stats_lbl.configure(text=f'Could not open folder: {e}')

    def _export(self):
        import tkinter.messagebox as _mb
        if not self._current_piece:
            _mb.showwarning('Export', 'No piece to export yet — run a calculation first.',
                            parent=self)
            return
        piece = self._current_piece
        # Run save and capture any exception directly
        try:
            if piece.image is not None:
                from MathCodeEngine import SESSION_DIR
                directory = os.path.abspath(SESSION_DIR)
                os.makedirs(directory, exist_ok=True)
                safe_domain = piece.domain.replace(' ','_').replace('/','–')
                filename    = f'{piece.rarity}_{piece.seed}_{safe_domain}.png'
                path        = os.path.join(directory, filename)
                piece.image.save(path)
                # JSON sidecar
                json_path = path.replace('.png', '.json')
                with open(json_path, 'w') as f:
                    f.write(piece.to_json())
                self.stats_lbl.configure(
                    text=f'✓ Saved → {os.path.basename(path)}')
                _mb.showinfo('Exported',
                             f'Saved to:\n{path}', parent=self)
            else:
                # Canvas EPS fallback
                from MathCodeEngine import SESSION_DIR
                directory = os.path.abspath(SESSION_DIR)
                os.makedirs(directory, exist_ok=True)
                safe_domain = piece.domain.replace(' ','_').replace('/','–')
                base        = f'{piece.rarity}_{piece.seed}_{safe_domain}'
                eps_path    = os.path.join(directory, base + '.eps')
                json_path   = os.path.join(directory, base + '.json')
                self.art_canvas.postscript(file=eps_path, colormode='color')
                with open(json_path, 'w') as f:
                    f.write(piece.to_json())
                self.stats_lbl.configure(
                    text=f'✓ Saved EPS → {os.path.basename(eps_path)}'
                         '  (pip install Pillow for PNG)')
                _mb.showinfo('Exported (EPS)',
                             f'Saved to:\n{eps_path}\n\n'
                             'Install Pillow for PNG:\n  pip install Pillow',
                             parent=self)
        except Exception as e:
            import traceback
            err = traceback.format_exc()
            self.stats_lbl.configure(text=f'✗ Export failed: {e}')
            _mb.showerror('Export Failed',
                          f'Error:\n{e}\n\nDetails:\n{err}', parent=self)

    def _export_piece(self, piece) -> Optional[str]:
        """
        Export a piece. Uses PIL PNG if available, falls back to canvas EPS.
        Never silently fails — always updates the status label with the outcome.
        """
        # ── Path 1: PIL image available → full PNG ────────────────────────────
        if piece.image is not None:
            try:
                path = piece.save_png()
                return path
            except Exception as e:
                self.stats_lbl.configure(text=f'PNG save error: {e}')
                return None

        # ── Path 2: No PIL — tkinter canvas PostScript fallback ───────────────
        # PIL is not installed so piece.image is None.
        # Tkinter can export its own canvas as EPS (vector, opens in any viewer).
        try:
            from MathCodeEngine import SESSION_DIR
            directory = os.path.abspath(SESSION_DIR)
            os.makedirs(directory, exist_ok=True)

            safe_domain = piece.domain.replace(' ', '_').replace('/', '-')
            base_name   = f'{piece.rarity}_{piece.seed}_{safe_domain}'
            eps_path    = os.path.join(directory, base_name + '.eps')
            json_path   = os.path.join(directory, base_name + '.json')

            self.art_canvas.postscript(
                file=eps_path,
                colormode='color',
                pagewidth=self.CANVAS_SIZE,
                pageheight=self.CANVAS_SIZE,
            )
            with open(json_path, 'w') as f:
                f.write(piece.to_json())

            self.stats_lbl.configure(
                text=f'Saved EPS → {os.path.basename(eps_path)}'
                     f'  |  pip install Pillow for PNG export')
            return eps_path

        except Exception as e:
            self.stats_lbl.configure(text=f'Export error: {e}')
            return None

    def _regen(self):
        """
        Re-queue the current piece's seed with the currently active profile.
        Passes the original inputs and result_seed so the math-driven
        visual parameters (angle bias, focal spread, freq etc) are preserved —
        only the profile (colors, thickness, opacity) changes on regen.
        """
        if not self._current_piece:
            return
        try:
            from MathCodeEngine import ACTIVE_PROFILE
            current_profile  = ACTIVE_PROFILE.name
            original_profile = self._current_piece.metadata.get('profile', 'Unknown')

            if current_profile != original_profile:
                label = f'{self._current_piece.fn_name} ⟳ [{original_profile}→{current_profile}]'
                self.stats_lbl.configure(
                    text=f'⟳ Regen with new style: {original_profile} → {current_profile}')
            else:
                label = self._current_piece.fn_name + ' ⟳'
                self.stats_lbl.configure(
                    text=f'⟳ Regen — same style ({current_profile})')

            # Retrieve stored inputs from metadata if available
            stored_inputs = self._current_piece.metadata.get('inputs', {})

            self.engine.feed(
                self._current_piece.seed,
                domain      = self._current_piece.domain,
                fn_name     = label,
                inputs      = stored_inputs,
            )
        except Exception as e:
            self.stats_lbl.configure(text=f'Regen error: {e}')

    def _toggle_ontop(self):
        self._on_top.set(not self._on_top.get())
        self.attributes('-topmost', self._on_top.get())
        col = C['accent'] if self._on_top.get() else C['text_dim']
        self._pin_btn.configure(fg=col)

    def _on_profile_change(self, event=None):
        name = self._profile_var.get()
        try:
            from MathCodeEngine import set_profile
            set_profile(name)
            self.stats_lbl.configure(text=f'Profile → {name}  (next calculation)')
        except Exception as e:
            self.stats_lbl.configure(text=f'Profile error: {e}')

    def _refresh_profile_menu(self):
        """Rebuild the dropdown with the current PROFILES registry."""
        try:
            from MathCodeEngine import PROFILES
            self._prof_menu['values'] = list(PROFILES.keys())
        except Exception:
            pass

    def _randomize_profile(self):
        """Generate a fully random GenerationProfile with all new fields."""
        try:
            from MathCodeEngine import (GenerationProfile, register_profile,
                                        set_profile, PROFILES)
            import random as _rng

            all_colors = ['#00FF9F','#00D4FF','#FF006E','#FFE600','#7B61FF',
                          '#FF7700','#FFFFFF','#ff00ff','#00ffff','#ff4400',
                          '#44ff00','#0044ff','#ffff00','#ff0088','#88ff00']
            all_strokes = ['line','arc','dot','orbit','spiral','wave','vector',
                           'lattice','grid','polygon','scatter','curve','radial','tree']

            # Colors with weight + random alpha range per color
            n_colors = _rng.randint(3, 6)
            cols = _rng.sample(all_colors, n_colors)
            palette = []
            for c in cols:
                w     = round(_rng.uniform(0.3, 2.0), 2)
                amin  = _rng.choice([0, 40, 80, 100, 120])
                amax  = _rng.choice([180, 200, 220, 240, 255])
                palette.append((c, w, amin, amax))

            # Stroke types with weights
            n_stroke_types = _rng.randint(4, 8)
            st = _rng.sample(all_strokes, n_stroke_types)
            stroke_weights = {s: round(_rng.uniform(0.3, 2.0), 2) for s in st}

            # Random angle biases — 40% chance of constraining any given stroke
            angle_ranges = {}
            for s in st:
                if _rng.random() < 0.4:
                    center = _rng.choice([0, 45, 90, 135, 180, 225, 270, 315])
                    spread = _rng.choice([20, 30, 45, 60, 90])
                    lo = (center - spread) % 360
                    hi = (center + spread) % 360
                    angle_ranges[s] = (lo, hi)

            # Freq range — can bias toward slow/smooth or fast/dense
            f_min = round(_rng.uniform(0.2, 2.0), 1)
            f_max = round(_rng.uniform(f_min + 0.5, 8.0), 1)

            name = f'random_{len([k for k in PROFILES if k.startswith("random_")])+1}'
            profile = GenerationProfile(
                name            = name,
                palette         = palette,
                stroke_weights  = stroke_weights,
                n_strokes       = _rng.choice([150, 200, 250, 300]),
                thickness_range = (_rng.randint(1,2), _rng.randint(2,5)),
                size_range      = (_rng.randint(5,15), _rng.randint(40,80)),
                freq_range      = (f_min, f_max),
                angle_ranges    = angle_ranges or None,
                bg_color        = _rng.choice(['#080b0f','#000000','#02020a',
                                               '#0a0500','#030a04','#020810']),
                randomize_each  = _rng.random() > 0.5,
            )
            register_profile(profile)
            set_profile(name)
            self._profile_var.set(name)
            self._refresh_profile_menu()
            angle_note = f', {len(angle_ranges)} angle biases' if angle_ranges else ''
            self.stats_lbl.configure(
                text=f'🎲 \"{name}\" — {n_colors} colors, '
                     f'{n_stroke_types} strokes{angle_note}, '
                     f'freq {f_min}–{f_max}')
        except Exception as e:
            self.stats_lbl.configure(text=f'Randomize error: {e}')

    def _save_profile(self):
        """Save the currently active profile to profiles/<name>.json"""
        try:
            from MathCodeEngine import ACTIVE_PROFILE
            import json as _json
            save_name = self._save_name_var.get().strip() or ACTIVE_PROFILE.name
            safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in save_name)
            os.makedirs("profiles", exist_ok=True)
            path = os.path.join("profiles", f"{safe}.json")
            pal = []
            for entry in (ACTIVE_PROFILE.palette or []):
                if len(entry) == 2:   pal.append([entry[0], entry[1], 120, 255])
                elif len(entry) == 3: pal.append([entry[0], entry[1], entry[2], 255])
                else:                 pal.append(list(entry[:4]))
            data = {
                "name":            save_name,
                "palette":         pal,
                "stroke_weights":  ACTIVE_PROFILE.stroke_weights or {},
                "n_strokes":       ACTIVE_PROFILE.n_strokes,
                "thickness_range": list(ACTIVE_PROFILE.thickness_range),
                "size_range":      list(ACTIVE_PROFILE.size_range),
                "freq_range":      list(ACTIVE_PROFILE.freq_range or [0.5, 6.0]),
                "angle_ranges":    {k: list(v) for k, v in
                                    (ACTIVE_PROFILE.angle_ranges or {}).items()},
                "bg_color":        ACTIVE_PROFILE.bg_color,
                "randomize_each":  ACTIVE_PROFILE.randomize_each,
            }
            with open(path, "w") as f:
                _json.dump(data, f, indent=2)
            self.stats_lbl.configure(text=f"\U0001f4be Saved \u2192 {path}")
            self._save_name_var.set("")
        except Exception as e:
            self.stats_lbl.configure(text=f"Save error: {e}")

    def _load_profile_file(self):
        """Open a file dialog, load a profile JSON, register and apply it."""
        try:
            from tkinter import filedialog
            from MathCodeEngine import GenerationProfile, register_profile, set_profile
            import json as _json
            path = filedialog.askopenfilename(
                title="Load Profile",
                initialdir="profiles" if os.path.isdir("profiles") else ".",
                filetypes=[("Profile JSON", "*.json"), ("All files", "*.*")],
            )
            if not path:
                return
            with open(path) as f:
                d = _json.load(f)
            angle_raw = d.get("angle_ranges") or {}
            profile = GenerationProfile(
                name            = d.get("name", os.path.basename(path)),
                palette         = [tuple(x) for x in d.get("palette", [])] or None,
                stroke_weights  = d.get("stroke_weights") or None,
                n_strokes       = d.get("n_strokes", 200),
                thickness_range = tuple(d.get("thickness_range", [1, 4])),
                size_range      = tuple(d.get("size_range", [10, 60])),
                freq_range      = tuple(d.get("freq_range", [0.5, 6.0])),
                angle_ranges    = {k: tuple(v) for k, v in angle_raw.items()} or None,
                bg_color        = d.get("bg_color", "#080b0f"),
                randomize_each  = d.get("randomize_each", False),
            )
            register_profile(profile)
            set_profile(profile.name)
            self._profile_var.set(profile.name)
            self._refresh_profile_menu()
            self.stats_lbl.configure(
                text=f"\U0001f4c2 Loaded \"{profile.name}\" from {os.path.basename(path)}")
        except Exception as e:
            self.stats_lbl.configure(text=f"Load error: {e}")

    def _quick_save_profile(self):
        """Save the active profile to disk immediately using its own name."""
        try:
            from MathCodeEngine import ACTIVE_PROFILE
            self._save_name_var.set(ACTIVE_PROFILE.name)
            self._save_profile()
        except Exception as e:
            self.stats_lbl.configure(text=f'Quick save error: {e}')

    def _toggle_inline_editor(self):
        """Show or hide the inline color/stroke editor below the profile row."""
        self._editor_open = not self._editor_open
        if self._editor_open:
            self._build_inline_editor()
            self._inline_editor_frame.pack(fill='x', padx=8, pady=(0,4))
            self._edit_toggle_btn.configure(text='▼ Edit')
        else:
            self._inline_editor_frame.pack_forget()
            for w in self._inline_editor_frame.winfo_children():
                w.destroy()
            self._edit_toggle_btn.configure(text='▶ Edit')

    def _build_inline_editor(self):
        """Build the compact inline editor inside _inline_editor_frame."""
        from MathCodeEngine import ACTIVE_PROFILE, GenerationProfile, register_profile, set_profile
        f = self._inline_editor_frame
        for w in f.winfo_children():
            w.destroy()

        tk.Frame(f, height=1, bg=C['border_hi']).pack(fill='x')

        # ── Colors ────────────────────────────────────────────────────────────
        hdr = tk.Frame(f, bg=C['bg3'])
        hdr.pack(fill='x', padx=6, pady=(4,1))
        tk.Label(hdr, text='COLOURS', font=FONTS['mono_sm'],
                 fg=C['accent'], bg=C['bg3']).pack(side='left')
        tk.Button(hdr, text='+ Add', font=FONTS['mono_sm'],
                  bg=C['btn'], fg=C['btn_text'], relief='flat',
                  padx=6, pady=1, cursor='hand2',
                  command=lambda: self._inline_add_color('#00FF9F', 1.0, 120, 255)
                  ).pack(side='right')

        self._inline_color_frame = tk.Frame(f, bg=C['bg3'])
        self._inline_color_frame.pack(fill='x', padx=6)
        self._inline_color_rows = []

        pal = ACTIVE_PROFILE.effective_palette('default')
        for entry in pal:
            self._inline_add_color(*entry)

        # ── Strokes ───────────────────────────────────────────────────────────
        tk.Label(f, text='STROKE WEIGHTS', font=FONTS['mono_sm'],
                 fg=C['accent'], bg=C['bg3']).pack(anchor='w', padx=8, pady=(6,1))
        stroke_grid = tk.Frame(f, bg=C['bg3'])
        stroke_grid.pack(fill='x', padx=6, pady=(0,4))

        self._inline_stroke_vars = {}
        current_weights = dict(ACTIVE_PROFILE.stroke_weights or {})
        all_strokes_list = ['line','arc','dot','orbit','spiral','wave','vector',
                            'lattice','grid','polygon','scatter','curve','radial','tree']
        cols = 2
        for i, stroke in enumerate(all_strokes_list):
            r, c = divmod(i, cols)
            cell = tk.Frame(stroke_grid, bg=C['bg3'])
            cell.grid(row=r, column=c, sticky='ew', padx=4, pady=1)
            stroke_grid.columnconfigure(c, weight=1)
            w = current_weights.get(stroke, 0.0)
            en_var  = tk.BooleanVar(value=w > 0)
            wt_var  = tk.DoubleVar(value=max(0.1, w) if w > 0 else 1.0)
            tk.Checkbutton(cell, text=stroke, variable=en_var,
                           font=FONTS['mono_sm'], fg=C['accent'], bg=C['bg3'],
                           selectcolor=C['bg'], activebackground=C['bg3'],
                           relief='flat', cursor='hand2',
                           width=8, anchor='w').pack(side='left')
            tk.Scale(cell, variable=wt_var, from_=0.1, to=3.0, resolution=0.05,
                     orient='horizontal', length=130,
                     bg=C['bg3'], fg=C['text'], troughcolor=C['bg'],
                     highlightthickness=0, font=('Consolas',7),
                     showvalue=True, activebackground=C['accent']
                     ).pack(side='left', fill='x', expand=True)
            self._inline_stroke_vars[stroke] = {'en': en_var, 'wt': wt_var}

        # ── Apply button ──────────────────────────────────────────────────────
        btn_row = tk.Frame(f, bg=C['bg3'])
        btn_row.pack(fill='x', padx=6, pady=(4,6))
        tk.Button(btn_row, text='✓ Apply', font=FONTS['mono'],
                  bg=C['accent'], fg=C['bg'], activebackground='#00cc80',
                  relief='flat', padx=14, pady=5, cursor='hand2',
                  command=self._inline_apply).pack(side='left')
        tk.Button(btn_row, text='💾 Apply + Save', font=FONTS['mono'],
                  bg=C['btn'], fg=C['btn_text'], relief='flat',
                  padx=14, pady=5, cursor='hand2',
                  command=self._inline_apply_and_save).pack(side='left', padx=6)
        tk.Button(btn_row, text='⚙ Advanced…', font=FONTS['mono_sm'],
                  bg=C['bg2'], fg=C['text_dim'], relief='flat',
                  padx=8, pady=5, cursor='hand2',
                  command=self._open_advanced_editor).pack(side='right')

    def _inline_add_color(self, color, weight, alpha_min=120, alpha_max=255):
        """Add one color row to the inline editor."""
        f = self._inline_color_frame
        row = tk.Frame(f, bg=C['bg3'])
        row.pack(fill='x', pady=1)

        hex_var    = tk.StringVar(value=color)
        weight_var = tk.DoubleVar(value=round(weight, 2))
        amin_var   = tk.IntVar(value=alpha_min)
        amax_var   = tk.IntVar(value=alpha_max)

        # Line 1: swatch + hex + picker + weight
        line1 = tk.Frame(row, bg=C['bg3'])
        line1.pack(fill='x')

        swatch = tk.Canvas(line1, width=20, height=20, bg=color,
                           highlightthickness=1, highlightbackground=C['border'],
                           cursor='hand2')
        swatch.pack(side='left', padx=(0,3))

        hex_e = tk.Entry(line1, textvariable=hex_var, font=FONTS['mono_sm'],
                         bg=C['bg'], fg=C['accent'], insertbackground=C['accent'],
                         relief='flat', width=9)
        hex_e.pack(side='left', ipady=2)

        def open_picker():
            ColorWheelPicker(self, initial=hex_var.get(),
                             on_pick=lambda h: hex_var.set(h))
        tk.Button(line1, text='🎨', font=FONTS['mono_sm'], bg=C['bg'],
                  fg=C['accent2'], relief='flat', padx=3, cursor='hand2',
                  command=open_picker).pack(side='left', padx=2)

        tk.Label(line1, text='w:', font=FONTS['mono_sm'],
                 fg=C['text_dim'], bg=C['bg3']).pack(side='left')
        tk.Scale(line1, variable=weight_var, from_=0.0, to=3.0, resolution=0.05,
                 orient='horizontal', length=100, bg=C['bg3'], fg=C['text'],
                 troughcolor=C['bg'], highlightthickness=0, font=('Consolas',7),
                 showvalue=True, activebackground=C['accent']).pack(side='left', padx=2)

        def remove():
            row.destroy()
            self._inline_color_rows.remove(entry)
        tk.Button(line1, text='✕', font=FONTS['mono_sm'], bg=C['bg3'],
                  fg=C['text_dim'], relief='flat', padx=3, cursor='hand2',
                  command=remove).pack(side='left', padx=2)

        # Line 2: alpha sliders
        line2 = tk.Frame(row, bg=C['bg3'])
        line2.pack(fill='x', padx=24)
        tk.Label(line2, text='α:', font=FONTS['mono_sm'],
                 fg=C['accent3'], bg=C['bg3']).pack(side='left')
        tk.Scale(line2, variable=amin_var, from_=0, to=255, resolution=5,
                 orient='horizontal', length=120, label='min opacity',
                 bg=C['bg3'], fg=C['text'], troughcolor=C['bg'],
                 highlightthickness=0, font=('Consolas',7),
                 showvalue=True, activebackground=C['accent3']).pack(side='left', padx=2)
        tk.Scale(line2, variable=amax_var, from_=0, to=255, resolution=5,
                 orient='horizontal', length=120, label='max opacity',
                 bg=C['bg3'], fg=C['text'], troughcolor=C['bg'],
                 highlightthickness=0, font=('Consolas',7),
                 showvalue=True, activebackground=C['accent3']).pack(side='left', padx=2)

        def on_hex(*_):
            try:
                h = hex_var.get().strip()
                if not h.startswith('#'): h = '#' + h
                if len(h) == 7: swatch.configure(bg=h)
            except Exception: pass
        hex_var.trace_add('write', on_hex)
        swatch.bind('<Button-1>', lambda e: open_picker())

        entry = {'hex': hex_var, 'weight': weight_var,
                 'amin': amin_var, 'amax': amax_var}
        self._inline_color_rows.append(entry)

    def _inline_apply(self):
        """Read inline editor values and apply as a new profile."""
        try:
            from MathCodeEngine import (ACTIVE_PROFILE, GenerationProfile,
                                        register_profile, set_profile)
            palette = []
            for e in self._inline_color_rows:
                h = e['hex'].get().strip()
                if not h.startswith('#'): h = '#' + h
                w = round(max(0.01, e['weight'].get()), 3)
                amin = e['amin'].get(); amax = max(amin+5, e['amax'].get())
                palette.append((h, w, amin, amax))

            stroke_weights = {}
            for stroke, sv in self._inline_stroke_vars.items():
                if sv['en'].get():
                    stroke_weights[stroke] = round(max(0.05, sv['wt'].get()), 3)

            p = GenerationProfile(
                name            = ACTIVE_PROFILE.name,
                palette         = palette or None,
                stroke_weights  = stroke_weights or None,
                n_strokes       = ACTIVE_PROFILE.n_strokes,
                thickness_range = ACTIVE_PROFILE.thickness_range,
                size_range      = ACTIVE_PROFILE.size_range,
                freq_range      = ACTIVE_PROFILE.freq_range,
                angle_ranges    = ACTIVE_PROFILE.angle_ranges,
                bg_color        = ACTIVE_PROFILE.bg_color,
                randomize_each  = ACTIVE_PROFILE.randomize_each,
            )
            register_profile(p)
            set_profile(p.name)
            self._profile_var.set(p.name)
            self._refresh_profile_menu()
            self.stats_lbl.configure(text=f'✓ Profile "{p.name}" updated')
        except Exception as e:
            self.stats_lbl.configure(text=f'Apply error: {e}')

    def _inline_apply_and_save(self):
        """Apply and immediately save to disk."""
        self._inline_apply()
        self._quick_save_profile()

    def _open_advanced_editor(self):
        """Open the full ProfileEditor popup for advanced settings."""
        from MathCodeEngine import ACTIVE_PROFILE
        ProfileEditor(self, ACTIVE_PROFILE, on_apply=self._apply_edited_profile)

    def _edit_profile(self):
        """Legacy — redirects to advanced editor."""
        self._open_advanced_editor()

    def _apply_edited_profile(self, profile):
        from MathCodeEngine import register_profile, set_profile
        register_profile(profile)
        set_profile(profile.name)
        self._profile_var.set(profile.name)
        self._refresh_profile_menu()
        self.stats_lbl.configure(text=f'✏ Profile "{profile.name}" applied')

    def _flash_border(self):
        """Briefly flash the border gold to celebrate a Legendary piece."""
        colors = [C['accent4'], C['border_hi'], C['accent4'], C['border_hi'], C['border']]
        def _step(i=0):
            if i >= len(colors): return
            try:
                self.art_canvas.configure(highlightbackground=colors[i])
                self.after(120, lambda: _step(i+1))
            except Exception:
                pass
        _step()

    def destroy(self):
        if self._pulse_job:
            try: self.after_cancel(self._pulse_job)
            except Exception: pass
        super().destroy()


# ══════════════════════════════════════════════════════════════════════════════
# STATUS BADGE  (inline widget for MathCoreUI top bar)
# ══════════════════════════════════════════════════════════════════════════════

class ArtStatusBadge(tk.Frame):
    """
    Compact indicator that lives in the MathCoreUI top bar.
    Shows: latest rarity dot + piece count + 'Art ◈' button.
    Click opens the full ArtMonitor.
    """
    def __init__(self, parent, monitor: ArtMonitor, engine, **kw):
        super().__init__(parent, bg=C['bg2'], **kw)
        self.monitor = monitor
        self.engine  = engine
        self._build()

    def _build(self):
        self.dot = tk.Canvas(self, width=8, height=8, bg=C['bg2'],
                             highlightthickness=0)
        self.dot.pack(side='left', pady=14, padx=(6,2))
        self.dot.create_oval(0,0,8,8, fill=C['border'], outline='', tags='dot')

        self.btn = tk.Button(self, text='Art ◈', font=('Consolas',9,'bold'),
                             bg=C['bg2'], fg=C['text_dim'],
                             activebackground=C['bg2'], relief='flat',
                             cursor='hand2', padx=6,
                             command=self._open_monitor)
        self.btn.pack(side='left', fill='y')

        self.info_lbl = tk.Label(self, text='—', font=('Consolas',9),
                                  fg=C['text_dim'], bg=C['bg2'], padx=2)
        self.info_lbl.pack(side='left', fill='y')

        # Poll engine every 2 seconds to update the badge
        self._poll()

    def _poll(self):
        try:
            s  = self.engine.current_status()
            rc = RARITY_COLOR.get(s['latest_rarity'], C['border'])
            self.dot.itemconfig('dot', fill=rc)
            if s['generated'] > 0:
                self.btn.configure(fg=C['accent'])
                self.info_lbl.configure(
                    text=f'{s["latest_rarity"]}  ℳ{s["latest_price"]:.1f}',
                    fg=rc)
            else:
                self.info_lbl.configure(text='idle', fg=C['text_dim'])
            self.after(2000, self._poll)
        except Exception:
            pass

    def _open_monitor(self):
        self.monitor.show()


# ══════════════════════════════════════════════════════════════════════════════
# PROFILE EDITOR
# ══════════════════════════════════════════════════════════════════════════════

ALL_COLORS = [
    '#00FF9F','#00D4FF','#FF006E','#FFE600','#7B61FF',
    '#FF7700','#FFFFFF','#ff00ff','#00ffff','#ff4400',
    '#44ff00','#0044ff','#ff0088','#88ff00','#aaaaaa',
    '#ff2222','#22ff22','#2222ff','#ffaa00','#00aaff',
]
ALL_STROKES = [
    'line','arc','dot','orbit','spiral','wave','vector',
    'lattice','grid','polygon','scatter','curve','radial','tree',
]

class ProfileEditor(tk.Toplevel):
    """
    Full visual editor for a GenerationProfile.
    Shows every tunable variable with live swatches and sliders.
    """
    def __init__(self, parent, profile, on_apply=None):
        super().__init__(parent)
        self.on_apply  = on_apply
        self.title('✏  Profile Editor')
        self.geometry('560x780')
        self.minsize(480, 600)
        self.configure(bg=C['bg'])
        self.resizable(True, True)
        self.grab_set()

        # Work on a copy so Cancel truly cancels
        import copy
        self._prof = copy.deepcopy(profile)
        # Ensure palette/strokes are mutable lists (not None)
        from MathCodeEngine import DOMAIN_PALETTES, STROKE_STYLES
        if not self._prof.palette:
            self._prof.palette = list(DOMAIN_PALETTES.get('default', []))
        if not self._prof.stroke_weights:
            self._prof.stroke_weights = dict(STROKE_STYLES.get('default', []))
        else:
            self._prof.stroke_weights = dict(self._prof.stroke_weights)

        self._build()

    # ── Build ─────────────────────────────────────────────────────────────────

    def _build(self):
        # ── Scrollable body ───────────────────────────────────────────────────
        sc = tk.Canvas(self, bg=C['bg'], highlightthickness=0)
        sb = tk.Scrollbar(self, orient='vertical', command=sc.yview,
                          bg=C['bg'], troughcolor=C['bg2'])
        sc.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')
        sc.pack(side='left', fill='both', expand=True)
        body = tk.Frame(sc, bg=C['bg'])
        win  = sc.create_window((0,0), window=body, anchor='nw')
        body.bind('<Configure>', lambda e: sc.configure(scrollregion=sc.bbox('all')))
        sc.bind('<Configure>', lambda e: sc.itemconfig(win, width=e.width))
        sc.bind_all('<MouseWheel>', lambda e: sc.yview_scroll(int(-1*(e.delta/120)),'units'))

        P = 12  # padding shorthand

        # ── Header ────────────────────────────────────────────────────────────
        tk.Label(body, text='✏  Edit Profile', font=FONTS['mono_lg'],
                 fg=C['accent'], bg=C['bg']).pack(anchor='w', padx=P, pady=(10,2))
        tk.Frame(body, height=1, bg=C['border_hi']).pack(fill='x', padx=P)

        # ── Name ──────────────────────────────────────────────────────────────
        self._mk_section(body, 'PROFILE NAME')
        name_row = tk.Frame(body, bg=C['bg'])
        name_row.pack(fill='x', padx=P, pady=4)
        self._name_var = tk.StringVar(value=self._prof.name)
        tk.Entry(name_row, textvariable=self._name_var,
                 font=FONTS['mono'], bg=C['bg3'], fg=C['accent'],
                 insertbackground=C['accent'], relief='flat',
                 highlightthickness=1, highlightcolor=C['border_hi'],
                 highlightbackground=C['border'], width=28).pack(side='left', ipady=5)

        # ── Palette ───────────────────────────────────────────────────────────
        self._mk_section(body, 'COLOUR PALETTE  (color · weight)')
        self._palette_frame = tk.Frame(body, bg=C['bg'])
        self._palette_frame.pack(fill='x', padx=P, pady=4)
        self._palette_rows = []
        for entry in self._prof.palette:
            if len(entry) == 4:
                self._add_palette_row(entry[0], entry[1], entry[2], entry[3])
            elif len(entry) == 3:
                self._add_palette_row(entry[0], entry[1], entry[2], 255)
            else:
                self._add_palette_row(entry[0], entry[1])
        tk.Button(body, text='+ Add colour', font=FONTS['mono_sm'],
                  bg=C['btn'], fg=C['btn_text'], relief='flat',
                  padx=8, pady=3, cursor='hand2',
                  command=lambda: self._add_palette_row('#00FF9F', 1.0, 120, 255)
                  ).pack(anchor='w', padx=P, pady=2)

        # ── Strokes ───────────────────────────────────────────────────────────
        self._mk_section(body, 'STROKE TYPES  (check to enable · drag weight)')
        self._stroke_frame = tk.Frame(body, bg=C['bg'])
        self._stroke_frame.pack(fill='x', padx=P, pady=4)
        self._stroke_rows = {}
        for stroke in ALL_STROKES:
            weight = self._prof.stroke_weights.get(stroke, 0.0)
            self._add_stroke_row(stroke, weight)

        # ── Numeric sliders ───────────────────────────────────────────────────
        self._mk_section(body, 'GENERATION SETTINGS')
        sliders_frame = tk.Frame(body, bg=C['bg'])
        sliders_frame.pack(fill='x', padx=P, pady=4)

        freq_range  = self._prof.freq_range if self._prof.freq_range else (0.5, 6.0)
        self._n_strokes_var   = tk.IntVar(value=self._prof.n_strokes)
        self._t_min_var       = tk.IntVar(value=self._prof.thickness_range[0])
        self._t_max_var       = tk.IntVar(value=self._prof.thickness_range[1])
        self._s_min_var       = tk.IntVar(value=self._prof.size_range[0])
        self._s_max_var       = tk.IntVar(value=self._prof.size_range[1])
        self._f_min_var       = tk.DoubleVar(value=freq_range[0])
        self._f_max_var       = tk.DoubleVar(value=freq_range[1])
        self._randomize_var   = tk.BooleanVar(value=self._prof.randomize_each)

        self._mk_slider(sliders_frame, 'Strokes per piece', self._n_strokes_var,
                        50, 500, resolution=10)
        self._mk_slider(sliders_frame, 'Thickness min',    self._t_min_var, 1, 8)
        self._mk_slider(sliders_frame, 'Thickness max',    self._t_max_var, 1, 8)
        self._mk_slider(sliders_frame, 'Size min',         self._s_min_var, 2, 40)
        self._mk_slider(sliders_frame, 'Size max',         self._s_max_var, 20, 120)
        self._mk_slider(sliders_frame, 'Freq min',         self._f_min_var,
                        0.1, 10.0, resolution=0.1)
        self._mk_slider(sliders_frame, 'Freq max',         self._f_max_var,
                        0.1, 10.0, resolution=0.1)

        rnd_row = tk.Frame(sliders_frame, bg=C['bg'])
        rnd_row.pack(fill='x', pady=3)
        tk.Checkbutton(rnd_row, text='Jitter weights each piece (randomize_each)',
                       variable=self._randomize_var,
                       font=FONTS['mono_sm'], fg=C['text_dim'], bg=C['bg'],
                       selectcolor=C['bg3'], activebackground=C['bg'],
                       relief='flat', cursor='hand2').pack(side='left')

        # ── Angle ranges per stroke type ──────────────────────────────────────
        self._mk_section(body, 'ANGLE RANGES  (min° – max° per stroke type)')
        angle_hint = tk.Label(body,
            text='  Constrain direction each stroke type draws in.  '
                 'Leave both at 0/360 for full rotation.  '
                 'e.g. line 45°–135° = diagonal only.',
            font=FONTS['mono_sm'], fg=C['text_dim'], bg=C['bg'],
            wraplength=480, justify='left')
        angle_hint.pack(anchor='w', padx=P, pady=(0,4))

        angle_frame = tk.Frame(body, bg=C['bg'])
        angle_frame.pack(fill='x', padx=P, pady=4)
        existing_ranges = self._prof.angle_ranges or {}
        self._angle_rows = {}   # stroke → {'min': IntVar, 'max': IntVar}

        for stroke in ALL_STROKES:
            lo, hi = existing_ranges.get(stroke, (0, 360))
            arow = tk.Frame(angle_frame, bg=C['bg'])
            arow.pack(fill='x', pady=1)
            tk.Label(arow, text=f'{stroke}:', font=FONTS['mono_sm'],
                     fg=C['accent'], bg=C['bg'], width=10, anchor='e').pack(side='left')
            lo_var = tk.IntVar(value=lo)
            hi_var = tk.IntVar(value=hi)
            tk.Scale(arow, variable=lo_var, from_=0, to=360, resolution=5,
                     orient='horizontal', length=160, label='min°',
                     bg=C['bg'], fg=C['text'], troughcolor=C['bg3'],
                     highlightthickness=0, font=('Consolas',7),
                     showvalue=True, activebackground=C['accent4']
                     ).pack(side='left', padx=2)
            tk.Scale(arow, variable=hi_var, from_=0, to=360, resolution=5,
                     orient='horizontal', length=160, label='max°',
                     bg=C['bg'], fg=C['text'], troughcolor=C['bg3'],
                     highlightthickness=0, font=('Consolas',7),
                     showvalue=True, activebackground=C['accent4']
                     ).pack(side='left', padx=2)
            tk.Label(arow,
                     text='(wrap)', font=FONTS['mono_sm'],
                     fg=C['text_dim'], bg=C['bg']).pack(side='left', padx=2)
            self._angle_rows[stroke] = {'min': lo_var, 'max': hi_var}

        # ── Background colour ─────────────────────────────────────────────────
        self._mk_section(body, 'BACKGROUND COLOUR')
        bg_row = tk.Frame(body, bg=C['bg'])
        bg_row.pack(fill='x', padx=P, pady=6)
        self._bg_var = tk.StringVar(value=self._prof.bg_color)
        self._bg_swatch = tk.Canvas(bg_row, width=28, height=28,
                                     bg=self._prof.bg_color, highlightthickness=1,
                                     highlightbackground=C['border'])
        self._bg_swatch.pack(side='left', padx=(0,8))
        bg_entry = tk.Entry(bg_row, textvariable=self._bg_var,
                            font=FONTS['mono'], bg=C['bg3'], fg=C['accent'],
                            insertbackground=C['accent'], relief='flat',
                            highlightthickness=1, highlightcolor=C['border_hi'],
                            highlightbackground=C['border'], width=12)
        bg_entry.pack(side='left', ipady=5)
        bg_entry.bind('<FocusOut>', self._update_bg_swatch)
        bg_entry.bind('<Return>',   self._update_bg_swatch)
        # Quick presets
        for hex_c in ['#080b0f','#000000','#02020a','#0a0500','#030a04','#020810']:
            swatch = tk.Canvas(bg_row, width=20, height=20, bg=hex_c,
                               highlightthickness=1, highlightbackground=C['border'],
                               cursor='hand2')
            swatch.pack(side='left', padx=2)
            swatch.bind('<Button-1>', lambda e, h=hex_c: self._pick_bg(h))

        # ── Preview strip ─────────────────────────────────────────────────────
        self._mk_section(body, 'COLOUR PREVIEW')
        self._preview_canvas = tk.Canvas(body, height=30, bg=C['bg2'],
                                          highlightthickness=0)
        self._preview_canvas.pack(fill='x', padx=P, pady=(2,8))
        self._refresh_preview()

        # ── Buttons ───────────────────────────────────────────────────────────
        tk.Frame(body, height=1, bg=C['border']).pack(fill='x', padx=P, pady=4)
        btn_row = tk.Frame(body, bg=C['bg'])
        btn_row.pack(fill='x', padx=P, pady=(0,12))
        tk.Button(btn_row, text='✓  Apply', font=FONTS['mono'],
                  bg=C['accent'], fg=C['bg'], activebackground='#00cc80',
                  relief='flat', padx=16, pady=6, cursor='hand2',
                  command=self._apply).pack(side='left')
        tk.Button(btn_row, text='✕  Cancel', font=FONTS['mono'],
                  bg=C['bg2'], fg=C['text_dim'], relief='flat',
                  padx=12, pady=6, cursor='hand2',
                  command=self.destroy).pack(side='left', padx=8)
        tk.Button(btn_row, text='↺  Reset to current', font=FONTS['mono_sm'],
                  bg=C['bg2'], fg=C['text_dim'], relief='flat',
                  padx=8, pady=6, cursor='hand2',
                  command=self._reset).pack(side='right')

    # ── Widget helpers ────────────────────────────────────────────────────────

    def _mk_section(self, parent, title):
        f = tk.Frame(parent, bg=C['bg'])
        f.pack(fill='x', padx=12, pady=(10,2))
        tk.Label(f, text=title, font=FONTS['mono_sm'],
                 fg=C['text_dim'], bg=C['bg']).pack(side='left')
        tk.Frame(f, height=1, bg=C['border']).pack(side='left', fill='x',
                                                    expand=True, padx=8, pady=5)

    def _mk_slider(self, parent, label, var, from_, to, resolution=1):
        row = tk.Frame(parent, bg=C['bg'])
        row.pack(fill='x', pady=3)
        tk.Label(row, text=f'{label}:', font=FONTS['mono_sm'],
                 fg=C['text_dim'], bg=C['bg'], width=20, anchor='e').pack(side='left')
        tk.Scale(row, variable=var, from_=from_, to=to,
                 orient='horizontal', resolution=resolution,
                 bg=C['bg'], fg=C['text'], troughcolor=C['bg3'],
                 highlightthickness=0, font=FONTS['mono_sm'],
                 length=220, showvalue=True,
                 activebackground=C['accent']).pack(side='left', padx=6)

    def _add_palette_row(self, color, weight, alpha_min=120, alpha_max=255):
        row = tk.Frame(self._palette_frame, bg=C['bg'])
        row.pack(fill='x', pady=2)
        hex_var = tk.StringVar(value=color)
        swatch = tk.Canvas(row, width=24, height=24, bg=color,
                           highlightthickness=1, highlightbackground=C['border'],
                           cursor='hand2')
        swatch.pack(side='left', padx=(0,2))
        hex_entry = tk.Entry(row, textvariable=hex_var,
                             font=FONTS['mono_sm'], bg=C['bg3'], fg=C['accent'],
                             insertbackground=C['accent'], relief='flat',
                             highlightthickness=1, highlightbackground=C['border'],
                             width=9)
        hex_entry.pack(side='left', padx=2, ipady=3)
        def open_picker():
            ColorWheelPicker(self, initial=hex_var.get(),
                             on_pick=lambda h: hex_var.set(h))
        tk.Button(row, text='\U0001f3a8', font=FONTS['mono_sm'],
                  bg=C['bg3'], fg=C['accent2'], relief='flat',
                  padx=4, cursor='hand2', command=open_picker).pack(side='left', padx=2)
        weight_var = tk.DoubleVar(value=round(weight, 2))
        tk.Label(row, text='w:', font=FONTS['mono_sm'],
                 fg=C['text_dim'], bg=C['bg']).pack(side='left')
        tk.Scale(row, variable=weight_var, from_=0.0, to=3.0, resolution=0.05,
                 orient='horizontal', length=75, bg=C['bg'], fg=C['text'],
                 troughcolor=C['bg3'], highlightthickness=0, font=FONTS['mono_sm'],
                 showvalue=True, activebackground=C['accent']).pack(side='left', padx=2)
        # Alpha min/max — per-color opacity control
        alpha_min_var = tk.IntVar(value=alpha_min)
        alpha_max_var = tk.IntVar(value=alpha_max)
        tk.Label(row, text='\u03b1:', font=FONTS['mono_sm'],
                 fg=C['accent3'], bg=C['bg']).pack(side='left', padx=(4,0))
        tk.Scale(row, variable=alpha_min_var, from_=0, to=255, resolution=5,
                 orient='horizontal', length=65, label='lo',
                 bg=C['bg'], fg=C['text'], troughcolor=C['bg3'],
                 highlightthickness=0, font=('Consolas',7),
                 showvalue=True, activebackground=C['accent3']).pack(side='left', padx=1)
        tk.Scale(row, variable=alpha_max_var, from_=0, to=255, resolution=5,
                 orient='horizontal', length=65, label='hi',
                 bg=C['bg'], fg=C['text'], troughcolor=C['bg3'],
                 highlightthickness=0, font=('Consolas',7),
                 showvalue=True, activebackground=C['accent3']).pack(side='left', padx=1)
        def remove_row():
            row.destroy()
            self._palette_rows.remove(entry)
            self._refresh_preview()
        tk.Button(row, text='\u2715', font=FONTS['mono_sm'],
                  bg=C['bg'], fg=C['text_dim'], relief='flat',
                  padx=4, cursor='hand2', command=remove_row).pack(side='left', padx=2)
        def on_hex_change(*_):
            try:
                h = hex_var.get().strip()
                if not h.startswith('#'): h = '#' + h
                if len(h) == 7:
                    swatch.configure(bg=h)
                    self._refresh_preview()
            except Exception:
                pass
        hex_var.trace_add('write', on_hex_change)
        weight_var.trace_add('write', lambda *_: self._refresh_preview())
        swatch.bind('<Button-1>', lambda e: open_picker())
        entry = {'hex': hex_var, 'weight': weight_var,
                 'alpha_min': alpha_min_var, 'alpha_max': alpha_max_var, 'row': row}
        self._palette_rows.append(entry)
        self._refresh_preview()

    def _add_stroke_row(self, stroke, weight):
        row = tk.Frame(self._stroke_frame, bg=C['bg'])
        row.pack(fill='x', pady=1)

        enabled_var = tk.BooleanVar(value=weight > 0)
        weight_var  = tk.DoubleVar(value=max(0.1, weight) if weight > 0 else 1.0)

        chk = tk.Checkbutton(row, text=stroke, variable=enabled_var,
                              font=FONTS['mono_sm'], fg=C['accent'], bg=C['bg'],
                              selectcolor=C['bg3'], activebackground=C['bg'],
                              relief='flat', cursor='hand2', width=10, anchor='w')
        chk.pack(side='left')

        tk.Label(row, text='w:', font=FONTS['mono_sm'],
                 fg=C['text_dim'], bg=C['bg']).pack(side='left')
        tk.Scale(row, variable=weight_var,
                 from_=0.1, to=3.0, resolution=0.05,
                 orient='horizontal', length=200,
                 bg=C['bg'], fg=C['text'], troughcolor=C['bg3'],
                 highlightthickness=0, font=FONTS['mono_sm'],
                 showvalue=True, activebackground=C['accent']).pack(side='left', padx=4)

        self._stroke_rows[stroke] = {'enabled': enabled_var, 'weight': weight_var}

    def _refresh_preview(self):
        """Redraw the colour preview strip."""
        self._preview_canvas.delete('all')
        W = self._preview_canvas.winfo_width() or 520
        colors = []
        for entry in self._palette_rows:
            try:
                h = entry['hex'].get().strip()
                if not h.startswith('#'): h = '#' + h
                w = max(0.01, entry['weight'].get())
                colors.append((h, w))
            except Exception:
                pass
        if not colors:
            return
        total = sum(w for _, w in colors)
        x = 0
        for h, w in colors:
            pw = max(4, int((w/total) * W))
            self._preview_canvas.create_rectangle(x, 0, x+pw, 30, fill=h, outline='')
            x += pw

    def _update_bg_swatch(self, event=None):
        try:
            h = self._bg_var.get().strip()
            if not h.startswith('#'): h = '#' + h
            self._bg_swatch.configure(bg=h)
        except Exception:
            pass

    def _pick_bg(self, hex_color):
        self._bg_var.set(hex_color)
        self._bg_swatch.configure(bg=hex_color)

    # ── Apply / Reset ─────────────────────────────────────────────────────────

    def _collect(self):
        """Read all widget values and write them back to self._prof."""
        from MathCodeEngine import GenerationProfile

        name = self._name_var.get().strip() or self._prof.name

        palette = []
        for entry in self._palette_rows:
            try:
                h = entry['hex'].get().strip()
                if not h.startswith('#'): h = '#' + h
                w     = round(max(0.0, entry['weight'].get()), 3)
                amin  = entry['alpha_min'].get()
                amax  = max(amin + 5, entry['alpha_max'].get())
                if w > 0:
                    palette.append((h, w, amin, amax))
            except Exception:
                pass

        stroke_weights = {}
        for stroke, row in self._stroke_rows.items():
            if row['enabled'].get():
                stroke_weights[stroke] = round(max(0.05, row['weight'].get()), 3)

        t_min = self._t_min_var.get()
        t_max = max(t_min, self._t_max_var.get())
        s_min = self._s_min_var.get()
        s_max = max(s_min + 5, self._s_max_var.get())
        f_min = round(self._f_min_var.get(), 2)
        f_max = round(max(f_min + 0.1, self._f_max_var.get()), 2)

        # Angle ranges — only store if NOT full 0–360 (avoid bloat)
        angle_ranges = {}
        for stroke, avars in self._angle_rows.items():
            lo = avars['min'].get()
            hi = avars['max'].get()
            if lo != 0 or hi != 360:
                angle_ranges[stroke] = (lo, hi)

        bg = self._bg_var.get().strip()
        if not bg.startswith('#'): bg = '#' + bg

        return GenerationProfile(
            name            = name,
            palette         = palette or None,
            stroke_weights  = stroke_weights or None,
            n_strokes       = self._n_strokes_var.get(),
            thickness_range = (t_min, t_max),
            size_range      = (s_min, s_max),
            freq_range      = (f_min, f_max),
            angle_ranges    = angle_ranges or None,
            bg_color        = bg,
            randomize_each  = self._randomize_var.get(),
        )

    def _apply(self):
        profile = self._collect()
        if self.on_apply:
            self.on_apply(profile)
        self.destroy()

    def _reset(self):
        """Close and reopen editor with the current engine profile (discards edits)."""
        from MathCodeEngine import ACTIVE_PROFILE
        self.destroy()
        ProfileEditor(self.master, ACTIVE_PROFILE, on_apply=self.on_apply)


# ══════════════════════════════════════════════════════════════════════════════
# COLOR WHEEL PICKER
# ══════════════════════════════════════════════════════════════════════════════

class ColorWheelPicker(tk.Toplevel):
    """
    HSV color wheel + brightness slider + hex input.
    Clicking anywhere on the wheel picks hue + saturation.
    The vertical slider controls brightness (value).
    on_pick(hex_str) is called when the user confirms.
    """
    SIZE    = 220   # wheel canvas size
    RSLIDER = 18    # slider width

    def __init__(self, parent, initial='#00FF9F', on_pick=None):
        super().__init__(parent)
        self.on_pick = on_pick
        self.title('🎨 Color Picker')
        self.configure(bg=C['bg'])
        self.resizable(False, False)
        self.grab_set()

        # Parse initial color to HSV
        self._h, self._s, self._v = self._hex_to_hsv(initial)
        self._build()
        self._draw_wheel()
        self._draw_brightness()
        self._update_preview()

    # ── Build UI ──────────────────────────────────────────────────────────────

    def _build(self):
        P = 10

        # Title
        tk.Label(self, text='🎨  Pick a Colour', font=FONTS['mono_lg'],
                 fg=C['accent'], bg=C['bg']).pack(padx=P, pady=(P,4), anchor='w')
        tk.Frame(self, height=1, bg=C['border_hi']).pack(fill='x', padx=P)

        body = tk.Frame(self, bg=C['bg'])
        body.pack(padx=P, pady=P)

        # ── Color wheel canvas ────────────────────────────────────────────────
        self._wheel_cv = tk.Canvas(body, width=self.SIZE, height=self.SIZE,
                                    bg=C['bg'], highlightthickness=0, cursor='crosshair')
        self._wheel_cv.grid(row=0, column=0, padx=(0,8))
        self._wheel_cv.bind('<Button-1>',        self._on_wheel_click)
        self._wheel_cv.bind('<B1-Motion>',       self._on_wheel_click)

        # ── Brightness slider (vertical canvas) ───────────────────────────────
        self._bright_cv = tk.Canvas(body, width=self.RSLIDER, height=self.SIZE,
                                     bg=C['bg'], highlightthickness=0, cursor='sb_v_double_arrow')
        self._bright_cv.grid(row=0, column=1, padx=(0,8))
        self._bright_cv.bind('<Button-1>',  self._on_bright_click)
        self._bright_cv.bind('<B1-Motion>', self._on_bright_click)

        # ── Preview + hex ──────────────────────────────────────────────────────
        right = tk.Frame(body, bg=C['bg'])
        right.grid(row=0, column=2, sticky='n')

        tk.Label(right, text='Preview:', font=FONTS['mono_sm'],
                 fg=C['text_dim'], bg=C['bg']).pack(anchor='w')
        self._preview = tk.Canvas(right, width=80, height=80,
                                   bg='#ffffff', highlightthickness=2,
                                   highlightbackground=C['border'])
        self._preview.pack(pady=(2,8))

        tk.Label(right, text='Hex:', font=FONTS['mono_sm'],
                 fg=C['text_dim'], bg=C['bg']).pack(anchor='w')
        self._hex_var = tk.StringVar()
        hex_e = tk.Entry(right, textvariable=self._hex_var,
                          font=FONTS['mono'], bg=C['bg3'], fg=C['accent'],
                          insertbackground=C['accent'], relief='flat',
                          highlightthickness=1, highlightcolor=C['border_hi'],
                          highlightbackground=C['border'], width=9)
        hex_e.pack(ipady=5, pady=(0,4))
        hex_e.bind('<Return>',   self._on_hex_typed)
        hex_e.bind('<FocusOut>', self._on_hex_typed)

        # HSV readout
        self._hsv_lbl = tk.Label(right, text='', font=FONTS['mono_sm'],
                                  fg=C['text_dim'], bg=C['bg'], justify='left')
        self._hsv_lbl.pack(anchor='w', pady=(2,8))

        # Quick swatches — common vivid colors
        tk.Label(right, text='Quick:', font=FONTS['mono_sm'],
                 fg=C['text_dim'], bg=C['bg']).pack(anchor='w')
        quick_frame = tk.Frame(right, bg=C['bg'])
        quick_frame.pack(anchor='w')
        quick_colors = [
            '#FF0000','#FF7700','#FFE600','#00FF00',
            '#00FF9F','#00D4FF','#0044FF','#7B61FF',
            '#FF006E','#FF00FF','#FFFFFF','#888888',
        ]
        for i, qc in enumerate(quick_colors):
            sw = tk.Canvas(quick_frame, width=16, height=16, bg=qc,
                           highlightthickness=0, cursor='hand2')
            sw.grid(row=i//4, column=i%4, padx=1, pady=1)
            sw.bind('<Button-1>', lambda e, h=qc: self._pick_quick(h))

        # ── Buttons ────────────────────────────────────────────────────────────
        btn_row = tk.Frame(self, bg=C['bg'])
        btn_row.pack(fill='x', padx=P, pady=(0,P))
        tk.Button(btn_row, text='✓  Use this color',
                  font=FONTS['mono'], bg=C['accent'], fg=C['bg'],
                  activebackground='#00cc80', relief='flat',
                  padx=16, pady=6, cursor='hand2',
                  command=self._confirm).pack(side='left')
        tk.Button(btn_row, text='✕  Cancel',
                  font=FONTS['mono'], bg=C['bg2'], fg=C['text_dim'],
                  relief='flat', padx=12, pady=6, cursor='hand2',
                  command=self.destroy).pack(side='left', padx=8)

    # ── Drawing ───────────────────────────────────────────────────────────────

    def _draw_wheel(self):
        """Draw the HSV color wheel as individual pixels."""
        import math as _m
        cv   = self._wheel_cv
        S    = self.SIZE
        cx, cy = S // 2, S // 2
        R    = S // 2 - 4

        # Use PIL if available for fast rendering, else draw arcs
        try:
            from PIL import Image, ImageTk
            img = Image.new('RGB', (S, S), (8, 11, 15))
            px  = img.load()
            for y in range(S):
                for x in range(S):
                    dx, dy = x - cx, y - cy
                    dist   = _m.sqrt(dx*dx + dy*dy)
                    if dist <= R:
                        h = (_m.degrees(_m.atan2(-dy, dx)) % 360) / 360.0
                        s = dist / R
                        r, g, b = self._hsv_to_rgb(h, s, self._v)
                        px[x, y] = (r, g, b)
                    # else stays bg color
            self._wheel_img  = ImageTk.PhotoImage(img)
            cv.create_image(0, 0, anchor='nw', image=self._wheel_img, tags='wheel')
        except ImportError:
            # Tkinter arc fallback — coarser but functional
            steps = 60
            for i in range(steps):
                angle = i * 360 / steps
                h = angle / 360
                for si in range(10):
                    s = si / 10
                    r, g, b = self._hsv_to_rgb(h, s, self._v)
                    col = f'#{r:02x}{g:02x}{b:02x}'
                    rad = _m.radians(angle)
                    px = cx + s * R * _m.cos(rad)
                    py = cy - s * R * _m.sin(rad)
                    cv.create_oval(px-4, py-4, px+4, py+4,
                                   fill=col, outline='', tags='wheel')

        self._draw_wheel_cursor()

    def _draw_wheel_cursor(self):
        """Draw the crosshair on the wheel at current H,S."""
        import math as _m
        cv   = self._wheel_cv
        S    = self.SIZE
        cx, cy = S // 2, S // 2
        R    = S // 2 - 4
        cv.delete('cursor')
        rad = _m.radians(self._h * 360)
        px  = cx + self._s * R * _m.cos(rad)
        py  = cy - self._s * R * _m.sin(rad)
        cv.create_oval(px-7, py-7, px+7, py+7,
                       outline='white', width=2, tags='cursor')
        cv.create_oval(px-5, py-5, px+5, py+5,
                       outline='black', width=1, tags='cursor')

    def _draw_brightness(self):
        """Draw the vertical brightness strip."""
        import math as _m
        cv = self._bright_cv
        W, H = self.RSLIDER, self.SIZE
        cv.delete('all')
        for y in range(H):
            v = 1.0 - y / H
            r, g, b = self._hsv_to_rgb(self._h, self._s, v)
            col = f'#{r:02x}{g:02x}{b:02x}'
            cv.create_line(0, y, W, y, fill=col, tags='bright')
        # Cursor line
        cursor_y = int((1.0 - self._v) * H)
        cv.create_line(0, cursor_y, W, cursor_y, fill='white', width=2, tags='bcursor')
        cv.create_line(0, cursor_y+1, W, cursor_y+1, fill='black', width=1, tags='bcursor')

    # ── Event handlers ────────────────────────────────────────────────────────

    def _on_wheel_click(self, event):
        import math as _m
        S  = self.SIZE
        cx, cy = S // 2, S // 2
        R  = S // 2 - 4
        dx, dy = event.x - cx, event.y - cy
        dist   = _m.sqrt(dx*dx + dy*dy)
        self._h = (_m.degrees(_m.atan2(-dy, dx)) % 360) / 360.0
        self._s = min(1.0, dist / R)
        self._draw_wheel_cursor()
        self._draw_brightness()
        self._update_preview()

    def _on_bright_click(self, event):
        H = self.SIZE
        self._v = max(0.0, min(1.0, 1.0 - event.y / H))
        self._draw_wheel()
        self._draw_brightness()
        self._update_preview()

    def _on_hex_typed(self, event=None):
        raw = self._hex_var.get().strip()
        if not raw.startswith('#'): raw = '#' + raw
        if len(raw) == 7:
            try:
                self._h, self._s, self._v = self._hex_to_hsv(raw)
                self._draw_wheel()
                self._draw_brightness()
                self._update_preview(skip_hex=True)
            except Exception:
                pass

    def _pick_quick(self, hex_color):
        self._h, self._s, self._v = self._hex_to_hsv(hex_color)
        self._draw_wheel()
        self._draw_brightness()
        self._update_preview()

    def _update_preview(self, skip_hex=False):
        r, g, b = self._hsv_to_rgb(self._h, self._s, self._v)
        col = f'#{r:02x}{g:02x}{b:02x}'
        self._preview.configure(bg=col)
        if not skip_hex:
            self._hex_var.set(col)
        self._hsv_lbl.configure(
            text=f'H {self._h*360:.0f}°\nS {self._s*100:.0f}%\nV {self._v*100:.0f}%')

    def _confirm(self):
        r, g, b = self._hsv_to_rgb(self._h, self._s, self._v)
        col = f'#{r:02x}{g:02x}{b:02x}'
        if self.on_pick:
            self.on_pick(col)
        self.destroy()

    # ── Color math ────────────────────────────────────────────────────────────

    @staticmethod
    def _hsv_to_rgb(h, s, v):
        """HSV (0-1 each) → (R,G,B) 0-255."""
        import math as _m
        if s == 0:
            c = int(v * 255)
            return c, c, c
        h6 = h * 6
        i  = int(h6)
        f  = h6 - i
        p  = v * (1 - s)
        q  = v * (1 - s * f)
        t  = v * (1 - s * (1 - f))
        m  = {0:(v,t,p), 1:(q,v,p), 2:(p,v,t), 3:(p,q,v), 4:(t,p,v), 5:(v,p,q)}
        r, g, b = m[i % 6]
        return int(r*255), int(g*255), int(b*255)

    @staticmethod
    def _hex_to_hsv(hex_color):
        """#RRGGBB → (h, s, v) each 0-1."""
        h = hex_color.lstrip('#')
        r, g, b = int(h[0:2],16)/255, int(h[2:4],16)/255, int(h[4:6],16)/255
        mx = max(r, g, b); mn = min(r, g, b); d = mx - mn
        v  = mx
        s  = (d / mx) if mx != 0 else 0
        if d == 0:
            hue = 0.0
        elif mx == r:
            hue = ((g - b) / d) % 6
        elif mx == g:
            hue = (b - r) / d + 2
        else:
            hue = (r - g) / d + 4
        return (hue / 6) % 1.0, s, v