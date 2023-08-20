import yarp;
import time;
import numpy as np;
import socket;
import errno;
from socket import error as SocketError;
import matplotlib.pyplot as plt;
from scipy.fft import fft, ifft, fftfreq
import select;


# Initialize socket connexion to receive PD-state coeff from brain model
"""# Initialize the client socket
sender_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_host = 'localhost'  # Replace with the appropriate IP address or hostname
sender_port = 12346 # The same port number used in the brain simulation program

# Connect to the server
sender_socket.bind((server_host, sender_port))

sender_socket.listen(1)
print('Waiting for client connection from brain model...')
client_socket, client_address = sender_socket.accept()
print('Client brain model connected:', client_address)

print('Sender socket connected')"""

global last_samp_t
global start_t

def getPos(jnt): # get the Pos of all joints
     iEnc.getEncoders(encs.data())
     return yarp.Vector(jnt+1, encs.data())[jnt]

def checkReachPos(comp, boundary_inf, boundary_sup, jnt): # Check if the pos of a joint has reached a particular value
    if comp == 'inf':
        if getPos(jnt) <= boundary_inf:
            return True
    elif comp == 'sup':
        if getPos(jnt) >= boundary_sup:
            return True
    elif comp == 'between':
        if getPos(jnt) <= boundary_inf and getPos(jnt) >= boundary_sup:
            return True
    return False

def goToStartPos(): # Go to start pos (pronation)
    start_pos = yarp.Vector(jnts)
    start_pos.set(0, -23.1)
    start_pos.set(1, 24)
    start_pos.set(2, 14.04)
    start_pos.set(3, 64.61)
    start_pos.set(4, 60)

    iPos.positionMove(start_pos.data())
    while checkReachPos('sup', None, 58, 4) == False:
            print('Going to start pos...')
    print('Start pos (pronation) reached, beginning movement in 3s')
    time.sleep(3)

def generateSingleTremor(amp, jnt):
    global last_samp_t
    global start_t

    # "Up" part of the tremor
    iPos.positionMove(jnt, amp)

    while checkReachPos('sup', None, amp*0.8, jnt) == False:
        check_t = time.time()
        if check_t- last_samp_t >= T_samp:
                #print('Tremor pos (up): ', getPos(4))
                # Collect joints data
                joint4_pos.append(getPos(4))
                joint5_pos.append(getPos(5))
                t.append(check_t-start_t)
                last_samp_t = check_t
    #print('Tremor up pos reached')

    # "Down" part of the tremor
    iPos.positionMove(jnt, -amp)

    while checkReachPos('inf', -amp*0.8, None, jnt) == False:
        check_t = time.time()
        if check_t- last_samp_t >= T_samp:
                #print('Tremor pos (down): ', getPos(4))
                # Collect joints data
                joint4_pos.append(getPos(4))
                joint5_pos.append(getPos(5))
                t.append(check_t-start_t)
                last_samp_t = check_t
    #print('Tremor down pos reached')

    # Back to 0
    iPos.positionMove(jnt, 0)

