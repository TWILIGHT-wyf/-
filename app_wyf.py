from flask import Flask, jsonify, request, redirect, url_for
from sqlalchemy import text
from config_wyf import BaseConfig
import auth_wyf as auth_wyf
import json
import random
import datetime
from redis import Redis
import pymssql
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

# 创建redis对象
redis_store = Redis(host=BaseConfig.REDIS_HOST, port=BaseConfig.REDIS_PORT, decode_responses=True)

# 跨域
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:8080"}})

# 添加配置数据库
app.config.from_object(BaseConfig)

# 显式设置 SECRET_KEY
app.config['SECRET_KEY'] = 'your_secret_key_here'

# 检查数据库连接是否成功
def check_db_connection():
    conn = pymssql.connect(server=BaseConfig.HOST, port=BaseConfig.PORT, user=BaseConfig.USERNAME, password=BaseConfig.PASSWORD, database=BaseConfig.DBNAME)
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    result = cursor.fetchone()
    print(result)
    conn.close()

check_db_connection()

# 根路径路由，重定向到 Vue 应用
@app.route("/", methods=["GET"])
def index():
    return redirect("http://localhost:8080")

@app.route("/api/user/register", methods=["POST"])
@cross_origin()
def user_register():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    telephone = data.get("telephone")
    role = data.get("role")

    print(f"接收到的注册数据: {data}")

    if not all([username, password, telephone, role]):
        return jsonify(status=400, message="Username, Password, Telephone, and Role are required"), 400

    # 检查手机号是否已经存在
    conn = pymssql.connect(server=BaseConfig.HOST, port=BaseConfig.PORT, user=BaseConfig.USERNAME, password=BaseConfig.PASSWORD, database=BaseConfig.DBNAME)
    cursor = conn.cursor(as_dict=True)
    check_sql = 'SELECT * FROM Users_wyf WHERE PhoneNumber=%s'
    cursor.execute(check_sql, (telephone,))
    existing_user = cursor.fetchone()
    conn.close()

    if existing_user:
        return jsonify(status=400, message=f"手机号 '{telephone}' 已经存在"), 400

    # 插入新用户记录
    conn = pymssql.connect(server=BaseConfig.HOST, port=BaseConfig.PORT, user=BaseConfig.USERNAME, password=BaseConfig.PASSWORD, database=BaseConfig.DBNAME)
    cursor = conn.cursor()
    sql = ('INSERT INTO Users_wyf (Username, PhoneNumber, Password, UserType) '
           'OUTPUT INSERTED.UserID '  # 获取插入的 UserID
           'VALUES (%s, %s, %s, %s)')
    cursor.execute(sql, (username, telephone, password, role))
    user_id = cursor.fetchone()[0]  # 获取 UserID
    conn.commit()
    conn.close()

    # 根据用户角色进行数据迁移
    if role == 'Vendor':
        migrate_to_vendors({'Username': username, 'PhoneNumber': telephone, 'Address': '', 'UserID': user_id})
    elif role == 'Rider':
        migrate_to_riders({'Username': username, 'RealName': '', 'PhoneNumber': telephone, 'Gender': '', 'UserID': user_id})

    return jsonify(status=200, message="注册成功")

from itsdangerous import TimestampSigner, URLSafeSerializer

def generate_token(user_id, secret_key, expiration=3600):
    signer = TimestampSigner(secret_key)
    serializer = URLSafeSerializer(secret_key)
    token = signer.sign(serializer.dumps(user_id)).decode('utf-8')
    return token

def verify_token(token, secret_key, max_age=3600):
    if token.startswith("Bearer "):
        token = token.split(" ")[1]
    signer = TimestampSigner(secret_key)
    serializer = URLSafeSerializer(secret_key)
    try:
        user_id = serializer.loads(signer.unsign(token, max_age=max_age))
        return user_id
    except Exception as e:
        return None

# 定义数据迁移函数
def migrate_users():
    # 检索 Users_wyf 表中的所有用户数据
    conn = pymssql.connect(server=BaseConfig.HOST, port=BaseConfig.PORT, user=BaseConfig.USERNAME, password=BaseConfig.PASSWORD, database=BaseConfig.DBNAME)
    cursor = conn.cursor(as_dict=True)
    sql = 'SELECT * FROM Users_wyf'
    cursor.execute(sql)
    users = cursor.fetchall()
    conn.close()

    for user in users:
        user_type = user['UserType']
        if user_type == 'Vendor':
            migrate_to_vendors(user)
        elif user_type == 'Rider':
            migrate_to_riders(user)

def migrate_to_riders(user):
    conn = pymssql.connect(server=BaseConfig.HOST, port=BaseConfig.PORT, user=BaseConfig.USERNAME, password=BaseConfig.PASSWORD, database=BaseConfig.DBNAME)
    cursor = conn.cursor(as_dict=True)
    
    # 检查是否已经存在相同的数据
    check_sql = 'SELECT * FROM Riders_wyf WHERE Username=%s OR PhoneNumber=%s'
    cursor.execute(check_sql, (user['Username'], user['PhoneNumber']))
    existing_rider = cursor.fetchone()
    
    if existing_rider:
        print(f"Rider with Username '{user['Username']}' or PhoneNumber '{user['PhoneNumber']}' already exists.")
        conn.close()
        return
    
    # 插入新数据
    sql = ('INSERT INTO Riders_wyf (Username, RealName, PhoneNumber, Gender, CurrentStatus, UserID) '
           'VALUES (%s, %s, %s, %s, %s, %s)')
    cursor.execute(sql, (user['Username'], '', user['PhoneNumber'], '', 'Available', user['UserID']))
    conn.commit()
    conn.close()
    print(f"Rider with Username '{user['Username']}' and PhoneNumber '{user['PhoneNumber']}' added successfully.")

# 初始化调度器并添加任务
scheduler = BackgroundScheduler()
scheduler.add_job(migrate_users, IntervalTrigger(hours=1))  # 每小时执行一次
scheduler.start()



@app.route("/api/user/login", methods=["POST"])
@cross_origin()
def user_login():
    data = request.json
    phone_number = data.get("PhoneNumber")
    password = data.get("password")

    if not all([phone_number, password]):
        return jsonify(status=400, message="PhoneNumber and Password are required"), 400

    app.logger.debug(f"Received login data: {data}")

    conn = pymssql.connect(server=BaseConfig.HOST, port=BaseConfig.PORT, user=BaseConfig.USERNAME, password=BaseConfig.PASSWORD, database=BaseConfig.DBNAME)
    cursor = conn.cursor(as_dict=True)

    # 查询用户信息
    sql = 'SELECT * FROM Users_wyf WHERE PhoneNumber=%s AND Password=%s'
    cursor.execute(sql, (phone_number, password))
    user = cursor.fetchone()

    if not user:
        conn.close()
        app.logger.debug(f"User not found for phone_number: {phone_number}")
        return jsonify(status=401, message="Invalid PhoneNumber or password"), 401

    user_type = user['UserType']

    # 根据用户角色获取相应的 ID
    if user_type == 'Rider':
        # 查询 Riders_wyf 表获取 RiderID
        sql = 'SELECT RiderID FROM Riders_wyf WHERE UserID=%s'
        cursor.execute(sql, (user['UserID'],))
        rider_info = cursor.fetchone()
        if not rider_info:
            conn.close()
            app.logger.debug(f"Rider ID not found for user: {user['UserID']}")
            return jsonify(status=401, message="Rider ID not found"), 401
        user_id = rider_info['RiderID']
    else:
        user_id = user['UserID']

    conn.close()

    token = generate_token(user_id, app.config['SECRET_KEY'])
    return jsonify(
        status=200,
        message="Login successful",
        role=user_type,
        token=token,
        user_id=user_id,
        rider_id=rider_info['RiderID'] if user_type == 'Rider' else None  # 确保返回 RiderID
    ), 200
