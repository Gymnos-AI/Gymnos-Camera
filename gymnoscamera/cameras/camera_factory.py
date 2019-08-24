class CameraFactory:
    """
    Returns an initialized implementation of a camera class, provided it has been registered.
    """

    def get_camera(self, db, camera_type: str, model_type: str, model_path: str):
        if camera_type == 'usb':
            from gymnoscamera.cameras.usb_camera_runner import UsbCameraRunner
            return UsbCameraRunner(db, model_type, model_path)
        elif camera_type == 'pi':
            from gymnoscamera.cameras.pi_camera_runner import PiCameraRunner
            return PiCameraRunner(db, model_type, model_path)
        elif camera_type == 'ip':
            from gymnoscamera.cameras.ip_camera_runner import IpCameraRunner
            return IpCameraRunner(db, model_type, model_path)
        else:
            raise ValueError(camera_type)


factory = CameraFactory()
