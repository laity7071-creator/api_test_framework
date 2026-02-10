#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@作者: laity.wang
@创建日期: 2026/2/10 14:51
@文件名: test_calc_node.py
@项目名称: api_test_framework
@文件完整绝对路径: D:/LaityTest/api_test_framework/test_cases/SkyHash_suanli\test_calc_node.py
@文件相对项目路径:   # 可选，不需要可以删掉这行
@描述: 
"""
import json

import allure

# -*- coding: utf-8 -*-
"""算力管理-节点管理接口调试用例（自动携带全局token）"""
from utils.log_util import logger
from core.base_request import request_util  # 自动带token的请求实例
from data.SkyHash_suanli.calc_node_data import (  # 新增：节点管理测试数据
    get_node_list_case,
    add_node_case,
    update_node_case,
    delete_node_case
)

# -------------------------- 示例1：查询节点列表（GET） --------------------------
# 用例级别、模块、标题
@allure.feature("算力管理模块")  # 大模块
@allure.story("节点管理")         # 子模块
@allure.title("查询算力节点列表") # 用例标题
@allure.severity("critical")     # 优先级：blocker/critical/normal/minor/trivial
def test_get_calc_node_list():
    """调试：查询算力节点列表"""
    logger.info("===== 开始调试：查询算力节点列表 =====")
    try:
        # 直接调用GET接口，无需手动传token（request_util自动带）
        with allure.step("调用节点列表接口"):  # 步骤拆分
            resp = request_util.post(
                path=get_node_list_case["request_path"],  # 节点管理列表接口路径，根据实际调整
                json=get_node_list_case["request_data"]
            )
            resp_json = resp.json()

        with allure.step("解析响应结果"):
            # 2. 第一层解析：接口返回的JSON
            resp_json = resp.json()
        logger.info(f"第一层解析结果：{json.dumps(resp_json, indent=2, ensure_ascii=False)}")

        # ========== 核心修正：二次解析body.response（JSON字符串转字典） ==========
        # 提取body里的response字符串
        response_str = resp_json["body"]["response"]
        # 解析response字符串为字典（关键：之前没这步，导致断言不到instances）
        response_json = json.loads(response_str)
        logger.info(f"二次解析response结果：{json.dumps(response_json, indent=2, ensure_ascii=False)}")

        # ========== 正确的断言逻辑（按层级校验） ==========
        # 断言1：HTTP状态码（基础校验）
        with allure.step("断言结果"):
            assert resp.status_code == 200, f"HTTP状态码错误：预期200，实际{resp.status_code}"

            # 断言2：第一层ret.code（接口通用成功标识）
            assert resp_json["ret"]["code"] == 0, f"第一层ret.code错误：预期0，实际{resp_json['ret']['code']}"

            # 断言3：response里的ret.code（嵌套层成功标识）
            assert response_json["ret"]["code"] == 0, f"response.ret.code错误：预期0，实际{response_json['ret']['code']}"

            # 断言4：response.body里的total（总数，预期1）
            total = response_json["body"]["total"]
            assert total == 1, f"节点总数错误：预期1，实际{total}"

            # 断言5：response.body里的area_type（区域类型，预期6090）
            area_type = response_json["body"]["area_type"]
            assert area_type == 6090, f"区域类型错误：预期6090，实际{area_type}"

            # 断言6：instances列表存在且非空（对应你要的“list”）
            instances = response_json["body"]["instances"]
            assert isinstance(instances, list), f"instances不是列表：实际类型{type(instances)}"
            assert len(instances) > 0, "instances列表为空，未查询到节点"

            # 断言7：instances第一个节点的核心字段（可选，校验具体节点信息）
            first_instance = instances[0]
            assert first_instance["id"] == 16, f"第一个节点ID错误：预期16，实际{first_instance['id']}"
            assert first_instance["host_id"] == 16, f"第一个节点host_id错误：预期16，实际{first_instance['host_id']}"
            # 断言节点IP（net_info里的ip）
            assert first_instance["net_info"][
                       "ip"] == "10.68.5.16", f"节点IP错误：预期10.68.5.16，实际{first_instance['net_info']['ip']}"
            # 断言节点运行状态描述
            assert first_instance[
                       "running_status_desc"] == "已关机", f"节点运行状态错误：预期已关机，实际{first_instance['running_status_desc']}"

            logger.info("===== 节点列表查询用例执行成功，所有断言通过 =====")

    except json.JSONDecodeError as e:
        # 专门捕获JSON解析错误（比如response字符串格式不对）
        logger.error(f"JSON解析失败：{str(e)}，原始response字符串：{resp_json['body']['response']}")
        raise
    except Exception as e:
        logger.error(f"查询节点列表失败：{str(e)}", exc_info=True)
        raise

# # -------------------------- 示例2：新增节点（POST） --------------------------
# def test_add_calc_node():
#     """调试：新增算力节点"""
#     logger.info("===== 开始调试：新增算力节点 =====")
#     try:
#         resp = request_util.post(
#             path="/calc/node/add",  # 新增节点接口路径
#             json=add_node_case["request_data"]  # 从测试数据导入参数
#         )
#         resp_json = resp.json()
#
#         assert resp.status_code == 200
#         assert resp_json["code"] == 200
#         assert resp_json["msg"] == "新增成功"
#         logger.info(f"新增节点成功，节点ID：{resp_json['body']['nodeId']}")
#     except Exception as e:
#         logger.error(f"新增节点失败：{str(e)}", exc_info=True)
#         raise
#
# # -------------------------- 示例3：修改节点（PUT） --------------------------
# def test_update_calc_node():
#     """调试：修改算力节点"""
#     logger.info("===== 开始调试：修改算力节点 =====")
#     try:
#         resp = request_util.put(
#             path="/calc/node/update",  # 修改节点接口路径
#             json=update_node_case["request_data"]
#         )
#         resp_json = resp.json()
#
#         assert resp.status_code == 200
#         assert resp_json["msg"] == "修改成功"
#         logger.info("节点修改成功")
#     except Exception as e:
#         logger.error(f"修改节点失败：{str(e)}", exc_info=True)
#         raise
#
# # -------------------------- 示例4：删除节点（DELETE） --------------------------
# def test_delete_calc_node():
#     """调试：删除算力节点"""
#     logger.info("===== 开始调试：删除算力节点 =====")
#     try:
#         resp = request_util.delete(
#             path="/calc/node/delete",  # 删除节点接口路径
#             params={"nodeId": 1001}  # 要删除的节点ID
#         )
#         resp_json = resp.json()
#
#         assert resp.status_code == 200
#         assert resp_json["msg"] == "删除成功"
#         logger.info("节点删除成功")
#     except Exception as e:
#         logger.error(f"删除节点失败：{str(e)}", exc_info=True)
#         raise

# 执行调试（可选）
if __name__ == "__main__":
    # 先执行登录，设置全局token（若已登录可注释）
    from test_cases.SkyHash_suanli.test_login import test_login_success
    test_login_success()

    # 调试节点管理接口
    test_get_calc_node_list()
    # test_add_calc_node()
    # test_update_calc_node()
    # test_delete_calc_node()