def migrate_to_vendors(user):
    conn = pymssql.connect(server=BaseConfig.HOST, port=BaseConfig.PORT, user=BaseConfig.USERNAME, password=BaseConfig.PASSWORD, database=BaseConfig.DBNAME)
    cursor = conn.cursor(as_dict=True)
    
    # 检查是否已经存在相同的数据
    check_sql = 'SELECT * FROM Vendors_wyf WHERE VendorName=%s OR ContactInfo=%s'
    cursor.execute(check_sql, (user['Username'], user['PhoneNumber']))
    existing_vendor = cursor.fetchone()
    
    if existing_vendor:
        print(f"Vendor with Username '{user['Username']}' or PhoneNumber '{user['PhoneNumber']}' already exists.")
        conn.close()
        return
    
    # 插入新数据
    sql = ('INSERT INTO Vendors_wyf (VendorName, ContactInfo, Description, VendorAddress, CustomerReviews, Rating, UserID) '
           'VALUES (%s, %s, %s, %s, %s, %s, %s)')
    cursor.execute(sql, (user['Username'], user['PhoneNumber'], '', user['Address'], '', 0, user['UserID']))
    conn.commit()
    conn.close()
import os
from werkzeug.utils import secure_filename

# 配置文件夹
app.config['UPLOAD_FOLDER'] = '/path/to/upload/folder'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
@app.route("/api/manager/shop", methods=["POST", "GET", "DELETE", "PUT"])
@cross_origin()
def manage_shop():
    try:
        token = request.headers.get('Authorization')
        app.logger.debug(f"Received token: {token}")
        if not token:
            return jsonify(status=401, message="Token is missing"), 401

        user_id = verify_token(token, app.config['SECRET_KEY'])
        if not user_id:
            return jsonify(status=401, message="Invalid token"), 401

        if request.method == 'POST':
            shop_data = request.form
            shop_name = shop_data.get("shop_name")
            address = shop_data.get("address")
            description = shop_data.get("description")
            contact = shop_data.get("contact")

            if not all([shop_name, address, description, contact]):
                return jsonify(status=400, message="All fields are required"), 400

            # 处理图片上传
            logo_image = request.files.get('logo_image')
            logo_path = None
            if logo_image:
                filename = secure_filename(logo_image.filename)
                logo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                logo_image.save(logo_path)

            # 检查是否已经有店铺
            conn = pymssql.connect(server=BaseConfig.HOST, port=BaseConfig.PORT, user=BaseConfig.USERNAME, password=BaseConfig.PASSWORD, database=BaseConfig.DBNAME)
            cursor = conn.cursor(as_dict=True)
            check_sql = 'SELECT * FROM Vendors_wyf WHERE VendorName=%s AND UserID=%d'
            cursor.execute(check_sql, (shop_name, user_id))
            existing_shop = cursor.fetchone()
            conn.close()

            if existing_shop:
                return jsonify(status=400, message="Shop already exists"), 400

            # 插入新店铺记录
            conn = pymssql.connect(server=BaseConfig.HOST, port=BaseConfig.PORT, user=BaseConfig.USERNAME, password=BaseConfig.PASSWORD, database=BaseConfig.DBNAME)
            cursor = conn.cursor()
            sql = ('INSERT INTO Vendors_wyf (VendorName, ContactInfo, Description, VendorAddress, Rating, UserID, LogoImage) '
                   'VALUES (%s, %s, %s, %s, %s, %s, %s)')
            cursor.execute(sql, (shop_name, contact, description, address, 0, user_id, logo_path))
            conn.commit()
            conn.close()

            return jsonify(status=200, message="Shop added successfully")

        if request.method == 'GET':
            conn = pymssql.connect(server=BaseConfig.HOST, port=BaseConfig.PORT, user=BaseConfig.USERNAME, password=BaseConfig.PASSWORD, database=BaseConfig.DBNAME)
            cursor = conn.cursor(as_dict=True)
            sql = 'SELECT VendorName AS shop_name, VendorAddress AS address, Description AS description, ContactInfo AS contact, LogoImage FROM Vendors_wyf WHERE UserID=%d' % user_id
            cursor.execute(sql)
            shops = cursor.fetchall()
            conn.close()

            return jsonify(status=200, data=shops)

        elif request.method == 'PUT':
            data = request.form  
            shop_name = data.get("shop_name")
            address = data.get("address")
            description = data.get("description")
            contact = data.get("contact")

            if not all([shop_name, address, description, contact]):
                return jsonify(status=400, message="All fields are required"), 400

            try:
                conn = pymssql.connect(server=BaseConfig.HOST, port=BaseConfig.PORT, user=BaseConfig.USERNAME, password=BaseConfig.PASSWORD, database=BaseConfig.DBNAME)
                cursor = conn.cursor()

                # 处理图片上传
                logo_image = request.files.get('logo_image')
                logo_path = None
                if logo_image:
                    filename = secure_filename(logo_image.filename)
                    logo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    logo_image.save(logo_path)

                # 构建 SQL 语句
                update_fields = []
                params = []

                if contact:
                    update_fields.append("ContactInfo=%s")
                    params.append(contact)
                if description:
                    update_fields.append("Description=%s")
                    params.append(description)
                if address:
                    update_fields.append("VendorAddress=%s")
                    params.append(address)
                if logo_path:
                    update_fields.append("LogoImage=%s")
                    params.append(logo_path)

                # 使用 UserID 作为筛选条件
                sql = f"UPDATE Vendors_wyf SET {', '.join(update_fields)} WHERE UserID=%d"
                cursor.execute(sql, tuple(params + [user_id]))
                conn.commit()  # 确保提交事务
                conn.close()
            except Exception as e:
                app.logger.error(f"Error updating shop {shop_name}: {e}")
                return jsonify(status=500, message="Internal server error"), 500

            return jsonify(status=200, message="Shop updated successfully")

        elif request.method == 'DELETE':
            data = request.json  # 使用 request.json 获取 JSON 数据
            shop_name = data.get("shop_name")

            if not shop_name:
                return jsonify(status=400, message="Shop name is required"), 400

            try:
                conn = pymssql.connect(server=BaseConfig.HOST, port=BaseConfig.PORT, user=BaseConfig.USERNAME, password=BaseConfig.PASSWORD, database=BaseConfig.DBNAME)
                cursor = conn.cursor()

                sql = "DELETE FROM Vendors_wyf WHERE VendorName=%s AND UserID=%d"
                cursor.execute(sql, (shop_name, user_id))
                conn.commit()
                conn.close()
            except Exception as e:
                app.logger.error(f"Error deleting shop {shop_name}: {e}")
                return jsonify(status=500, message="Internal server error"), 500

            return jsonify(status=200, message="Shop deleted successfully")

        app.logger.info("Operation completed successfully")
        return jsonify(status=200, message="Operation completed successfully")

    except Exception as e:
        app.logger.error(f"Error in manage_shop: {e}")
        return jsonify(status=500, message="Internal server error"), 500
    






