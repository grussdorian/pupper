import socket
import pickle
import time
UDP_IP = "localhost"
UDP_PORT = 9999
UDP_PORT2 = 6666
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) 
left_y = 0
left_x = 0
right_x = 0
right_y = 0
L2 = 0
R2 = 0
R1 = 0
L1 = 0
dpady = 0
dpadx = 0
x = 0
square = 0
circle = 0
triangle = 0
MESSAGE_RATE = 20
delta_time = 0.15
class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


getch = _Getch()
print("Enter input \n p to activate, x to stop, w to move forward, a to move left, d to move right, s to move back")

if __name__ == "__main__":
    # from Object_Detection_Files.control_pupper import send_control_signal as scs
    controller_dataframe = {
    "ly": left_y,
    "lx": left_x,
    "rx": right_x,
    "ry": right_y,
    "L2": L2,
    "R2": R2,
    "R1": R1,
    "L1": L1,
    "dpady": dpady,
    "dpadx": dpadx,
    "x": x,
    "square": square,
    "circle": circle,
    "triangle": triangle,
    "message_rate": MESSAGE_RATE
    }

    while(True):
        zoom = 0
        yaw = 0
        inp = getch()
        print(f"{inp}", end ="\r")
        if inp == 'x':
            break
        elif inp == 'w':
            zoom = 1
            controller_dataframe['ly'] = zoom
            time_target = int(time.time()) + delta_time
            while (True):
                if int(time.time()) > time_target:
                    break
                raw_data = pickle.dumps(controller_dataframe)
                sock.sendto(raw_data, (UDP_IP, UDP_PORT2))
                time.sleep(0.005)
            controller_dataframe['ly'] = 0
        elif inp == 's':
            zoom = -1
            controller_dataframe['ly'] = zoom
            time_target = int(time.time()) + delta_time
            while (True):
                if int(time.time()) > time_target:
                    break
                raw_data = pickle.dumps(controller_dataframe)
                sock.sendto(raw_data, (UDP_IP, UDP_PORT2))
                time.sleep(0.005)
            controller_dataframe['ly'] = 0
        elif inp == 'a':
            yaw = 1
            controller_dataframe['rx'] = yaw
            time_target = int(time.time()) + delta_time
            while (True):
                if int(time.time()) > time_target:
                    break
                raw_data = pickle.dumps(controller_dataframe)
                sock.sendto(raw_data, (UDP_IP, UDP_PORT2))
                time.sleep(0.005)
            controller_dataframe['rx'] = 0
        elif inp == 'd':
            yaw = -1
            controller_dataframe['rx'] = yaw
            time_target = int(time.time()) + delta_time
            while (True):
                if int(time.time()) > time_target:
                    break
                raw_data = pickle.dumps(controller_dataframe)
                sock.sendto(raw_data, (UDP_IP, UDP_PORT2))
                time.sleep(0.005)
            controller_dataframe['rx'] = 0
        elif inp == 'p':
            activation_signal = {
            "ly": 0,
            "lx": 0,
            "rx": 0,
            "ry": 0,
            "L2": 0,
            "R2": 0,
            "R1": 0,
            "L1": 1,
            "dpady": 0,
            "dpadx": 0,
            "x": 0,
            "square": 0,
            "circle": 0,
            "triangle": 0,
            "message_rate": 20
            }
            activation_signal = pickle.dumps(activation_signal)
            sock.sendto(activation_signal, (UDP_IP, UDP_PORT))
            time.sleep(2)
            activation_signal = {
            "ly": 0,
            "lx": 0,
            "rx": 0,
            "ry": 0,
            "L2": 0,
            "R2": 0,
            "R1": 1,
            "L1": 0,
            "dpady": 0,
            "dpadx": 0,
            "x": 0,
            "square": 0,
            "circle": 0,
            "triangle": 0,
            "message_rate": 20
            }
            activation_signal = pickle.dumps(activation_signal)
            sock.sendto(activation_signal, (UDP_IP, UDP_PORT))
            print("ROBOT ACTIVATED")
            continue
        else:
            continue

        controller_dataframe['ly'] = zoom
        controller_dataframe['rx'] = yaw
        raw_data = pickle.dumps(controller_dataframe)
        sock.sendto(raw_data, (UDP_IP, UDP_PORT))
        sock.sendto(raw_data, (UDP_IP, UDP_PORT2))
        # print("signal sent")
