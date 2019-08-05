### Section 1: Directory structure
```
.
├── README.md
├── Widgets
├── YoloNetwork
├── cameras
├── gym_info.json -> Add manually and 
├── machine.py
├── predictors.py
└── yolo_network
```

### Section 2: Initializing the gym_info.json
- This file stores all information about your gym and it's machines. It is used by the client to access the database
1. Create a json file called gym_info.json
2. Add the following template
```
{
    "GymName": "Golds Gym",
    "Location": "NW",
    "GymID": "DewdmGRDsqLyxChcJCKp",
    "Machines": []
}
```
3. Run the camera with the --configure parameter to initialize the Machines array
```
python3 run_camera.py --model yolo.h5 --usb --configure
```