@app.route("/api/manager/dishes", methods=["POST"])
@cross_origin()
def add_dish():
    try:
        token = request.headers.get('Authorization')
        if not token:
            return jsonify(status=401, message="Token is missing"), 401

        user_id = verify_token(token, app.config['SECRET_KEY'])
        if not user_id:
            return jsonify(status=401, message="Invalid token"), 401

        dish_data = request.json
        app.logger.debug(f"Received dish data: {dish_data}")

        dish_name = dish_data.get("DishName")
        stock = dish_data.get("QuantityInStock")
        description = dish_data.get("Description")
        unit_price = dish_data.get("UnitPrice", 0)  # 默认价格为0

        if not all([dish_name, stock, description]):
            return jsonify(status=400, message="DishName, QuantityInStock, and Description are required"), 400

        # 查询 Vendors_wyf 表以获取 VendorID
        conn = pymssql.connect(server=BaseConfig.HOST, port=BaseConfig.PORT, user=BaseConfig.USERNAME, password=BaseConfig.PASSWORD, database=BaseConfig.DBNAME)
        cursor = conn.cursor(as_dict=True)
        sql = 'SELECT VendorID FROM Vendors_wyf WHERE UserID=%d' % user_id
        cursor.execute(sql)
        vendor = cursor.fetchone()
        conn.close()

        if not vendor:
            return jsonify(status=400, message="Vendor not found for the user"), 400

        vendor_id = vendor['VendorID']

        # 插入新菜品记录
        conn = pymssql.connect(server=BaseConfig.HOST, port=BaseConfig.PORT, user=BaseConfig.USERNAME, password=BaseConfig.PASSWORD, database=BaseConfig.DBNAME)
        cursor = conn.cursor()
        sql = ('INSERT INTO Dishes_wyf (VendorID, DishName, UnitPrice, QuantityInStock, Description) '
               'VALUES (%s, %s, %s, %s, %s)')
        cursor.execute(sql, (vendor_id, dish_name, unit_price, stock, description))
        conn.commit()
        conn.close()

        return jsonify(status=200, message="Dish added successfully")

    except Exception as e:
        app.logger.error(f"Error adding dish: {e}")
        return jsonify(status=500, message="Internal server error"), 500
    
@app.route("/api/manager/dishes", methods=["DELETE"])
@cross_origin()
def delete_dish():
    try:
        token = request.headers.get('Authorization')
        if not token:
            return jsonify(status=401, message="Token is missing"), 401

        user_id = verify_token(token, app.config['SECRET_KEY'])
        if not user_id:
            return jsonify(status=401, message="Invalid token"), 401

        data = request.json
        app.logger.debug(f"Received data: {data}")  # 添加日志

        name = data.get("name")

        if not name:
            app.logger.error("Dish name is required")
            return jsonify(status=400, message="Dish name is required"), 400

        conn = pymssql.connect(server=BaseConfig.HOST, port=BaseConfig.PORT, user=BaseConfig.USERNAME, password=BaseConfig.PASSWORD, database=BaseConfig.DBNAME)
        cursor = conn.cursor()

        sql = "DELETE FROM Dishes_wyf WHERE DishName=%s"
        cursor.execute(sql, (name,))
        conn.commit()
        conn.close()

        return jsonify(status=200, message="Dish deleted successfully")

    except Exception as e:
        app.logger.error(f"Error deleting dish {name}: {e}")
        return jsonify(status=500, message="Internal server error"), 500


@app.route("/api/manager/dishes", methods=["GET"])
@cross_origin()
def get_dishes():
    try:
        token = request.headers.get('Authorization')
        if not token:
            return jsonify(status=401, message="Token is missing"), 401

        user_id = verify_token(token, app.config['SECRET_KEY'])
        if not user_id:
            return jsonify(status=401, message="Invalid token"), 401

        conn = pymssql.connect(server=BaseConfig.HOST, port=BaseConfig.PORT, user=BaseConfig.USERNAME, password=BaseConfig.PASSWORD, database=BaseConfig.DBNAME)
        cursor = conn.cursor(as_dict=True)
        sql = '''
        SELECT d.*
        FROM Dishes_wyf d
        JOIN Vendors_wyf v ON d.VendorID = v.VendorID
        WHERE v.UserID = %d
        ''' % user_id
        cursor.execute(sql)
        dishes = cursor.fetchall()
        conn.close()

        return jsonify(status=200, tabledata=dishes)

    except Exception as e:
        app.logger.error(f"Error getting dishes: {e}")
        return jsonify(status=500, message="Internal server error"), 500
    

@app.route("/api/manager/dishes", methods=["PUT"])
@cross_origin()
def update_dish():
    try:
        token = request.headers.get('Authorization')
        if not token:
            app.logger.error("Token is missing")
            return jsonify(status=401, message="Token is missing"), 401

        user_id = verify_token(token, app.config['SECRET_KEY'])
        if not user_id:
            app.logger.error("Invalid token")
            return jsonify(status=401, message="Invalid token"), 401

        dish_data = request.json
        app.logger.debug(f"Received dish data: {dish_data}")

        dish_id = dish_data.get("DishID")  # 修改这里
        new_stock = dish_data.get("QuantityInStock")
        new_description = dish_data.get("Description")
        new_dish_name = dish_data.get("DishName")
        new_unit_price = dish_data.get("UnitPrice")

        if not dish_id:
            app.logger.error("Dish ID is required")
            return jsonify(status=400, message="Dish ID is required"), 400

        # 可选字段检查
        if not any([new_stock, new_description, new_dish_name, new_unit_price]):
            app.logger.error("At least one field to update is required")
            return jsonify(status=400, message="At least one field to update is required"), 400

        conn = pymssql.connect(server=BaseConfig.HOST, port=BaseConfig.PORT, user=BaseConfig.USERNAME, password=BaseConfig.PASSWORD, database=BaseConfig.DBNAME)
        cursor = conn.cursor()

        # 构建 SQL 更新语句
        update_fields = []
        params = []

        if new_stock is not None:  # 确保 stock 可以被设置为 0
            try:
                new_stock = int(new_stock)  # 尝试将 stock 转换为整数
            except ValueError:
                try:
                    new_stock = float(new_stock)  # 如果转换为整数失败，尝试转换为浮点数
                except ValueError:
                    app.logger.error("Invalid stock value")
                    return jsonify(status=400, message="Invalid stock value"), 400
            update_fields.append("QuantityInStock=%s")
            params.append(new_stock)
        if new_description:
            update_fields.append("Description=%s")
            params.append(new_description)
        if new_dish_name:
            update_fields.append("DishName=%s")
            params.append(new_dish_name)
        if new_unit_price is not None:
            try:
                new_unit_price = float(new_unit_price)  # 尝试将 unit_price 转换为浮点数
            except ValueError:
                app.logger.error("Invalid unit price value")
                return jsonify(status=400, message="Invalid unit price value"), 400
            update_fields.append("UnitPrice=%s")
            params.append(new_unit_price)

        # 使用 DishID 作为筛选条件
        sql = f"UPDATE Dishes_wyf SET {', '.join(update_fields)} WHERE DishID=%s"
        cursor.execute(sql, tuple(params + [dish_id]))
        conn.commit()
        conn.close()

        return jsonify(status=200, message="Dish updated successfully")

    except Exception as e:
        app.logger.error(f"Error updating dish {dish_id}: {e}")
        return jsonify(status=500, message="Internal server error"), 500

@app.route("/api/user/shop", methods=["GET"])
@cross_origin()
def get_shops():
    try:
        token = request.headers.get('Authorization')
        if not token:
            return jsonify(status=401, message="Token is missing"), 401

        user_id = verify_token(token, app.config['SECRET_KEY'])
        if not user_id:
            return jsonify(status=401, message="Invalid token"), 401

        conn = pymssql.connect(server=BaseConfig.HOST, port=BaseConfig.PORT, user=BaseConfig.USERNAME, password=BaseConfig.PASSWORD, database=BaseConfig.DBNAME)
        cursor = conn.cursor(as_dict=True)
        sql = 'SELECT VendorID, VendorName, VendorAddress, Rating FROM Vendors_wyf WHERE UserID=%d' % user_id
        cursor.execute(sql)
        shops = cursor.fetchall()
        conn.close()

        return jsonify(status=200, tabledata=shops)

    except Exception as e:
        app.logger.error(f"Error getting shops: {e}")
        return jsonify(status=500, message="Internal server error"), 500

@app.route("/api/user/dishes/<int:vendor_id>", methods=["GET"])
@cross_origin()
def get_vendor_dishes(vendor_id):
    try:
        conn = pymssql.connect(server=BaseConfig.HOST, port=BaseConfig.PORT, user=BaseConfig.USERNAME, password=BaseConfig.PASSWORD, database=BaseConfig.DBNAME)
        cursor = conn.cursor(as_dict=True)
        sql = 'SELECT DishID, DishName, UnitPrice, QuantityInStock, MonthlySales, Description FROM Dishes_wyf WHERE VendorID=%d' % vendor_id
        cursor.execute(sql)
        dishes = cursor.fetchall()
        conn.close()

        return jsonify(status=200, tabledata=dishes)

    except Exception as e:
        app.logger.error(f"Error getting vendor dishes: {e}")
        return jsonify(status=500, message="Internal server error"), 500
    
@app.route("/api/user/update", methods=["PUT"])
@cross_origin()
def update_user_info():
    try:
        token = request.headers.get('Authorization')
        if not token:
            return jsonify(status=401, message="Token is missing"), 401

        user_id = verify_token(token, app.config['SECRET_KEY'])
        if not user_id:
            return jsonify(status=401, message="Invalid token"), 401

        data = request.get_json()
        username = data.get("Username")
        real_name = data.get("RealName")
        age = data.get("Age")
        gender = data.get("Gender")

        if not all([username, real_name, age, gender]):
            return jsonify(status=400, message="Missing required fields"), 400

        # 确保 age 是整数类型
        try:
            age = int(age)
        except ValueError:
            return jsonify(status=400, message="Age must be an integer"), 400

        conn = pymssql.connect(server=BaseConfig.HOST, port=BaseConfig.PORT, user=BaseConfig.USERNAME, password=BaseConfig.PASSWORD, database=BaseConfig.DBNAME)
        cursor = conn.cursor()

        # 更新 Users 表
        sql_users = "UPDATE Users_wyf SET Username=%s, RealName=%s, Age=%s, Gender=%s WHERE UserID=%s"
        params_users = [username, real_name, age, gender]
        cursor.execute(sql_users, tuple(params_users + [user_id]))

        # 更新 Riders_wyf 表
        sql_riders = "UPDATE Riders_wyf SET Username=%s, RealName=%s,  Gender=%s WHERE UserID=%s"
        params_riders = [username, real_name, gender]
        cursor.execute(sql_riders, tuple(params_riders + [user_id]))

        conn.commit()
        conn.close()

        return jsonify(status=200, message="User info updated successfully")

    except Exception as e:
        app.logger.error(f"Error updating user info: {e}")
        return jsonify(status=500, message="Internal server error"), 500

@app.route("/api/user/usermsg", methods=["GET"])
@cross_origin()
def get_user_info():
    token = request.headers.get('Authorization')
    app.logger.debug(f"Received token: {token}")
    if not token:
        return jsonify(status=401, message="Token is missing"), 401

    user_id = verify_token(token, app.config['SECRET_KEY'])
    app.logger.debug(f"Verified user_id: {user_id}")
    if not user_id:
        return jsonify(status=401, message="Invalid token"), 401

    try:
        conn = pymssql.connect(server=BaseConfig.HOST, port=BaseConfig.PORT, user=BaseConfig.USERNAME, password=BaseConfig.PASSWORD, database=BaseConfig.DBNAME)
        cursor = conn.cursor(as_dict=True)
        sql = 'SELECT Username, RealName, Age, Gender, PhoneNumber, Address FROM Users_wyf WHERE UserID=%d' % user_id
        app.logger.debug(f"Executing SQL: {sql}")
        cursor.execute(sql)
        user_info = cursor.fetchone()
        conn.close()

        if not user_info:
            app.logger.debug(f"User not found for user_id: {user_id}")
            return jsonify(status=404, message="User not found"), 404

        app.logger.debug(f"User info: {user_info}")
        return jsonify(status=200, data=user_info)

    except Exception as e:
        app.logger.error(f"Error getting user info: {e}")
        return jsonify(status=500, message="Internal server error"), 500


