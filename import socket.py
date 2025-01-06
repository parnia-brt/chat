import socket
import threading
from db import *
import json

username = 'parnia'
password = 'parnia'



HOST = '127.0.0.1'  # آدرس سرور
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
            message = client_socket.recv(1024)  # دریافت پیام از کلاینت
            if message:
                # تبدیل پیام از بایت به رشته
                message_str = message.decode('utf-8')  
                
                try:
                    message_data = json.loads(message_str)  # تبدیل رشته به دیکشنری (اگر پیام JSON باشد)
                    
                    if 'login' in message_data:  # بررسی وجود کلید 'login' در داده‌ها
                        username = message_data['username']
                        password = message_data['password']
                        
                        user = get_user_logined(username, password)  # تلاش برای یافتن کاربر
                        if user:
                            data = {
                                'login': 'success'
                            }
                        else:
                            data = {
                                'login': 'failed'
                            }
                        
                        client_socket.send(json.dumps(data).encode('utf-8'))
                except json.JSONDecodeError:
                    print("Error decoding JSON message")
                    break
            else:
                break
        except Exception as e:
            print(f"Error handling client: {e}")
            break

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