-- ===================================================
-- 请数据库管理员执行此脚本
-- ===================================================
-- 用途：为 TextDiff 项目创建独立数据库并授权
-- 执行者：需要 MySQL 管理员权限
-- ===================================================

-- 1. 创建 textdiff 数据库
CREATE DATABASE IF NOT EXISTS textdiff
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- 2. 授予 work 用户对 textdiff 数据库的完全权限
GRANT ALL PRIVILEGES ON textdiff.* TO 'work'@'%';

-- 3. 刷新权限
FLUSH PRIVILEGES;

-- 4. 验证授权
SHOW GRANTS FOR 'work'@'%';

-- 5. 验证数据库创建
SHOW DATABASES LIKE 'textdiff';

-- ===================================================
-- 执行完成后，请告知开发人员可以继续初始化表结构
-- ===================================================
