import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from PIL import ImageTk, Image
pagefont = ("Arial",10, "italic")
infofont = ("Arial",12)
LARGEFONT = ("Arial", 25, 'bold')\

class tkinterApp(tk.Tk):

    # __init__ function for class tkinterApp
    def __init__(self, *args, **kwargs):
        # __init__ function for class Tk
        tk.Tk.__init__(self, *args, **kwargs)

        # creating a container
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # initializing frames to an empty array
        self.frames = {}

        # iterating through a tuple consisting
        # of the different page layouts
        for F in (StartPage, Page1, Page2, Page3, Page4, Page5, LastPage):
            frame = F(container, self)

            # initializing frame of that object from
            # startpage, page1, page2 respectively with
            # for loop
            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    # to display the current frame passed as
    # parameter
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

# first window frame startpage

class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        def next_page():
            controller.show_frame(Page1)
            Image_Label.config(image='')

        tk.Frame.__init__(self, parent, background = "white")

        Page_Image = Image.open("../assets/images/Purdue_logo.png")
        Header_Image = ImageTk.PhotoImage(Page_Image)
        Image_Label = ttk.Label(image=Header_Image)
        Image_Label.image = Header_Image
        h = Header_Image.height()
        w = Header_Image.width()
        window_width = self.winfo_screenwidth()
        Image_Label.place(x=int((window_width - w) / 2), y=int(h/2))

        # label of frame Layout 2
        Header_Label = ttk.Label(self, text="\n\n\n\n\n\nCPS: Human Automation Interaction Study", font=LARGEFONT, background="white")
        Header_Label.pack()

        Info_Label = ttk.Label(self, text="\nThank you for your interest to participate in this study."
                                          "\nIf you encounter any technical difficulties, please make note of the issue"
                                          " and describe you experience in the survey at the end."
                                          "\nWe greatly appreciate your feedback."
                                          "\n\nPress Next to continue", font = infofont, background="white")

        # Info_Label.configure(anchor=CENTER)
        Info_Label.pack()

        # Next Button
        button2 = ttk.Button(self, text="Next", command= next_page)
        button2.pack()


# second window frame page1
class Page1(tk.Frame):

    def __init__(self, parent, controller):
        def next_page():
            controller.show_frame(Page2)
            Image_Label.config(image='')

        tk.Frame.__init__(self, parent, background = "white")

        Header_Label = ttk.Label(self, text="\nINSTRUCTIONS", font=LARGEFONT, background = "white")
        Header_Label.pack()

        Instruction_Label1 = ttk.Label(self, text="cdffff",  font = infofont, background="white")
        Instruction_Label1.pack()

        Page_Image = Image.open("../assets/images/Purdue.jpg")
        Header_Image = ImageTk.PhotoImage(Page_Image)
        Image_Label = ttk.Label(image=Header_Image)
        Image_Label.image = Header_Image
        h = Header_Image.height()
        w = Header_Image.width()
        window_width = self.winfo_screenwidth()
        Image_Label.place(x=int((window_width - w) / 2), y=int(h / 2))

        #Previous button
        Prev_Button = ttk.Button(self, text="Previous",
                             command=lambda: controller.show_frame(StartPage))
        Prev_Button.pack()

        # Next Button
        Next_Button = ttk.Button(self, text="Next", command=next_page)
        Next_Button.pack()

        #Page Number
        Page_Label = ttk.Label(self, text="\nPage 1", font=pagefont, background="white")
        Page_Label.pack()


# third window frame page2
class Page2(tk.Frame):
    def __init__(self, parent, controller):
        def next_page():
            controller.show_frame(Page3)
            Image_Label.config(image='')

        tk.Frame.__init__(self, parent, background = "white")
        Header_Label = ttk.Label(self, text="\nINSTRUCTIONS", font=LARGEFONT, background = "white")
        Header_Label.pack()

        # Previous button
        Prev_Button = ttk.Button(self, text="Previous", command=lambda: controller.show_frame(Page1))
        Prev_Button.pack()

        # Next Button
        Next_Button = ttk.Button(self, text="Next", command=next_page)
        Next_Button.pack()

        # Page Number
        Page_Label = ttk.Label(self, text="\nPage 2", font=pagefont, background="white")
        Page_Label.pack()

