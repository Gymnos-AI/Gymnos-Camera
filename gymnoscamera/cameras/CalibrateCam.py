# Python program to extract rectangular
# Shape using OpenCV and tkinter in Python3
import json
import tkinter as tk
from tkinter import *

import cv2
# Constants
# Keys to accessing and storing into the Json File
from gymnos_firestore import machines
from gymnos_firestore.machines import MACHINE_LOC_TOPX, MACHINE_LOC_LEFTY, MACHINE_LOC_BOTTOMX, MACHINE_LOC_RIGHTY, \
    MACHINE_COLLECTION

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
    """This class runs the configuration app which allows for machine modification"""
    def __init__(self, camera, using_mac):
        self.camera = camera
        self.using_mac = using_mac
        self.drawing = False

        # Get current machines from db
        # TODO: This should be a specific query for machines controlled by this camera
        machines_list = list(machines.Machines.objects.all().execute())
        self.machines_container = [
            (machine, self.convert_scaled_to_absolute(machine.location, self.camera.get_dimensions()))
            for machine in machines_list
        ]
        self.new_machines_idx_list = []
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
                    print("GUI not supported on Mac, please enter machine name through command line.")
                    print("Press Q when finished")
                    machine_name = input("Machine name: ")
                else:
                    machine_name = self.popup_msg()

                raw_location = {
                    MACHINE_LOC_TOPX: self.p1[0],
                    MACHINE_LOC_LEFTY: self.p1[1],
                    MACHINE_LOC_BOTTOMX: self.p2[0],
                    MACHINE_LOC_RIGHTY: self.p2[1]
                }
                scaled_location = self.convert_absolute_to_scaled(raw_location, self.camera.get_dimensions())

                # Update location if newly drawn machine has same name as an existing machine
                updating_existing_machine = False
                for i, machine_tuple in enumerate(self.machines_container):
                    machine_model, _ = machine_tuple
                    if machine_name == machine_model.name:
                        updating_existing_machine = True
                        machine_model.location = scaled_location
                        self.machines_container[i] = (machine_model, raw_location)
                        break
                # Otherwise, create a new machine
                if not updating_existing_machine:
                    self.machines_container.append((
                        machines.Machines(
                            name=machine_name,
                            location=scaled_location
                        ), raw_location
                    ))

        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing is True:
                self.p2 = (x, y)

    def convert_scaled_to_absolute(self, points: dict, camera_dimensions: tuple) -> dict:
        """
        Converts points from scaled values (0-1) to absolute pixel values. Creates a new dict.
        :param points:
        :param camera_dimensions:
        :return: Absolute points data
        """
        (camera_width, camera_height) = camera_dimensions
        new_points = dict()
        new_points[MACHINE_LOC_TOPX] = int(points[MACHINE_LOC_TOPX] * camera_width)
        new_points[MACHINE_LOC_LEFTY] = int(points[MACHINE_LOC_LEFTY] * camera_height)
        new_points[MACHINE_LOC_BOTTOMX] = int(points[MACHINE_LOC_BOTTOMX] * camera_width)
        new_points[MACHINE_LOC_RIGHTY] = int(points[MACHINE_LOC_RIGHTY] * camera_height)
        return new_points

    def convert_absolute_to_scaled(self, points: dict, camera_dimensions: tuple) -> dict:
        """
        Converts points from absolute pixel values to scaled values (0-1). Creates a new dict.
        :param points:
        :param camera_dimensions:
        :return: Scaled points data
        """
        (camera_width, camera_height) = camera_dimensions
        new_points = dict()
        new_points[MACHINE_LOC_TOPX] = int(points[MACHINE_LOC_TOPX]) / camera_width
        new_points[MACHINE_LOC_LEFTY] = int(points[MACHINE_LOC_LEFTY]) / camera_height
        new_points[MACHINE_LOC_BOTTOMX] = int(points[MACHINE_LOC_BOTTOMX]) / camera_width
        new_points[MACHINE_LOC_RIGHTY] = int(points[MACHINE_LOC_RIGHTY]) / camera_height
        return new_points

    def write_json(self):
        """
        Writes machine locations that the user chose into the json file. Also saves existing machines to the DB.
        """
        with open(JSON_LOCATION, 'r') as gym_info:
            gym_dict = json.load(gym_info)

        """
        First convert all raw pixel values into their ratios
        this helps with dealing with variable sizing. We will
        also create new entry's of machines in the database
        """
        for machine, raw_location in self.machines_container:
            # Update Machines document in the Database
            machine.save()

        with open(JSON_LOCATION, 'w') as outfile:
            gym_dict[MACHINE_COLLECTION] = [machine.get_fields() for machine, _ in self.machines_container]
            json.dump(gym_dict, outfile, indent=4)

    def remove_machine(self):
        """
        Handles the removal of the machine from the list of machines
        """
        if self.machines_container:
            self.machines_container.pop()

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
            img, _ = self.camera.get_frame()
            img_temp = img

            if self.p1 and self.p2:
                cv2.rectangle(img_temp, self.p1, self.p2, ANNOTATION_COLOUR, 2)

            for machine, raw_location in self.machines_container:
                points = raw_location
                cv2.rectangle(img_temp,
                              (points[MACHINE_LOC_TOPX],
                               points[MACHINE_LOC_LEFTY]),
                              (points[MACHINE_LOC_BOTTOMX],
                               points[MACHINE_LOC_RIGHTY]),
                              ANNOTATION_COLOUR,
                              2)

                cv2.putText(img_temp,
                            machine.name,
                            (points[MACHINE_LOC_TOPX],
                             points[MACHINE_LOC_RIGHTY] - 5),
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
