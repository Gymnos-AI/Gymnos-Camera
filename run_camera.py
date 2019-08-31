import argparse
import os
import logging
from datetime import date
from os.path import expanduser

from gymnos_firestore import gyms, machines, usage
from matchbox import database
from matchbox.queries.error import DocumentDoesNotExists

from gymnoscamera.cameras import camera_factory
from gymnoscamera.cameras import CalibrateCam

# Initialize orm
database.db_initialization('./serviceAccount.json')

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

    return parser.parse_args()


def get_gym(gym_name: str = None, gym_location: str = None) -> gyms.Gyms:

    if not gym_name:
        gym_name = input('Please enter the gym name: ')

    if not gym_location:
        gym_location = input('Please enter the gym location: ')

    try:
        gym = gyms.Gyms.objects.get(name=gym_name, location=gym_location)
    except DocumentDoesNotExists as e:
        response = input('Gym not found, do you want to create a new gym? (y/N): ')
        if response == 'y':
            gym = gyms.Gyms.objects.create(name=gym_name, location=gym_location)
        else:
            raise DocumentDoesNotExists(e)

    if not gym:
        raise ValueError("Could not find a gym with name '{}' and location '{}'".format(gym_name, gym_location))

    return gym


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

    # Get the gym
    gym = get_gym(args.gym, args.location)

    # Hack to select the correct collection names
    # noinspection PyProtectedMember
    machines.Machines._meta.collection_name = "{}/{}/{}".format(
        gyms.Gyms.collection_name(), gym.id, machines.Machines.collection_name())
    # noinspection PyProtectedMember
    usage.Usage._meta.collection_name = "{}/{}/{}".format(
        gyms.Gyms.collection_name(), gym.id, usage.Usage.collection_name())

    # Get the selected camera
    camera = camera_factory.factory.get_camera(camera_type, model_type, model_path)

    if args.headless:
        camera.set_headless()

    if args.view_only:
        camera.set_view_only()

    if args.configure:
        # TODO: Add option to read from gymnos_info.json file to retrieve machines locally instead of querying the DB.
        calibrate = CalibrateCam.CalibrateCam(camera, args.mac)
        calibrate.main()
    else:
        camera.run_loop()


if __name__ == '__main__':
    main()
