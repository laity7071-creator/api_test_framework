#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@作者: laity.wang
@创建日期: 2026/2/10 18:55
@文件名: app.py
@项目名称: api_test_framework
@文件完整绝对路径: D:/LaityTest/api_test_framework/web\app.py
@文件相对项目路径:   # 可选，不需要可以删掉这行
@描述: 
"""
"""Web后端入口：封装SSH/SQL测试框架为HTTP接口"""
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from core.ssh_operation import exec_ssh_command
from core.db_operation import db_util
from utils.common_util import get_env_base_url
from utils.log_util import logger
from utils.common_util import read_config

WEB_HOST = read_config("WEB", "host")
WEB_PORT = int(read_config("WEB", "port"))
WEB_DEBUG = read_config("WEB", "debug").lower() == "true"

# 初始化Flask应用
app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)  # 解决跨域问题


# -------------------------- 页面路由（返回前端页面） --------------------------
@app.route("/")
def index():
    """首页：测试框架可视化操作界面"""
    return render_template("index.html")


# -------------------------- SSH测试接口 --------------------------
@app.route("/api/ssh/exec", methods=["POST"])
def ssh_exec():
    """执行SSH命令接口"""
    try:
        # 获取前端传参（环境、命令）
        data = request.json
        env = data.get("env", "test")
        command = data.get("command", "")

        if not command:
            return jsonify({"code": 400, "msg": "SSH命令不能为空", "data": ""})

        # 调用原有SSH逻辑（一行不改，直接调用）
        stdout, stderr = exec_ssh_command(command, env=env)

        # 返回结果给前端
        return jsonify({
            "code": 200,
            "msg": "执行成功",
            "data": {"stdout": stdout, "stderr": stderr}
        })
    except Exception as e:
        logger.error(f"SSH执行接口异常：{e}")
        return jsonify({"code": 500, "msg": f"执行失败：{str(e)}", "data": ""})


# -------------------------- SQL测试接口 --------------------------
@app.route("/api/sql/exec", methods=["POST"])
def sql_exec():
    """执行SQL命令接口"""
    try:
        data = request.json
        env = data.get("env", "test")
        sql = data.get("sql", "")

        if not sql:
            return jsonify({"code": 400, "msg": "SQL语句不能为空", "data": ""})

        # 切换数据库环境（调用原有配置读取逻辑）
        db_util.__init__(env=env)  # 重新初始化db_util为指定环境
        db_util.connect()

        # 区分查询/增删改
        if sql.strip().upper().startswith(("SELECT", "SHOW", "DESC")):
            # 查询操作
            if "LIMIT" not in sql.upper():
                sql += " LIMIT 100"  # 限制返回行数，避免前端卡死
            result = db_util.query_all(sql)
        else:
            # 增删改操作
            affect_rows = db_util.execute(sql)
            result = f"执行成功，影响行数：{affect_rows}"

        db_util.close()
        return jsonify({
            "code": 200,
            "msg": "执行成功",
            "data": result
        })
    except Exception as e:
        logger.error(f"SQL执行接口异常：{e}")
        return jsonify({"code": 500, "msg": f"执行失败：{str(e)}", "data": ""})


# -------------------------- 环境配置接口（获取所有环境） --------------------------
@app.route("/api/env/list", methods=["GET"])
def env_list():
    """获取所有环境列表（从config.ini读取）"""
    try:
        envs = ["test", "pre", "prod"]  # 可从config.ini自动解析，这里简化
        return jsonify({"code": 200, "msg": "成功", "data": envs})
    except Exception as e:
        return jsonify({"code": 500, "msg": f"获取环境失败：{str(e)}", "data": []})


# -------------------------- 启动入口 --------------------------
if __name__ == "__main__":
    # 本地测试：debug=True（代码修改自动重启），host=0.0.0.0（局域网可访问）
    app.run(host="0.0.0.0", port=5000, debug=True)

if __name__ == "__main__":
   app.run(host=WEB_HOST, port=WEB_PORT, debug=WEB_DEBUG)