@app.route("/api/user/addorder", methods=["POST"])
@cross_origin()
def add_order():
    try:
        token = request.headers.get('Authorization')
        if not token:
            return jsonify(status=401, message="Token is missing"), 401

        user_id = verify_token(token, app.config['SECRET_KEY'])
        if not user_id:
            return jsonify(status=401, message="Invalid token"), 401

        order_data = request.json
        vendor_id = order_data.get("VendorID")
        dishes = order_data.get("dishes")
        cons_name = order_data.get("cons_name")
        cons_addre = order_data.get("cons_addre")

        if not all([vendor_id, dishes, cons_name, cons_addre]):
            return jsonify(status=400, message="All fields are required"), 400

        # 获取商家地址和商家名称
        conn = pymssql.connect(server=BaseConfig.HOST, port=BaseConfig.PORT, user=BaseConfig.USERNAME, password=BaseConfig.PASSWORD, database=BaseConfig.DBNAME)
        cursor = conn.cursor(as_dict=True)
        sql = 'SELECT VendorAddress, VendorName FROM Vendors_wyf WHERE VendorID=%d' % vendor_id
        cursor.execute(sql)
        vendor = cursor.fetchone()
        conn.close()

        if not vendor:
            return jsonify(status=400, message="Vendor not found"), 400

        vendor_address = vendor['VendorAddress']
        vendor_name = vendor['VendorName']

        # 计算订单总价
        total_price = 0
        for dish in dishes:
            unit_price = dish.get("UnitPrice")
            quantity = dish.get("quantity")

            # 确保 unit_price 和 quantity 是数值类型
            if unit_price is None or quantity is None:
                return jsonify(status=400, message="UnitPrice and quantity are required for each dish"), 400

            try:
                unit_price = float(unit_price)
                quantity = int(quantity)
            except ValueError:
                return jsonify(status=400, message="UnitPrice must be a number and quantity must be an integer"), 400

            total_price += unit_price * quantity

        # 插入订单记录
        conn = pymssql.connect(server=BaseConfig.HOST, port=BaseConfig.PORT, user=BaseConfig.USERNAME, password=BaseConfig.PASSWORD, database=BaseConfig.DBNAME)
        cursor = conn.cursor()

        # 创建订单
        order_sql = ('INSERT INTO Orders_wyf (UserID, VendorID, VendorAddress, VendorName, ConsigneeName, ConsigneeAddress, status, Price) '
                     'VALUES (%s, %s, %s, %s, %s, %s, %s, %s)')
        cursor.execute(order_sql, (user_id, vendor_id, vendor_address, vendor_name, cons_name, cons_addre, '商家已接单', total_price))
        conn.commit()

        # 获取刚插入的 OrderID
        order_id_sql = 'SELECT SCOPE_IDENTITY()'
        cursor.execute(order_id_sql)
        order_id = cursor.fetchone()[0]

        # 插入订单详情
        for dish in dishes:
            dish_id = dish.get("DishID")
            quantity = dish.get("quantity")
            unit_price = dish.get("UnitPrice")

            if not all([dish_id, quantity, unit_price]):
                conn.close()
                return jsonify(status=400, message="All fields in dishes are required"), 400

            try:
                unit_price = float(unit_price)
                quantity = int(quantity)
            except ValueError:
                conn.close()
                return jsonify(status=400, message="UnitPrice must be a number and quantity must be an integer"), 400

            order_details_sql = ('INSERT INTO OrderDetails_wyf (OrderID, DishID, Quantity, UnitPrice) '
                                 'VALUES (%s, %s, %s, %s)')
            cursor.execute(order_details_sql, (order_id, dish_id, quantity, unit_price))
            conn.commit()

        conn.close()
        return jsonify(status=200, message="Order added successfully", order_id=order_id)

    except Exception as e:
        app.logger.error(f"Error adding order: {e}")
        return jsonify(status=500, message="Internal server error"), 500

@app.route("/api/user/order/accept", methods=["PUT"])
@cross_origin()
def accept_order():
    try:
        token = request.headers.get('Authorization')
        if not token:
            return jsonify(status=401, message="Token is missing"), 401

        user_id = verify_token(token, app.config['SECRET_KEY'])
        if not user_id:
            return jsonify(status=401, message="Invalid token"), 401

        data = request.json
        order_id = data.get("orderId")
        rider_id = data.get("riderId")

        if not all([order_id, rider_id]):
            return jsonify(status=400, message="OrderID and RiderID are required"), 400

        # 获取骑手名字
        conn = pymssql.connect(server=BaseConfig.HOST, port=BaseConfig.PORT, user=BaseConfig.USERNAME, password=BaseConfig.PASSWORD, database=BaseConfig.DBNAME)
        cursor = conn.cursor(as_dict=True)
        cursor.execute("SELECT RealName FROM Riders_wyf WHERE RiderID=%s", (rider_id,))
        rider = cursor.fetchone()
        if not rider:
            return jsonify(status=400, message="Invalid RiderID"), 400
        rider_name = rider['RealName']

        # 更新订单状态并分配骑手
        sql = "UPDATE Orders_wyf SET RiderID=%s, RiderName=%s, Status='骑手配送中' WHERE OrderID=%s"
        cursor.execute(sql, (rider_id, rider_name, order_id))
        conn.commit()
        conn.close()

        return jsonify(status=200, message="Order accepted successfully")

    except Exception as e:
        app.logger.error(f"Error accepting order: {e}")
        return jsonify(status=500, message="Internal server error"), 500
@app.route("/api/user/unsend", methods=["GET"])
@cross_origin()
def get_unsent_orders():
    try:
        token = request.headers.get('Authorization')
        if not token:
            return jsonify(status=401, message="Token is missing"), 401

        user_id = verify_token(token, app.config['SECRET_KEY'])
        if not user_id:
            return jsonify(status=401, message="Invalid token"), 401

        conn = pymssql.connect(server=BaseConfig.HOST, port=BaseConfig.PORT, user=BaseConfig.USERNAME, password=BaseConfig.PASSWORD, database=BaseConfig.DBNAME)
        cursor = conn.cursor(as_dict=True)
        
        # 获取 VendorID
        cursor.execute('SELECT VendorID FROM Vendors_wyf WHERE UserID = %d' % user_id)
        vendor = cursor.fetchone()
        if not vendor:
            return jsonify(status=404, message="Vendor not found"), 404
        vendor_id = vendor['VendorID']

        sql = '''
        SELECT 
            o.OrderID AS order_id, 
            v.VendorName AS shop_name, 
            d.DishName AS dish_name, 
            r.RealName AS rider_name, 
            o.ConsigneeName AS cons_name, 
            o.Price AS price, 
            o.OrderTime AS create_time, 
            '未送达' AS deliver_time
        FROM 
            Orders_wyf o 
        LEFT JOIN 
            Riders_wyf r ON o.RiderID = r.RiderID 
        LEFT JOIN 
            Vendors_wyf v ON o.VendorID = v.VendorID
        LEFT JOIN 
            OrderDetails_wyf od ON o.OrderID = od.OrderID
        LEFT JOIN 
            Dishes_wyf d ON od.DishID = d.DishID
        WHERE 
            o.Status = '商家已接单' AND o.VendorID = %d
        ''' % vendor_id
        cursor.execute(sql)
        orders = cursor.fetchall()
        conn.close()

        # 格式化时间
        for order in orders:
            if order['create_time']:
                order['create_time'] = order['create_time'].strftime('%Y年%m月%d日 %H:%M:%S')

        return jsonify(status=200, tabledata=orders)

    except Exception as e:
        app.logger.error(f"Error getting unsent orders: {e}")
        return jsonify(status=500, message="Internal server error"), 500
