import argparse
import logging
import os
from datetime import date
from os.path import expanduser
from typing import ClassVar

from gymnos_firestore import camera, gyms, machines, usage
from matchbox import database, models
from matchbox.queries.error import DocumentDoesNotExists

from gymnoscamera.cameras import CalibrateCam, camera_runner_factory

model_types = [
    'HOG',
    'YOLOV3',
    'YOLOV3RT'
]

log_location = expanduser("~") + '/logs/gymnos_camera'
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

    parser.add_argument('--configure', help='Configuring the camera',
                        action='store_true')
    parser.add_argument('--gym', help='Which gym to attempt to connect to',
                        action='store')
    parser.add_argument('--location', help='Which gym location to attempt to connect to',
                        action='store')
    parser.add_argument('--camera-name', help='Which camera to attempt to connect to',
                        action='store_true')
    parser.add_argument('--model-location', help='A file path to a model file',
                        action='store', required=True)
    parser.add_argument('--model-type', help='Choose from [HOG, YOLOV3, YOLOV3RT]',
                        action='store')
    parser.add_argument('--usbcam', help='Use a USB webcam instead of picamera',
                        action='store_true')
    parser.add_argument('--ipcam', help='Use an IP webcam',
                        action='store_true')
    parser.add_argument('--mac', help='Using a mac',
                        action='store_true')
    parser.add_argument('--headless', help='Run the algorithm without GUI',
                        action='store_true')
    parser.add_argument('--view-only', help='View camera without running algorithm',
                        action='store_true')
    parser.add_argument('--production', help='Uses production database',
                        action='store_true')

    return parser.parse_args()


def get_gym(gym_name: str = None, gym_location: str = None) -> gyms.Gyms:
    """
    Find a gym and optionally create a new one if one does not exist.

    :param gym_name:
    :param gym_location:
    :return:
    """
    if not gym_name:
        gym_name = input('Please enter the gym name: ')

    if not gym_location:
        gym_location = input('Please enter the gym location: ')

    try:
        gym = gyms.Gyms.objects.get(name=gym_name, location=gym_location)
    except DocumentDoesNotExists:
        response = input('Gym with name {} and location {} not found, do you want to create a new gym? (y/N): '
                         .format(gym_name, gym_location))
        if response == 'y':
            gym = gyms.Gyms()
            gym.name = gym_name
            gym.location = gym_location
            gym.save()
        else:
            raise

    return gym


def get_camera(camera_name: str = None) -> camera.Camera:
    if not camera_name:
        camera_name = input('Please enter the camera name/MAC address: ')

    try:
        camera_model = camera.Camera.objects.get(name=camera_name)
    except DocumentDoesNotExists:
        response = input('Camera with name {} not found, do you want to create a new camera? (y/N): '
                         .format(camera_name))
        if response == 'y':
            camera_model = camera.Camera()
            camera_model.name = camera_name
            camera_model.machine_id_list = list()
            camera_model.save()
        else:
            raise

    return camera_model


def main():
    """
    Runs the desired camera type for this device.

    When called with '--configure' option, will run a configuration mode different from run mode.

    :return:
    """

    args = parse_args()

    logging.info("Starting GymnosCamera with: " + str(args))

    # Initialize the database connection
    service_file = "serviceAccount.json"
    if args.production:
        service_file = "prod-serviceAccount.json"

    service_account = os.path.expanduser(os.path.join(os.path.dirname(__file__), service_file))
    database.db_initialization(service_account)

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

    # Get the gym
    gym = get_gym(args.gym, args.location)

    # Set sub-collections
    for model_class in [camera.Camera, machines.Machines, usage.Usage]:
        model_class.set_base_path(gym)

    camera_model = get_camera(args.camera_name)

    # Get the selected camera
    camera_device = camera_runner_factory.factory.get_camera_runner(camera_type, model_type, model_path)

    if args.headless:
        camera_device.set_headless()

    if args.view_only:
        camera_device.set_view_only()

    if args.configure:
        # TODO: Add option to read from gymnos_info.json file to retrieve machines locally instead of querying the DB.
        calibrate = CalibrateCam.CalibrateCam(camera_device, camera_model, args.mac)
        calibrate.main()
    else:
        camera_device.run_loop()


if __name__ == '__main__':
    main()
