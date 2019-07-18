import cv2
import numpy as np

from gymnoscamera.cameras.camera import Camera

iou_threshold = 0.01
time_threshold = 2  # how many seconds until machine is sure you are in or out


class UsbCameraRunner(Camera):
    """
    An implementation of a Camera runner which sources its camera from a USB camera
    """
    def __init__(self, model_path: str):
        super().__init__(model_path)

        # initialize the camera
        self.camera = cv2.VideoCapture(0)

    def run_loop(self):
        """
        This main loop will grab frames from the camera and print it onto the screen
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
                    station.increment_machine_time(person, image, self.ft)

            image = np.asarray(image)
            cv2.imshow("Video Feed", image)
            self.root.update()

            # Press 'q' to quit
            if cv2.waitKey(1) == ord('q'):
                break
