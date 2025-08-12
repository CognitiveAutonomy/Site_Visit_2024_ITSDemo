
import socket
import time
import numpy as np

#senddup is a function that takes the parameter, string. When called, it will send the string to the specified IP address and port number (set within this function)
#For testing purposes, download ncat: https://nmap.org/dist/nmap-7.01-win32.zipncat, open a command prompt and type ncat -l -u -p 8088, then set the UDP_PORT below to 8088 and run. The string should be printed to the command prompt

UDP_IP="128.46.98.89"
UDP_PORT=8089 

def sendudp(string_for_iMotions):
    sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    sock.sendto(bytes(string_for_iMotions,"utf-8"),(UDP_IP,UDP_PORT))

    #string_for_iMotions="E;1;EventSourceId;1;0.0;;;SampleId;" + "Flag" + "\r\n"
    #sendudp(string_for_iMotions)

    # print("Sending Data to Port " + str(UDP_PORT))



# Port Setup

# Assuming expInfo is a dictionary
# expInfo = {
#     'with_socket': '1',  # This value determines whether to use the socket
#     # Add other relevant information about the experiment
#     # 'experiment_name': 'MyExperiment',
#     'participant_id': '001',
#     'group_number': '1',
#     'trial': '1'
#     # ... other experiment-related information
# }

# Now you can use expInfo in your provided code snippet


# def sendtcp(byte_for_NIRSIT):
#     if (expInfo['with_socket'] == '1'):
#         serverIp =  '127.0.0.1' # '128.46.185.118'
#         tcpPort = 60000 # 60000
#         MyPort = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
#         MyPort.connect((serverIp, tcpPort))
#         addr = (serverIp, tcpPort)
#         print ('Connected by', addr)

# if (expInfo['with_socket'] == '1'):
#     serverIp =  '127.0.0.1' # '128.46.185.118'
#     tcpPort = 60000 # 60000
#     MyPort = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
#     MyPort.connect((serverIp, tcpPort))
#     addr = (serverIp, tcpPort)
#     print ('Connected by', addr)

# Define "send_marker" function
############# USED FOR FNIRS #######################
serverIp =  '127.0.0.1' # '128.46.185.118'
tcpPort = 60000 # 60000
MyPort = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
MyPort.connect((serverIp, tcpPort))
addr = (serverIp, tcpPort)
print ('Connected by', addr)

def send_marker(marker):
    # check whether marker is int
    if not isinstance(marker, int):
        try:
            marker = int(marker)
        except: 
            print('Error!! Markers must be numbers.')
    # send marker 
    msg = bytes(b'abc') + marker.to_bytes(4, byteorder="little") + bytes(b'xyz')
    MyPort.send(msg)
    print("Sending marker No:" f'{marker}')
############# USED FOR FNIRS #######################


# block_start_marker = 1
# test_end = 2

#### Send markers whenever required  #####
# if (expInfo['with_socket'] == '1'):
#     send_marker(block_start_marker)  # if any number (e.g., 1001) is assigned to the variable "block_start_marker".
#     print('Hello world!')


# ##### When Task application is closed
# if (expInfo['with_socket'] == '1'):
#     send_marker(test_end) # if any number (e.g., 9999) is assigned to the variable "test_end". 
#     time.sleep(0.3)
#     MyPort.close()
#     del(MyPort)
#     print('Hello world! 2')


# #### If variable assginment is not necessary  #####
# if (expInfo['with_socket'] == '1'):
#     send_marker(1111)




