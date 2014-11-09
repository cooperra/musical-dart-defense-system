#!/usr/bin/python

import retaliation as re
import time, threading
import sys

# Yaw measured clockwise

# Seconds
YAW_TIME_RIGHT = 18.5 # 15 on laptop
YAW_TIME_LEFT = 17.5 # 15 on laptop
PITCH_TIME = 2 # 1.5 on laptop

MIN_YAW = 0
MAX_YAW = 315 # degrees
YAW_SPEED = (MAX_YAW - MIN_YAW) / (YAW_TIME_RIGHT * 1000.0) # degrees/ms (aka 21 degrees/sec)
YAW_FRONT = 135
MIN_PITCH = -10 # maybe?
MAX_PITCH = 30 # maybe?
PITCH_SPEED = (MAX_PITCH - MIN_PITCH) / (PITCH_TIME * 1000.0) # 40 degrees over 1.5 seconds
PITCH_FRONT = 0
SHOT_DURATION = 4.5

if sys.version_info.major == 2:
    input = raw_input

class Turret:
    def __init__(self):
        re.setup_usb();
        #re.run_command('zero', 0)
        #re.run_command('zero', 0)
        self.yaw = 0
        self.pitch = -10
        self.status = 'stopped'
        self.queue = [] #empty
        self.action_start = None
        self.action_timer = None

    def set_angle(self, yaw, pitch):
        self.yaw = yaw
        self.pitch = pitch
    
    def zero(self):
        print("Zeroing...")
        self.status = 'zeroing'
        if self.action_timer != None:
            self.action_timer.cancel()
        re.run_command('zero', 0)
        re.run_command('zero', 0)
        self.yaw = 0
        self.pitch = -10
        self.status = 'stopped'
        print("Ready!")

    def reset(self):
        re.setup_usb()

    def aim(self, yaw, pitch):
        "Interrupts the current operation to aim in the desired direction"
        self.stop()
        self.queue = [] # empty queue
        self._queue_aiming(yaw, pitch)
        self.do_next_queue_action()

    def _queue_aiming(self, yaw, pitch):
        delta_yaw = abs(yaw - self.yaw)
        delta_pitch = abs(pitch - self.pitch)
        # Try to move the biggest delta first
        if delta_yaw > delta_pitch:
            self.queue.insert(0, ("setyaw", yaw))
            self.queue.insert(0, ("setpitch", pitch))
        else:
            self.queue.insert(0, ("setpitch", pitch))
            self.queue.insert(0, ("setyaw", yaw))

    def fire(self, amt):
        self.stop()
        self.queue = [("fire", amt)]
        self.do_next_queue_action()

    def fire_at(self, yaw, pitch, amt):
        "Interrupts the current operation to aim and fire in the desired direction"
        self.stop()
        self.queue = [] # empty queue
        self._queue_aiming(yaw, pitch)
        self.queue.insert(0, ("fire", amt))
        self.do_next_queue_action()

    def do_next_queue_action(self):
        self.stop()
        try:
            action, arg = self.queue.pop()
        except IndexError:
            # Empty queue; we're done here
            return
        command_mapping = {"setyaw": self.do_setyaw, "setpitch": self.do_setpitch, "fire": self.do_fire, "sleep": self.do_sleep}
        duration = command_mapping[action](arg) # duration in seconds
        self.action_start = time.time()
        if duration == None or duration == 0:
            self.do_next_queue_action()
        else:
            self.action_timer = threading.Timer(duration, self.do_next_queue_action)
            self.action_timer.start()
        
    def do_setyaw(self, yaw):
        yaw_delta = yaw - self.yaw
        if yaw_delta > 0:
            direction = re.RIGHT
        elif yaw_delta < 0:
            direction = re.LEFT
        else:
            # Already on target
            return
        duration = abs(yaw_delta / (YAW_SPEED * 1000.0))
        self.status = direction
        re.send_cmd(direction)
        return duration
        
    def do_setpitch(self, pitch):
        pitch_delta = pitch - self.pitch
        if pitch_delta > 0:
            direction = re.UP
        elif pitch_delta < 0:
            direction = re.DOWN
        else:
            # Already on target
            return
        duration = abs(pitch_delta / (PITCH_SPEED * 1000.0))
        self.status = direction
        re.send_cmd(direction)
        return duration

    def do_fire(self, amt):
        # TODO: add awareness of available ammo
        if amt <= 0:
            amt = 0
        if amt > 3:
            amt = 3
        self.status = re.FIRE
        re.send_cmd(re.FIRE)
        return SHOT_DURATION * amt

    def do_sleep(self, secs):
        return secs
        
    def stop(self):
        "Stop operations and calculate current direction"
        if self.action_timer != None:
            self.action_timer.cancel()
        if self.status != 'stopped':
            re.send_cmd(re.STOP)
            delta_time = 1000 * (time.time() - self.action_start)
            if self.status == re.UP or self.status == re.DOWN:
                delta_pitch = delta_time * PITCH_SPEED
                if self.status == re.UP:
                    self.pitch += delta_pitch
                else:
                    self.pitch -= delta_pitch
            elif self.status == re.LEFT or self.status == re.RIGHT:
                delta_yaw = delta_time * YAW_SPEED
                if self.status == re.RIGHT:
                    self.yaw += delta_yaw
                else:
                    self.yaw -= delta_yaw
            elif self.status == re.FIRE:
                # TODO: is this right?
                # stopping workaround for firing (STOP doesn't work)
                re.send_cmd(re.RIGHT)
                re.send_cmd(re.STOP)
            else:
                print('Unexpected status: %r' % self.status)
            self.validate_angle()
            self.status = 'stopped'
            
    def validate_angle(self):
        "Makes sure that the calculated angle is within the turret's range of movement"
        if self.yaw < MIN_YAW:
            self.yaw = MIN_YAW
        elif self.yaw > MAX_YAW:
            self.yaw = MAX_YAW
        
        if self.pitch < MIN_PITCH:
            self.pitch = MIN_PITCH
        elif self.pitch > MAX_PITCH:
            self.pitch = MAX_PITCH

def main():
    t = Turret()
    while True:
        command_line = input("Turret> ")
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

if __name__ == '__main__':
    main()
