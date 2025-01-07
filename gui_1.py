from tkinter import *
from tkinter import messagebox
from tkinter import filedialog  # این خط رو به کد وارد کنید
import sounddevice as sd
import numpy as np
import wave
import socket
import threading
import json

client_socket = None

# دیکشنری برای ذخیره نام کاربری و پسورد و کاربران آنلاین
users_online = []
active_chat = 'everybody'

# تابع تایید ورود
def authenticate_user(username, password):
    return users.get(username) == password


class Server:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_ip = "192.168.56.251"
        self.client_socket.connect((server_ip, 1234))  # آدرس و پورت سرور

    def login_user(self, username, password):
        self.username = username
        self.password = password
        user_data = {"username": username, "password": password, "type": "login"}
        data = json.dumps(user_data).encode("utf-8")
        self.client_socket.send(data)  # ارسال نام کاربری به سرور
        return self.client_socket.recv(1024)

    def register_user(self, username, password, email):
        self.username = username
        self.password = password
        user_data = {"username": username, "password": password, "type": "register"}
        data = json.dumps(user_data).encode("utf-8")
        self.client_socket.send(data)
        return self.client_socket.recv(1024)

    def new_message(self, message , receiver = None):
        user_data = {
            "username": self.username,
            # "password": self.password,
            "receiver" : receiver,
            "message": message,
            "type": "message",
        }
        data = json.dumps(user_data).encode("utf-8")
        self.client_socket.send(data)
        # return self.client_socket.recv(1024)

    def receive_messages(self):
        while True:
            try:
                print("receive")
                message = self.client_socket.recv(1024).decode("utf-8")
                if message:
                    print("i receive that " + message)
                    return json.loads(message)
                else:
                    print("i have not message")
            except Exception as e:
                print(f"Error receiving message: {e}")
            break

    def start_receiving_online_users(self, online_listbox):
        threading.Thread(
            target=get_online_user_from_server,
            args=(self.client_socket, online_listbox),
            daemon=True,
        ).start()


server = Server()


def receive_messages(chatbox, online_listbox):
    """دریافت پیام‌ها از سرور"""
    while True:
        try:
            message = server.receive_messages()
            print(message)
            if message["type"] == "message":
                if message["receiver"] == active_chat:
                    if "filedata" in message["message"]:
                        file_content = message["message"]["filedata"].encode("latin1")
                        filename = message["message"]["filename"]
                        with open(filename, "wb") as file:
                            file.write(file_content)

                        chatbox.config(state=NORMAL)
                        chatbox.insert(
                            END,
                            f"{message['username']} sent a file: {filename}\n",
                            "received_message",
                        )
                        chatbox.config(state=DISABLED)
                    chatbox.config(state=NORMAL)
                    chatbox.insert(END, f"{message['username']} : {message['message']} \n")
                    chatbox.config(state=DISABLED)
            elif message["type"] == "private_message":
                if message["sender"] == active_chat:
                    if "filedata" in message["message"]:
                        file_content = message["message"]["filedata"].encode("latin1")
                        filename = message["message"]["filename"]
                        with open(filename, "wb") as file:
                            file.write(file_content)
                        chatbox.config(state=NORMAL)
                        chatbox.insert(
                            END,
                            f"{message['username']} sent a file: {filename}\n",
                            "received_message",
                        )
                        chatbox.config(state=DISABLED)
                    chatbox.config(state=NORMAL)
                    chatbox.insert(
                        END, f"{message['sender']} : {message['message']} \n"
                    )
                    chatbox.config(state=DISABLED)
            elif message["type"] == "online_users":
                get_online_user_from_server(client_socket, online_listbox, message)
        except Exception as e:
            print(f"Error receiving message: {e}")
            break


