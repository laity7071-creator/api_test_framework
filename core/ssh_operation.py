#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@作者: laity.wang
@创建日期: 2026/2/9 18:51
@文件名: ssh_operation.py
@项目名称: api_test_framework
@文件完整绝对路径: D:/LaityTest/api_test_framework/core\ssh_operation.py
@文件相对项目路径:   # 可选，不需要可以删掉这行
@描述: 
"""
import paramiko
from utils.log_util import logger
from utils.common_util import common_util


class SSHOperation:
    """SSH操作类：封装远程服务器连接、执行命令、关闭"""

    def __init__(self):
        # 读取SSH配置
        self.ssh_host = common_util.read_config("SSH", "ssh_host")
        self.ssh_port = int(common_util.read_config("SSH", "ssh_port"))
        self.ssh_user = common_util.read_config("SSH", "ssh_user")
        self.ssh_password = common_util.read_config("SSH", "ssh_password")
        # SSH客户端对象
        self.ssh_client = None

    def connect(self):
        """建立SSH连接"""
        try:
            self.ssh_client = paramiko.SSHClient()
            # 允许连接未知的主机（生产环境建议配置known_hosts）
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
            raise

    def execute_command(self, command):
        """
        执行SSH命令
        :param command: 待执行的命令（如ls、ps -ef | grep java）
        :return: (stdout, stderr) 标准输出/标准错误
        """
        try:
            if not self.ssh_client:
                self.connect()
            logger.info(f"执行SSH命令：{command}")
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            # 读取输出（decode转字符串，strip去空格）
            stdout_result = stdout.read().decode("utf-8").strip()
            stderr_result = stderr.read().decode("utf-8").strip()
            logger.info(f"SSH命令执行结果：stdout={stdout_result}, stderr={stderr_result}")
            return stdout_result, stderr_result
        except Exception as e:
            logger.error(f"SSH命令执行失败：{str(e)}")
            raise

    def close(self):
        """关闭SSH连接"""
        try:
            if self.ssh_client:
                self.ssh_client.close()
                logger.info("SSH连接已关闭")
        except Exception as e:
            logger.error(f"关闭SSH连接失败：{str(e)}")
            raise

    def __del__(self):
        """析构函数：自动关闭连接"""
        self.close()


# 初始化SSH操作对象
ssh_util = SSHOperation()