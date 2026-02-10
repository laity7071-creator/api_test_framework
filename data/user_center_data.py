#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@作者: laity.wang
@创建日期: 2026/2/9 18:51
@文件名: user_center_data.py
@项目名称: api_test_framework
@文件完整绝对路径: D:/LaityTest/api_test_framework/data\user_center_data.py
@文件相对项目路径:   # 可选，不需要可以删掉这行
@描述: 
"""


class UserCenterData:
    """个人中心接口测试数据"""

    # 获取个人信息用例
    get_user_info_case = {
        "case_name": "获取个人信息-已登录",
        "request_params": {
            "user_id": 1001  # 测试用户ID
        },
        "headers": {
            "token": "test_token_123456"  # 登录后的token
        },
        "expected_code": 200,
        "expected_username": "test_user"
    }

    # 更新个人信息用例
    update_user_info_case = {
        "case_name": "更新个人信息-昵称修改",
        "request_data": {
            "user_id": 1001,
            "nickname": "测试用户_2026",
            "phone": "13800138000"
        },
        "headers": {
            "token": "test_token_123456"
        },
        "expected_code": 200,
        "expected_msg": "更新成功"
    }


# 初始化个人中心测试数据
user_center_data = UserCenterData()