def get_online_user_from_server(client_socket, online_listbox, message):
    try:
        print("im in online function")
        print(message["users"])
        # message = json.loads(message)
        global users_online
        users_online = message["users"]
        print("Updated online users:", users_online)
        # پاک کردن کاربران قبلی در لیست
        online_listbox.delete(0, END)

        # استفاده از `after` برای به روز رسانی لیست در نخ اصلی
        def update_listbox():
            online_listbox.insert(END, "everybody")
            for user in users_online:
                online_listbox.insert(END, user)
        online_listbox.pack(padx=10, pady=5)

        online_listbox.after(
            0, update_listbox
        )  # Schedule the update in the main thread
    except Exception as e:
        print(f"Error receiving message: {e}")


def on_item_click(event , chatbox):
    # گرفتن اندیس انتخاب‌شده
    global active_chat
    selected_index = event.widget.curselection()
    if selected_index:
        # دریافت متن انتخاب‌شده
        selected_item = event.widget.get(selected_index)
        print(f"You clicked on: {selected_item}")
        # فراخوانی تابع یا انجام عملیات دیگر
        print('active = ' + active_chat)
        print("selected_item = " + selected_item)

        if active_chat != selected_item:
            active_chat = selected_item
            chatbox.config(state=NORMAL)
            chatbox.delete(1.0, END)  # پاک کردن کل محتوای قبلی
            chatbox.insert(END, f"Chat with {active_chat}...\n")  # پیغام جدید
            chatbox.config(state=DISABLED)
# صفحه ورود
def login_page(root):
    def login():
        username = username_entry.get()
        password = password_entry.get()
        response = server.login_user(username, password)
        response = json.loads(response)
        if response["login"] == "success":
            # users_online[username] = "Online"
            messagebox.showinfo("Login", "Login successful! Redirecting to chatroom...")
            root.destroy()
            chatroom_root = Tk()
            chatroom_root.geometry("600x400")
            ChatroomPage(chatroom_root, username)
            # threading.Thread(target=receive_messages, daemon=True).start()
            chatroom_root.mainloop()
        else:
            error_label.config(text="Incorrect username or password", fg="red")
            root.after(2000, lambda: error_label.config(text=""))

    def open_register_page():
        root.destroy()  # بستن صفحه ورود
        register_root = Tk()
        register_root.geometry("400x400")
        register_page(register_root)
        register_root.mainloop()

    root.title("Login")
    header_label = Label(
        root,
        text="Welcome to Man o Ostad Chatroom",
        font=("Arial", 16, "bold"),
        fg="#FF1493",
        bg="#FFC0CB",
    )
    header_label.pack(pady=(20, 10))

    root.configure(bg="#FFC0CB")

    username_frame = Frame(root, bg="#FFFFFF")
    username_frame.pack(pady=10, fill=X)
    username_label = Label(
        username_frame, text="Username:", font=("Arial", 12), bg="#FFFFFF", anchor="w"
    )
    username_label.pack(side=LEFT, padx=10, pady=5, fill=X)
    username_entry = Entry(username_frame, font=("Arial", 14), bd=2, relief=SOLID)
    username_entry.pack(side=LEFT, padx=10, pady=5, fill=X)

    password_frame = Frame(root, bg="#FFFFFF")
    password_frame.pack(pady=10, fill=X)
    password_label = Label(
        password_frame, text="Password:", font=("Arial", 12), bg="#FFFFFF", anchor="w"
    )
    password_label.pack(side=LEFT, padx=10, pady=5, fill=X)
    password_entry = Entry(
        password_frame, font=("Arial", 14), bd=2, relief=SOLID, show="*"
    )
    password_entry.pack(side=LEFT, padx=10, pady=5, fill=X)

    error_label = Label(root, text="", font=("Arial", 10), bg="#FFC0CB")
    error_label.pack(pady=5)

    login_button = Button(
        root,
        text="Login",
        command=login,
        font=("Arial", 12),
        bg="#FF1493",
        fg="white",
        bd=0,
        relief=RAISED,
    )
    login_button.pack(pady=(10, 5), fill=X)

    # دکمه ثبت نام دوباره اضافه شد
    register_button = Button(
        root,
        text="Register",
        command=open_register_page,
        font=("Arial", 12),
        bg="#FF1493",
        fg="white",
        bd=0,
        relief=RAISED,
    )
    register_button.pack(pady=5, fill=X)

    # def send_message():
    #     message = message_entry.get()
    #     if message:
    #         client_socket.send(f"{username}: {message}".encode("utf-8"))
    #         message_entry.delete(0, END)


