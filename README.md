# MDDS

This project was the winner of the 2014 HackKentucky hackathon.

See our [ChallengePost submission](http://challengepost.com/software/musical-dart-defense-system) for more info, including photos and video of our hack in action.

## What is this?

This repository allows one to use a USB DreamCheeky dart launcher and a webcam to shoot at or play music for people depending on whether their faces are recognized.

There are two main parts:

1. A wrapper for [retaliation.py](https://github.com/codedance/Retaliation) to make controlling the dart launcher easier. 
2. Face detection/recognition/training

## Contributors

- Robbie Cooper
- Lorinda Peoples
- Tegjyot Sethi
- Anuteja Mallampati

# Setup and Usage

Disclaimer: As the hackathon was only 24 hours and we no longer have access to the dart launcher, we can't test these instructions thoroughly. If you have any issues or questions, feel free to file an issue or pull request. 

## Retaliation wrapper

The wrapper lets you specify absolute angles to aim the turret. Without the wrapper, you can only do movement relative to where you are currently aiming. The USB interface does not support introspection about its aim, which is why this wrapper exists.

When the wrapper starts, it will "zero" the turret by moving both left and down until it thinks it can't go any farther.

Files:

- retaliation.py -- Basic USB turret control (see the [original repo](https://github.com/codedance/Retaliation))
- turret_aim.py -- Absolute aiming by angle
- webcam_turret.py -- Absolute aiming by image coordinate

Each one depends on the previous ones. 

### Setup

Dependencies: pyusb, python-urllib3

This should work:

  $ sudo apt-get install python-urllib3 python-pip
  $ sudo pip install pyusb

Then:

  $ chmod +x turretaim.py retaliation.py webcam_turret.py

### Controlling the turret

There are two ways to control the turret, turretaim.py and webcam_turret.py.

turretaim.py allows aiming the turret at absolute angles relative to a "zero" position. 

webcam_turret.py is a wrapper around turretaim.py that maps an XY coordinate in an image to a turret angle. Since it does everything turretaim.py can do plus more, you might as well just use it instead.

#### Calibration

You may need to tweak globals in the files to calibrate the turret. The movement speed of the turret is particularly important. It varies depending on how powerful your USB port is. Aiming the turret accurately depends on having a good measurement of this speed. We used a stopwatch to time how long it took for the turret to make a full rotation and calculated the speed from that. 

#### turretaim.py

To control the turret directly:

  $ ./turretaim.py

This gives you an interactive prompt to control the turret. 

Turret> aim <yaw> <pitch>
Turret> fire <num_shots>
Turret> attack <yaw> <pitch>	(Aims and then fires)
Turret> stop
Turret> zero	(To move back to leftmost lowest position)
Turret> reset	(If it stops working)
Turret> exit

Also, you'll probably have to run as root for it to work. Otherwise, you'll probably lack permissions for the low-level USB control that retaliation.py needs.

  $ sudo ./turretaim.py

#### webcam_turret.py

webcam_turret.py has the same interface as turretaim.py, but adds the following commands:

WebcamTurret> offsets <yaw> <pitch>	(Set the current aim without moving, useful when you want to zero manually)
WebcamTurret> center	(Aim at the center of the image)
WebcamTurret> centered	(Consider the current aim to be the center of the image)
WebcamTurret> image <x> <y>	(Aim at the given image coordinate)
WebcamTurret> lock	(Assume that the webcam is attached to the turret and moves with it--untested)
WebcamTurret> unlock	(Assume that the webcam is close to the turret, but not connected to it--default behavior)

## Face recognition and detection and spotify integration

Depends on:

- spotify api (python library included here?)
- espeak
- opencv

See these files:

- train.py -- Train the face recognition
- test_model.py -- Run the entire MDDS system. Remember: you'll probably need sudo for USB. 

### Spotify api key

You'll need a file named spotify_appkey.key.

### Other info

The dataset files are in the att_faces folder

- facerec.py is used for recording faces for positive dataset
- train.py uses Eigen Faces to classify the detected faces
- test_model.py reads the live feed and classifies the faces
- fetch_user_playlist.py  fetches starred playlist of user
- pyspotify_login_1.py uses the username and reads the songs list off of the data.txt file and then uses it to play music.