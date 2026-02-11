#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Web模块专属配置（独立于接口自动化，字典式多数据库配置）
"""
import os
from Crypto.Cipher import AES

# ===================== 多数据库连接配置（字典式，新增直接加） =====================
DB_CONFIGS = {
    # 自定义名称: 连接信息（后续新增数据库直接加键值对）
    "测试环境-本地库": {
        "host": "127.0.0.1",
        "port": 3306,
        "user": "root",
        "password": "root",
        "charset": "utf8mb4"
    },
    "测试环境-2": {
        "host": "127.0.0.1",
        "port": 3306,
        "user": "root",
        "password": "root",
        "charset": "utf8mb4"
    },
    "测试环境-3": {
        "host": "127.0.0.1",
        "port": 3306,
        "user": "root",
        "password": "root",
        "charset": "utf8mb4"
    }
}

# ===================== Web本地存储库配置（保存SQL查询条件） =====================
LOCAL_WEB_DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "root",
    "database": "web_sql_manager",  # Web专属库名
    "charset": "utf8mb4"
}

# ===================== 页面/功能配置 =====================
PAGE_CONFIG = {
    "title": "可视化SQL管理平台",
    "theme_color": "#1677ff",
    "max_result_rows": 1000,
    # 支持的结果展示样式
    "result_styles": ["表格", "JSON", "卡片式", "CSV下载"],
    # 可视化SQL生成支持的操作类型
    "operation_types": ["SELECT", "UPDATE", "DELETE"],
    # 支持的条件运算符（高频常用）
    "condition_operators": [
        "=", "!=", ">", ">=", "<", "<=", "LIKE", "NOT LIKE",
        "IN", "NOT IN", "BETWEEN", "NOT BETWEEN", "IS NULL", "IS NOT NULL"
    ],
    # 条件连接符
    "condition_connectors": ["AND", "OR"]
}

# ===================== 加密配置（保存密码用） =====================
AES_CONFIG = {
    "key": b"web_sql_manager_16",  # 16字节
    "iv": b"web_iv_20260211",      # 16字节
    "mode": AES.MODE_CBC
}