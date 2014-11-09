#!/usr/bin/python

from turretaim import Turret
import sys

class WebcamTurret(Turret):
    "Just like a regular Turret, but can also target based on image coordinates."
    def __init__(self, yaw_difference=135, pitch_difference=0, viewing_angle_horiz=24.0, viewing_angle_vert=18.0, res_horiz=640, res_vert=480, locked_mode=False):
        if sys.version_info.major > 2:
            super().__init__()
        else:
            super(WebcamTurret, self).__init__()
        self.yaw_difference = yaw_difference
        self.pitch_difference = pitch_difference
        self.viewing_angle_horiz = viewing_angle_horiz
        self.viewing_angle_vert = viewing_angle_vert
        self.res_horiz = res_horiz
        self.res_vert = res_vert
        self.locked_mode = locked_mode # True if webcam and turret are phsycally joined
        #self.zero()
        # Aim the turret where the webcam is pointing
        #self.aim_center();

    def aim_center(self):
        self.aim_at_image_coords(self.res_horiz / 2, self.res_vert / 2)

    def aim_at_image_coords(self, x, y):
        "Relative to top left of webcam image."
        yaw, pitch = self.image_coord_to_turret_angles(x, y)
        self.aim(yaw, pitch)

    def fire_at_image_coords(self, x, y, amt):
        "Relative to top left of webcam image."
        yaw, pitch = self.image_coord_to_turret_angles(x, y)
        self.attack(yaw, pitch, amt)
        
    def image_coord_to_webcam_angles(self, x, y):
        "Relative to top left of webcam image. Result is relative to center"
        yaw_webcam = ((1.0 * x / self.res_horiz) - 0.5) * self.viewing_angle_horiz
        pitch_webcam = -((1.0 * y / self.res_vert) - 0.5) * self.viewing_angle_vert
        return (yaw_webcam, pitch_webcam)

    def webcam_angles_to_turret_angles(self, yaw, pitch):
        if self.locked_mode:
            # Webcam is facing the same way the turret is pointed
            # Stop in order to recalculate turret angle
            self.stop()
            # Since webcam angle 
            self.yaw_difference = self.yaw
            self.pitch_difference = self.pitch
            # TODO: Consider tying this more closely to stop() to recalculate every time
        else:
            # Webcam is stationary like normal
            pass
        return (yaw + self.yaw_difference, pitch + self.pitch_difference)
    
    def image_coord_to_turret_angles(self, x, y):
        yaw_webcam, pitch_webcam = self.image_coord_to_webcam_angles(x, y)
        return self.webcam_angles_to_turret_angles(yaw_webcam, pitch_webcam)

def main():
    t = WebcamTurret()
    while True:
        command_line = input("WebcamTurret> ")
        command_line = command_line.split()
        if len(command_line) == 0:
            continue
        if command_line[0] == 'exit':
            break
        if command_line[0] == 'reset':
            t.reset()
            continue
        if command_line[0] == 'stop':
            t.stop()
            continue
        if command_line[0] == 'zero':
            t.zero()
            continue
        if command_line[0] == 'aim':
            _, yaw, pitch = command_line
            t.aim(float(yaw), float(pitch))
        if command_line[0] == 'fire':
            _, amt = command_line
            t.fire(int(amt))
        if command_line[0] == 'attack':
            _, yaw, pitch = command_line
            amt = 3
            t.fire_at(float(yaw), float(pitch), int(amt))
        if command_line[0] == 'offsets':
            _, yaw, pitch = command_line
            t.yaw_difference = yaw
            t.pitch_difference = pitch
        if command_line[0] == 'image':
            _, x, y = command_line
            t.aim_at_image_coords(int(x), int(y))
        if command_line[0] == 'attack':
            _, x, y = command_line
            amt = 3
            t.fire_at_image_coords(int(x), int(y), int(amt))
        if command_line[0] == 'center':
            t.aim_center()
        if command_line[0] == 'centered':
            t.set_angle(t.yaw_difference, t.pitch_difference)
        if command_line[0] == 'lock':
            t.locked_mode = True
        if command_line[0] == 'unlock':
            t.locked_mode = False

if __name__ == '__main__':
    main()
