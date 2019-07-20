import json
import os
import tkinter
from abc import ABC
import time
import numpy as np

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
        This main loop tracks machine usage
        """
        # initialize the Widgets
        root = tkinter.Tk()
        ft = frame_timer.frameTimers(root)
        while True:
            # Retrieve a frame and timestamp it
            image = self.get_frame()
            frame_cap_time = self.get_time()

            # Draw machines and users
            self.draw_machines(image)
            people_coords = self.draw_people(image)

            # Calculate station usage
            for station in self.stations:
                station.increment_machine_time(people_coords, image, frame_cap_time, ft)

            image = np.asarray(image)
            cv2.imshow("Video Feed", image)
            root.update()

            # Press 'q' to quit
            if cv2.waitKey(1) == ord('q'):
                break

    def get_time(self):
        """
        Retrieves the time in seconds since epoch
        """
        return time.time()

    def get_frame(self):
        """
        Retrieves a frames from the camera and returns it
        """
        pass

    def draw_people(self, image):
        """
        Draws bounding boxes around each person located

        :param image: frame we will run predictions on
        :return: list of the coordinates of each person our model detects
        """
        list_of_coords = self.predictor.yolo_v3_detector(image)
        for (topX, leftY, bottomX, rightY) in list_of_coords:
            cv2.rectangle(image, (topX, leftY), (bottomX, rightY), (0, 0, 255), 2)

        return list_of_coords

    def draw_machines(self, image):
        """
        Draws bounding boxes around each station
        """
        for station in self.stations:
            station.draw_machine(image)