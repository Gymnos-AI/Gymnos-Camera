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


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--configure', help='If true',
                        action='store_true')
    parser.add_argument('--model', help='A file path to a model file',
                        action='store', required=True)
    parser.add_argument('--usbcam', help='Use a USB webcam instead of picamera',
                        action='store_true')
    parser.add_argument('--mac', help='Using a mac',
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
    camera = camera_factory.factory.get_camera(db, camera_type, model_path)

    if args.configure:
        calibrate = CalibrateCam.CalibrateCam(db, camera, args.mac)
        calibrate.main()
    else:
        camera.run_loop()


if __name__ == '__main__':
    main()
