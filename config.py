import os
import yaml
from dataclasses import dataclass


@dataclass
class QQConfig:
    qq_number: str
    check_interval_seconds: int = 300


@dataclass
class EmailConfig:
    smtp_server: str
    smtp_port: int
    username: str
    password: str
    from_email: str
    to_email: str
    use_tls: bool = True


@dataclass
class Config:
    qq: QQConfig
    email: EmailConfig
    state_file: str = "avatar_state.json"


def load_config(config_path: str = "config.yaml") -> Config:
    if not os.path.exists(config_path):
        raise FileNotFoundError(
            f"配置文件不存在: {config_path}。请复制 config.yaml.example 并填写信息。"
        )

    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    qq_config = QQConfig(
        qq_number=str(data["qq"]["qq_number"]),
        check_interval_seconds=data["qq"].get("check_interval_seconds", 300),
    )

    email_config = EmailConfig(
        smtp_server=data["email"]["smtp_server"],
        smtp_port=data["email"]["smtp_port"],
        username=data["email"]["username"],
        password=data["email"]["password"],
        from_email=data["email"]["from_email"],
        to_email=data["email"]["to_email"],
        use_tls=data["email"].get("use_tls", True),
    )

    return Config(
        qq=qq_config,
        email=email_config,
        state_file=data.get("state_file", "avatar_state.json"),
    )
