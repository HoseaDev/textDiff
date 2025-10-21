-- 添加邮箱验证码表
-- 执行时间: 2025-10-21

USE textdiff;

-- 创建验证码表
CREATE TABLE IF NOT EXISTS verification_codes (
    id VARCHAR(36) PRIMARY KEY COMMENT '验证码ID',
    email VARCHAR(100) NOT NULL COMMENT '邮箱地址',
    code VARCHAR(10) NOT NULL COMMENT '验证码',
    purpose VARCHAR(20) NOT NULL DEFAULT 'register' COMMENT '用途: register/login/reset_password',
    is_used BOOLEAN DEFAULT FALSE COMMENT '是否已使用',
    expires_at TIMESTAMP NOT NULL COMMENT '过期时间',
    used_at TIMESTAMP NULL COMMENT '使用时间',
    ip_address VARCHAR(45) COMMENT 'IP地址',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    INDEX idx_email (email),
    INDEX idx_email_purpose (email, purpose),
    INDEX idx_created_at (created_at),
    INDEX idx_expires_at (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='邮箱验证码表';

-- 创建定时清理过期验证码的事件(可选)
-- DELIMITER $$
-- CREATE EVENT IF NOT EXISTS cleanup_expired_verification_codes
-- ON SCHEDULE EVERY 1 HOUR
-- DO
-- BEGIN
--     DELETE FROM verification_codes
--     WHERE expires_at < NOW()
--     OR (is_used = TRUE AND used_at < DATE_SUB(NOW(), INTERVAL 7 DAY));
-- END$$
-- DELIMITER ;

SELECT 'verification_codes table created successfully' AS status;
