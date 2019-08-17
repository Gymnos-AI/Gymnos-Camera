import argparse
import os

from gymnos_firestore import gyms, machines, usage
from matchbox import database

from gymnoscamera.cameras import camera_factory
from gymnoscamera.cameras import CalibrateCam

# Initialize orm
database.db_initialization('./serviceAccount.json')


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--configure', help='Configuring the camera',
                        action='store_true')
    parser.add_argument('--gym', help='Which gym to attempt to connect to',
                        action='store')
    parser.add_argument('--location', help='Which gym location to attempt to connect to',
                        action='store')
    parser.add_argument('--mac', help='Using a mac',
                        action='store_true')
    parser.add_argument('--model', help='A file path to a model file',
                        action='store', required=True)
    parser.add_argument('--usbcam', help='Use a USB webcam instead of picamera',
                        action='store_true')

    return parser.parse_args()


def get_gym(gym_name: str = None, gym_location: str = None) -> gyms.Gyms:

    if not gym_name:
        gym_name = input('Please enter the gym name: ')

    if not gym_location:
        gym_location = input('Please enter the gym location: ')

    gym = gyms.Gyms.objects.get(Name=gym_name, Location=gym_location)

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

    camera_type = 'pi'
    if args.usbcam:
        camera_type = 'usb'
    model_path = os.path.abspath(args.model)

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
    camera = camera_factory.factory.get_camera(camera_type, model_path)

    if args.configure:
        # TODO: Add option to read from gymnos_info.json file to retrieve machines locally instead of querying the DB.
        calibrate = CalibrateCam.CalibrateCam(camera, args.mac)
        calibrate.main()
    else:
        camera.run_loop()


if __name__ == '__main__':
    main()