def register_page(root):
    def register():
        username = username_entry.get()
        password = password_entry.get()
        confirm_password = confirm_password_entry.get()

        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match. Please try again.")

        response = server.register_user(username, password, confirm_password)
        response = json.loads(response)
        if response["register"] == "failed" or response["error"]:
            messagebox.showerror(
                "Error", "Username already exists. Please choose another username."
            )
        else:
            messagebox.showinfo(
                "Register", "Registration successful! You can now log in."
            )
            root.destroy()
            login_root = Tk()
            login_root.geometry("400x400")
            login_page(login_root)
            login_root.mainloop()

    root.title("Register")
    root.configure(bg="#FFC0CB")

    header_label = Label(
        root,
        text="Register for Man o Ostad Chatroom",
        font=("Arial", 16, "bold"),
        fg="#FF1493",
        bg="#FFC0CB",
    )
    header_label.pack(pady=(20, 10))

    username_frame = Frame(root, bg="#FFFFFF")
    username_frame.pack(pady=10, fill=X)
    username_label = Label(
        username_frame, text="Username:", font=("Arial", 12), bg="#FFFFFF", anchor="w"
    )
    username_label.pack(side=LEFT, padx=10, pady=5, fill=X)
    username_entry = Entry(username_frame, font=("Arial", 14), bd=2, relief=SOLID)
    username_entry.pack(side=LEFT, padx=10, pady=5, fill=X)

    password_frame = Frame(root, bg="#FFFFFF")
    password_frame.pack(pady=10, fill=X)
    password_label = Label(
        password_frame, text="Password:", font=("Arial", 12), bg="#FFFFFF", anchor="w"
    )
    password_label.pack(side=LEFT, padx=10, pady=5, fill=X)
    password_entry = Entry(
        password_frame, font=("Arial", 14), bd=2, relief=SOLID, show="*"
    )
    password_entry.pack(side=LEFT, padx=10, pady=5, fill=X)

    confirm_password_frame = Frame(root, bg="#FFFFFF")
    confirm_password_frame.pack(pady=10, fill=X)
    confirm_password_label = Label(
        confirm_password_frame,
        text="Confirm Password:",
        font=("Arial", 12),
        bg="#FFFFFF",
        anchor="w",
    )
    confirm_password_label.pack(side=LEFT, padx=10, pady=5, fill=X)
    confirm_password_entry = Entry(
        confirm_password_frame, font=("Arial", 14), bd=2, relief=SOLID, show="*"
    )
    confirm_password_entry.pack(side=LEFT, padx=10, pady=5, fill=X)

    register_button = Button(
        root,
        text="Register",
        command=register,
        font=("Arial", 12),
        bg="#FF1493",
        fg="white",
        bd=0,
        relief=RAISED,
    )
    register_button.pack(pady=(10, 5), fill=X)