# fourth window frame page3
class Page3(tk.Frame):
    def __init__(self, parent, controller):
        def next_page():
            controller.show_frame(Page4)
            Image_Label.config(image='')

        tk.Frame.__init__(self, parent, background = "white")
        Header_Label = ttk.Label(self, text="\nINSTRUCTIONS", font=LARGEFONT, background = "white")
        Header_Label.pack()

        # Previous button
        Prev_Button = ttk.Button(self, text="Previous", command=lambda: controller.show_frame(Page2))
        Prev_Button.pack()

        # Next Button
        Next_Button = ttk.Button(self, text="Next", command=next_page)
        Next_Button.pack()

        # Page Number
        Page_Label = ttk.Label(self, text="\nPage 3", font=pagefont, background="white")
        Page_Label.pack()


# fifth window frame page4
class Page4(tk.Frame):
    def __init__(self, parent, controller):
        def next_page():
            controller.show_frame(Page5)
            Image_Label.config(image='')

        tk.Frame.__init__(self, parent, background = "white")
        Header_Label = ttk.Label(self, text="\nINSTRUCTIONS", font=LARGEFONT, background = "white")
        Header_Label.pack()

        # Previous button
        Prev_Button = ttk.Button(self, text="Previous", command=lambda: controller.show_frame(Page3))
        Prev_Button.pack()

        # Next Button
        Next_Button = ttk.Button(self, text="Next", command=next_page)
        Next_Button.pack()

        # Page Number
        Page_Label = ttk.Label(self, text="\nPage 4", font=pagefont, background="white")
        Page_Label.pack()

# sixth window frame page4
class Page5(tk.Frame):
    def __init__(self, parent, controller):
        def next_page():
            controller.show_frame(LastPage)
            Image_Label.config(image='')

        tk.Frame.__init__(self, parent, background = "white")
        Header_Label = ttk.Label(self, text="\nINSTRUCTIONS", font=LARGEFONT, background = "white")
        Header_Label.pack()

        # Previous button
        Prev_Button = ttk.Button(self, text="Previous", command=lambda: controller.show_frame(Page4))
        Prev_Button.pack()

        # Next Button
        Next_Button = ttk.Button(self, text="Next", command=next_page)
        Next_Button.pack()

        # Page Number
        Page_Label = ttk.Label(self, text="\nPage 5", font=pagefont, background="white")
        Page_Label.pack()

# Last window frame page4
class LastPage(tk.Frame):
    def __init__(self, parent, controller):
        def exit_application():
            MsgBox = messagebox.askquestion('Close \nInstructions', 'Are you sure?',
                                        icon='warning')
            if MsgBox == 'yes':
                app.destroy()

            else:
                messagebox.showinfo('Return', 'Review as needed')

        tk.Frame.__init__(self, parent, background = "white")
        Header_Label = ttk.Label(self, text="\nINSTRUCTIONS", font=LARGEFONT, background = "white")
        Header_Label.pack()

        # Previous button
        Prev_Button = ttk.Button(self, text="Previous", command=lambda: controller.show_frame(Page5))
        Prev_Button.pack()

        # Exit Button
        Exit_Button = ttk.Button(self, text="Close", command= exit_application)
        Exit_Button.pack()

        # Page Number
        Page_Label = ttk.Label(self, text="\nPage 6", font=pagefont, background="white")
        Page_Label.pack()


# Driver Code
app = tkinterApp()
app.title("CPS Human Automation Interaction Study")
window_width = app.winfo_screenwidth()
window_height = app.winfo_screenheight()
screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()
center_x = int(screen_width / 2 - window_width / 2)
center_y = int(screen_height / 2 - window_height / 2)
app.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
app.configure(background='white')
app.mainloop()