@app.route("/api/user/sending", methods=["GET"])
@cross_origin()
def get_sending_orders():
    try:
        token = request.headers.get('Authorization')
        if not token:
            return jsonify(status=401, message="Token is missing"), 401

        user_id = verify_token(token, app.config['SECRET_KEY'])
        if not user_id:
            return jsonify(status=401, message="Invalid token"), 401

        conn = pymssql.connect(server=BaseConfig.HOST, port=BaseConfig.PORT, user=BaseConfig.USERNAME, password=BaseConfig.PASSWORD, database=BaseConfig.DBNAME)
        cursor = conn.cursor(as_dict=True)
        
        # 获取 VendorID
        cursor.execute('SELECT VendorID FROM Vendors_wyf WHERE UserID = %d' % user_id)
        vendor = cursor.fetchone()
        if not vendor:
            return jsonify(status=404, message="Vendor not found"), 404
        vendor_id = vendor['VendorID']

        sql = '''
        SELECT 
            o.OrderID AS order_id, 
            v.VendorName AS shop_name, 
            d.DishName AS dish_name, 
            r.RealName AS rider_name, 
            o.ConsigneeName AS cons_name, 
            o.Price AS price, 
            o.OrderTime AS create_time, 
            '配送中' AS deliver_time
        FROM 
            Orders_wyf o 
        LEFT JOIN 
            Riders_wyf r ON o.RiderID = r.RiderID 
        LEFT JOIN 
            Vendors_wyf v ON o.VendorID = v.VendorID
        LEFT JOIN 
            OrderDetails_wyf od ON o.OrderID = od.OrderID
        LEFT JOIN 
            Dishes_wyf d ON od.DishID = d.DishID
        WHERE 
            o.Status = '骑手配送中' AND o.VendorID = %d
        ''' % vendor_id
        cursor.execute(sql)
        orders = cursor.fetchall()
        conn.close()

        # 格式化时间
        for order in orders:
            if order['create_time']:
                order['create_time'] = order['create_time'].strftime('%Y年%m月%d日 %H:%M:%S')

        return jsonify(status=200, tabledata=orders)

    except Exception as e:
        app.logger.error(f"Error getting sending orders: {e}")
        return jsonify(status=500, message="Internal server error"), 500
    

import datetime

@app.route("/api/user/deliver", methods=["PUT"])
@cross_origin()
def mark_order_as_delivered():
    try:
        token = request.headers.get('Authorization')
        if not token:
            return jsonify(status=401, message="Token is missing"), 401

        user_id = verify_token(token, app.config['SECRET_KEY'])
        if not user_id:
            return jsonify(status=401, message="Invalid token"), 401

        data = request.get_json()  # 确保正确解析 JSON 数据
        order_id = data.get("orderId")

        if not order_id:
            return jsonify(status=400, message="Order ID is required"), 400

        # 获取当前时间并格式化为数据库兼容的格式
        deliver_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        conn = pymssql.connect(server=BaseConfig.HOST, port=BaseConfig.PORT, user=BaseConfig.USERNAME, password=BaseConfig.PASSWORD, database=BaseConfig.DBNAME)
        cursor = conn.cursor()

        # 更新订单状态和送达时间
        sql = "UPDATE Orders_wyf SET Status='已完成', Time=%s WHERE OrderID=%s"
        cursor.execute(sql, (deliver_time, order_id))
        conn.commit()
        conn.close()

        return jsonify(status=200, message="Order marked as delivered successfully")

    except Exception as e:
        app.logger.error(f"Error marking order as delivered: {e}")
        return jsonify(status=500, message="Internal server error"), 500
    
@app.route("/api/user/order", methods=["DELETE"])
@cross_origin()
def delete_order():
    try:
        token = request.headers.get('Authorization')
        if not token:
            return jsonify(status=401, message="Token is missing"), 401

        user_id = verify_token(token, app.config['SECRET_KEY'])
        if not user_id:
            return jsonify(status=401, message="Invalid token"), 401

        data = request.json
        order_id = data.get("orderId")

        if not order_id:
            return jsonify(status=400, message="Order ID is required"), 400

        conn = pymssql.connect(server=BaseConfig.HOST, port=BaseConfig.PORT, user=BaseConfig.USERNAME, password=BaseConfig.PASSWORD, database=BaseConfig.DBNAME)
        cursor = conn.cursor()

        sql = "DELETE FROM Orders_wyf WHERE OrderID=%s"
        cursor.execute(sql, (order_id,))
        conn.commit()
        conn.close()

        return jsonify(status=200, message="Order deleted successfully")

    except Exception as e:
        app.logger.error(f"Error deleting order {order_id}: {e}")
        return jsonify(status=500, message="Internal server error"), 500

import datetime

@app.route("/api/user/finished", methods=["GET"])
@cross_origin()
def get_finished_orders():
    try:
        token = request.headers.get('Authorization')
        if not token:
            return jsonify(status=401, message="Token is missing"), 401

        user_id = verify_token(token, app.config['SECRET_KEY'])
        if not user_id:
            return jsonify(status=401, message="Invalid token"), 401

        conn = pymssql.connect(server=BaseConfig.HOST, port=BaseConfig.PORT, user=BaseConfig.USERNAME, password=BaseConfig.PASSWORD, database=BaseConfig.DBNAME)
        cursor = conn.cursor(as_dict=True)
        
        # 获取 VendorID
        cursor.execute('SELECT VendorID FROM Vendors_wyf WHERE UserID = %d' % user_id)
        vendor = cursor.fetchone()
        if not vendor:
            return jsonify(status=404, message="Vendor not found"), 404
        vendor_id = vendor['VendorID']

        sql = '''
        SELECT 
            o.OrderID AS order_id, 
            v.VendorName AS shop_name, 
            d.DishName AS dish_name, 
            r.RealName AS rider_name, 
            o.ConsigneeName AS cons_name, 
            o.Price AS price, 
            o.OrderTime AS create_time, 
            o.Time AS deliver_time
        FROM 
            Orders_wyf o 
        LEFT JOIN 
            Riders_wyf r ON o.RiderID = r.RiderID 
        LEFT JOIN 
            Vendors_wyf v ON o.VendorID = v.VendorID
        LEFT JOIN 
            OrderDetails_wyf od ON o.OrderID = od.OrderID
        LEFT JOIN 
            Dishes_wyf d ON od.DishID = d.DishID
        WHERE 
            o.Status = '已完成' AND o.VendorID = %d
        ''' % vendor_id
        cursor.execute(sql)
        orders = cursor.fetchall()
        conn.close()

        # 格式化时间
        for order in orders:
            if order['create_time']:
                order['create_time'] = order['create_time'].strftime('%Y年%m月%d日 %H:%M:%S')
            if order['deliver_time']:
                order['deliver_time'] = order['deliver_time'].strftime('%Y年%m月%d日 %H:%M:%S')

        return jsonify(status=200, tabledata=orders)

    except Exception as e:
        app.logger.error(f"Error getting finished orders: {e}")
        return jsonify(status=500, message="Internal server error"), 500
    
