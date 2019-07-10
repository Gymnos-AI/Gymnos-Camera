# Continuously capture frames and perform object detection on them
import cv2
import numpy as np

from gymnoscamera import Machine
from gymnoscamera import Predictors

# TODO: Fetch this from a json file, currently being mocked with this dict
CAMERA_MACHINES = {
    "Main Floor": [
        [0.1, 0.1, 0.3, 0.8, "Squat-Rack"],
        [0.75, 0.2, 0.95, 0.8, "Bench"]
    ]
}

CURRENT_LOCATION = "Main Floor"
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
        for station in CAMERA_MACHINES[CURRENT_LOCATION]:
            self.stations.append(Machine.Machine(station,
                                                 self.camera_width,
                                                 self.camera_height))

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

            image = np.asarray(image)
            cv2.imshow("Video Feed", image)

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
