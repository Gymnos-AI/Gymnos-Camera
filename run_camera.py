import argparse
import os
import logging
from datetime import date
from os.path import expanduser

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

log_location = expanduser("~") + '/tmp/gymnos_camera'
try:
    os.makedirs(log_location)
except OSError:
    print("Creation of the directory %s failed" % log_location)
else:
    print("Successfully created the directory %s " % log_location)

today = date.today()
file_name = '{}/{}.log'.format(log_location, today)
logging.basicConfig(format='%(asctime)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S',
                    filename=file_name,
                    level=logging.INFO)


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
    parser.add_argument('--view_only', help='View camera without running algorithm',
                        action='store_true')

    return parser.parse_args()


def main():
    """
    Runs the desired camera type for this device.

    When called with '--configure' option, will run a configuration mode different from run mode.

    :return:
    """

    args = parse_args()
    logging.info("Starting GymnosCamera with: " + str(args))

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
    camera = camera_factory.factory.get_camera(db, camera_type, model_type, model_path)

    if args.headless:
        camera.set_head_less()

    if args.view_only:
        camera.set_view_only()

    if args.configure:
        calibrate = CalibrateCam.CalibrateCam(db, camera, args.mac)
        calibrate.main()
    else:
        camera.run_loop()


if __name__ == '__main__':
    main()
