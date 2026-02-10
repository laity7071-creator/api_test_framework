"""极简数据库操作：仅核心功能"""
import pymysql
from utils.common_util import read_config
from utils.log_util import logger

class DBOperation:
    def __init__(self):
        self.host = read_config("DATABASE", "host")
        self.port = int(read_config("DATABASE", "port"))
        self.user = read_config("DATABASE", "user")
        self.password = read_config("DATABASE", "password")
        self.database = read_config("DATABASE", "database")
        self.charset = read_config("DATABASE", "charset")
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            self.conn = pymysql.connect(
                host=self.host, port=self.port, user=self.user, password=self.password,
                database=self.database, charset=self.charset, cursorclass=pymysql.cursors.DictCursor
            )
            self.cursor = self.conn.cursor()
            logger.info("数据库连接成功")
        except Exception as e:
            logger.error(f"数据库连接失败：{str(e)}")
            raise

    def query(self, sql, params=None):
        if not self.conn:
            self.connect()
        try:
            self.cursor.execute(sql, params)
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"SQL查询失败：{str(e)}")
            raise

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("数据库连接已关闭")

db_util = DBOperation()