"""
邮件发送服务模块
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
import logging

from ..core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """邮件发送服务"""

    @staticmethod
    def send_email(
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        发送邮件

        Args:
            to_email: 收件人邮箱
            subject: 邮件主题
            html_content: HTML格式邮件内容
            text_content: 纯文本格式邮件内容（可选）

        Returns:
            发送是否成功
        """
        try:
            # 创建邮件对象
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
            msg['To'] = to_email

            # 添加纯文本版本（如果提供）
            if text_content:
                part1 = MIMEText(text_content, 'plain', 'utf-8')
                msg.attach(part1)

            # 添加HTML版本
            part2 = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(part2)

            # 连接SMTP服务器并发送邮件
            if settings.SMTP_USE_TLS:
                server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT)

            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
            server.quit()

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    @staticmethod
    def send_verification_code(email: str, code: str, expire_minutes: int = 5) -> bool:
        """
        发送验证码邮件

        Args:
            email: 收件人邮箱
            code: 验证码
            expire_minutes: 过期时间（分钟）

        Returns:
            发送是否成功
        """
        subject = f"【{settings.APP_NAME}】邮箱验证码"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .code-box {{
                    background: white;
                    border: 2px dashed #667eea;
                    padding: 20px;
                    text-align: center;
                    margin: 20px 0;
                    border-radius: 8px;
                }}
                .code {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #667eea;
                    letter-spacing: 8px;
                }}
                .warning {{
                    color: #f44336;
                    font-size: 14px;
                    margin-top: 20px;
                }}
                .footer {{
                    text-align: center;
                    color: #999;
                    font-size: 12px;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📝 {settings.APP_NAME}</h1>
                    <p>邮箱验证码</p>
                </div>
                <div class="content">
                    <p>您好,</p>
                    <p>您正在注册 {settings.APP_NAME} 账号,您的验证码是:</p>

                    <div class="code-box">
                        <div class="code">{code}</div>
                    </div>

                    <p>验证码有效期为 <strong>{expire_minutes} 分钟</strong>,请尽快完成验证。</p>

                    <div class="warning">
                        <p>⚠️ 安全提示:</p>
                        <ul style="text-align: left;">
                            <li>如果这不是您本人的操作,请忽略此邮件</li>
                            <li>请勿将验证码告诉任何人</li>
                            <li>官方人员不会向您索要验证码</li>
                        </ul>
                    </div>
                </div>
                <div class="footer">
                    <p>此邮件由系统自动发送,请勿回复</p>
                    <p>&copy; 2025 {settings.APP_NAME}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        【{settings.APP_NAME}】邮箱验证码

        您好,

        您正在注册 {settings.APP_NAME} 账号,您的验证码是: {code}

        验证码有效期为 {expire_minutes} 分钟,请尽快完成验证。

        安全提示:
        - 如果这不是您本人的操作,请忽略此邮件
        - 请勿将验证码告诉任何人
        - 官方人员不会向您索要验证码

        此邮件由系统自动发送,请勿回复。
        """

        return EmailService.send_email(email, subject, html_content, text_content)
