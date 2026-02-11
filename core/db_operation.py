import pymysql
import logging

# 初始化logger（如果你的log_util有问题，先兜底）
logger = logging.getLogger("api_test")


class DBOperation:
    def __init__(self, host=None, port=None, user=None, password=None, database=None, charset="utf8mb4", env="test"):
        """
        初始化数据库连接
        :param host: 数据库IP
        :param port: 端口
        :param user: 账号
        :param password: 密码
        :param database: 库名
        :param charset: 字符集
        :param env: 环境（兼容原有逻辑）
        """
        # 优先使用直接传参（Web多库场景）
        self.host = host
        self.port = port if port else 3306
        self.user = user
        self.password = password
        self.database = database
        self.charset = charset

        # 兼容旧逻辑（如果没传参，从配置读，这里先注释，避免依赖问题）
        # if not all([self.host, self.port, self.user, self.password]):
        #     from utils.config_util import read_config
        #     self.host = read_config(f"DB_{env.upper()}", "host")
        #     self.port = int(read_config(f"DB_{env.upper()}", "port"))
        #     self.user = read_config(f"DB_{env.upper()}", "user")
        #     self.password = read_config(f"DB_{env.upper()}", "password")
        #     self.database = read_config(f"DB_{env.upper()}", "database")

        self.conn = None
        self.cursor = None

    def connect(self):
        """建立数据库连接（关闭DictCursor，改用默认元组游标，避免解析错误）"""
        try:
            # 关键修复：移除DictCursor，改用默认游标（返回元组列表，适配x[0]取值）
            self.conn = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                charset=self.charset,
                # 核心：注释掉DictCursor，用默认游标！
                # cursorclass=pymysql.cursors.DictCursor
            )
            self.cursor = self.conn.cursor()
            logger.info("数据库连接成功")
        except Exception as e:
            logger.error(f"数据库连接失败：{str(e)}")
            raise e  # 抛出异常，让上层捕获

    def close(self):
        """安全关闭连接"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
            logger.info("数据库连接已关闭")
        except Exception as e:
            logger.error(f"关闭连接失败：{str(e)}")

    # 补充基础执行方法（确保app.py能调用）
    def execute(self, sql, params=None):
        if not self.conn:
            self.connect()
        try:
            self.cursor.execute(sql, params or ())
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"执行SQL失败：{str(e)}")
            raise e