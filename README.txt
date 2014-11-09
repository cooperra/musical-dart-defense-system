Dependencies: pyusb, python-urllib3

This should work:

sudo apt-get install python-urllib3 python-pip
sudo pip install pyusb

Then:
chmod +x turretaim.py retaliation.py

To control the turret:
./turretaim.py
Angle? aim <yaw> <pitch>
Angle? fire <num_shots>
Angle? attack <yaw> <pitch>	(Aims and then fires)
Angle? stop
Angle? zero	(To move back to leftmost lowest position)
Angle? reset	(If it stops working)
Angle? exit

Also, you'll probably have to run as root for it to work.
sudo ./turretaim.py
