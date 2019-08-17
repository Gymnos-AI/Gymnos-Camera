import argparse
import os

from gymnoscamera.cameras import camera_factory
from gymnoscamera.cameras import CalibrateCam

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Initialize the database connection
# Use a service account to connect to the databse
cred = credentials.Certificate('./serviceAccount.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

model_types = [
    'HOG',
    'YOLOV3',
    'YOLOV3RT'
]


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('model_type', help='Choose from [HOG, YOLOV3, YOLOV3RT]',
                        action='store')
    parser.add_argument('--configure', help='Configure Machine locations',
                        action='store_true')
    parser.add_argument('--model_location', help='A file path to a model file',
                        action='store', required=True)
    parser.add_argument('--usbcam', help='Use a USB webcam instead of picamera',
                        action='store_true')
    parser.add_argument('--ipcam', help='Use an IP webcam',
                        action='store_true')
    parser.add_argument('--mac', help='Using a mac',
                        action='store_true')
    parser.add_argument('--headless', help='Run the algorithm without GUI',
                        action='store_true')

    return parser.parse_args()


def main():
    """
    Runs the desired camera type for this device.

    When called with '--configure' option, will run a configuration mode different from run mode.

    :return:
    """
    args = parse_args()

    headless_mode = False
    if args.headless:
        headless_mode = True

    if args.usbcam:
        camera_type = 'usb'
    elif args.ipcam:
        camera_type = 'ip'
    else:
        camera_type = 'pi'

    model_type = args.model_type
    if model_type not in model_types:
        raise ValueError('Use one of the following Model types: ' + str(model_types))

    model_path = os.path.abspath(args.model_location)

    # Get the selected camera
    camera = camera_factory.factory.get_camera(db, camera_type, model_type, model_path, headless_mode)

    if args.configure:
        calibrate = CalibrateCam.CalibrateCam(db, camera, args.mac)
        calibrate.main()
    else:
        camera.run_loop()


if __name__ == '__main__':
    main()
