#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@作者: laity.wang
@创建日期: 2026/2/10 15:40
@文件名: 设置allure做系统变量（永久有效）.py
@项目名称: api_test_framework
@文件完整绝对路径: D:/LaityTest/api_test_framework/盘前操作截图\设置allure做系统变量（永久有效）.py
@文件相对项目路径:   # 可选，不需要可以删掉这行
@描述: 
"""
import ctypes
import os
import sys
import winreg  # Windows 注册表模块

def set_env_permanent_windows(env_name: str, env_value: str):
    """
    Windows 永久设置系统环境变量（需管理员权限）
    :param env_name: 环境变量名（如 PATH）
    :param env_value: 新增的环境变量值
    """
    # 管理员权限检测
    if not os.environ.get("USERNAME") or not ctypes.windll.shell32.IsUserAnAdmin():
        print("❌ 请以管理员身份运行此脚本！")
        sys.exit(1)

    # 打开系统环境变量注册表（HKEY_LOCAL_MACHINE）
    reg_key = winreg.OpenKey(
        winreg.HKEY_LOCAL_MACHINE,
        r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
        0,
        winreg.KEY_READ | winreg.KEY_WRITE
    )

    try:
        # 获取现有 PATH 值
        current_value, _ = winreg.QueryValueEx(reg_key, env_name)
        # 拼接新路径（避免覆盖）
        if env_value not in current_value:
            new_value = f"{current_value};{env_value}"
            # 写入注册表
            winreg.SetValueEx(reg_key, env_name, 0, winreg.REG_EXPAND_SZ, new_value)
            print(f"✅ Windows 永久设置 {env_name} 成功！新增路径：{env_value}")
        else:
            print(f"✅ {env_value} 已存在于 {env_name} 中，无需重复设置")
    except FileNotFoundError:
        # 若环境变量不存在，直接创建
        winreg.SetValueEx(reg_key, env_name, 0, winreg.REG_EXPAND_SZ, env_value)
        print(f"✅ Windows 永久创建 {env_name} 并设置值：{env_value}")
    finally:
        winreg.CloseKey(reg_key)

    # 通知系统更新环境变量（需重启终端生效）
    os.system('setx /M PATH "%PATH%"')
    print("⚠️ 永久设置需重启终端/电脑后生效！")

if __name__ == "__main__":
    # Windows 下设置 Allure 路径（替换为你的实际路径）
    allure_bin_path = r"D:\LaityTest\allure-2.36.0\bin"
    set_env_permanent_windows("PATH", allure_bin_path)