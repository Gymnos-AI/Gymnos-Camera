import json
import os
import tkinter
from abc import ABC

import cv2

from gymnoscamera import machine, predictors
from gymnoscamera.Widgets import frame_timer


class Camera(ABC):

    def __init__(self, model_path: str):
        """
        Initialize the camera, predictor and stations
        :param model_path:
        """
        # initialize general camera params
        self.camera_height = 256
        self.camera_width = 256

        # initialize the Predictor
        self.predictor = predictors.Predictors('YOLOV3', model_path)

        # initialize stations
        self.stations = []
        for station in self.get_stations():
            self.stations.append(machine.Machine(station,
                                                 self.camera_width,
                                                 self.camera_height))
        # initialize the Widgets
        self.root = tkinter.Tk()
        self.ft = frame_timer.frameTimers(self.root)

    def get_stations(self):
        """
        Retrieves the machines from the JSON file and returns it
        as a list

        :return: stations: [[name, topX, leftY, bottomX, rightY]]
        """
        json_file_location = "../Machines.json"
        machine_key = "machines"
        machine_name_key = "name"
        top_x_key = "topX"
        left_y_key = "leftY"
        bottom_x_key = "bottomX"
        right_y_key = "rightY"

        stations = []
        with open(os.path.join(os.path.dirname(__file__), json_file_location)) as json_file:
            data = json.load(json_file)
            for machine in data[machine_key]:
                stations.append([machine[machine_name_key],
                                 machine[top_x_key],
                                 machine[left_y_key],
                                 machine[bottom_x_key],
                                 machine[right_y_key]])

        return stations

    def run_loop(self):
        """
        This main loop will grab frames the camera and print it onto the screen
        """
        pass

    def draw_people(self, image):
        list_of_coords = self.predictor.yolo_v3_detector(image)
        for (topX, leftY, bottomX, rightY) in list_of_coords:
            cv2.rectangle(image, (topX, leftY), (bottomX, rightY), (0, 0, 255), 2)

        return list_of_coords

    def draw_machines(self, image):
        # Calculate station usage
        for station in self.stations:
            station.draw_machine(image)
