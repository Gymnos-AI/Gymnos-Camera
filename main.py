import os

camera_type = 'picamera'

# import the necessary packages
try:
    import gymnoscamera.PiCameraMain as piCam
except ImportError:
    print('No PiCamera available, setting as usb device')
    camera_type = 'usb'
    import gymnoscamera.UsbCameraMain as usbCam

import argparse

# Select camera type (if user enters --usbcam when calling this script,
# a USB webcam will be used)
parser = argparse.ArgumentParser()
parser.add_argument('--usbcam', help='Use a USB webcam instead of picamera',
                    action='store_true')
parser.add_argument('--model', help='A file path to a model file',
                    action='store', required=True)
args = parser.parse_args()
if args.usbcam:
    camera_type = 'usb'
model_path = os.path.abspath(args.model)

# Run loop of either PiCamera or USB
if camera_type == 'picamera':
    piCam = piCam.PiCameraMain(model_path)

    piCam.run_loop()
else:
    usbCam = usbCam.UsbCameraMain(model_path)
    usbCam.run_loop()
