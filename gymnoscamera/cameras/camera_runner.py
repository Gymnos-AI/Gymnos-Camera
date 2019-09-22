import json
import logging
import os
import time
from abc import ABC

import cv2
from gymnos_firestore import machines
from gymnos_firestore.machines import MACHINE_COLLECTION

from gymnoscamera import machine, predictors

JSON_LOCATION = "../gym_info.json"


class CameraRunner(ABC):

    def __init__(self, model_type: str, model_path: str):
        """
        Initialize the camera, predictor and stations
        :param model_path:
        """
        self.headless_mode = False
        self.view_only = False

        # initialize general camera params
        self.camera_height = 256
        self.camera_width = 256

        self.check_in_period = 60

        # initialize the Predictor
        self.predictor = predictors.Predictors(model_type, model_path)

        # initialize stations
        self.stations = []
        self.set_stations()

    def set_stations(self):
        """
        Set the machine stations for this camera
        :return:
        """
        for station in self.get_configured_machines():
            self.stations.append(machine.Machine(station, self.camera_width, self.camera_height))
        logging.info("Stations used: " + str(self.get_configured_machines()))

    def get_configured_machines(self):
        """
        Retrieves the machines from the JSON file and returns it
        as a list of machine models

        :return: stations: [machine model]
        """

        stations = []
        with open(os.path.join(os.path.dirname(__file__), JSON_LOCATION)) as json_file:
            data = json.load(json_file)
            for machine_data in data[MACHINE_COLLECTION]:
                machine_model = machines.Machines()
                machine_model.id = machine_data['id']
                machine_model.name = machine_data[machines.MACHINE_NAME]
                machine_model.location = machine_data[machines.MACHINE_LOC]

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
        draw_people = self.draw_people
        draw_machines = self.draw_machines
        get_frame = self.get_frame
        show_feed = cv2.imshow

        while True:
            # Retrieve a frame and timestamp it
            image, frame_cap_time = get_frame()

            if int(frame_cap_time) % self.check_in_period == 0:
                logging.info("Camera checking in")

            if not self.view_only:
                people_coords = draw_people(image)

                # Calculate station usage
                for station in self.stations:
                    station.increment_machine_time(people_coords, frame_cap_time)

            draw_machines(image)

            if not self.headless_mode:
                show_feed("Video Feed", image)

                # Press 'q' to quit
                if cv2.waitKey(1) == ord('q'):
                    break

    def set_view_only(self):
        logging.info("Setting view only mode")
        self.view_only = True
        for station in self.stations:
            station.watch_machine_status()

    def set_headless(self):
        logging.info("Setting headless mode")
        self.headless_mode = True

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
        rectanglefy = cv2.rectangle
        list_of_coords = self.predictor.run_prediction(image)
        for (topX, leftY, bottomX, rightY) in list_of_coords:
            rectanglefy(image, (topX, leftY), (bottomX, rightY), (0, 0, 255), 2)

        return list_of_coords

    def draw_machines(self, image):
        """
        Draws bounding boxes around each station
        """
        for station in self.stations:
            station.draw_machine(image)
