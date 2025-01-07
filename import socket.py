import socket
import threading
import json
from db import *  # فرض بر این است که توابع پایگاه داده شما در این فایل هستند
from module import *  # فرض بر این است که توابع کمکی شما در این فایل هستند

# تنظیمات سرور
HOST = '0.0.0.0'  # آدرس سرور
PORT = 1234        # پورت سرور

clients = []  # لیستی از تمام کلاینت‌های متصل
online_users = {}  # نگهداری نام کاربران آنلاین و سوکت‌های آنها


def broadcast(message, sender_socket=None):
    """
    ارسال پیام به تمام کلاینت‌ها به جز کلاینت ارسال کننده (در صورت مشخص بودن)
    """
    for client in clients[:]:  # از لیست کپی گرفته می‌شود تا در هنگام حذف مشکلی ایجاد نشود
        if client != sender_socket:
            try:
                client.send(message.encode('utf-8') if isinstance(message, str) else message)
            except Exception as e:
                print(f"Error broadcasting to client: {e}")
                remove_client(client)


def broadcast_online_users():
    """
    ارسال لیست کاربران آنلاین به تمام کلاینت‌ها
    """
    data = {
        "type": "online_users",
        "users": list(online_users.keys())  # ارسال لیست نام کاربران آنلاین
    }
    broadcast(json.dumps(data))


def remove_client(client_socket):
    """
    حذف کلاینت از لیست کلاینت‌ها و کاربران آنلاین
    """
    if client_socket in clients:
        clients.remove(client_socket)
    username_to_remove = [user for user, sock in online_users.items() if sock == client_socket]
    for user in username_to_remove:
        del online_users[user]
    broadcast_online_users()  # بروزرسانی کاربران آنلاین برای کلاینت‌ها

def send_to_user(sender, receiver, message_data):
    """
    ارسال پیام از یک کاربر به کاربر دیگر.
    :param sender: نام کاربری ارسال‌کننده
    :param receiver: نام کاربری گیرنده
    :param message_data: داده پیام (فرمت JSON)
    """
    if receiver in online_users:
        receiver_socket = online_users[receiver]
        try:
            message = {
                "type": "private_message",
                "sender": sender,
                "message": message_data['message']
            }
            # تبدیل پیام به بایت
            receiver_socket.send(json.dumps(message).encode('utf-8'))
            print(f"Message sent from {sender} to {receiver}: {message_data['message']}")
        except Exception as e:
            print(f"Error sending message to {receiver}: {e}")
    else:
        print(f"User {receiver} is not online.")
        if sender in online_users:
            sender_socket = online_users[sender]
            try:
                error_message = {
                    "type": "error",
                    "message": f"User {receiver} is not online."
                }
                # تبدیل پیام خطا به بایت
                sender_socket.send(json.dumps(error_message).encode('utf-8'))
            except Exception as e:
                print(f"Error sending error message to {sender}: {e}")

def handle_client(client_socket):
    """
    مدیریت ارتباط با هر کلاینت
    """
    try:
        while True:
            message = client_socket.recv(1024)
            if not message:
                print("Client disconnected")
                break

            message_str = message.decode('utf-8')
            print(f"Received: {message_str}")

            try:
                message_data = json.loads(message_str)
                if message_data['type'] == 'login':
                    response = vlidation_user_login(message_data)  # فرض بر این است که این تابع موجود است
                    client_socket.send(response)

                    if json.loads(response.decode('utf-8')).get('login') == 'success':
                        username = message_data['username']
                        online_users[username] = client_socket
                        print(f"{username} logged in.")
                        print(online_users) 
                        broadcast_online_users()

                elif message_data['type'] == 'register':
                    client_socket.send(register_user(message_data))  # فرض بر این است که این تابع موجود است

                elif message_data['type'] == 'message':
                    if message_data.get('receiver') == 'everybody':
                        print('hame')
                        if message_data['message']['type'] == 'file':
                            file_data = message_data['message']["filedata"].encode("latin1")
                            with open(message_data['message']["filename"], "wb") as file:
                                file.write(file_data)
                        broadcast(json.dumps(message_data).encode('utf-8'), client_socket)

                    else:
                        
                        sender = message_data['username']  
                        receiver = message_data['receiver']
                        if message_data['message']['type'] == 'file':
                            file_data = message_data['message']["filedata"].encode("latin1")
                            with open(message_data['message']["filename"], "wb") as file:
                                file.write(file_data)
                        send_to_user(sender, receiver, message_data)
                        

                else:
                    print("Unknown message format")
            except json.JSONDecodeError:
                print("Error decoding JSON message, skipping...")

    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        remove_client(client_socket)
        client_socket.close()


def start_server():
    """
    شروع سرور و مدیریت اتصال کلاینت‌ها
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server is running on {HOST}:{PORT}")

    try:
        while True:
            client_socket, addr = server.accept()
            print(f"New connection from {addr}")
            clients.append(client_socket)
            threading.Thread(target=handle_client, args=(client_socket,)).start()

    except KeyboardInterrupt:
        print("Server shutting down...")
    finally:
        server.close()


if __name__ == "__main__":
    start_server()
