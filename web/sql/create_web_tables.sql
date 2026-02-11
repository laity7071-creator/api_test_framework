-- 创建本地存储库（用于保存SQL查询条件）
CREATE DATABASE IF NOT EXISTS web_sql_storage DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用该数据库
USE web_sql_storage;

-- 创建保存SQL的表
CREATE TABLE IF NOT EXISTS saved_sql_queries (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    config_name VARCHAR(50) NOT NULL COMMENT '数据库配置名称',
    db_host VARCHAR(50) NOT NULL COMMENT '数据库IP',
    db_port INT NOT NULL COMMENT '数据库端口',
    db_user VARCHAR(50) NOT NULL COMMENT '数据库账号',
    db_password VARCHAR(100) NOT NULL COMMENT '数据库密码',
    db_name VARCHAR(50) NOT NULL COMMENT '库名',
    table_name VARCHAR(50) NOT NULL COMMENT '表名',
    operation_type VARCHAR(10) NOT NULL COMMENT '操作类型（select/update）',
    fields TEXT COMMENT '查询字段',
    conditions TEXT COMMENT '查询条件（JSON格式）',
    update_fields TEXT COMMENT '更新字段（JSON格式）',
    sql_text TEXT NOT NULL COMMENT '生成的SQL文本',
    remark VARCHAR(200) DEFAULT '' COMMENT '备注',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='已保存的SQL查询条件表';