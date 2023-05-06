import socket
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

def send_control_signal(yaw, zoom):
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
    controller_dataframe['ly'] = zoom
    controller_dataframe['rx'] = yaw
    controller_dataframe = pickle.dumps(controller_dataframe)
    sock.sendto(controller_dataframe, (UDP_IP, UDP_PORT))
    sock.sendto(controller_dataframe, (UDP_IP, UDP_PORT2))
    print("signal sent")