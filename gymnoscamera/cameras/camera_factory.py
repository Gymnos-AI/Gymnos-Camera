class CameraFactory:
    """
    Returns an initialized implementation of a camera class, provided it has been registered.
    """

    def get_camera(self, camera_type: str, model_path: str):
        if camera_type == 'usb':
            from gymnoscamera.cameras.usb_camera_runner import UsbCameraRunner
            return UsbCameraRunner(model_path)
        elif camera_type == 'pi':
            from gymnoscamera.cameras.pi_camera_runner import PiCameraRunner
            return PiCameraRunner(model_path)
        else:
            raise ValueError(camera_type)


factory = CameraFactory()
