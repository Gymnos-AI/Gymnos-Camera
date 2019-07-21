# Python program to extract rectangular
# Shape using OpenCV and tkinter in Python3
import cv2
import json
from tkinter import *
import tkinter as tk

# a list of Machine Names to chose from
OPTIONS = [
    "bench",
    "squat_rack"
]  # etc


class CalibrateCam:
    def __init__(self, image, using_mac):
        self.p1 = (0, 0)
        self.p2 = (0, 0)
        self.drawing = False
        self.machines_container = {"machines": []}
        self.using_mac = using_mac

        self.img = image
        cv2.namedWindow('Cam View')
        cv2.setMouseCallback('Cam View', self.draw_rectangle)

    def draw_rectangle(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            if self.drawing is False:
                self.drawing = True
                self.p1 = (x, y)
                self.p2 = self.p1
            else:
                self.drawing = False
                self.p2 = (x, y)
                if self.using_mac:
                    print("GUI not supported on Mac")
                    machine_name = input("Machine name: ")
                else:
                    machine_name = self.popup_msg()

                self.machines_container["machines"].append(
                    {"name": machine_name, "topX": self.p1[0], "leftY": self.p1[1], "bottomX": self.p2[0], "rightY": self.p2[1]})

        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing is True:
                self.p2 = (x, y)

    def convert_to_ratios(self):
        for points in self.machines_container["machines"]:
            points["topX"] = int(points["topX"]) / 256
            points["leftY"] = int(points["leftY"]) / 256
            points["bottomX"] = int(points["bottomX"]) / 256
            points["rightY"] = int(points["rightY"]) / 256


    def remove_machine(self):
        if self.machines_container["machines"]:
            self.machines_container["machines"].pop()

    def popup_msg(self):
        popup = tk.Tk()
        popup.wm_title("!")

        popup.geometry('100x100')

        variable = StringVar(popup)
        variable.set(OPTIONS[0])  # default value

        def get_machine():
            print("Machine name: " + variable.get())
            popup.destroy()
            return variable.get()

        w = OptionMenu(popup, variable, *OPTIONS)
        w.pack()

        button = Button(popup, text="OK",
                        command=get_machine)
        button.pack()

        popup.mainloop()
        return variable.get()

    def main(self):
        while(1):

            #!!!! NEEDS WORK
            # img_temp = cv2.imread(self.img, -1)
            img_temp = self.img
            img_temp = cv2.resize(self.img, (0, 0), fx=1, fy=1)

            if self.p1 and self.p2:
                cv2.rectangle(img_temp, self.p1, self.p2, (0, 255, 0), 2)

            for points in self.machines_container["machines"]:
                cv2.rectangle(img_temp, (points["topX"], points["leftY"]), (
                    points["bottomX"], points["rightY"]), (0, 255, 0), 2)
                cv2.putText(img_temp, points["name"], (points["topX"], points["leftY"] - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

            cv2.imshow('Cam View', img_temp)

            k = cv2.waitKey(1)  # & 0xFF

            if k == ord('r'):
                self.remove_machine()

            if k == 27 or k == ord('q'):
                break

        cv2.destroyAllWindows()
        self.convert_to_ratios()
        with open('./gymnoscamera/Machines.json', 'w') as outfile:
            json.dump(self.machines_container, outfile)
