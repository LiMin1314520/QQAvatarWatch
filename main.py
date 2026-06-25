import signal
import sys
import time

from config import load_config
from email_sender import EmailSender
from qq_monitor import QQAvatarMonitor


class AvatarMonitorApp:
    def __init__(self, config_path: str = "config.yaml"):
        self.config = load_config(config_path)
        self.monitor = QQAvatarMonitor(self.config.qq, self.config.state_file)
        self.email_sender = EmailSender(self.config.email)
        self.running = True

        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        print("\n正在停止...")
        self.running = False

    def run(self):
        print(f"启动 QQ 头像监控: {self.config.qq.qq_number}")
        print(f"检查间隔: {self.config.qq.check_interval_seconds} 秒")
        print(f"状态文件: {self.config.state_file}")
        print("按 Ctrl+C 停止\n")

        initial_check = True
        while self.running:
            try:
                changed, image_data, avatar_hash = self.monitor.check_for_changes()

                if changed and image_data:
                    if initial_check:
                        print(f"初始头像获取成功 (哈希: {avatar_hash[:16]}...)")
                        initial_check = False
                    else:
                        print(f"检测到头像变更! 新哈希: {avatar_hash[:16]}...")
                        if self.email_sender.send_avatar_notification(
                            self.config.qq.qq_number, image_data, avatar_hash
                        ):
                            print("邮件通知发送成功")
                        else:
                            print("邮件发送失败")

                if self.running:
                    time.sleep(self.config.qq.check_interval_seconds)

            except Exception as e:
                print(f"检查出错: {e}")
                if self.running:
                    time.sleep(60)

        print("监控已停止。")


if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    app = AvatarMonitorApp(config_path)
    app.run()
