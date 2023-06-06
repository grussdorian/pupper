import UDPComms
import numpy as np
import time
from src.State import BehaviorState, State
from src.Command import Command
from src.Utilities import deadband, clipped_first_order_filter
import socket
import pickle
from pprint import pprint
import threading
import queue

# Parallelly enqueue commands sent by the controller
class EnqueueCommandsThread(threading.Thread):
    def __init__(self, command_buffer, sock):
        threading.Thread.__init__(self)
        self.command_buffer = command_buffer
        self._stop_event = threading.Event()
        self.sock = sock

    def run(self):
        while not self._stop_event.is_set():
            # Read frame from socket
            data, addr = self.sock.recvfrom(1024) # buffer size is 1024 bytes
            msg = pickle.loads(data)
            # Add controller_dataframe to buffer
            if msg != None:
                self.command_buffer.put(msg)

    def stop(self):
        self._stop_event.set()


class JoystickInterface:
    # We were experimenting by sending commands over network thus local ip is listed below
    def __init__(self, config, UDP_PORT=6666, udp_publisher_port = 8840, UDP_IP = "192.168.0.183"):
        self.config = config
        self.previous_gait_toggle = 0
        self.previous_state = BehaviorState.REST
        self.previous_hop_toggle = 0
        self.previous_activate_toggle = 0
        self.message_rate = 50
        # self.udp_handle = UDPComms.Subscriber(udp_port, timeout=0.3)
        # self.udp_publisher = UDPComms.Publisher(udp_publisher_port)
        self.command_buffer = queue.Queue(maxsize=5)
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # UDP
        self.sock.bind((UDP_IP, UDP_PORT))
        # enqueue_thread = EnqueueCommandsThread(self.command_buffer, self.sock)
        # EnqueueCommandsThread.start(self)

    def get_command(self, state, do_print=False):
        try:
            # msg = self.udp_handle.get()

            # Modified UDP code
            print("before receiving input in joystickinterface")
            msg = self.command_buffer.get()
            # data, addr = self.sock.recvfrom(1024) # buffer size is 1024 bytes
            # msg = pickle.loads(data) # MODIFIED
            pprint(msg)
            print("after receiving input in joystickinterface")

            command = Command()
            
            ####### Handle discrete commands ########
            # Check if requesting a state transition to trotting, or from trotting to resting
            gait_toggle = msg["R1"]
            command.trot_event = (gait_toggle == 1 and self.previous_gait_toggle == 0)

            # Check if requesting a state transition to hopping, from trotting or resting
            hop_toggle = msg["x"]
            command.hop_event = (hop_toggle == 1 and self.previous_hop_toggle == 0)            
            
            activate_toggle = msg["L1"]
            command.activate_event = (activate_toggle == 1 and self.previous_activate_toggle == 0)

            # Update previous values for toggles and state
            self.previous_gait_toggle = gait_toggle
            self.previous_hop_toggle = hop_toggle
            self.previous_activate_toggle = activate_toggle

            ####### Handle continuous commands ########
            # if (msg["ly"] > 0.01 or msg["ly"] < -0.01):
            #     x_vel = msg["ly"] * self.config.max_x_velocity
            # else:
            #     x_vel = 0
            
            # if (msg["lx"] > 0.01 or msg["lx"] < -0.01):
            #     y_vel = msg["lx"] * -self.config.max_y_velocity
            # else:
            #     y_vel = 0

            #
            x_vel = msg["ly"] * self.config.max_x_velocity
            y_vel = msg["lx"] * -self.config.max_y_velocity
            command.horizontal_velocity = np.array([x_vel, y_vel])

            # if (msg["rx"] > 0.01):
            #     command.yaw_rate = msg["rx"] * -self.config.max_yaw_rate
            # else:
            #     command.yaw_rate = 0

            command.yaw_rate = msg["rx"] * -self.config.max_yaw_rate

            message_rate = msg["message_rate"]
            message_dt = 1.0 / message_rate

            pitch = msg["ry"] * self.config.max_pitch
            deadbanded_pitch = deadband(
                pitch, self.config.pitch_deadband
            )
            pitch_rate = clipped_first_order_filter(
                state.pitch,
                deadbanded_pitch,
                self.config.max_pitch_rate,
                self.config.pitch_time_constant,
            )
            command.pitch = state.pitch + message_dt * pitch_rate

            height_movement = msg["dpady"]
            command.height = state.height - message_dt * self.config.z_speed * height_movement
            
            roll_movement = - msg["dpadx"]
            command.roll = state.roll + message_dt * self.config.roll_speed * roll_movement

            return command

        except UDPComms.timeout:
            if do_print:
                print("UDP Timed out")
            return Command()


    def set_color(self, color):
        # joystick_msg = {"ps4_color": color}
        # self.udp_publisher.send(joystick_msg)
        pass
    
    def get_sock(self):
        return self.sock
    def get_command_buffer(self):
        return self.command_buffer