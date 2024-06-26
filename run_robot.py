import numpy as np
import time
from src.IMU import IMU
from src.Controller import Controller
from src.JoystickInterface import JoystickInterface
from src.State import State
from pupper.HardwareInterface import HardwareInterface
from pupper.Config import Configuration
from pupper.Kinematics import four_legs_inverse_kinematics
import pickle
import socket
from pprint import pprint
from src.JoystickInterface import EnqueueCommandsThread
# Initialising UDP port and ip

#UDP_IP = "localhost"
# We were experimenting by sending commands over network thus local ip is listed below
UDP_IP = "192.168.0.183"
UDP_PORT = 9999

# Binding the socket object to correct UDP IP and Port

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))


def main(use_imu=False):
    """Main program
    """

    # Create config
    config = Configuration()
    hardware_interface = HardwareInterface()

    # Create imu handle
    if use_imu:
        imu = IMU(port="/dev/ttyACM0")
        imu.flush_buffer()

    # Create controller and user input handles
    controller = Controller(
        config,
        four_legs_inverse_kinematics,
    )
    state = State()
    print(f"Run Robot code is listening on port {UDP_PORT} and ip {UDP_IP} " )
    joystick_interface = JoystickInterface(config)

    # command_buffer = queue.Queue(maxsize=5)
    command_buffer = joystick_interface.get_command_buffer()
    socket2 = joystick_interface.get_sock()
    enqueue_thread = EnqueueCommandsThread(command_buffer, socket2)
    

    print("Done.")

    last_loop = time.time()

    print("Summary of gait parameters:")
    print("overlap time: ", config.overlap_time)
    print("swing time: ", config.swing_time)
    print("z clearance: ", config.z_clearance)
    print("x shift: ", config.x_shift)

    # Wait until the activate button has been pressed
    while True:
        print("Waiting for L1 to activate robot.")
        while True:
            # command = joystick_interface.get_command(state)
            data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
            msg = pickle.loads(data)
            pprint(msg)
            # joystick_interface.set_color(config.ps4_deactivated_color)
            # if command.activate_event == 1:
            #     break
            
            if msg["L1"] == 1:
                print("Got activation signal")
                break
            time.sleep(0.1)
        print("Robot activated.")
        # joystick_interface.set_color(config.ps4_color)

        enqueue_thread.start()
        while True:
            now = time.time()
            if now - last_loop < config.dt:
                continue
            last_loop = time.time()

            # Parse the udp joystick commands and then update the robot controller's parameters
            print("Got before command = joystick_interface")
            command = joystick_interface.get_command(state)
            print("Got after command = joystick_interface")
            # data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
            # dummy_msg = pickle.loads(data)
            # pprint(dummy_msg)

            # if dummy_msg["L1"] == 1:
            #     print("Deactivating Robot")
            #     break

            # Read imu data. Orientation will be None if no data was available
            quat_orientation = (
                imu.read_orientation() if use_imu else np.array([1, 0, 0, 0])
            )
            state.quat_orientation = quat_orientation
            print("got before controller.run(state, command), continue")
            # continue
            # Step the controller forward by dt
            controller.run(state, command)

            # Update the pwm widths going to the servos
            hardware_interface.set_actuator_postions(state.joint_angles)


main()
