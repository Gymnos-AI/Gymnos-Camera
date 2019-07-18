import argparse
import os

from gymnoscamera.cameras import camera_factory


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--configure', help='If true',
                        action='store_true')
    parser.add_argument('--model', help='A file path to a model file',
                        action='store', required=True)
    parser.add_argument('--usbcam', help='Use a USB webcam instead of picamera',
                        action='store_true')

    return parser.parse_args()


def main():
    """
    Runs the desired camera type for this device.

    When called with '--configure' option, will run a configuration mode different from run mode.

    :return:
    """
    args = parse_args()

    camera_type = 'pi'
    if args.usbcam:
        camera_type = 'usb'
    model_path = os.path.abspath(args.model)

    # Get the selected camera
    camera = camera_factory.factory.get_camera(camera_type, model_path)

    if args.configure:
        raise ValueError('configure not implemented')
    else:
        camera.run_loop()


if __name__ == '__main__':
    main()
