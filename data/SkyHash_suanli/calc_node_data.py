#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@作者: laity.wang
@创建日期: 2026/2/10 14:52
@文件名: calc_node_data.py
@项目名称: api_test_framework
@文件完整绝对路径: D:/LaityTest/api_test_framework/data/SkyHash_suanli\calc_node_data.py
@文件相对项目路径:   # 可选，不需要可以删掉这行
@描述: 
"""
# -*- coding: utf-8 -*-
"""算力管理-节点管理接口测试数据"""
# 查询节点列表测试数据
get_node_list_case = {
    "case_name": "查询节点列表-默认条件",
    "request_path":"/cdpdiskapi/v1/DisklessCloudWeb/PostAreaApi",
    "request_data": {"api":"search_instances","subsystem":"iaas","area_id":"6090","request":"{\"flow_id\":\"diskless_ec71fe4d627f\",\"offset\":0,\"length\":30,\"device_types\":[0],\"ids\":[16]}"}
}

# 新增节点测试数据
add_node_case = {
    "case_name": "新增算力节点-正常参数",
    "request_data": {
        "nodeName": "测试节点001",
        "ip": "192.168.1.100",
        "port": 8080,
        "status": 1,  # 1-启用，0-禁用
        "remark": "测试节点"
    }
}

# 修改节点测试数据
update_node_case = {
    "case_name": "修改算力节点-更新备注",
    "request_data": {
        "nodeId": 1001,
        "nodeName": "测试节点001",
        "ip": "192.168.1.100",
        "port": 8080,
        "status": 1,
        "remark": "修改后的测试节点备注"
    }
}

# 删除节点测试数据
delete_node_case = {
    "case_name": "删除算力节点-正常删除",
    "request_data": {"nodeId": 1001}
}