def ChatroomPage(root, username):
    root.title("Man o Ostad Chatroom")

    def send_message():
        message = message_entry.get()
        if message:
            message_entry.delete(0, END)  # پاک کردن پیام از ورودی
            chatbox.config(state=NORMAL)
            chatbox.insert(END, f"You: {message}\n", "self_message")
            chatbox.config(state=DISABLED)

            def send_to_server():
                try:
                    server.new_message(message , active_chat)
                    # chatbox.config(state=NORMAL)
                    # chatbox.insert(END, f"Server: {response.decode('utf-8')}\n")
                    # chatbox.config(state=DISABLED)
                except Exception as e:
                    print(f"Error sending message: {e}")

            threading.Thread(target=send_to_server, daemon=True).start()

    def send_file():
        # باز کردن پنجره انتخاب فایل
        file_path = filedialog.askopenfilename()  # این پنجره برای انتخاب فایل باز می‌شود
        if file_path:
            try:
                # خواندن محتوای فایل
                with open(file_path, "rb") as file:
                    file_data = file.read()
                
                # ارسال فایل به سرور
                threading.Thread(
                    target=lambda: server.new_message(
                        json.dumps({
                            "filename": file_path.split("/")[-1],  # نام فایل
                            "filedata": file_data.decode("latin1"),  # ارسال فایل به صورت رشته
                        }),
                        active_chat
                    ),
                    daemon=True
                ).start()
    
                # نمایش در چت‌باکس
                chatbox.config(state=NORMAL)
                chatbox.insert(END, f"You sent a file: {file_path.split('/')[-1]}\n", "self_message")
                chatbox.config(state=DISABLED)
    
            except Exception as e:
                print(f"Error sending file: {e}")
    
    
    def open_menu():
        menu_frame.place(x=0, y=0, width=200, relheight=1)
        toggle_menu_button.place_forget()

    def close_menu():
        menu_frame.place_forget()
        toggle_menu_button.place(x=10, y=50)

    def exit_chat():
        if messagebox.askyesno("Exit", "Are you sure you want to exit the chatroom?"):
            # del users_online[username]
            root.destroy()

    root.geometry("800x400")
    root.configure(bg="#FFC0CB")

    # منوی کاربران آنلاین
    menu_frame = Frame(root, bg="#2E3B4E")

    menu_label = Label(
        menu_frame,
        text="Online Users",
        font=("Arial", 12, "bold"),
        fg="white",
        bg="#2E3B4E",
    )
    menu_label.pack(pady=10)

    online_listbox = Listbox(
        menu_frame, font=("Arial", 12), bg="#FFFFFF", fg="black", height=10
    )
    online_listbox.bind("<<ListboxSelect>>", lambda event: on_item_click(event, chatbox))

    close_menu_button = Button(
        menu_frame,
        text="Close Menu",
        command=close_menu,
        font=("Arial", 12),
        bg="#FF1493",
        fg="white",
    )
    close_menu_button.pack(side=TOP, padx=10, pady=10)

    logout_button = Button(
        menu_frame,
        text="Logout",
        command=exit_chat,
        font=("Arial", 12),
        bg="#FF1493",
        fg="white",
    )
    logout_button.pack(side=BOTTOM, padx=10, pady=20)

    # سربرگ صفحه
    header_label = Label(
        root,
        text=f"Welcome {username} to Man o Ostad Chatroom",
        font=("Arial", 18, "bold"),
        fg="#FF1493",
        bg="#FFC0CB",
        anchor="center",
    )
    header_label.place(x=210, y=10, width=570, height=30)

    # قسمت چت
    chatbox_frame = Frame(root)
    chatbox_frame.place(x=210, y=50, width=570, height=230)

    chatbox = Text(chatbox_frame, font=("Arial", 12), state=DISABLED, bg="#FFFFFF")
    chatbox.pack(padx=10, pady=10, fill=BOTH, expand=True)
    threading.Thread(
        target=receive_messages, args=(chatbox, online_listbox), daemon=True
    ).start()
    # قسمت ارسال پیام
    message_frame = Frame(root, bg="#FFC0CB")
    message_frame.place(x=210, y=290, width=570, height=50)

    message_entry = Entry(message_frame, font=("Arial", 14), bd=2, relief=SOLID)
    message_entry.pack(side=LEFT, fill=X, expand=True, padx=5)

    send_button = Button(
        message_frame,
        text="Send",
        command=send_message,
        font=("Arial", 12),
        bg="#FF1493",
        fg="white",
    )
    send_button.pack(side=LEFT, padx=5)

    send_file_button = Button(
        message_frame,
        text="Send File",
        command=send_file,
        font=("Arial", 12),
        bg="#FF1493",
        fg="white",
    )
    send_file_button.pack(side=LEFT, padx=5)

    # دکمه باز کردن منو
    toggle_menu_button = Button(
        root,
        text="Toggle Menu",
        command=open_menu,
        font=("Arial", 12),
        bg="#FF1493",
        fg="white",
    )
    toggle_menu_button.place(x=10, y=50)


# اجرای صفحه ورود
root = Tk()
login_page(root)
root.mainloop()
