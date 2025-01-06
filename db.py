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
    finally:
        connection.close()

