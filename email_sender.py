import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.utils import formatdate

from config import EmailConfig


class EmailSender:
    def __init__(self, config: EmailConfig):
        self.config = config

    def send_avatar_notification(
        self, qq_number: str, image_data: bytes, avatar_hash: str
    ) -> bool:
        try:
            msg = MIMEMultipart()
            msg["From"] = self.config.from_email
            msg["To"] = self.config.to_email
            msg["Subject"] = f"QQ {qq_number} 头像已更新"
            msg["Date"] = formatdate(localtime=True)

            body = (
                f"QQ 头像变更检测\n\n"
                f"QQ 号: {qq_number}\n"
                f"新头像哈希: {avatar_hash[:16]}...\n"
                f"时间: {formatdate(localtime=True)}\n\n"
                "新头像已作为附件发送。"
            )
            msg.attach(MIMEText(body, "plain", "utf-8"))

            img = MIMEImage(image_data, name=f"qq_{qq_number}_avatar.png")
            img.add_header(
                "Content-Disposition",
                "attachment",
                filename=f"qq_{qq_number}_avatar.png",
            )
            msg.attach(img)

            if self.config.smtp_port == 465 or (
                self.config.use_tls is False and self.config.smtp_port != 587
            ):
                with smtplib.SMTP_SSL(
                    self.config.smtp_server, self.config.smtp_port
                ) as server:
                    server.login(self.config.username, self.config.password)
                    server.send_message(msg)
            else:
                with smtplib.SMTP(
                    self.config.smtp_server, self.config.smtp_port
                ) as server:
                    if self.config.use_tls:
                        server.starttls()
                    server.login(self.config.username, self.config.password)
                    server.send_message(msg)

            return True

        except Exception as e:
            print(f"发送邮件失败: {e}")
            return False
