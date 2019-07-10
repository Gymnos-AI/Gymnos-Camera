# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import time
from gymnoscamera import Predictors


class PiCameraMain:
    def __init__(self, model_path: str):
        # initialize the HOG descriptor/person detector
        self.IM_WIDTH = 128
        self.IM_HEIGHT = 128
        self.camera = PiCamera()
        self.rawCapture = PiRGBArray(self.camera, size=(self.IM_WIDTH, self.IM_HEIGHT))
        self.camera.resolution = (self.IM_WIDTH, self.IM_HEIGHT)
        self.camera.framerate = 32

        # allow the camera to warm up
        time.sleep(0.1)

        # initialize the Predictors
        self.predictor = Predictors.Predictors('YOLOV3', model_path)

    def run_loop(self):
        """
        This main loop will grab frames the camera and print it onto the screen
        """
        # capture frames from the camera
        for frame in self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True):
            # Retrieve frame as numpy array
            image = frame.array

            # Pass frame into the model
            list_of_coords = self.predictor.yolo_v3_detector(image)
            for (topX, leftY, bottomX, rightY) in list_of_coords:
                cv2.rectangle(image, (topX, leftY), (bottomX, rightY), (0, 0, 255), 2)

            # show the output images
            cv2.imshow("Video Feed", image)

            # clear the stream in preparation for the next frame
            self.rawCapture.truncate(0)

            # Press 'q' to quit
            if cv2.waitKey(1) == ord('q'):
                break
