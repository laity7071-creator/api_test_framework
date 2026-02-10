"""数据库操作类（适配增删改查，兼容原有逻辑）"""
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
        """建立数据库连接（原有逻辑，不变）"""
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
        """
        专做【查询（SELECT）】（原有逻辑，不变）
        :return: 查询结果（列表[字典]）
        """
        if not self.conn:
            self.connect()
        try:
            self.cursor.execute(sql, params)
            result = self.cursor.fetchall()
            logger.info(f"SQL查询成功，结果行数：{len(result)}")
            return result
        except Exception as e:
            logger.error(f"SQL查询失败：{str(e)}")
            raise

    def execute(self, sql, params=None):
        """
        专做【增/删/改（INSERT/UPDATE/DELETE）】（新增核心方法）
        :return: 受影响的行数（比如新增1条返回1，修改2条返回2）
        """
        if not self.conn:
            self.connect()
        try:
            affected_rows = self.cursor.execute(sql, params)
            self.conn.commit()  # 关键：增删改必须提交事务，否则数据不生效
            logger.info(f"SQL执行成功（增/删/改），受影响行数：{affected_rows}")
            return affected_rows
        except Exception as e:
            self.conn.rollback()  # 执行失败则回滚事务，避免脏数据
            logger.error(f"SQL执行失败（增/删/改）：{str(e)}，已回滚事务")
            raise

    def close(self):
        """关闭数据库连接（原有逻辑，不变）"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("数据库连接已关闭")

# 全局实例（原有逻辑，不变）
db_util = DBOperation()