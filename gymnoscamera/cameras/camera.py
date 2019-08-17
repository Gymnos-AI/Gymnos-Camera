import json
import os
from abc import ABC
import time

import cv2

from gymnoscamera import machine, predictors

JSON_LOCATION = "../gym_info.json"
GYM_ID = "GymID"
MACHINES = "Machines"
MACHINE_ID = "MachineID"
MACHINE_OPEN = "Open"
MACHINE_NAME = "Name"
MACHINE_LOCATION = "Location"
TOP_X = "TopX"
LEFT_Y = "LeftY"
BOTTOM_X = "BottomX"
RIGHT_Y = "RightY"


class Camera(ABC):

    def __init__(self, db, model_type, model_path: str):
        """
        Initialize the camera, predictor and stations
        :param model_path:
        """
        self.db = db

        self.headless_mode = False

        self.view_only = False

        # initialize general camera params
        self.camera_height = 256
        self.camera_width = 256

        # initialize the Predictor
        self.predictor = predictors.Predictors(model_type, model_path)

        # initialize stations
        self.stations = []
        self.set_stations()


    def set_stations(self):
        for station in self.get_stations():
            self.stations.append(machine.Machine(self.db, station,
                                                 self.camera_width,
                                                 self.camera_height))

    def get_stations(self):
        """
        Retrieves the machines from the JSON file and returns it
        as a list

        :return: stations: [[name, topX, leftY, bottomX, rightY]]
        """
        stations = []
        with open(os.path.join(os.path.dirname(__file__), JSON_LOCATION)) as json_file:
            data = json.load(json_file)
            gym_id = data[GYM_ID]
            for machine in data[MACHINES]:
                locations = machine[MACHINE_LOCATION]
                machine_id = machine[MACHINE_ID]
                stations.append([gym_id,
                                 machine_id,
                                 machine[MACHINE_NAME],
                                 locations[TOP_X],
                                 locations[LEFT_Y],
                                 locations[BOTTOM_X],
                                 locations[RIGHT_Y]])

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
        while True:
            # Retrieve a frame and timestamp it
            image, frame_cap_time = self.get_frame()

            # Draw machines and users
            self.draw_machines(image)
            if not self.view_only:
                people_coords = self.draw_people(image)

                # Calculate station usage
                for station in self.stations:
                    station.increment_machine_time(people_coords, image, frame_cap_time)

            if not self.headless_mode:
                cv2.imshow("Video Feed", image)

                # Press 'q' to quit
                if cv2.waitKey(1) == ord('q'):
                    break

    def set_view_only(self):
        print("Setting to View only")
        self.view_only = True
        for station in self.stations:
            station.watch_machine_status()

    def set_head_less(self):
        print("Setting Headless Mode on")
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
        list_of_coords = self.predictor.run_prediction(image)
        for (topX, leftY, bottomX, rightY) in list_of_coords:
            cv2.rectangle(image, (topX, leftY), (bottomX, rightY), (0, 0, 255), 2)

        return list_of_coords

    def draw_machines(self, image):
        """
        Draws bounding boxes around each station
        """
        for station in self.stations:
            station.draw_machine(image)
