#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
可视化SQL管理平台主程序（全屏UI/可视化生成/多样式展示）
"""
import os
import sys
import logging
import json
import csv
import io
import pymysql
from flask import Flask, render_template, jsonify, request, send_file
from dbutils.pooled_db import PooledDB

# 解决模块导入路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入自定义模块
from web.config.web_config import DB_CONFIGS, LOCAL_WEB_DB_CONFIG, PAGE_CONFIG
from web.core.web_db_operation import WebDBOperation, SQLGenerator

# ===================== 基础配置 =====================
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['JSON_AS_ASCII'] = False
app.config['SECRET_KEY'] = os.urandom(24)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# ===================== 日志配置 =====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('web_sql_manager.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('web_sql_manager')

# ===================== 数据库连接池 =====================
db_pools = {}


def init_db_pools():
    """初始化多数据库连接池"""
    for db_alias, config in DB_CONFIGS.items():
        try:
            pool = PooledDB(
                creator=pymysql,
                maxconnections=10,
                mincached=0,
                maxcached=5,
                maxshared=3,
                blocking=True,
                maxusage=None,
                setsession=[],
                ping=0,
                host=config['host'],
                port=config['port'],
                user=config['user'],
                password=config['password'],
                charset=config['charset']
            )
            db_pools[db_alias] = pool
            logger.info(f"数据库连接池初始化成功：{db_alias}")
        except Exception as e:
            logger.error(f"连接池初始化失败 - {db_alias}：{str(e)}", exc_info=True)
            continue


init_db_pools()


# ===================== 工具函数 =====================
def get_db_connection(db_alias):
    """从连接池获取连接"""
    if db_alias not in db_pools:
        logger.error(f"未找到连接池：{db_alias}")
        return None
    try:
        return db_pools[db_alias].connection()
    except Exception as e:
        logger.error(f"获取连接失败：{str(e)}", exc_info=True)
        return None


def format_result(data, style):
    """格式化结果（支持多样式）"""
    if style == "JSON":
        return json.dumps(data, ensure_ascii=False, indent=2)
    elif style == "CSV下载":
        # 生成CSV文件
        output = io.StringIO()
        writer = csv.writer(output)
        if data and isinstance(data, list) and isinstance(data[0], dict):
            # 写表头
            writer.writerow(data[0].keys())
            # 写数据
            for row in data:
                writer.writerow(row.values())
        output.seek(0)
        return output
    else:
        # 表格/卡片式由前端处理
        return data


# ===================== 路由 =====================
@app.route('/')
def index():
    """可视化SQL生成/执行页面（全屏）"""
    return render_template('index.html', page_config=PAGE_CONFIG)


@app.route('/saved_sql')
def saved_sql():
    """保存的SQL管理页面"""
    return render_template('saved_sql.html', page_config=PAGE_CONFIG)


# -------------------- 数据库基础接口 --------------------
@app.route('/api/get_db_list', methods=['GET'])
def get_db_list():
    """获取数据库连接列表（字典式）"""
    try:
        db_list = [{"alias": alias, "config": config} for alias, config in DB_CONFIGS.items()]
        return jsonify({
            "code": 200,
            "msg": "成功",
            "data": db_list
        })
    except Exception as e:
        return jsonify({
            "code": 500,
            "msg": f"获取失败：{str(e)}",
            "data": None
        })


@app.route('/api/get_db_names', methods=['POST'])
def get_db_names():
    """获取指定数据库的库名列表"""
    try:
        data = request.get_json()
        db_alias = data.get('db_alias')
        if not db_alias:
            return jsonify({"code": 400, "msg": "缺少数据库别名", "data": None})

        conn = get_db_connection(db_alias)
        if not conn:
            return jsonify({"code": 500, "msg": "数据库连接失败", "data": None})

        cursor = conn.cursor()
        cursor.execute("SHOW DATABASES")
        db_names = [item[0] for item in cursor.fetchall()]

        cursor.close()
        conn.close()

        return jsonify({
            "code": 200,
            "msg": "成功",
            "data": db_names
        })
    except Exception as e:
        return jsonify({
            "code": 500,
            "msg": f"获取失败：{str(e)}",
            "data": None
        })


@app.route('/api/get_table_names', methods=['POST'])
def get_table_names():
    """获取指定数据库+库名的表名列表"""
    try:
        data = request.get_json()
        db_alias = data.get('db_alias')
        db_name = data.get('db_name')

        if not db_alias or not db_name:
            return jsonify({"code": 400, "msg": "缺少参数", "data": None})

        conn = get_db_connection(db_alias)
        if not conn:
            return jsonify({"code": 500, "msg": "数据库连接失败", "data": None})

        cursor = conn.cursor()
        cursor.execute(f"USE {db_name}")
        cursor.execute("SHOW TABLES")
        table_names = [item[0] for item in cursor.fetchall()]

        cursor.close()
        conn.close()

        return jsonify({
            "code": 200,
            "msg": "成功",
            "data": table_names
        })
    except Exception as e:
        return jsonify({
            "code": 500,
            "msg": f"获取失败：{str(e)}",
            "data": None
        })


@app.route('/api/get_table_fields', methods=['POST'])
def get_table_fields():
    """获取指定表的字段列表"""
    try:
        data = request.get_json()
        db_alias = data.get('db_alias')
        db_name = data.get('db_name')
        table_name = data.get('table_name')

        if not db_alias or not db_name or not table_name:
            return jsonify({"code": 400, "msg": "缺少参数", "data": None})

        conn = get_db_connection(db_alias)
        if not conn:
            return jsonify({"code": 500, "msg": "数据库连接失败", "data": None})

        cursor = conn.cursor()
        cursor.execute(f"USE {db_name}")
        cursor.execute(f"DESCRIBE {table_name}")
        fields = [item[0] for item in cursor.fetchall()]

        cursor.close()
        conn.close()

        return jsonify({
            "code": 200,
            "msg": "成功",
            "data": fields
        })
    except Exception as e:
        return jsonify({
            "code": 500,
            "msg": f"获取失败：{str(e)}",
            "data": None
        })


# -------------------- 可视化SQL生成接口 --------------------
@app.route('/api/generate_sql', methods=['POST'])
def generate_sql():
    """生成SQL语句"""
    try:
        data = request.get_json()
        generator = SQLGenerator()
        sql, err = generator.generate_sql(data)

        if err:
            return jsonify({"code": 400, "msg": err, "data": None})

        return jsonify({
            "code": 200,
            "msg": "生成成功",
            "data": {"sql_text": sql}
        })
    except Exception as e:
        return jsonify({
            "code": 500,
            "msg": f"生成失败：{str(e)}",
            "data": None
        })


# -------------------- SQL执行接口 --------------------
@app.route('/api/execute_sql', methods=['POST'])
def execute_sql():
    """执行SQL（支持多样式返回）"""
    try:
        data = request.get_json()
        db_alias = data.get('db_alias')
        db_name = data.get('db_name')
        sql_text = data.get('sql_text')
        result_style = data.get('result_style', '表格')

        # 参数校验
        if not db_alias or not sql_text:
            return jsonify({"code": 400, "msg": "缺少数据库别名或SQL语句", "data": None})

        # 获取连接
        conn = get_db_connection(db_alias)
        if not conn:
            return jsonify({"code": 500, "msg": "数据库连接失败", "data": None})

        cursor = conn.cursor(pymysql.cursors.DictCursor)
        result = None
        fields = []

        try:
            # 切换数据库（如果指定）
            if db_name:
                cursor.execute(f"USE {db_name}")

            # 执行SQL
            cursor.execute(sql_text)

            # 处理查询结果
            if sql_text.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
                fields = [desc[0] for desc in cursor.description] if cursor.description else []
            else:
                conn.commit()
                result = {"affected_rows": cursor.rowcount}

            # 格式化结果
            formatted_result = format_result(result, result_style)

            # CSV下载特殊处理
            if result_style == "CSV下载":
                return send_file(
                    io.BytesIO(formatted_result.getvalue().encode('utf-8-sig')),
                    mimetype='text/csv',
                    as_attachment=True,
                    download_name=f"sql_result_{int(time.time())}.csv"
                )

            return jsonify({
                "code": 200,
                "msg": "执行成功",
                "data": {
                    "fields": fields,
                    "result": formatted_result,
                    "style": result_style
                }
            })
        except Exception as e:
            conn.rollback()
            return jsonify({"code": 500, "msg": f"SQL执行失败：{str(e)}", "data": None})
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        return jsonify({"code": 500, "msg": f"执行异常：{str(e)}", "data": None})


# -------------------- 保存/管理SQL配置接口 --------------------
@app.route('/api/init_web_db', methods=['GET'])
def init_web_db():
    """初始化Web本地数据库"""
    db_oper = WebDBOperation()
    success, msg = db_oper.init_web_db()
    code = 200 if success else 500
    return jsonify({"code": code, "msg": msg, "data": None})


@app.route('/api/save_sql_config', methods=['POST'])
def save_sql_config():
    """保存SQL配置"""
    try:
        data = request.get_json()
        db_oper = WebDBOperation()
        success, msg = db_oper.save_sql_query(data)
        code = 200 if success else 500
        return jsonify({"code": code, "msg": msg, "data": None})
    except Exception as e:
        return jsonify({"code": 500, "msg": f"保存失败：{str(e)}", "data": None})


@app.route('/api/get_saved_sql', methods=['GET'])
def get_saved_sql():
    """获取所有保存的SQL配置"""
    try:
        db_oper = WebDBOperation()
        data = db_oper.get_all_saved_queries()
        return jsonify({"code": 200, "msg": "查询成功", "data": data})
    except Exception as e:
        return jsonify({"code": 500, "msg": f"查询失败：{str(e)}", "data": None})


@app.route('/api/get_sql_detail/<int:query_id>', methods=['GET'])
def get_sql_detail(query_id):
    """获取SQL配置详情"""
    try:
        db_oper = WebDBOperation()
        data = db_oper.get_query_detail_by_id(query_id)
        if data:
            return jsonify({"code": 200, "msg": "查询成功", "data": data})
        else:
            return jsonify({"code": 404, "msg": "未找到配置", "data": None})
    except Exception as e:
        return jsonify({"code": 500, "msg": f"查询失败：{str(e)}", "data": None})


@app.route('/api/delete_sql/<int:query_id>', methods=['DELETE'])
def delete_sql(query_id):
    """删除SQL配置"""
    try:
        db_oper = WebDBOperation()
        success, msg = db_oper.delete_query_by_id(query_id)
        code = 200 if success else 500
        return jsonify({"code": code, "msg": msg, "data": None})
    except Exception as e:
        return jsonify({"code": 500, "msg": f"删除失败：{str(e)}", "data": None})


@app.route('/api/execute_saved_sql/<int:query_id>', methods=['POST'])
def execute_saved_sql(query_id):
    """执行保存的SQL配置"""
    try:
        # 获取配置详情
        db_oper = WebDBOperation()
        detail = db_oper.get_query_detail_by_id(query_id)
        if not detail:
            return jsonify({"code": 404, "msg": "未找到配置", "data": None})

        # 执行SQL
        data = {
            "db_alias": detail["db_alias"],
            "db_name": detail["db_name"],
            "sql_text": detail["sql_text"],
            "result_style": request.get_json().get("result_style", "表格")
        }

        # 调用执行接口的逻辑
        conn = get_db_connection(detail["db_alias"])
        if not conn:
            return jsonify({"code": 500, "msg": "数据库连接失败", "data": None})

        cursor = conn.cursor(pymysql.cursors.DictCursor)
        result = None
        fields = []

        try:
            if detail["db_name"]:
                cursor.execute(f"USE {detail['db_name']}")
            cursor.execute(detail["sql_text"])

            if detail["operation_type"] == "SELECT":
                result = cursor.fetchall()
                fields = [desc[0] for desc in cursor.description] if cursor.description else []
            else:
                conn.commit()
                result = {"affected_rows": cursor.rowcount}

            formatted_result = format_result(result, data["result_style"])

            if data["result_style"] == "CSV下载":
                return send_file(
                    io.BytesIO(formatted_result.getvalue().encode('utf-8-sig')),
                    mimetype='text/csv',
                    as_attachment=True,
                    download_name=f"saved_sql_result_{query_id}.csv"
                )

            return jsonify({
                "code": 200,
                "msg": "执行成功",
                "data": {
                    "fields": fields,
                    "result": formatted_result,
                    "style": data["result_style"]
                }
            })
        except Exception as e:
            conn.rollback()
            return jsonify({"code": 500, "msg": f"执行失败：{str(e)}", "data": None})
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        return jsonify({"code": 500, "msg": f"执行异常：{str(e)}", "data": None})


# ===================== 错误处理 =====================
@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"code": 404, "msg": "接口不存在", "data": None}), 404


@app.errorhandler(500)
def internal_server_error(e):
    logger.error(f"服务器错误：{str(e)}", exc_info=True)
    return jsonify({"code": 500, "msg": "服务器内部错误", "data": None}), 500


# ===================== 启动入口 =====================
if __name__ == '__main__':
    # 先初始化数据库
    WebDBOperation().init_web_db()

    # 启动服务（全屏访问）
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )