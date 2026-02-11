-- 创建Web专属数据库
CREATE DATABASE IF NOT EXISTS web_sql_manager DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用该数据库
USE web_sql_manager;

-- 创建保存SQL查询条件的表（存储完整信息）
DROP TABLE IF EXISTS saved_sql_queries;
CREATE TABLE saved_sql_queries (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    config_name VARCHAR(100) NOT NULL COMMENT '配置自定义名称',
    db_alias VARCHAR(50) NOT NULL COMMENT '数据库连接别名（对应web_config中的自定义名称）',
    db_host VARCHAR(50) NOT NULL COMMENT '数据库IP',
    db_port INT NOT NULL COMMENT '数据库端口',
    db_user VARCHAR(50) NOT NULL COMMENT '数据库账号',
    db_password VARCHAR(255) NOT NULL COMMENT '数据库密码（加密存储）',
    db_name VARCHAR(50) COMMENT '数据库名（可为空）',
    table_name VARCHAR(100) COMMENT '表名（可为空）',
    operation_type VARCHAR(10) NOT NULL COMMENT '操作类型：SELECT/UPDATE/DELETE',
    fields TEXT COMMENT '查询/更新字段（JSON格式）',
    conditions TEXT COMMENT '查询条件（JSON格式）',
    update_fields TEXT COMMENT '更新字段（JSON格式，UPDATE专用）',
    limit_num INT COMMENT '返回行数',
    sql_text TEXT NOT NULL COMMENT '生成的完整SQL',
    remark TEXT COMMENT '备注信息',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_config_name (config_name),
    INDEX idx_create_time (create_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='保存的SQL查询条件表';

-- 初始化测试数据（可选）
INSERT INTO saved_sql_queries (
    config_name, db_alias, db_host, db_port, db_user, db_password,
    db_name, table_name, operation_type, fields, conditions,
    update_fields, limit_num, sql_text, remark
) VALUES (
    '测试查询-用户表',
    '测试环境-本地库',
    '127.0.0.1',
    3306,
    'root',
    '',  # 实际使用会加密
    'test_db',
    'user',
    'SELECT',
    '["id", "name", "age"]',
    '[{"field":"age","operator":">","value":"18","connector":"AND"},{"field":"status","operator":"=","value":"1","connector":""}]',
    '',
    10,
    'SELECT id, name, age FROM test_db.user WHERE age > 18 AND status = 1 LIMIT 10',
    '查询18岁以上的有效用户'
);