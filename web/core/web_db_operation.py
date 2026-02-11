#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Web模块数据库操作类（独立，支持加密/可视化SQL生成/保存）
"""
import pymysql
import json
import logging
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import os

# 手动添加web_config的导入路径（防止路径问题）
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.web_config import LOCAL_WEB_DB_CONFIG, AES_CONFIG, PAGE_CONFIG

# 初始化日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('web_db_operation')


# ===================== 加密解密工具 =====================
def aes_encrypt(data):
    """AES加密（用于密码存储）"""
    if not data:
        return ""
    try:
        cipher = AES.new(AES_CONFIG["key"], AES_CONFIG["mode"], AES_CONFIG["iv"])
        encrypted = cipher.encrypt(pad(data.encode("utf8"), AES.block_size))
        return base64.b64encode(encrypted).decode("utf8")
    except Exception as e:
        logger.error(f"AES加密失败：{str(e)}")
        return ""


def aes_decrypt(encrypted_data):
    """AES解密"""
    if not encrypted_data:
        return ""
    try:
        cipher = AES.new(AES_CONFIG["key"], AES_CONFIG["mode"], AES_CONFIG["iv"])
        decrypted = unpad(cipher.decrypt(base64.b64decode(encrypted_data)), AES.block_size)
        return decrypted.decode("utf8")
    except Exception as e:
        logger.error(f"AES解密失败：{str(e)}")
        return ""


# ===================== 可视化SQL生成工具 =====================
class SQLGenerator:
    @staticmethod
    def generate_select_sql(params):
        """生成SELECT语句"""
        # 参数：db_name, table_name, fields, conditions, limit_num
        if not params.get("table_name"):
            return "", "表名不能为空"

        # 处理字段（默认*）
        fields = params.get("fields", ["*"])
        field_str = ", ".join(fields) if fields else "*"

        # 处理表名（带库名）
        table_str = f"{params.get('db_name')}.{params.get('table_name')}" if params.get("db_name") else params.get(
            "table_name")

        # 基础SQL
        sql = f"SELECT {field_str} FROM {table_str}"

        # 处理条件
        conditions = params.get("conditions", [])
        where_clauses = []
        for cond in conditions:
            field = cond.get("field")
            operator = cond.get("operator")
            value = cond.get("value")
            connector = cond.get("connector", "")

            if not field or not operator:
                continue

            # 处理不同运算符的格式
            if operator in ["=", "!=", ">", ">=", "<", "<="]:
                clause = f"{field} {operator} '{value}'"
            elif operator in ["LIKE", "NOT LIKE"]:
                clause = f"{field} {operator} '%{value}%'"
            elif operator in ["IN", "NOT IN"]:
                # 处理IN的值（逗号分隔）
                values = [v.strip() for v in value.split(",")]
                clause = f"{field} {operator} ('{' , '.join(values)}')"
            elif operator in ["BETWEEN", "NOT BETWEEN"]:
                # 处理BETWEEN的值（两个值用逗号分隔）
                values = [v.strip() for v in value.split(",")]
                if len(values) == 2:
                    clause = f"{field} {operator} '{values[0]}' AND '{values[1]}'"
                else:
                    continue
            elif operator == "IS NULL":
                clause = f"{field} IS NULL"
            elif operator == "IS NOT NULL":
                clause = f"{field} IS NOT NULL"
            else:
                continue

            where_clauses.append(clause + (f" {connector}" if connector else ""))

        if where_clauses:
            sql += f" WHERE {' '.join(where_clauses)}"

        # 处理LIMIT
        limit_num = params.get("limit_num")
        if limit_num and limit_num.isdigit():
            sql += f" LIMIT {limit_num}"

        return sql, ""

    @staticmethod
    def generate_update_sql(params):
        """生成UPDATE语句"""
        if not params.get("table_name") or not params.get("update_fields"):
            return "", "表名和更新字段不能为空"

        # 处理表名
        table_str = f"{params.get('db_name')}.{params.get('table_name')}" if params.get("db_name") else params.get(
            "table_name")

        # 处理更新字段
        update_fields = params.get("update_fields", [])
        update_clauses = []
        for field in update_fields:
            field_name = field.get("field")
            field_value = field.get("value")
            if field_name and field_value:
                update_clauses.append(f"{field_name} = '{field_value}'")

        if not update_clauses:
            return "", "更新字段格式错误"

        # 基础SQL
        sql = f"UPDATE {table_str} SET {', '.join(update_clauses)}"

        # 处理条件
        conditions = params.get("conditions", [])
        where_clauses = []
        for cond in conditions:
            field = cond.get("field")
            operator = cond.get("operator")
            value = cond.get("value")
            connector = cond.get("connector", "")

            if not field or not operator:
                continue

            # 同SELECT的条件处理逻辑
            if operator in ["=", "!=", ">", ">=", "<", "<="]:
                clause = f"{field} {operator} '{value}'"
            elif operator in ["LIKE", "NOT LIKE"]:
                clause = f"{field} {operator} '%{value}%'"
            elif operator in ["IN", "NOT IN"]:
                values = [v.strip() for v in value.split(",")]
                clause = f"{field} {operator} ('{' , '.join(values)}')"
            elif operator in ["BETWEEN", "NOT BETWEEN"]:
                values = [v.strip() for v in value.split(",")]
                if len(values) == 2:
                    clause = f"{field} {operator} '{values[0]}' AND '{values[1]}'"
                else:
                    continue
            elif operator == "IS NULL":
                clause = f"{field} IS NULL"
            elif operator == "IS NOT NULL":
                clause = f"{field} IS NOT NULL"
            else:
                continue

            where_clauses.append(clause + (f" {connector}" if connector else ""))

        if where_clauses:
            sql += f" WHERE {' '.join(where_clauses)}"
        else:
            return "", "UPDATE必须加条件（防止全表更新）"

        return sql, ""

    @staticmethod
    def generate_delete_sql(params):
        """生成DELETE语句"""
        if not params.get("table_name"):
            return "", "表名不能为空"

        # 处理表名
        table_str = f"{params.get('db_name')}.{params.get('table_name')}" if params.get("db_name") else params.get(
            "table_name")

        # 基础SQL
        sql = f"DELETE FROM {table_str}"

        # 处理条件
        conditions = params.get("conditions", [])
        where_clauses = []
        for cond in conditions:
            field = cond.get("field")
            operator = cond.get("operator")
            value = cond.get("value")
            connector = cond.get("connector", "")

            if not field or not operator:
                continue

            # 同SELECT的条件处理逻辑
            if operator in ["=", "!=", ">", ">=", "<", "<="]:
                clause = f"{field} {operator} '{value}'"
            elif operator in ["LIKE", "NOT LIKE"]:
                clause = f"{field} {operator} '%{value}%'"
            elif operator in ["IN", "NOT IN"]:
                values = [v.strip() for v in value.split(",")]
                clause = f"{field} {operator} ('{' , '.join(values)}')"
            elif operator in ["BETWEEN", "NOT BETWEEN"]:
                values = [v.strip() for v in value.split(",")]
                if len(values) == 2:
                    clause = f"{field} {operator} '{values[0]}' AND '{values[1]}'"
                else:
                    continue
            elif operator == "IS NULL":
                clause = f"{field} IS NULL"
            elif operator == "IS NOT NULL":
                clause = f"{field} IS NOT NULL"
            else:
                continue

            where_clauses.append(clause + (f" {connector}" if connector else ""))

        if where_clauses:
            sql += f" WHERE {' '.join(where_clauses)}"
        else:
            return "", "DELETE必须加条件（防止全表删除）"

        return sql, ""

    @staticmethod
    def generate_sql(params):
        """统一生成SQL入口（修复self错误）"""
        operation_type = params.get("operation_type", "SELECT")
        if operation_type == "SELECT":
            return SQLGenerator.generate_select_sql(params)
        elif operation_type == "UPDATE":
            return SQLGenerator.generate_update_sql(params)
        elif operation_type == "DELETE":
            return SQLGenerator.generate_delete_sql(params)
        else:
            return "", f"不支持的操作类型：{operation_type}"


# ===================== 本地存储库操作类 =====================
class WebDBOperation:
    def __init__(self):
        self.host = LOCAL_WEB_DB_CONFIG["host"]
        self.port = LOCAL_WEB_DB_CONFIG["port"]
        self.user = LOCAL_WEB_DB_CONFIG["user"]
        self.password = LOCAL_WEB_DB_CONFIG["password"]
        self.database = LOCAL_WEB_DB_CONFIG["database"]
        self.charset = LOCAL_WEB_DB_CONFIG["charset"]
        self.conn = None
        self.cursor = None

    def connect(self):
        """连接本地存储库"""
        try:
            self.conn = pymysql.connect(
                host=self.host, port=self.port, user=self.user,
                password=self.password, database=self.database, charset=self.charset
            )
            self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)
            logger.info("Web本地存储库连接成功")
            return True
        except Exception as e:
            logger.error(f"Web本地存储库连接失败：{str(e)}", exc_info=True)
            return False

    def close(self):
        """关闭连接"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
        except Exception as e:
            logger.error(f"关闭连接失败：{str(e)}")

    def save_sql_query(self, data):
        """保存SQL查询条件（完整信息，密码加密）"""
        # 校验必要参数
        required_fields = ["config_name", "db_alias", "db_host", "db_port",
                           "db_user", "db_password", "operation_type", "sql_text"]
        for field in required_fields:
            if not data.get(field):
                logger.error(f"保存失败：缺少字段{field}")
                return False, "缺少必要参数"

        if not self.connect():
            return False, "本地存储库连接失败"

        # 加密密码
        encrypted_pwd = aes_encrypt(data.get("db_password"))

        # ========== 关键修复：处理limit_num（空值转NULL） ==========
        limit_num = data.get("limit_num")
        # 空字符串/空值转为NULL，非空则转为整数
        if not limit_num or not str(limit_num).isdigit():
            limit_num = None
        else:
            limit_num = int(limit_num)

        # JSON序列化复杂字段
        try:
            fields = json.dumps(data.get("fields", []), ensure_ascii=False)
            conditions = json.dumps(data.get("conditions", []), ensure_ascii=False)
            update_fields = json.dumps(data.get("update_fields", []), ensure_ascii=False)
        except Exception as e:
            logger.error(f"JSON序列化失败：{str(e)}")
            self.close()
            return False, "参数格式错误"

        # 插入SQL（limit_num改为%s，接收NULL）
        sql = """
        INSERT INTO saved_sql_queries (
            config_name, db_alias, db_host, db_port, db_user, db_password,
            db_name, table_name, operation_type, fields, conditions,
            update_fields, limit_num, sql_text, remark
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            data.get("config_name"), data.get("db_alias"), data.get("db_host"),
            data.get("db_port"), data.get("db_user"), encrypted_pwd,
            data.get("db_name"), data.get("table_name"), data.get("operation_type"),
            fields, conditions, update_fields, limit_num,  # 传入处理后的limit_num
            data.get("sql_text"), data.get("remark", "")
        )

        try:
            self.cursor.execute(sql, params)
            self.conn.commit()
            logger.info(f"SQL配置保存成功：{data.get('config_name')}")
            return True, "保存成功"
        except Exception as e:
            logger.error(f"保存失败：{str(e)}", exc_info=True)
            self.conn.rollback()
            return False, f"保存失败：{str(e)}"
        finally:
            self.close()

    def get_all_saved_queries(self):
        """获取所有保存的SQL配置（隐藏密码）"""
        if not self.connect():
            return []

        sql = """
        SELECT id, config_name, db_alias, db_name, table_name, 
               operation_type, sql_text, remark, create_time
        FROM saved_sql_queries ORDER BY create_time DESC
        """
        try:
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"查询保存的SQL失败：{str(e)}", exc_info=True)
            return []
        finally:
            self.close()

    def get_query_detail_by_id(self, query_id):
        """获取SQL配置详情（密码解密）"""
        if not self.connect():
            return None

        sql = "SELECT * FROM saved_sql_queries WHERE id = %s"
        try:
            self.cursor.execute(sql, (query_id,))
            detail = self.cursor.fetchone()
            if not detail:
                return None

            # 解密密码
            detail["db_password"] = aes_decrypt(detail["db_password"])

            # JSON解析复杂字段
            for field in ["fields", "conditions", "update_fields"]:
                try:
                    detail[field] = json.loads(detail[field]) if detail[field] else []
                except:
                    detail[field] = []

            return detail
        except Exception as e:
            logger.error(f"获取详情失败：{str(e)}", exc_info=True)
            return None
        finally:
            self.close()

    def delete_query_by_id(self, query_id):
        """删除保存的SQL配置"""
        if not self.connect():
            return False, "连接失败"

        try:
            self.cursor.execute("DELETE FROM saved_sql_queries WHERE id = %s", (query_id,))
            self.conn.commit()
            logger.info(f"删除SQL配置成功：ID={query_id}")
            return True, "删除成功"
        except Exception as e:
            logger.error(f"删除失败：{str(e)}", exc_info=True)
            self.conn.rollback()
            return False, f"删除失败：{str(e)}"
        finally:
            self.close()

    def init_web_db(self):
        """初始化Web数据库（执行建表SQL）"""
        # 先连接MySQL（不指定数据库）
        try:
            conn = pymysql.connect(
                host=self.host, port=self.port, user=self.user,
                password=self.password, charset=self.charset
            )
            cursor = conn.cursor()

            # 读取建表SQL文件
            sql_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sql", "init_web_db.sql")
            with open(sql_file_path, "r", encoding="utf8") as f:
                sql_commands = f.read().split(";")

            # 执行SQL命令
            for cmd in sql_commands:
                cmd = cmd.strip()
                if cmd:
                    cursor.execute(cmd)

            conn.commit()
            cursor.close()
            conn.close()
            logger.info("Web数据库初始化成功")
            return True, "初始化成功"
        except Exception as e:
            logger.error(f"初始化失败：{str(e)}", exc_info=True)
            return False, f"初始化失败：{str(e)}"