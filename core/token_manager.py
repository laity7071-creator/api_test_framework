#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@作者: laity.wang
@创建日期: 2026/2/10 14:46
@文件名: token_manager.py
@项目名称: api_test_framework
@文件完整绝对路径: D:/LaityTest/api_test_framework/core\token_manager.py
@文件相对项目路径:   # 可选，不需要可以删掉这行
@描述: 
"""
# -*- coding: utf-8 -*-
"""全局Token管理工具：单例模式，确保token全局唯一"""
from utils.log_util import logger

class TokenManager:
    """
    单例模式：整个项目只有一个TokenManager实例，保证token全局共享
    核心功能：存储token、获取token、清空token、验证token有效性
    """
    # 私有静态变量：存储唯一实例和token
    _instance = None
    _token = None

    def __new__(cls):
        """单例模式：确保只创建一个实例"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def set_token(self, token: str):
        """
        设置全局token
        :param token: 登录接口返回的token字符串
        """
        if not isinstance(token, str) or len(token) == 0:
            logger.error("设置token失败：token为空或非字符串")
            raise ValueError("token必须是非空字符串")
        self._token = token
        logger.info(f"全局token设置成功：{token[:20]}...（隐藏后半段，避免日志泄露）")

    def get_token(self):
        """获取全局token（无token则抛异常）"""
        if self._token is None:
            logger.error("获取token失败：全局token未设置")
            raise RuntimeError("请先执行登录接口获取token，或手动设置token")
        return self._token

    def clear_token(self):
        """清空token（登出/切换用户时调用）"""
        self._token = None
        logger.info("全局token已清空")

    def is_token_valid(self):
        """验证token是否有效（简单校验：非空+长度>10）"""
        return self._token is not None and len(self._token) > 10

# 全局token管理器实例（项目中所有模块直接导入此实例）

token_manager = TokenManager()
# MANUAL_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjozMDAsInVzZXJfbmFtZSI6ImxhaXR5YWRtaW4iLCJyb2xlX2lkIjo2LCJwbGF0Zm9ybSI6MSwiaXNfYWRtaW4iOmZhbHNlLCJleHAiOjE3NzA3MTQ1NDQsImlhdCI6MTc3MDcwNzM0NH0.VKsR1TRA_7ucysY2MML8RaLOIogD-2yo_3VehQfC4Y4"
# token_manager.set_token(MANUAL_TOKEN)