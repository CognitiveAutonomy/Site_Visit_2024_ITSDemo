import os
import sys
import platform
import tkinter as tk
from PIL import Image, ImageTk

# ----------------------- fNIRS image window (Toplevel) -----------------------
class fNIRS_comparison:
    """
    A Toplevel window that shows 3 images with captions in a row,
    keeping aspect ratio, evenly spaced, vertically centered,
    with a title and a top-right close (✕) button.
    """
    def __init__(self, master, image_paths, captions, title="fNIRS Comparison",
                 fullscreen=False, geometry=None):
        self.master = master
        self.win = tk.Toplevel(master, bg="white")
        self.win.title(title)
        if fullscreen:
            self.win.attributes("-fullscreen", True)
        elif geometry:
            self.win.geometry(geometry)

        self.image_paths = image_paths
        self.captions = captions
        self.title_text = title

        self._photo_images = []  # strong refs to PhotoImage

        self.outer_pad = 24
        self.gutter = 24

        # Top bar
        top_bar = tk.Frame(self.win, bg="white")
        top_bar.pack(fill="x", pady=(10, 5))
        tk.Label(top_bar, text=self.title_text,
                 font=("Arial", 24, "bold"), fg="black", bg="white").pack(side="left", padx=(20, 0))
        tk.Button(top_bar, text="✕", command=self.win.destroy,
                  font=("Arial", 16, "bold"), bg="red", fg="white",
                  bd=0, relief="flat", activebackground="darkred",
                  activeforeground="white", width=2, height=1,
                  highlightthickness=0).pack(side="right", padx=(0, 20))

        # Main area
        self.frame = tk.Frame(self.win, bg="white")
        self.frame.pack(expand=True, fill="both")
        for i in range(3):
            self.frame.grid_columnconfigure(i, weight=1, uniform="col")
        self.frame.grid_rowconfigure(0, weight=1)

        screen_w = self.win.winfo_screenwidth()
        screen_h = self.win.winfo_screenheight()
        self.col_width = int((screen_w - (2 * self.outer_pad) - (2 * self.gutter)) / 3)
        self.max_img_height = int(screen_h * 0.6)

        # Build after Tk is ready
        self.win.after(0, self._build_columns)

        # Keybinds (this window only)
        self.win.bind("<Escape>", lambda e: self.win.destroy())
        self.win.bind("q",        lambda e: self.win.destroy())

    def _padx(self, idx):
        left  = self.outer_pad if idx == 0 else self.gutter
        right = self.outer_pad if idx == 2 else self.gutter
        return (left, right)

    def _scale_to_fit(self, w, h, max_w, max_h):
        if w <= 0 or h <= 0:
            return max_w, max_h
        s = min(max_w / w, max_h / h)
        return max(1, int(w * s)), max(1, int(h * s))

    def _build_columns(self):
        for idx, (img_path, caption) in enumerate(zip(self.image_paths, self.captions)):
            col = tk.Frame(self.frame, width=self.col_width, bg="white")
            col.grid(row=0, column=idx, sticky="nsew",
                     padx=self._padx(idx), pady=(self.outer_pad, self.outer_pad))

            inner = tk.Frame(col, bg="white")   # vertical centering
            inner.pack(expand=True)

            abs_path = os.path.abspath(img_path)
            if not os.path.exists(abs_path):
                tk.Label(inner, text=f"Could not find file:\n{abs_path}",
                         fg="red", bg="white", justify="center",
                         wraplength=self.col_width-12).pack(pady=(0, 8))
            else:
                try:
                    pil = Image.open(abs_path)
                    nw, nh = self._scale_to_fit(*pil.size, self.col_width, self.max_img_height)
                    pil = pil.resize((nw, nh), Image.Resampling.LANCZOS)
                    tk_img = ImageTk.PhotoImage(pil, master=self.master)  # bind to same interpreter
                    self._photo_images.append(tk_img)
                    lbl = tk.Label(inner, image=tk_img, bg="white")
                    lbl.image = tk_img  # widget-level strong ref
                    lbl.pack(pady=(0, 8))
                except Exception as e:
                    tk.Label(inner, text=f"Could not load:\n{abs_path}\n{e}",
                             fg="red", bg="white", justify="center",
                             wraplength=self.col_width-12).pack(pady=(0, 8))

            tk.Label(inner, text=caption, font=("Arial", 14),
                     fg="black", bg="white", wraplength=self.col_width-12,
                     justify="center").pack()