def generateMovement():
    global last_samp_t
    global start_t

    # Set ref speeds and accelerations
    iPos.setRefSpeed(1, 10)
    iPos.setRefAcceleration(1, 50)

    iPos.setRefSpeed(4, 180)
    iPos.setRefAcceleration(4,60)

    iPos.setRefSpeed(5, 50)
    iPos.setRefAcceleration(5,20)

    # Set joints target positions for pronation and supination
    prono_pos = yarp.Vector(jnts)
    prono_pos.set(0, -23.1)
    prono_pos.set(1, 24)
    prono_pos.set(2, 14.04)
    prono_pos.set(3, 64.61)
    prono_pos.set(4, 60)

    supin_pos = yarp.Vector(jnts)
    supin_pos.set(0, -23.1)
    supin_pos.set(1, 16)
    supin_pos.set(2, 14.04)
    supin_pos.set(3, 64.61)
    supin_pos.set(4, -60)

    # Start timing to gather data
    start_t = time.time()
    last_samp_t = start_t
    last_trem_t = start_t

    PD_state = 0
    while time.time() < start_t + N_samp*T_samp: # while max time of simulation has not been reached
        socket_as_list = [receiver_socket]

        readable, _, _ = select.select(socket_as_list, [], [], 0.1)

        if receiver_socket in readable: # if we received a new coefficient
            try:
                # Receive PD_state value from the brain model
                PD_state = float(receiver_socket.recv(1024).decode())
                print('PD COEFF RECEIVED :', PD_state)

            except (socket.error, ValueError) as e:
                print('Error receiving data:', e)

        print('Time : ', time.time()-start_t)

        # Moving to pronation position
        print('Moving pronation position')
        iPos.positionMove(prono_pos.data())

        while checkReachPos('sup', None, 55, 4) == False:
            check_t = time.time()
            if check_t- last_samp_t >= T_samp:
                # Collect joints data
                joint4_pos.append(getPos(4))
                joint5_pos.append(getPos(5))
                t.append(check_t-start_t)
                last_samp_t = check_t
                #print('Joint 4 angle : ', joint4_pos[-1])
            if PD_state > 1: # if not healthy
                if check_t - last_trem_t >= T_tremor:
                    # Generate tremors whose amplitude is dicted by PDstate
                    trem_amp = 2.5/8 * PD_state + 0.2
                    generateSingleTremor(trem_amp,5)
                    last_trem_t = check_t

        # Moving to supination position
        print('Moving supination position')
        iPos.positionMove(supin_pos.data())

        while checkReachPos('inf', -55, None, 4) == False:
            check_t = time.time()
            if check_t- last_samp_t >= T_samp:
                # Collect joints data
                joint4_pos.append(getPos(4))
                joint5_pos.append(getPos(5))
                t.append(check_t-start_t)
                last_samp_t = check_t
                #print('Joint 4 angle : ', joint4_pos[-1])
            if PD_state > 1: # if not healthy
                if check_t - last_trem_t >= T_tremor:
                    # Generate tremors whose amplitude is dicted by PDstate
                    trem_amp = 2.2/8 * PD_state + 0.2
                    generateSingleTremor(trem_amp,5)
                    last_trem_t = check_t

    print('t len : ', len(t), 'pos4 len : ', len(joint4_pos))

    # Joints temporal dynamics
    plt.plot(t, joint4_pos)
    plt.title('Joint 4 (pronosupination) angle relative to time')
    plt.xlabel('Time (s)')
    plt.ylabel('Joint 4 angle (°)')
    plt.show()

    plt.plot(t, joint5_pos)
    plt.title('Tremor amplitudes angle')
    plt.xlabel('Time (s)')
    plt.ylabel('Joint 5 angle (°)')
    plt.ylim([-3,3])
    plt.show()

    real_Nsamp = len(t)
    real_Tsamp = (t[-1]-t[0])/len(t)

    # Joints FFT signals
    fft_joint4 = fft(joint4_pos)
    freq_fft = fftfreq(real_Nsamp, real_Tsamp)[:real_Nsamp//2]
    plt.plot(freq_fft, 2.0/real_Nsamp * np.abs(fft_joint4[0:real_Nsamp//2]))
    plt.title('FFT of joint 4 angle')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Power')
    plt.show()

    fft_joint5 = fft(joint5_pos)
    plt.plot(freq_fft, 2.0/real_Nsamp * np.abs(fft_joint5[0:real_Nsamp//2]))
    plt.title('FFT of joint 5 angle')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Power')
    plt.show()


if __name__ == '__main__':
    yarp.Network.init();
  
    # prepare a property object
    props = yarp.Property()
    props.put("device","remote_controlboard")
    props.put("local","/client/left_arm")
    props.put("remote","/icubSim/left_arm")
    
    # create remote driver
    armDriver = yarp.PolyDriver(props)
    
    #query motor control interfaces
    iPos = armDriver.viewIPositionControl()
    iVel = armDriver.viewIVelocityControl()
    iTorque = armDriver.viewITorqueControl()
    iEnc = armDriver.viewIEncoders()
    iimp = armDriver.viewIImpedanceControl()
    ictrl = armDriver.viewIControlMode()

    #retrieve number of joints
    jnts=iPos.getAxes()
    print ('Controlling', jnts, 'joints')

    # read encoders
    encs=yarp.Vector(jnts)
    iEnc.getEncoders(encs.data())

    # Initialize the client socket
    receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_host = 'localhost'  # Replace with the appropriate IP address or hostname
    receiver_port = 12345  # The same port number used in the brain simulation program

    # Connect to the server
    receiver_socket.connect((server_host, receiver_port))
    print('Receiver socket connected')

    N_samp = 9000
    T_samp = 0.01
    T_tremor = 0.2

    joint4_pos = []
    joint5_pos = []
    t = []

    goToStartPos()
    generateMovement()

    print("Program finished")
    receiver_socket.close()

    



