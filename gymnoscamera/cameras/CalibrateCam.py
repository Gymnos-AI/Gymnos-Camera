# Python program to extract rectangular
# Shape using OpenCV and tkinter in Python3
import cv2
import json
from tkinter import *
import tkinter as tk
import gymnos_firestore.Machines as machines_db

# Constants
# Keys to accessing and storing into the Json File
GYM_ID = "GymID"
MACHINES = "Machines"
MACHINE_ID = "MachineID"
MACHINE_NAME = "Name"
MACHINE_LOCATION = "Location"
TOP_X = "TopX"
LEFT_Y = "LeftY"
BOTTOM_X = "BottomX"
RIGHT_Y = "RightY"

# Popup constants
JSON_LOCATION = "./gymnoscamera/gym_info.json"
POPUP_TITLE = "Options"
POPUP_DIMENSIONS = "100x100"
ANNOTATION_COLOUR = (0, 255, 0)  # RGB
OPTIONS = [
    "bench",
    "squat_rack"
]


class CalibrateCam:
    def __init__(self, db, camera, using_mac):
        self.using_mac = using_mac
        self.camera = camera
        self.db = db
        self.drawing = False
        self.machines_container = {MACHINES: []}
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

                self.machines_container[MACHINES].append(
                    {MACHINE_NAME: machine_name,
                     MACHINE_ID: "",
                     MACHINE_LOCATION: {
                         TOP_X: self.p1[0],
                         LEFT_Y: self.p1[1],
                         BOTTOM_X: self.p2[0],
                         RIGHT_Y: self.p2[1]}
                     })

        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing is True:
                self.p2 = (x, y)

    def write_json(self):
        """
        Writes machine locations that the user chose into the json file
        """
        with open(JSON_LOCATION, 'r') as gym_info:
            gym_dict = json.load(gym_info)

        """
        First convert all raw pixel values into their ratios
        this helps with dealing with variable sizing. We will
        also create new entry's of machines in the database
        """
        camera_width, camera_height = self.camera.get_dimensions()
        for machine in self.machines_container[MACHINES]:
            points = machine[MACHINE_LOCATION]
            points[TOP_X] = int(points[TOP_X]) / camera_width
            points[LEFT_Y] = int(points[LEFT_Y]) / camera_height
            points[BOTTOM_X] = int(points[BOTTOM_X]) / camera_width
            points[RIGHT_Y] = int(points[RIGHT_Y]) / camera_height

            # Create Machine document in the database
            result, machine_id = machines_db.create_machine(self.db, gym_dict[GYM_ID], machine)
            machine[MACHINE_ID] = machine_id
            """
            Result is false because machine already exists in database.
            Update database with the new co-ordinates of machine
            """
            if result is False:
                machines_db.update_machine_location(self.db, gym_dict[GYM_ID], machine_id, points)

        with open(JSON_LOCATION, 'w') as outfile:
            gym_dict[MACHINES] = self.machines_container[MACHINES]
            json.dump(gym_dict, outfile, indent=4)

    def remove_machine(self):
        """
        Handles the removal of the machine from the list of machines
        """
        if self.machines_container[MACHINES]:
            self.machines_container[MACHINES].pop()

    def popup_msg(self):
        """
        Shows a drop down option menu for users to choose between a
        set list of possible machines.
        """
        popup = tk.Tk()
        popup.wm_title(POPUP_TITLE)

        popup.geometry(POPUP_DIMENSIONS)

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
        while True:
            img = self.camera.get_frame()
            img_temp = img

            if self.p1 and self.p2:
                cv2.rectangle(img_temp, self.p1, self.p2, ANNOTATION_COLOUR, 2)

            machines = self.machines_container[MACHINES]
            for machine in machines:
                points = machine[MACHINE_LOCATION]
                cv2.rectangle(img_temp,
                              (points[TOP_X],
                               points[LEFT_Y]),
                              (points[BOTTOM_X],
                               points[RIGHT_Y]),
                              ANNOTATION_COLOUR,
                              2)

                cv2.putText(img_temp,
                            machine[MACHINE_NAME],
                            (points[TOP_X],
                             points[RIGHT_Y] - 5),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1,
                            ANNOTATION_COLOUR,
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