@app.route("/api/rider/info", methods=["GET"])
@cross_origin()
def get_rider_info():
    token = request.headers.get('Authorization')
    app.logger.debug(f"Received token: {token}")
    if not token:
        return jsonify(status=401, message="Token is missing"), 401

    user_id = verify_token(token, app.config['SECRET_KEY'])
    app.logger.debug(f"Verified user_id: {user_id}")
    if not user_id:
        return jsonify(status=401, message="Invalid token"), 401

    try:
        conn = pymssql.connect(server=BaseConfig.HOST, port=BaseConfig.PORT, user=BaseConfig.USERNAME, password=BaseConfig.PASSWORD, database=BaseConfig.DBNAME)
        cursor = conn.cursor(as_dict=True)
        sql = '''
        SELECT 
            r.Username, 
            r.RealName, 
            u.Age, 
            r.Gender 
        FROM 
            Riders_wyf r 
        JOIN 
            Users_wyf u ON r.UserID = u.UserID 
        WHERE 
            r.RiderID = %d
        ''' % user_id
        app.logger.debug(f"Executing SQL: {sql}")
        cursor.execute(sql)
        rider_info = cursor.fetchone()
        conn.close()

        if not rider_info:
            app.logger.debug(f"Rider not found for user_id: {user_id}")
            return jsonify(status=404, message="Rider not found"), 404

        app.logger.debug(f"Rider info: {rider_info}")
        return jsonify(status=200, data=rider_info)

    except Exception as e:
        app.logger.error(f"Error getting rider info: {e}")
        return jsonify(status=500, message="Internal server error"), 500
    
@app.route("/api/user/pwd_chg", methods=["POST"])
@cross_origin()
def change_password():
    data = request.get_json()
    old_pwd = data.get('old_pwd')
    new_pwd = data.get('new_pwd')
    user_id = verify_token(request.headers.get('Authorization'), app.config['SECRET_KEY'])

    if not user_id:
        return jsonify(status=401, message="Invalid token"), 401

    try:
        conn = pymssql.connect(server=BaseConfig.HOST, port=BaseConfig.PORT, user=BaseConfig.USERNAME, password=BaseConfig.PASSWORD, database=BaseConfig.DBNAME)
        cursor = conn.cursor(as_dict=True)
        
        # 验证旧密码
        cursor.execute("SELECT Password FROM Users_wyf WHERE UserID = %d", user_id)
        user = cursor.fetchone()
        if not user or user['Password'] != old_pwd:
            return jsonify(status=400, message="Old password is incorrect"), 400
        
        # 更新新密码
        cursor.execute("UPDATE Users_wyf SET Password = %s WHERE UserID = %d", (new_pwd, user_id))
        conn.commit()
        conn.close()

        return jsonify(status=200, message="Password changed successfully")

    except Exception as e:
        app.logger.error(f"Error changing password: {e}")
        return jsonify(status=500, message="Internal server error"), 500
    

@app.route("/api/user/orders/unsend", methods=["GET"])
@cross_origin()
def get_user_unsent_orders():
    try:
        token = request.headers.get('Authorization')
        if not token:
            return jsonify(status=401, message="Token is missing"), 401

        user_id = verify_token(token, app.config['SECRET_KEY'])
        if not user_id:
            return jsonify(status=401, message="Invalid token"), 401

        conn = pymssql.connect(server=BaseConfig.HOST, port=BaseConfig.PORT, user=BaseConfig.USERNAME, password=BaseConfig.PASSWORD, database=BaseConfig.DBNAME)
        cursor = conn.cursor(as_dict=True)
        
        sql = '''
        SELECT 
            o.OrderID AS order_id, 
            v.VendorName AS shop_name, 
            d.DishName AS dish_name, 
            r.RealName AS rider_name, 
            o.ConsigneeName AS cons_name, 
            o.Price AS price, 
            o.OrderTime AS create_time, 
            '未送达' AS deliver_time
        FROM 
            Orders_wyf o 
        LEFT JOIN 
            Riders_wyf r ON o.RiderID = r.RiderID 
        LEFT JOIN 
            Vendors_wyf v ON o.VendorID = v.VendorID
        LEFT JOIN 
            OrderDetails_wyf od ON o.OrderID = od.OrderID
        LEFT JOIN 
            Dishes_wyf d ON od.DishID = d.DishID
        WHERE 
            o.Status = '商家已接单' AND o.UserID = %d
        ''' % user_id
        cursor.execute(sql)
        orders = cursor.fetchall()
        conn.close()

        # 格式化时间
        for order in orders:
            if order['create_time']:
                order['create_time'] = order['create_time'].strftime('%Y年%m月%d日 %H:%M:%S')

        return jsonify(status=200, tabledata=orders)

    except Exception as e:
        app.logger.error(f"Error getting user unsent orders: {e}")
        return jsonify(status=500, message="Internal server error"), 500
    
@app.route("/api/user/orders/sending", methods=["GET"])
@cross_origin()
def get_user_sending_orders():
    try:
        token = request.headers.get('Authorization')
        if not token:
            return jsonify(status=401, message="Token is missing"), 401

        user_id = verify_token(token, app.config['SECRET_KEY'])
        if not user_id:
            return jsonify(status=401, message="Invalid token"), 401

        conn = pymssql.connect(server=BaseConfig.HOST, port=BaseConfig.PORT, user=BaseConfig.USERNAME, password=BaseConfig.PASSWORD, database=BaseConfig.DBNAME)
        cursor = conn.cursor(as_dict=True)
        
        sql = '''
        SELECT 
            o.OrderID AS order_id, 
            v.VendorName AS shop_name, 
            d.DishName AS dish_name, 
            r.RealName AS rider_name, 
            o.ConsigneeName AS cons_name, 
            o.Price AS price, 
            o.OrderTime AS create_time, 
            '配送中' AS deliver_time
        FROM 
            Orders_wyf o 
        LEFT JOIN 
            Riders_wyf r ON o.RiderID = r.RiderID 
        LEFT JOIN 
            Vendors_wyf v ON o.VendorID = v.VendorID
        LEFT JOIN 
            OrderDetails_wyf od ON o.OrderID = od.OrderID
        LEFT JOIN 
            Dishes_wyf d ON od.DishID = d.DishID
        WHERE 
            o.Status = '骑手配送中' AND o.UserID = %d
        ''' % user_id
        cursor.execute(sql)
        orders = cursor.fetchall()
        conn.close()

        # 格式化时间
        for order in orders:
            if order['create_time']:
                order['create_time'] = order['create_time'].strftime('%Y年%m月%d日 %H:%M:%S')

        return jsonify(status=200, tabledata=orders)

    except Exception as e:
        app.logger.error(f"Error getting user sending orders: {e}")
        return jsonify(status=500, message="Internal server error"), 500

