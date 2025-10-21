-- ===================================================
-- TextDiff MySQL 数据库初始化脚本
-- 注意：假设数据库 textdiff 已经存在
-- ===================================================

-- 选择数据库
USE textdiff;

-- 设置时区
SET time_zone = '+8:00';

-- ===================================================
-- 1. 用户相关表
-- ===================================================

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY COMMENT '用户ID',
    username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
    email VARCHAR(100) UNIQUE NOT NULL COMMENT '邮箱',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    full_name VARCHAR(100) COMMENT '全名',
    avatar_url VARCHAR(500) COMMENT '头像URL',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否激活',
    is_superuser BOOLEAN DEFAULT FALSE COMMENT '是否超级用户',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    last_login_at TIMESTAMP NULL COMMENT '最后登录时间',
    timezone VARCHAR(50) DEFAULT 'Asia/Shanghai' COMMENT '时区',
    INDEX idx_email (email),
    INDEX idx_username (username),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 用户会话表
CREATE TABLE IF NOT EXISTS user_sessions (
    id VARCHAR(36) PRIMARY KEY COMMENT '会话ID',
    user_id VARCHAR(36) NOT NULL COMMENT '用户ID',
    token VARCHAR(500) NOT NULL COMMENT 'JWT Token',
    refresh_token VARCHAR(500) COMMENT '刷新Token',
    expires_at TIMESTAMP NOT NULL COMMENT '过期时间',
    ip_address VARCHAR(45) COMMENT 'IP地址',
    user_agent TEXT COMMENT '用户代理',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_token (token(255)),
    INDEX idx_user_expires (user_id, expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户会话表';

-- ===================================================
-- 2. 文件夹/项目表
-- ===================================================

CREATE TABLE IF NOT EXISTS folders (
    id VARCHAR(36) PRIMARY KEY COMMENT '文件夹ID',
    name VARCHAR(255) NOT NULL COMMENT '名称',
    description TEXT COMMENT '描述',
    parent_id VARCHAR(36) COMMENT '父文件夹ID',
    owner_id VARCHAR(36) NOT NULL COMMENT '所有者ID',
    color VARCHAR(7) COMMENT '颜色(HEX)',
    icon VARCHAR(50) COMMENT '图标',
    is_public BOOLEAN DEFAULT FALSE COMMENT '是否公开',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (parent_id) REFERENCES folders(id) ON DELETE CASCADE,
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_owner (owner_id),
    INDEX idx_parent (parent_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='文件夹表';

-- ===================================================
-- 3. 文档表（扩展）
-- ===================================================

CREATE TABLE IF NOT EXISTS documents (
    id VARCHAR(36) PRIMARY KEY COMMENT '文档ID',
    title VARCHAR(255) NOT NULL COMMENT '标题',
    folder_id VARCHAR(36) COMMENT '文件夹ID',
    owner_id VARCHAR(36) NOT NULL COMMENT '所有者ID',
    is_public BOOLEAN DEFAULT FALSE COMMENT '是否公开',
    view_count INT DEFAULT 0 COMMENT '浏览次数',
    star_count INT DEFAULT 0 COMMENT '收藏次数',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    last_accessed_at TIMESTAMP NULL COMMENT '最后访问时间',
    current_version_number INT DEFAULT 0 COMMENT '当前版本号',
    FOREIGN KEY (folder_id) REFERENCES folders(id) ON DELETE SET NULL,
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_owner_folder (owner_id, folder_id),
    INDEX idx_created_at (created_at),
    INDEX idx_updated_at (updated_at),
    FULLTEXT INDEX ft_title_search (title)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='文档表';

-- ===================================================
-- 4. 版本表（扩展）
-- ===================================================

CREATE TABLE IF NOT EXISTS versions (
    id VARCHAR(36) PRIMARY KEY COMMENT '版本ID',
    document_id VARCHAR(36) NOT NULL COMMENT '文档ID',
    version_number INT NOT NULL COMMENT '版本号',
    content LONGTEXT NOT NULL COMMENT '内容',
    content_hash VARCHAR(64) NOT NULL COMMENT '内容哈希',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    author VARCHAR(100) DEFAULT 'anonymous' COMMENT '作者（旧字段）',
    author_id VARCHAR(36) COMMENT '作者ID',
    commit_message TEXT COMMENT '提交信息',
    save_type VARCHAR(20) DEFAULT 'manual' COMMENT '保存类型: manual, auto, draft',
    parent_version_id VARCHAR(36) COMMENT '父版本ID',
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (parent_version_id) REFERENCES versions(id) ON DELETE SET NULL,
    INDEX idx_document_version (document_id, version_number),
    INDEX idx_created_at (created_at),
    INDEX idx_content_hash (content_hash),
    INDEX idx_author (author_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='版本表';

-- ===================================================
-- 5. 版本标签表
-- ===================================================

CREATE TABLE IF NOT EXISTS version_tags (
    id VARCHAR(36) PRIMARY KEY COMMENT '标签ID',
    version_id VARCHAR(36) NOT NULL COMMENT '版本ID',
    tag_name VARCHAR(50) NOT NULL COMMENT '标签名称',
    description TEXT COMMENT '描述',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (version_id) REFERENCES versions(id) ON DELETE CASCADE,
    INDEX idx_version_id (version_id),
    INDEX idx_tag_name (tag_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='版本标签表';

-- ===================================================
-- 6. 权限与协作表
-- ===================================================

-- 文档权限表
CREATE TABLE IF NOT EXISTS document_permissions (
    id VARCHAR(36) PRIMARY KEY COMMENT '权限ID',
    document_id VARCHAR(36) NOT NULL COMMENT '文档ID',
    user_id VARCHAR(36) NOT NULL COMMENT '用户ID',
    permission ENUM('viewer', 'editor', 'admin') NOT NULL COMMENT '权限级别',
    granted_by VARCHAR(36) NOT NULL COMMENT '授权者ID',
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '授权时间',
    expires_at TIMESTAMP NULL COMMENT '过期时间',
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (granted_by) REFERENCES users(id),
    UNIQUE KEY unique_doc_user (document_id, user_id),
    INDEX idx_user_docs (user_id, permission)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='文档权限表';

-- 文档分享链接表
CREATE TABLE IF NOT EXISTS document_shares (
    id VARCHAR(36) PRIMARY KEY COMMENT '分享ID',
    document_id VARCHAR(36) NOT NULL COMMENT '文档ID',
    share_code VARCHAR(20) UNIQUE NOT NULL COMMENT '分享码',
    created_by VARCHAR(36) NOT NULL COMMENT '创建者ID',
    permission ENUM('viewer', 'editor') DEFAULT 'viewer' COMMENT '权限级别',
    password VARCHAR(255) COMMENT '密码保护',
    expires_at TIMESTAMP NULL COMMENT '过期时间',
    max_views INT COMMENT '最大访问次数',
    view_count INT DEFAULT 0 COMMENT '访问次数',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否激活',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_share_code (share_code),
    INDEX idx_document (document_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='文档分享表';

-- 收藏表
CREATE TABLE IF NOT EXISTS user_favorites (
    user_id VARCHAR(36) NOT NULL COMMENT '用户ID',
    document_id VARCHAR(36) NOT NULL COMMENT '文档ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (user_id, document_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户收藏表';

-- ===================================================
-- 7. 审计日志表
-- ===================================================

CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '日志ID',
    user_id VARCHAR(36) COMMENT '用户ID',
    document_id VARCHAR(36) COMMENT '文档ID',
    action VARCHAR(50) NOT NULL COMMENT '操作: create, update, delete, view, share',
    details JSON COMMENT '详细信息',
    ip_address VARCHAR(45) COMMENT 'IP地址',
    user_agent TEXT COMMENT '用户代理',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_user_action (user_id, action),
    INDEX idx_document (document_id),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='审计日志表';

-- ===================================================
-- 8. 创建默认管理员用户
-- ===================================================

-- 默认密码: admin123 (请在生产环境修改)
-- 密码哈希使用 bcrypt: $2b$12$
INSERT INTO users (id, username, email, password_hash, full_name, is_active, is_superuser, timezone)
VALUES (
    'default-admin-user-id-0001',
    'admin',
    'admin@textdiff.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5/PXR.qv5A9qK',  -- admin123
    '系统管理员',
    TRUE,
    TRUE,
    'Asia/Shanghai'
);

-- ===================================================
-- 完成
-- ===================================================

SELECT '数据库初始化完成！' AS status;
SELECT
    COUNT(*) as table_count,
    GROUP_CONCAT(table_name) as tables
FROM information_schema.tables
WHERE table_schema = 'textdiff';
