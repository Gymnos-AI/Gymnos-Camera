# GymnosCamera

Library for camera and predictions

## Setup
1. Add the serviceAccount.json into the root directory. This file will give this client access to the database. Link: https://drive.google.com/drive/u/0/folders/1HuFFFOWCW10DOTLfIKfUGBdGEdzQYOiP
2. Add the gym_info.json file in ./gymnoscamera. This file stores all information about your gym and it's machines. 
It is also used by the client to access the database. Link: https://drive.google.com/drive/u/0/folders/1HuFFFOWCW10DOTLfIKfUGBdGEdzQYOiP
3. Add the yolo.h5 to the root directory. This file will load the AI during runtime. Link: https://drive.google.com/drive/u/0/folders/1fibgr4c2CUMItWOngjTxwhqSzsHXBXvT
4. pip install -r requirements.txt

### Running

To run this library standalone:

Possible run options:
```
model_type = 
--configure = To configure machines info in gym_info.json
--model_location = Path to Yolo model from your working directory
--usbcam = If you are running this library on Laptop or USB camera
--ipcam = If you want to connect to the Security Camera
--mac = If you are running this library on a mac
--headless = Run without GUI
```
1. Run the camera with the --configure parameter to initialize the Machines array
    ```
    python3 run_camera.py model_type --model_location yolo.h5 --usb --configure
    ```
2. Run the library
    ```
    python3 run_camera.py model_type --model_location yolo.h5 --usbcam
    ```

### Installation

To install this library with local changes:

```bash
pip install -e .
```
or (if you are in a different directory)
```bash
pip install -e path/to/GymnosCamera
```
or if you want the distribution from the server
```
pip install --trusted-host thefirstjedi.asuscomm.com --index-url http://thefirstjedi.asuscomm.com:3141/gymnos/staging/+simple distribution==version
```

To uninstall this library, simply run `pip uninstall gymnoscamera`

## Building

To build this library, ensure you are in a virtualenv, and install the requirements from the main
directory.

Run the following command from this directory:

```bash
python3 setup.py sdist
```

## Publishing

To publish this library, ensure you are in a virtualenv, and install 'devpi-client'

```bash
pip install devpi-client
```

Log into the server as user 'gymnos' (see google drive 'Shared Credentials' for password)

```bash
> devpi login gymnos
password for user gymnos:
logged in 'gymnos', credentials valid for 10.00 hours
```

Choose which repository to upload to:

1) Stable (cannot overwrite uploaded versions!)
    ```bash
    devpi use http://thefirstjedi.asuscomm.com:3141/gymnos/stable
    ```
2) Staging (can overwrite uploaded versions)
    ```bash
    devpi use http://thefirstjedi.asuscomm.com:3141/gymnos/staging
    ```

Ensure you are in the GymnosCamera directory and upload using devpi:

```bash
devpi upload
```
