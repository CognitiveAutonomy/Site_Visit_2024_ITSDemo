import os
import tkinter as tk
from PIL import Image, ImageTk

class fNIRS_comparison:
    def __init__(self, image_paths, captions, title="fNIRS Comparison"):
        self.root = tk.Tk()
        self.root.title(title)
        self.root.attributes("-fullscreen", True)  # Esc or q to exit

        self.image_paths = image_paths
        self.captions = captions
        self.title_text = title

        # Keep strong references to ALL PhotoImage objects
        self._photo_images = []

        self.outer_pad = 24
        self.gutter = 24

        # Top bar: title (left) + circular exit button (right)
        top_bar = tk.Frame(self.root, bg="white")
        top_bar.pack(fill="x", pady=(10, 5))

        tk.Label(top_bar, text=self.title_text,
                 font=("Arial", 24, "bold"), fg="black", bg="white").pack(side="left", padx=(20, 0))

        tk.Button(top_bar, text="✕", command=self.root.destroy,
                  font=("Arial", 16, "bold"),
                  bg="red", fg="white", bd=0, relief="flat",
                  activebackground="darkred", activeforeground="white",
                  width=2, height=1, highlightthickness=0).pack(side="right", padx=(0, 20))

        # Image area
        self.frame = tk.Frame(self.root)
        self.frame.pack(expand=True, fill="both")

        for i in range(3):
            self.frame.grid_columnconfigure(i, weight=1, uniform="col")
        self.frame.grid_rowconfigure(0, weight=1)

        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()

        # 3 equal columns with outer padding + two gutters
        self.col_width = int((self.screen_w - (2 * self.outer_pad) - (2 * self.gutter)) / 3)
        self.max_img_height = int(self.screen_h * 0.6)

        # Build after Tk is fully ready (prevents pyimage errors)
        self.root.after(0, self._build_columns)

        self.root.bind("<Escape>", lambda e: self.root.destroy())
        self.root.bind("q", lambda e: self.root.destroy())

    def _padx_for_col(self, idx):
        left = self.outer_pad if idx == 0 else self.gutter
        right = self.outer_pad if idx == 2 else self.gutter
        return (left, right)

    def _scale_to_fit(self, w, h, max_w, max_h):
        if w <= 0 or h <= 0:
            return max_w, max_h
        s = min(max_w / w, max_h / h)
        return max(1, int(w * s)), max(1, int(h * s))

    def _build_columns(self):
        for idx, (img_path, caption) in enumerate(zip(self.image_paths, self.captions)):
            col = tk.Frame(self.frame, width=self.col_width)
            col.grid(row=0, column=idx, sticky="nsew",
                     padx=self._padx_for_col(idx), pady=(self.outer_pad, self.outer_pad))

            inner = tk.Frame(col)          # centers content vertically
            inner.pack(expand=True)

            abs_path = os.path.abspath(img_path)
            if not os.path.exists(abs_path):
                tk.Label(inner, text=f"Could not find file:\n{abs_path}",
                         fg="red", justify="center",
                         wraplength=self.col_width-12).pack(pady=(0, 8))
            else:
                try:
                    pil = Image.open(abs_path)
                    nw, nh = self._scale_to_fit(*pil.size, self.col_width, self.max_img_height)
                    pil = pil.resize((nw, nh), Image.Resampling.LANCZOS)

                    # IMPORTANT: bind PhotoImage to the SAME root
                    tk_img = ImageTk.PhotoImage(pil, master=self.root)

                    # Keep strong refs (list + widget attribute)
                    self._photo_images.append(tk_img)
                    img_label = tk.Label(inner, image=tk_img)
                    img_label.image = tk_img
                    img_label.pack(pady=(0, 8))
                except Exception as e:
                    tk.Label(inner, text=f"Could not load:\n{abs_path}\n{e}",
                             fg="red", justify="center",
                             wraplength=self.col_width-12).pack(pady=(0, 8))

            tk.Label(inner, text=caption, font=("Arial", 14),
                     fg="black", wraplength=self.col_width-12, justify="center").pack()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    images = [
        r"C:\Users\myuh\Documents\GitHub\Site_Visit_2024_ITSDemo\QuadrotorEnv\fnirs\elmo_trial_5_fNIRs.png",
        r"C:\Users\myuh\Documents\GitHub\Site_Visit_2024_ITSDemo\QuadrotorEnv\fnirs\TBD.png",
        r"C:\Users\myuh\Documents\GitHub\Site_Visit_2024_ITSDemo\QuadrotorEnv\fnirs\TBD.png",
    ]
    captions = ["Trial 1–5", "Trial 6–10", "Trial 11–15"]

    fNIRS_comparison(images, captions, title="fNIRS Comparison").run()
