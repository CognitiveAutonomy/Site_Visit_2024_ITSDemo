import tkinter as tk
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
from itertools import count

root = tk.Tk()
root.configure(bg='white', highlightthickness=0)
window_width = root.winfo_screenwidth()
window_height = root.winfo_screenheight()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
center_x = int(screen_width / 2 - window_width / 2)
center_y = int(screen_height / 2 - window_height / 2)
root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')


spacer1 = Label(root, text = " ", bg='#fff')
spacer1.pack()

global Page_Num
Page_Num = 1

def exit_application():
    global Page_Num
    MsgBox = messagebox.askquestion('Begin practice round', 'Are you ready to start the practice round??',
                                    icon='warning')
    if MsgBox == 'yes':
        root.destroy()

    else:
        Page_Num = 1
        messagebox.showinfo('Return', 'Please review tutorial as needed')


# function to change to next image
def close():
    global Page_Num
    Page_Num = Page_Num + 1
    if Page_Num == 2:
        exit_application()
    if Page_Num == 1:
        label.configure(image=frame)


class ImageLabel(tk.Label):
    """a label that displays images, and plays them if they are gifs"""
    def load(self, im):
        if isinstance(im, str):
            im = Image.open(im)
        self.loc = 0
        self.frames = []

        try:
            for i in count(1):
                self.frames.append(ImageTk.PhotoImage(im.copy()))
                im.seek(i)
        except EOFError:
            pass

        self.delay = 40

        if len(self.frames) == 1:
            self.config(image=self.frames[0])
        else:
            self.next_frame()

    def unload(self):
        self.config(image="")
        self.frames = None

    def next_frame(self):
        if self.frames:
            self.loc += 1
            self.loc %= len(self.frames)
            self.config(image=self.frames[self.loc])
            self.after(self.delay, self.next_frame)

lbl = ImageLabel(root)
lbl.config(bg='white', highlightthickness=0)
lbl.pack()
lbl.load('../assets/images/All_control.gif')

spacer2 = Label(root, text = " ", bg='#fff')
spacer2.pack()

Close_button = Button(root, text="Begin practice round", width=20, height=2, highlightbackground='#fff', command=close)
Close_button.pack()

spacer3 = Label(root, text = " ", bg='#fff')
spacer3.pack()

root.title("Thrust and Attitude Control Tutorial")
root.mainloop()