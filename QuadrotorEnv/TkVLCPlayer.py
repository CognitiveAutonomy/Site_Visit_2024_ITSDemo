import sys
import os
import platform
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import vlc


class TkVLCPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Counterfactual")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Keyboard shortcuts
        self.root.bind("<Escape>", lambda e: self.on_close())
        self.root.bind("<space>", lambda e: self.play_pause())
        self.root.bind("<o>", lambda e: self.open_file())

        # VLC instance & player
        self.vlc_instance = vlc.Instance("--quiet", "--no-xlib")
        self.player = self.vlc_instance.media_player_new()

        # ---- UI ----
        self.video_panel = ttk.Frame(root)
        self.video_panel.pack(fill="both", expand=True)

        controls = ttk.Frame(root, padding=(8, 6))
        controls.pack(fill="x", side="bottom")

        # Buttons
        self.open_btn = ttk.Button(controls, text="Open Video", command=self.open_file)
        self.open_btn.grid(row=0, column=0, padx=(0, 6))

        self.play_btn = ttk.Button(controls, text="Play/Pause", command=self.play_pause)
        self.play_btn.grid(row=0, column=1, padx=6)

        self.stop_btn = ttk.Button(controls, text="Stop", command=self.stop)
        self.stop_btn.grid(row=0, column=2, padx=6)

        # Seek
        self.pos_var = tk.DoubleVar(value=0.0)
        self.seek = ttk.Scale(
            controls, from_=0, to=1000, orient="horizontal",
            variable=self.pos_var, command=self._maybe_preview_seek
        )
        self.seek.grid(row=0, column=3, sticky="ew", padx=10)
        controls.columnconfigure(3, weight=1)
        self.seek.bind("<ButtonRelease-1>", self._commit_seek)

        # Time
        self.time_label = ttk.Label(controls, text="00:00 / 00:00")
        self.time_label.grid(row=0, column=4, padx=6)

        # Volume
        ttk.Label(controls, text="Vol").grid(row=0, column=5, padx=(10, 2))
        self.vol_var = tk.IntVar(value=80)
        self.vol = ttk.Scale(
            controls, from_=0, to=100, orient="horizontal",
            variable=self.vol_var, command=self.set_volume
        )
        self.vol.grid(row=0, column=6, padx=(0, 6))
        self.player.audio_set_volume(self.vol_var.get())

        # Close button
        self.close_btn = ttk.Button(controls, text="Close", command=self.on_close)
        self.close_btn.grid(row=0, column=7, padx=(10, 0))

        # Attach video output
        self._set_video_output()
        # On some platforms (macOS), rebinding after size changes helps
        self.video_panel.bind("<Configure>", lambda e: self._set_video_output())

        # Poll UI
        self._is_updating = True
        self.media = None
        self.user_is_dragging = False
        self._update_ui()

    # ---------- Helpers ----------
    def _set_video_output(self):
        try:
            handle = self.video_panel.winfo_id()
            system = platform.system()
            if system == "Windows":
                self.player.set_hwnd(handle)
            elif system == "Darwin":  # macOS
                self.player.set_nsobject(handle)
            else:  # Linux/X11
                self.player.set_xwindow(handle)
        except Exception as e:
            messagebox.showerror("VLC Error", f"Failed to set video output:\n{e}")

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
        # Ensure video output is still bound (macOS may need re-binding)
        self._set_video_output()
        self.player.play()

    def play_pause(self):
        state = self.player.get_state()
        if state in (vlc.State.Playing, vlc.State.Buffering):
            self.player.pause()
        elif self.media is None or state == vlc.State.Ended:
            # No media or ended: prompt open
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

        self.root.after(200, self._update_ui)

    def on_close(self):
        self._is_updating = False
        try:
            self.player.stop()
            self.player.release()
            self.vlc_instance.release()
        except Exception:
            pass
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("900x540")

    app = TkVLCPlayer(root)

    # Auto-load a file (optional)
    video_path = r"./output/testing_trial_5_trajectory.mp4"  # <-- change this if desired
    if os.path.exists(video_path):
        media = app.vlc_instance.media_new_path(video_path)
        app.player.set_media(media)
        app.media = media
        app.play()
    else:
        print("Video file not found:", video_path)

    root.mainloop()
