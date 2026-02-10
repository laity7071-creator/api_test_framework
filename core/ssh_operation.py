#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@作者: laity.wang
@创建日期: 2026/2/9 18:51
@文件名: ssh_operation.py
@项目名称: api_test_framework
@描述: SSH操作封装（依赖common_util读取配置）
"""
import paramiko
from utils.log_util import logger
from utils.common_util import get_ssh_config  # 导入修正后的方法
from utils.common_util import get_ssh_config_batch

class SSHOperation:
    def __init__(self, env="test"):
        # 批量读取指定环境的SSH配置
        self.ssh_config = get_ssh_config_batch(env)
        self.ssh_host = self.ssh_config["ssh_host"]
        self.ssh_port = self.ssh_config["ssh_port"]
        self.ssh_user = self.ssh_config["ssh_user"]
        self.ssh_password = self.ssh_config["ssh_password"]
        self.ssh_client = None
        # ========== 新增调试日志：打印读取的配置 ==========
        logger.info(f"读取的SSH配置：host={self.ssh_host}, port={self.ssh_port}, user={self.ssh_user}")
        # 注意：密码只打印前3位，避免泄露
        logger.info(f"读取的SSH密码（前3位）：{self.ssh_password[:3]}***")

    def connect(self):
        """建立SSH连接"""
        try:
            if self.ssh_client and self.ssh_client.get_transport().is_active():
                logger.info("SSH连接已存在，无需重复连接")
                return
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(
                hostname=self.ssh_host,
                port=self.ssh_port,
                username=self.ssh_user,
                password=self.ssh_password,
                timeout=10
            )
            logger.info(f"SSH连接成功：{self.ssh_host}:{self.ssh_port}")
        except Exception as e:
            logger.error(f"SSH连接失败：{str(e)}")
            self.ssh_client = None  # 连接失败重置为None
            raise

    def execute_command(self, command):
        """执行单个SSH命令（内部自动处理连接）"""
        if not command:
            logger.error("SSH命令为空，无需执行")
            raise ValueError("SSH命令不能为空")

        try:
            if not self.ssh_client:
                self.connect()  # 自动重连
            logger.info(f"执行SSH命令：{command}")
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            stdout_result = stdout.read().decode("utf-8").strip()
            stderr_result = stderr.read().decode("utf-8").strip()
            logger.info(f"SSH命令执行结果：stdout={stdout_result}, stderr={stderr_result}")
            return stdout_result, stderr_result
        except Exception as e:
            logger.error(f"SSH命令执行失败：{str(e)}")
            raise

    def close(self):
        """关闭SSH连接（优化判断逻辑，避免属性缺失）"""
        try:
            # ========== 修改2：多层判断，避免访问不存在的属性 ==========
            if self.ssh_client:
                transport = self.ssh_client.get_transport()
                if transport and transport.is_active():
                    self.ssh_client.close()
                    logger.info("SSH连接已关闭")
                self.ssh_client = None  # 关闭后重置为None
        except Exception as e:
            logger.error(f"关闭SSH连接失败：{str(e)}")
            # 仅打印日志，不抛出异常（避免析构时放大错误）

    def __del__(self):
        """析构函数：自动关闭连接（增加异常捕获）"""
        # ========== 修改3：析构函数捕获所有异常，避免测试中断 ==========
        try:
            self.close()
        except Exception:
            pass  # 析构时的异常不影响主流程


# -------------------------- 高层封装：测试用例直接调用 --------------------------
def exec_ssh_command(command):
    """
    一键执行SSH命令（测试用例直接调用）
    :param command: 待执行的SSH命令
    :return: (stdout, stderr) 执行结果
    """
    ssh_obj = SSHOperation()
    try:
        return ssh_obj.execute_command(command)
    finally:
        ssh_obj.close()


# ========== 修改4：延迟初始化全局对象（避免导入时就报错） ==========
# 注释掉自动初始化，测试用例按需创建，或改为懒加载
# ssh_util = SSHOperation()
