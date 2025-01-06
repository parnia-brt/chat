from db import *
import json


def vlidation_user_login(message_data):
    username = message_data.get('username')
    password = message_data.get('password')
    if username and password:
        user = get_user_logined(username, password)  # تلاش برای یافتن کاربر
        if user:
            data = {'login': 'success'}
        else:
            data = {'login': 'failed'}
    else:
        data = {'error': 'Invalid login data'}
    
    return (json.dumps(data).encode('utf-8'))

def register_user(message_data):
    print('in register_user')

    username = message_data.get('username')
    password = message_data.get('password')
    if username and password:
        user = register_user_in_db(username, password)  # تلاش برای یافتن کاربر
        if user:
            data = {'register': 'success'}
        else:
            data = {'register': 'failed'}
    else:
        data = {'error': 'Invalid register data'}
    
    return (json.dumps(data).encode('utf-8'))