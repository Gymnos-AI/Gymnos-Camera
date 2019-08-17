import time

from picamera import PiCamera
from picamera.array import PiRGBArray

from gymnoscamera.cameras.camera import Camera


class PiCameraRunner(Camera):
    """
    An implementation of a Camera runner which sources its camera from a Pi Camera
    """
    def __init__(self, db, model_type: str, model_path: str, headless_mode):
        super().__init__(db, model_type, model_path, headless_mode)

        # initialize the HOG descriptor/person detector
        self.camera = PiCamera()
        self.rawCapture = PiRGBArray(self.camera, size=(self.camera_width, self.camera_height))
        self.camera.resolution = (self.camera_width, self.camera_height)
        self.camera.framerate = 32

        time.sleep(0.1)  # allow the camera to warm up

    def get_frame(self):
        """
        Retrieves a frames from the camera and returns it
        """
        frame = self.camera.capture(self.rawCapture, format="bgr", use_video_port=True)
        image = frame.array

        return image, time.time()
