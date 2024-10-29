import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter import messagebox
from PIL import ImageTk, Image


root = tk.Tk()
root.configure(bg='white', highlightthickness=0)
window_width = root.winfo_screenwidth()
window_height = root.winfo_screenheight()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
center_x = int(screen_width / 2 - window_width / 2)
center_y = int(screen_height / 2 - window_height / 2)
root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

Slide1 = ImageTk.PhotoImage(Image.open("../assets/images/instructions/Slide1.png"))
Slide2 = ImageTk.PhotoImage(Image.open("../assets/images/instructions/Slide2.png"))
Slide3 = ImageTk.PhotoImage(Image.open("../assets/images/instructions/Slide3.png"))
Slide4 = ImageTk.PhotoImage(Image.open("../assets/images/instructions/Slide4.png"))
Slide5 = ImageTk.PhotoImage(Image.open("../assets/images/instructions/Slide5.png"))
Slide6 = ImageTk.PhotoImage(Image.open("../assets/images/instructions/Slide6.png"))
Slide7 = ImageTk.PhotoImage(Image.open("../assets/images/instructions/Slide7.png"))
Slide8 = ImageTk.PhotoImage(Image.open("../assets/images/instructions/Slide8.png"))
Slide9 = ImageTk.PhotoImage(Image.open("../assets/images/instructions/Slide9.png"))
Slide10 = ImageTk.PhotoImage(Image.open("../assets/images/instructions/Slide10.png"))
Slide11 = ImageTk.PhotoImage(Image.open("../assets/images/instructions/Slide11.png"))
Slide12 = ImageTk.PhotoImage(Image.open("../assets/images/instructions/Slide12.png"))
Slide13 = ImageTk.PhotoImage(Image.open("../assets/images/instructions/Slide13.png"))
Slide14 = ImageTk.PhotoImage(Image.open("../assets/images/instructions/Slide14.png"))

spacer = Label(root, text = " ", bg='#fff')
spacer.pack()
l = Label(bg='white', highlightthickness=0)
l.config(image=Slide1)
l.pack()
# using recursion to slide to next image
global Slide_Num
Slide_Num = 1


def exit_application():
    global Slide_Num
    MsgBox = messagebox.askquestion('Exit', 'Close tutorial?',
                                    icon='warning')
    if MsgBox == 'yes':
        root.destroy()

    else:
        Slide_Num = 14
        messagebox.showinfo('Return', 'Please review tutorial as needed')


# function to change to next image
def next():
    global Slide_Num
    Slide_Num = Slide_Num + 1
    if Slide_Num == 15:
        exit_application()
    if Slide_Num == 1:
        l.config(image=Slide1)
    elif Slide_Num == 2:
        l.config(image=Slide2)
    elif Slide_Num == 3:
        l.config(image=Slide3)
    elif Slide_Num == 4:
        l.config(image=Slide4)
    elif Slide_Num == 5:
        l.config(image=Slide5)
    elif Slide_Num == 6:
        l.config(image=Slide6)
    elif Slide_Num == 7:
        l.config(image=Slide7)
    elif Slide_Num == 8:
        l.config(image=Slide8)
    elif Slide_Num == 9:
        l.config(image=Slide9)
    elif Slide_Num == 10:
        l.config(image=Slide10)
    elif Slide_Num == 11:
        l.config(image=Slide11)
    elif Slide_Num == 12:
        l.config(image=Slide12)
    elif Slide_Num == 13:
        l.config(image=Slide13)
    elif Slide_Num == 14:
        l.config(image=Slide14)

def prev():
    global Slide_Num
    Slide_Num = Slide_Num - 1
    if Slide_Num == 0:
        Slide_Num = 1
    if Slide_Num == 1:
        l.config(image=Slide1)
    elif Slide_Num == 2:
        l.config(image=Slide2)
    elif Slide_Num == 3:
        l.config(image=Slide3)
    elif Slide_Num == 4:
        l.config(image=Slide4)
    elif Slide_Num == 5:
        l.config(image=Slide5)
    elif Slide_Num == 6:
        l.config(image=Slide6)
    elif Slide_Num == 7:
        l.config(image=Slide7)
    elif Slide_Num == 8:
        l.config(image=Slide8)
    elif Slide_Num == 9:
        l.config(image=Slide9)
    elif Slide_Num == 10:
        l.config(image=Slide10)
    elif Slide_Num == 11:
        l.config(image=Slide11)
    elif Slide_Num == 12:
        l.config(image=Slide12)
    elif Slide_Num == 13:
        l.config(image=Slide13)
    elif Slide_Num == 14:
        l.config(image=Slide14)



# Buttons
Next_button = Button(root, text="Next", width=10, height=2, highlightbackground='#fff', command=next)
Next_button.pack()

spacer1 = Label(root, text = " ", bg='#fff')
spacer1.pack()

Prev_button = Button(root, text="Previous", width=10, height=2, highlightbackground='#fff', command=prev)
Prev_button.pack()

root.title("Tutorial")
root.mainloop()