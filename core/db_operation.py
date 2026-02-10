"""数据库工具类（仅封装增删改查，无任何用例代码）"""
import pymysql
from utils.log_util import logger
from utils.common_util import read_config

class DBOperation:
    def __init__(self, env="test"):
        # 读取指定环境的数据库配置
        env_section = f"ENV_{env.upper()}"
        self.host = read_config(env_section, "db_host")
        self.port = int(read_config(env_section, "db_port"))
        self.user = read_config(env_section, "db_user")
        self.password = read_config(env_section, "db_password")
        self.db = read_config(env_section, "db_name")
        self.charset = "utf8mb4"
        # 初始化连接/游标
        self.conn = None
        self.cursor = None

    def connect(self):
        """建立数据库连接"""
        self.conn = pymysql.connect(
            host=self.host, port=self.port, user=self.user,
            password=self.password, db=self.db, charset=self.charset,
            cursorclass=pymysql.cursors.DictCursor  # 返回字典格式
        )
        self.cursor = self.conn.cursor()
        logger.info("数据库连接成功")

    def close(self):
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("数据库连接已关闭")

    def execute(self, sql):
        """执行单条SQL（增/删/改，自动提交）"""
        try:
            rows = self.cursor.execute(sql)
            self.conn.commit()
            return rows
        except Exception as e:
            self.conn.rollback()
            logger.error(f"SQL执行失败：{sql[:100]} → {e}")
            raise

    def executemany(self, sql, data_list):
        """批量执行SQL"""
        try:
            rows = self.cursor.executemany(sql, data_list)
            self.conn.commit()
            return rows
        except Exception as e:
            self.conn.rollback()
            logger.error(f"批量SQL执行失败 → {e}")
            raise

    def query_one(self, sql):
        """查询单条数据"""
        self.cursor.execute(sql)
        return self.cursor.fetchone()

    def query_all(self, sql):
        """查询多条数据"""
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def begin_transaction(self):
        """开启事务（关闭自动提交）"""
        self.conn.autocommit(False)
        logger.info("事务已开启")

    def commit(self):
        """提交事务"""
        self.conn.commit()
        self.conn.autocommit(True)
        logger.info("事务已提交")

    def rollback(self):
        """回滚事务"""
        self.conn.rollback()
        self.conn.autocommit(True)
        logger.info("事务已回滚")

# 全局数据库工具对象（供用例直接调用）
db_util = DBOperation(env="test")