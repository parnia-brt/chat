import socket
import threading
from db import *
import json
from module import *


username = 'parnia'
password = 'parnia'



HOST = '0.0.0.0'  # آدرس سرور
PORT = 1234        # پورت سرور

clients = []

def broadcast(message, sender_socket):
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message)
            except:
                clients.remove(client)

# def handle_client(client_socket):
#     while True:
#         try:
#             message = client_socket.recv(1024)
#             if message:
#                 if [message['login']]:
#                     user = get_user_logined(username, password)
#                     if user :
#                         data = {
#                             login : 'success'
#                         }
#                         client_socket.send(data)
#                 broadcast(message, client_socket)
#             else:
#                 break
#         except:
#             clients.remove(client_socket)
#             break

def handle_client(client_socket):
    while True:
        try:
            message = client_socket.recv(1024)
            if not message:
                print("Client disconnected")
                break
            
            message_str = message.decode('utf-8')
            print(f"Received: {message_str}")

            try:
                message_data = json.loads(message_str)  # تبدیل رشته به JSON
                if message_data['type'] == 'login' :
                    client_socket.send(vlidation_user_login(message_data))
                elif message_data['type'] == 'register':
                    client_socket.send(register_user(message_data))

                else:
                    print("Unknown message format")
            except json.JSONDecodeError:
                print("Error decoding JSON message, skipping...")
                continue

        except Exception as e:
            print(f"Error handling client: {e}")
            break
        # finally:
        #     client_socket.close()
        #     print("Connection closed")
        #     break

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', PORT))
    server.listen()
    print(f"Server is running on {HOST}:{PORT}")

    try:  
        while True:
            client_socket, addr = server.accept()
            clients.append(client_socket)
            threading.Thread(target=handle_client, args=(client_socket,)).start()
    except KeyboardInterrupt as e:
        exit()

if __name__ == "__main__":
    start_server()