# --------------------- VLC video window (Toplevel) ---------------------
class VLCVideoWindow:
    """
    A Toplevel window embedding VLC with Open, Play/Pause, Stop, Seek, Volume,
    time display, and white backgrounds. Based directly on your TkVLCPlayer logic,
    adapted to Toplevel so it doesn't destroy the whole app on close.
    """
    def __init__(self, master, title="Counterfactual", geometry="900x540", autoplay_path=None):
        import vlc  # requires python-vlc and VLC installed

        self.vlc = vlc
        self.master = master
        self.win = tk.Toplevel(master, bg="white")
        self.win.title(title)
        self.win.geometry(geometry)

        # Keyboard shortcuts (bound to this window only)
        self.win.bind("<Escape>", lambda e: self.on_close())
        self.win.bind("<space>",  lambda e: self.play_pause())
        self.win.bind("<o>",      lambda e: self.open_file())

        # VLC instance & player
        self.vlc_instance = self.vlc.Instance("--quiet", "--no-xlib")
        self.player = self.vlc_instance.media_player_new()

        # ---- UI (all white) ----
        self.video_panel = tk.Frame(self.win, bg="white")
        self.video_panel.pack(fill="both", expand=True)

        controls = tk.Frame(self.win, bg="white")
        controls.pack(fill="x", side="bottom", padx=8, pady=(6, 8))

        # Buttons
        tk.Button(controls, text="Open Video", command=self.open_file, bg="white").grid(row=0, column=0, padx=(0, 6))
        tk.Button(controls, text="Play/Pause", command=self.play_pause, bg="white").grid(row=0, column=1, padx=6)
        tk.Button(controls, text="Stop",       command=self.stop,       bg="white").grid(row=0, column=2, padx=6)

        # Seek
        self.pos_var = tk.DoubleVar(value=0.0)
        self.seek = tk.Scale(
            controls, from_=0, to=1000, orient="horizontal",
            variable=self.pos_var, command=self._maybe_preview_seek,
            showvalue=0, bg="white", highlightthickness=0
        )
        self.seek.grid(row=0, column=3, sticky="ew", padx=10)
        controls.columnconfigure(3, weight=1)
        self.seek.bind("<ButtonRelease-1>", self._commit_seek)

        # Time
        self.time_label = tk.Label(controls, text="00:00 / 00:00", bg="white")
        self.time_label.grid(row=0, column=4, padx=6)

        # Volume
        tk.Label(controls, text="Vol", bg="white").grid(row=0, column=5, padx=(10, 2))
        self.vol_var = tk.IntVar(value=80)
        self.vol = tk.Scale(
            controls, from_=0, to=100, orient="horizontal",
            variable=self.vol_var, command=self.set_volume,
            showvalue=0, bg="white", highlightthickness=0
        )
        self.vol.grid(row=0, column=6, padx=(0, 6))
        self.player.audio_set_volume(self.vol_var.get())

        # Close button
        tk.Button(controls, text="Close", command=self.on_close, bg="white").grid(row=0, column=7, padx=(10, 0))

        # Attach video output
        self._set_video_output()
        self.video_panel.bind("<Configure>", lambda e: self._set_video_output())

        # Poll UI
        self._is_updating = True
        self.media = None
        self.user_is_dragging = False
        self._update_ui()

        # Optional autoplay
        if autoplay_path and os.path.exists(autoplay_path):
            media = self.vlc_instance.media_new_path(autoplay_path)
            self.player.set_media(media)
            self.media = media
            self.play()

        # Window close protocol
        self.win.protocol("WM_DELETE_WINDOW", self.on_close)

    # ---------- Helpers ----------
    def _set_video_output(self):
        try:
            handle = self.video_panel.winfo_id()
            system = platform.system()
            if system == "Windows":
                self.player.set_hwnd(handle)
            elif system == "Darwin":  # macOS
                # Note: some Tk builds on macOS make embedding tricky.
                self.player.set_nsobject(handle)
            else:  # Linux/X11
                self.player.set_xwindow(handle)
        except Exception as e:
            # Avoid modal messageboxes in embedded apps; print instead:
            print("VLC Error: Failed to set video output:", e, file=sys.stderr)

    @staticmethod
    def _format_ms(ms):
        if ms is None or ms < 0:
            return "00:00"
        s = int(ms // 1000)
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"

    # ---------- UI Callbacks ----------
    def open_file(self):
        from tkinter import filedialog
        path = filedialog.askopenfilename(
            title="Open video",
            filetypes=[
                ("Video files", "*.mp4 *.mkv *.avi *.mov *.webm *.wmv"),
                ("All files", "*.*"),
            ],
        )
        if not path:
            return
        media = self.vlc_instance.media_new_path(path)
        self.player.set_media(media)
        self.media = media
        self.play()

    def play(self):
        self._set_video_output()  # rebind (esp. macOS)
        self.player.play()

    def play_pause(self):
        state = self.player.get_state()
        if state in (self.vlc.State.Playing, self.vlc.State.Buffering):
            self.player.pause()
        elif self.media is None or state == self.vlc.State.Ended:
            self.open_file()
        else:
            self.play()

    def stop(self):
        self.player.stop()
        self.pos_var.set(0)
        self.time_label.configure(text="00:00 / 00:00")

    def set_volume(self, _=None):
        self.player.audio_set_volume(int(self.vol_var.get()))

    def _maybe_preview_seek(self, _=None):
        self.user_is_dragging = True

    def _commit_seek(self, _event=None):
        self.user_is_dragging = False
        self.player.set_position(self.pos_var.get() / 1000.0)

    def _update_ui(self):
        if not self._is_updating:
            return
        length = self.player.get_length()  # ms
        cur = self.player.get_time()       # ms
        if length and length > 0:
            self.time_label.configure(
                text=f"{self._format_ms(cur)} / {self._format_ms(length)}"
            )
            if not self.user_is_dragging:
                pos = self.player.get_position()
                if 0.0 <= pos <= 1.0:
                    self.pos_var.set(pos * 1000)
        else:
            self.time_label.configure(text="00:00 / 00:00")
        # poll again
        self.win.after(200, self._update_ui)

    def on_close(self):
        self._is_updating = False
        try:
            self.player.stop()
            self.player.release()
            self.vlc_instance.release()
        except Exception:
            pass
        self.win.destroy()


# --------------------------- Example: open both ---------------------------
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # keep the root hidden; use Toplevels

    # fNIRS images window
    images1 = [
        r".\fnirs\elmo_trial_5_fNIRs.png",
        r".\fnirs\elmo_trial_10_fNIRs.png",
        r".\fnirs\elmo_trial_15_fNIRs.png"
    ]
    captions1 = ["Trial 1–5", "Trial 6–10", "Trial 11–15"]
    win1 = fNIRS_comparison(
        root, images1, captions1,
        title="fNIRS Comparison",
        fullscreen=False,
        geometry="1200x800+50+50"
    )

    # VLC video window (autoplay optional)
    video_path = r"./output/testing_trial_5_trajectory.mp4"
    win2 = VLCVideoWindow(
        root,
        title="Counterfactual",
        geometry="960x540+1300+50",
        autoplay_path=video_path if os.path.exists(video_path) else None
    )

    root.mainloop()


# -------------------- Example --------------------
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    images = [
        r"C:\Users\myuh\Documents\GitHub\Site_Visit_2024_ITSDemo\QuadrotorEnv\fnirs\elmo_trial_5_fNIRs.png",
        r"C:\Users\myuh\Documents\GitHub\Site_Visit_2024_ITSDemo\QuadrotorEnv\fnirs\TBD.png",
        r"C:\Users\myuh\Documents\GitHub\Site_Visit_2024_ITSDemo\QuadrotorEnv\fnirs\TBD.png",
    ]
    captions = ["Trial 1–5", "Trial 6–10", "Trial 11–15"]

    win1 = fNIRS_comparison(
        root, images, captions,
        title="fNIRS Comparison",
        fullscreen=True,
    )

    video_path = r"./output/testing_trial_5_trajectory.mp4"
    win2 = VLCVideoWindow(
        root,
        title="Counterfactual",
        geometry="960x540+1300+50",
        autoplay_path=video_path if os.path.exists(video_path) else None
    )

    root.mainloop()
