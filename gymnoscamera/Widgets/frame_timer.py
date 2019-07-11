#!/usr/bin/python

try:
    import tkinter
    from tkinter import *
except ImportError:
    import Tkinter as tkinter
    from tkinter import *

WIDTH = 256     #width of the window
HEIGHT = 286    #height of the window
OFFSET_X = 230   #offset for window x axis
OFFSET_Y = 340    #offset for window y axis
FONT_SIZE = 20

class frameTimers:

    def __init__(self, master):
        master.title("Frame Timers")
        master.geometry("%dx%d+%d+%d" % (WIDTH, HEIGHT, OFFSET_X, OFFSET_Y))
        self.canvas = Canvas(master, width=256, height=256, relief='raised', borderwidth=1)
        self.canvas.pack()

        #left side rectangle
        self.rectangleOne = self.canvas.create_rectangle(0, 0, 126, 255, fill='red')

        #squat label at top
        self.labelOne = self.canvas.create_text(60, 20, font=("Purisa", FONT_SIZE),text="Squat")

        #right side rectangle
        self.rectangleTwo = self.canvas.create_rectangle(126, 0, 255, 255, fill='blue')

        #bench label at top
        self.labelTwo = self.canvas.create_text(190, 20, font=("Purisa", FONT_SIZE),text="Bench")

        #Squat and Bench timer results
        self.squat = self.canvas.create_text(55, 165, font=("Purisa", FONT_SIZE), text=0)
        self.bench = self.canvas.create_text(185, 165, font=("Purisa", FONT_SIZE), text=0)

        #reset button
        self.resetButton = Button(master, text="Reset Timers", command=self.resetTimers)
        self.resetButton.pack(side=BOTTOM)

    def squatTime(self, x):
        x = int(x)
        self.canvas.itemconfig(self.squat, text=x)

    def benchTime(self, x):
        x = int(x)
        self.canvas.itemconfig(self.bench, text=x)


    def resetTimers(self):
        self.squatTime(0)
        self.benchTime(0)

#test
# initialize the Widgets
#root = tkinter.Tk()
#ft = frameTimers(root)
#root.mainloop()

#ft.squatTime(100)    #this is how you use the class
#ft.benchTime(50)     #this is how you use the class