# config.py
class BaseConfig(object):

    # 数据库的配置
    DIALCT = "mssql+pymssql"
    HOST = '127.0.0.1'
    PORT = "1433" 
    USERNAME = "sa"  
    PASSWORD = "wyfqq11111"
    DBNAME = 'Takeoutsystem_wyf'

    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    SQLALCHEMY_DATABASE_URI = f"{DIALCT}://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False  

    # pymssql连接字符串
    PYMSSQL_CONNECTION_STRING = f"server={HOST};port={PORT};database={DBNAME};uid={USERNAME};pwd={PASSWORD}"