@app.route("/api/user/orders/finished", methods=["GET"])
@cross_origin()
def get_user_finished_orders():
    try:
        token = request.headers.get('Authorization')
        if not token:
            return jsonify(status=401, message="Token is missing"), 401

        user_id = verify_token(token, app.config['SECRET_KEY'])
        if not user_id:
            return jsonify(status=401, message="Invalid token"), 401

        conn = pymssql.connect(server=BaseConfig.HOST, port=BaseConfig.PORT, user=BaseConfig.USERNAME, password=BaseConfig.PASSWORD, database=BaseConfig.DBNAME)
        cursor = conn.cursor(as_dict=True)
        
        sql = '''
        SELECT 
            o.OrderID AS order_id, 
            v.VendorName AS shop_name, 
            d.DishName AS dish_name, 
            r.RealName AS rider_name, 
            o.ConsigneeName AS cons_name, 
            o.Price AS price, 
            o.OrderTime AS create_time, 
            o.Time AS deliver_time
        FROM 
            Orders_wyf o 
        LEFT JOIN 
            Riders_wyf r ON o.RiderID = r.RiderID 
        LEFT JOIN 
            Vendors_wyf v ON o.VendorID = v.VendorID
        LEFT JOIN 
            OrderDetails_wyf od ON o.OrderID = od.OrderID
        LEFT JOIN 
            Dishes_wyf d ON od.DishID = d.DishID
        WHERE 
            o.Status = '已完成' AND o.UserID = %d
        ''' % user_id
        cursor.execute(sql)
        orders = cursor.fetchall()
        conn.close()

        # 格式化时间
        for order in orders:
            if order['create_time']:
                order['create_time'] = order['create_time'].strftime('%Y年%m月%d日 %H:%M:%S')
            if order['deliver_time']:
                order['deliver_time'] = order['deliver_time'].strftime('%Y年%m月%d日 %H:%M:%S')

        return jsonify(status=200, tabledata=orders)

    except Exception as e:
        app.logger.error(f"Error getting user finished orders: {e}")
        return jsonify(status=500, message="Internal server error"), 500
    
@app.route("/api/user/allshops", methods=["GET"])
@cross_origin()
def get_all_shops():
    try:
        token = request.headers.get('Authorization')
        if not token:
            return jsonify(status=401, message="Token is missing"), 401

        app.logger.info(f"Received token: {token}")

        user_id = verify_token(token, app.config['SECRET_KEY'])
        if not user_id:
            return jsonify(status=401, message="Invalid token"), 401

        app.logger.info(f"Verified user ID: {user_id}")

        conn = pymssql.connect(server=BaseConfig.HOST, port=BaseConfig.PORT, user=BaseConfig.USERNAME, password=BaseConfig.PASSWORD, database=BaseConfig.DBNAME)
        cursor = conn.cursor(as_dict=True)
        sql = 'SELECT VendorID, VendorName, LogoImage, VendorAddress, MonthlySales FROM Vendors_wyf'
        cursor.execute(sql)
        shops = cursor.fetchall()
        conn.close()

        return jsonify(status=200, tabledata=shops)

    except Exception as e:
        app.logger.error(f"Error getting shops: {e}")
        return jsonify(status=500, message="Internal server error"), 500
    

@app.route("/api/orders/unsend", methods=["GET"])
@cross_origin()
def get_all_unsend_orders():
    try:
        conn = pymssql.connect(server=BaseConfig.HOST, port=BaseConfig.PORT, user=BaseConfig.USERNAME, password=BaseConfig.PASSWORD, database=BaseConfig.DBNAME)
        cursor = conn.cursor(as_dict=True)
        sql = "SELECT * FROM Orders_wyf WHERE Status = '商家已接单'"
        cursor.execute(sql)
        orders = cursor.fetchall()
        conn.close()

        # 格式化时间
        for order in orders:
            if order['OrderTime']:
                order['OrderTime'] = order['OrderTime'].strftime('%Y年%m月%d日 %H:%M:%S')
            if order['Time']:
                order['Time'] = order['Time'].strftime('%Y年%m月%d日 %H:%M:%S')

        return jsonify(status=200, tabledata=[order for order in orders if 'OrderID' in order])

    except Exception as e:
        app.logger.error(f"Error getting unsend orders: {e}")
        return jsonify(status=500, message="Internal server error"), 500
    

@app.route("/api/orders/sending", methods=["GET"])
@cross_origin()
def get_rider_sending_orders():
    try:
        token = request.headers.get('Authorization')
        if not token:
            app.logger.warning("Token is missing")
            return jsonify(status=401, message="Token is missing"), 401

        user_id = verify_token(token, app.config['SECRET_KEY'])
        if not user_id:
            app.logger.warning("Invalid token")
            return jsonify(status=401, message="Invalid token"), 401

        conn = pymssql.connect(server=BaseConfig.HOST, port=BaseConfig.PORT, user=BaseConfig.USERNAME, password=BaseConfig.PASSWORD, database=BaseConfig.DBNAME)
        cursor = conn.cursor(as_dict=True)
        sql = "SELECT * FROM Orders_wyf WHERE Status = '骑手配送中' AND RiderID = %s"
        cursor.execute(sql, (user_id,))
        orders = cursor.fetchall()
        conn.close()

        # 格式化时间
        for order in orders:
            if order['OrderTime']:
                order['OrderTime'] = order['OrderTime'].strftime('%Y年%m月%d日 %H:%M:%S')
            if order['Time']:
                order['Time'] = order['Time'].strftime('%Y年%m月%d日 %H:%M:%S')

        return jsonify(status=200, tabledata=[order for order in orders if 'OrderID' in order])

    except Exception as e:
        app.logger.error(f"Error getting sending orders: {e}")
        return jsonify(status=500, message="Internal server error"), 500
    

@app.route("/api/orders/finished", methods=["GET"])
@cross_origin()
def get_rider_finished_orders():
    try:
        token = request.headers.get('Authorization')
        if not token:
            app.logger.warning("Token is missing")
            return jsonify(status=401, message="Token is missing"), 401

        user_id = verify_token(token, app.config['SECRET_KEY'])
        if not user_id:
            app.logger.warning("Invalid token")
            return jsonify(status=401, message="Invalid token"), 401

        conn = pymssql.connect(server=BaseConfig.HOST, port=BaseConfig.PORT, user=BaseConfig.USERNAME, password=BaseConfig.PASSWORD, database=BaseConfig.DBNAME)
        cursor = conn.cursor(as_dict=True)
        sql = "SELECT * FROM Orders_wyf WHERE status = '已完成' AND RiderID = %s"
        cursor.execute(sql, (user_id,))
        orders = cursor.fetchall()
        conn.close()

        # 格式化时间
        for order in orders:
            if order['OrderTime']:
                order['OrderTime'] = order['OrderTime'].strftime('%Y年%m月%d日 %H:%M:%S')
            if order['Time']:
                order['Time'] = order['Time'].strftime('%Y年%m月%d日 %H:%M:%S')

        return jsonify(status=200, tabledata=[order for order in orders if 'OrderID' in order])

    except Exception as e:
        app.logger.error(f"Error getting finished orders: {e}")
        return jsonify(status=500, message="Internal server error"), 500
    

import pymssql
import datetime

def update_monthly_sales():
    try:
        conn = pymssql.connect(server=BaseConfig.HOST, port=BaseConfig.PORT, user=BaseConfig.USERNAME, password=BaseConfig.PASSWORD, database=BaseConfig.DBNAME)
        cursor = conn.cursor()

        # 更新 MonthlySales 字段
        sql = """
        UPDATE Vendors_wyf
        SET MonthlySales = (
            SELECT COUNT(*)
            FROM Orders_wyf
            WHERE Orders_wyf.VendorID = Vendors_wyf.VendorID
              AND Orders_wyf.OrderTime >= DATEADD(MONTH, -1, GETDATE())
        );
        """
        cursor.execute(sql)
        conn.commit()
        conn.close()
        print("Monthly sales updated successfully.")
    except Exception as e:
        print(f"Error updating monthly sales: {e}")

# 调用函数更新月销量
update_monthly_sales()

    



    





if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port='5000')