import socket
import threading
# import pickle
import pickle
import sys
import server_change_receiver
lock=threading.Lock
import struct
import main

# server socket is a global variable
# Wrapper method to send data to client
def send_to_client(server_socket, message_type, data):
    message = {
        'type': message_type,
        'data': data
    }
    serialized_message = pickle.dumps(message)
    message_length = struct.pack('!I', len(serialized_message))
    server_socket.sendall(message_length + serialized_message)
    # server_socket.sendall(serialized_message)

def handle_client_message(message, client_socket):
    message_type = message['type']
    data = message['data']
    if message_type == 'add':
        file_path = data['file_path']
        file_data = data['file_data']
        server_change_receiver.handle_receive_add(file_path,file_data)
    if message_type == 'small_update':
        file_path = data['file_path']
        file_data = data['file_data']
        server_change_receiver.handle_receive_update(file_path,file_data)
    if message_type == 'large_update':
        file_path = data['file_path']
        file_data = data['file_data']
        server_change_receiver.handle_receive_update(file_path,file_data)
    if message_type == 'delete':
        file_path = data['file_path']
        server_change_receiver.handle_receive_delete(file_path)
    else:
        print("Unknown message type received")

def receive_from_client(client_socket):
    # Read message length and unpack it into an integer
    raw_message_length = recvall(client_socket, 4)
    if not raw_message_length:
        return None
    message_length = struct.unpack('!I', raw_message_length)[0]
    
    # Read the message data based on the message length
    serialized_message = recvall(client_socket, message_length)
    if not serialized_message:
        return None
    
    message = pickle.loads(serialized_message)
    return message

def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    print("IN RECVALL!")
    return data

def pre_process_message(server_socket,client_socket):
    # TIMEOUT_DURATION = 100

    # server_socket.settimeout(TIMEOUT_DURATION)
    raw_message_length = recvall(client_socket, 4)
    if not raw_message_length:
        return None
    message_length = struct.unpack('!I', raw_message_length)[0]
    # Read the message data based on the message length
    serialized_message = recvall(client_socket, message_length)
    message = pickle.loads(serialized_message)
    print(message)
    message_type = message['type']
    if message_type in ['small_update', 'large_update']:

        file_path = message['data']['file_path']
        message['data'] = {
            "file_path": file_path,
            "file_data": message,
        }

    print("SUCCESS!!BEFORE SENDING DATA")
    print(message)

    return message

# to avoid timeout
# def pre_process_message(server_socket,client_socket):
#     TIMEOUT_DURATION = 100
 
#     server_socket.settimeout(TIMEOUT_DURATION)
#     serialized_message = client_socket.recv(4096)
#     message = pickle.loads(serialized_message)
#     print("pre called!!!!!!")
#     print(message)
#     message_type = message['type']
#     if message_type in ['small_update', 'large_update']:
#         file_data = b''
#         file_data += message['data']['file_data']
#         while True:
#             try:
#                 serialized_message_sub = client_socket.recv(4096)
#                 message_sub = pickle.loads(serialized_message_sub)
#                 if message_sub['data'] == b'END':
#                     break
#                 else:
#                     print("received data!!!!!!!!")
#                     file_data += message_sub['data']['file_data']
#             except socket.timeout:
#                 print("Timeout occurred while receiving file data.")
#                 # Handle Timeout
#                 break
#             finally:
#                 server_socket.settimeout(None)  # 将超时设置回无限制

#         file_path = message['data']['file_path']
#         message['data'] = {
#             "file_path": file_path,
#             "file_data": file_data,
#         }

#     return message

def handle_client(server_socket,client_socket):
    while True:
         message = pre_process_message(server_socket,client_socket)
         handle_client_message(message,client_socket)
