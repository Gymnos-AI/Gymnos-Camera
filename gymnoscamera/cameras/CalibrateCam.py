# Python program to extract rectangular
# Shape using OpenCV and tkinter in Python3
import cv2
import json
from tkinter import *
import tkinter as tk


class CalibrateCam:
    def __init__(self, camera, using_mac):
        # Constants
        self.using_mac = using_mac

        # reference to camera
        self.camera = camera

        self.OPTIONS = [
            "bench",
            "squat_rack"
        ]
        self.json_location = "./gymnoscamera/Machines.json"
        self.pop_title = "Options"
        self.popup_dimensions = "100x100"
        self.annotation_colour = (0, 255, 0)  # RGB

        # Keys to accessing and storing into the Json File
        self.machines = "machines"
        self.name = "name"
        self.top_x = "topX"
        self.left_y = "leftY"
        self.bottom_x = "bottomX"
        self.right_y = "rightY"

        self.drawing = False
        self.machines_container = {"machines": []}
        self.p1 = (0, 0)
        self.p2 = (0, 0)
        cv2.namedWindow('Cam View')
        cv2.setMouseCallback('Cam View', self.draw_rectangle)

    def draw_rectangle(self, event, x, y, flags, param):
        """
        Event handler that draws the rectangle on users click
        """
        if event == cv2.EVENT_LBUTTONDOWN:
            if self.drawing is False:
                self.drawing = True
                self.p1 = (x, y)
                self.p2 = self.p1
            else:
                self.drawing = False
                self.p2 = (x, y)
                if self.using_mac:
                    print("GUI not supported on Mac, please enter machine name through command line")
                    machine_name = input("Machine name: ")
                else:
                    machine_name = self.popup_msg()

                self.machines_container[self.machines].append(
                    {self.name: machine_name,
                     self.top_x: self.p1[0],
                     self.left_y: self.p1[1],
                     self.bottom_x: self.p2[0],
                     self.right_y: self.p2[1]})

        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing is True:
                self.p2 = (x, y)

    def write_json(self):
        """
        Writes machine locations that the user chose into the json file
        """
        # first convert all raw pixel values into their ratios
        # this helps with dealing with variable sizing
        camera_width, camera_height = self.camera.get_dimensions()
        for points in self.machines_container[self.machines]:
            points[self.top_x] = int(points[self.top_x]) / camera_width
            points[self.left_y] = int(points[self.left_y]) / camera_height
            points[self.bottom_x] = int(points[self.bottom_x]) / camera_width
            points[self.right_y] = int(points[self.right_y]) / camera_height

        with open(self.json_location, 'w') as outfile:
            json.dump(self.machines_container, outfile, indent=4)

    def remove_machine(self):
        """
        Handles the removal of the machine from the list of machines
        """
        if self.machines_container[self.machines]:
            self.machines_container[self.machines].pop()

    def popup_msg(self):
        """
        Shows a drop down option menu for users to choose between a
        set list of possible machines.
        """
        popup = tk.Tk()
        popup.wm_title(self.pop_title)

        popup.geometry(self.popup_dimensions)

        variable = StringVar(popup)
        variable.set(self.OPTIONS[0])  # default value

        def get_machine():
            print("Machine name: " + variable.get())
            popup.destroy()
            return variable.get()

        w = OptionMenu(popup, variable, *self.OPTIONS)
        w.pack()

        button = Button(popup, text="OK",
                        command=get_machine)
        button.pack()

        popup.mainloop()
        return variable.get()

    def main(self):
        while True:
            img = self.camera.get_frame()
            img_temp = img

            if self.p1 and self.p2:
                cv2.rectangle(img_temp, self.p1, self.p2, self.annotation_colour, 2)

            for points in self.machines_container[self.machines]:
                cv2.rectangle(img_temp,
                              (points[self.top_x],
                               points[self.left_y]),
                              (points[self.bottom_x],
                               points[self.right_y]),
                              self.annotation_colour,
                              2)

                cv2.putText(img_temp,
                            points[self.name],
                            (points[self.top_x],
                             points[self.right_y] - 5),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1,
                            self.annotation_colour,
                            2,
                            cv2.LINE_AA)

            cv2.imshow('Cam View', img_temp)

            k = cv2.waitKey(1)  # & 0xFF

            if k == ord('r'):
                self.remove_machine()

            if k == 27 or k == ord('q'):
                break

        cv2.destroyAllWindows()
        self.write_json()
