# Continuously capture frames and perform object detection on them
import cv2
import numpy as np
import json
import tkinter
import gymnoscamera.Widgets.frame_timer as frame_timer

from gymnoscamera import Machine
from gymnoscamera import Predictors

iou_threshold = 0.01
time_threshold = 2  # how many seconds until machine is sure you are in or out


class UsbCameraMain:
    def __init__(self, model_path: str):
        # initialize the camera
        self.camera = cv2.VideoCapture(0)
        self.camera_height = 256
        self.camera_width = 256

        # initialize the Predictor
        self.predictor = Predictors.Predictors('YOLOV3', model_path)

        # initialize stations
        self.stations = []
        for station in self.get_stations():
            self.stations.append(Machine.Machine(station,
                                                 self.camera_width,
                                                 self.camera_height))

        # initialize the Widgets
        self.root = tkinter.Tk()
        self.ft = frame_timer.frameTimers(self.root)
        #self.root.update()

    def get_stations(self):
        """
        Retrieves the machines from the JSON file and returns it
        as a list

        :return: stations: [[name, topX, leftY, bottomX, rightY]]
        """
        json_file_location = "./gymnoscamera/Machines.json"
        machine_key = "machines"
        machine_name_key = "name"
        topX_key = "topX"
        leftY_key = "leftY"
        bottomX_key = "bottomX"
        rightY_key = "rightY"

        stations = []
        with open(json_file_location) as json_file:
            data = json.load(json_file)
            for machine in data[machine_key]:
                stations.append([machine[machine_name_key],
                                 machine[topX_key],
                                 machine[leftY_key],
                                 machine[bottomX_key],
                                 machine[rightY_key]])

        return stations

    def run_loop(self):
        """
        This main loop will grab frames the camera and print it onto the screen
        """
        while True:
            # Retrieve frame from camera
            ret, image = self.camera.read()
            image = cv2.resize(image, (self.camera_height, self.camera_width))

            # Draw machines and users
            self.draw_machines(image)
            people_coords = self.draw_people(image)

            # Calculate station usage
            for station in self.stations:
                for person in people_coords:
                    # If there is somebody standing in a station
                    station.increment_machine_time(person, image)
                if(station.name == "squat_rack"):
                    self.ft.squatTime(station.time_used)
                elif(station.name == "bench"):
                    self.ft.benchTime(station.time_used)

            image = np.asarray(image)
            cv2.imshow("Video Feed", image)
            self.root.update()


            # Press 'q' to quit
            if cv2.waitKey(1) == ord('q'):
                break

    def draw_people(self, image):
        list_of_coords = self.predictor.yolo_v3_detector(image)
        for (topX, leftY, bottomX, rightY) in list_of_coords:
            cv2.rectangle(image, (topX, leftY), (bottomX, rightY), (0, 0, 255), 2)

        return list_of_coords

    def draw_machines(self, image):
        # Calculate station usage
        for station in self.stations:
            station.draw_machine(image)
