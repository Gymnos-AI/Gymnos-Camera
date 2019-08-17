import json
import os
from abc import ABC
import time
import numpy as np

import cv2
from gymnos_firestore import machines

from gymnoscamera import machine, predictors

JSON_LOCATION = "../gym_info.json"
GYM_ID = "GymID"
MACHINES = "Machines"
MACHINE_ID = "MachineID"
MACHINE_NAME = "Name"
MACHINE_LOCATION = "Location"


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

    def set_stations(self):
        """
        Set the machine stations for this camera
        :return:
        """
        for station in self.get_configured_machines():
            self.stations.append(machine.Machine(station, self.camera_width, self.camera_height))

    def get_configured_machines(self):
        """
        Retrieves the machines from the JSON file and returns it
        as a list of machine models

        :return: stations: [machine model]
        """
        stations = []
        with open(os.path.join(os.path.dirname(__file__), JSON_LOCATION)) as json_file:
            data = json.load(json_file)
            for machine_data in data[MACHINES]:
                machine_model = machines.Machines()
                machine_model.id = machine_data['id']
                machine_model.machine_id = machine_data['machine_id']
                machine_model.name = machine_data['name']
                machine_model.location = machine_data['location']

                stations.append(machine_model)

        return stations

    def get_dimensions(self):
        """
        Returns width and height of the camera

        :return: (width, height)
        """
        return self.camera_width, self.camera_height

    def run_loop(self):
        """
        This main loop tracks machine usage
        """
        # initialize the Widgets
        self.set_stations()
        while True:
            # Retrieve a frame and timestamp it
            image = self.get_frame()
            frame_cap_time = self.get_time()

            # Draw machines and users
            self.draw_machines(image)
            people_coords = self.draw_people(image)

            # Calculate station usage
            for station in self.stations:
                station.increment_machine_time(people_coords, frame_cap_time)

            image = np.asarray(image)
            cv2.imshow("Video Feed", image)

            # Press 'q' to quit
            if cv2.waitKey(1) == ord('q'):
                break

    def get_time(self):
        """
        Retrieves the time in seconds since epoch
        """
        return int(time.time())

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
