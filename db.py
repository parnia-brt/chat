import pymysql

# اطلاعات اتصال به دیتابیس
connection = pymysql.connect(
    host='localhost',  # آدرس سرور دیتابیس (اگر روی سیستم خودتان است، localhost)
    user='root',  # نام کاربری
    password='',  # پسورد
    db='chatroom',  # نام دیتابیس
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor  # برای برگشت نتایج به صورت دیکشنری
)

def get_user_logined(username, password):
    try:
        with connection.cursor() as cursor:
            # نوشتن کوئری برای جستجو یوزر و پسورد
            sql = "SELECT * FROM users WHERE username = %s AND password = %s"
            
            # اجرای کوئری
            cursor.execute(sql, (username, password))
            
            # گرفتن نتایج
            result = cursor.fetchone()
            
            # اگر یوزر پیدا شود، آن را برمی‌گرداند
            if result:
                return result
            else:
                return None
    except pymysql.MySQLError as e:
        print(f"Error executing query: {e}")
        return None

def get_username(username):
    try:
        with connection.cursor() as cursor:
            # نوشتن کوئری برای جستجو یوزر و پسورد
            sql = "SELECT * FROM users WHERE username = %s"
            
            # اجرای کوئری
            cursor.execute(sql, (username))
            
            # گرفتن نتایج
            result = cursor.fetchone()
            
            # اگر یوزر پیدا شود، آن را برمی‌گرداند
            if result:
                return result
            else:
                return None
    except pymysql.MySQLError as e:
        print(f"Error executing query: {e}")
        return None


def register_user_in_db(username , password):
    try:
        with connection.cursor() as cursor:
            if get_username(username):
                return None
            # نوشتن کوئری برای جستجو یوزر و پسورد
            sql = "INSERT INTO `users`(`id`, `username`, `password`) VALUES (%s,%s,%s)"
            # اجرای کوئری
            cursor.execute(sql, (None , username, password))
            last_id = cursor.lastrowid
            # بازیابی کل اطلاعات ردیف ثبت‌شده
            sql_select = "SELECT * FROM users WHERE id = %s"
            cursor.execute(sql_select, (last_id,))
            row = cursor.fetchone()
    
            print("Inserted row:", row)
    
            connection.commit()
    except pymysql.MySQLError as e:
        print(f"Error executing query: {e}")
        return None