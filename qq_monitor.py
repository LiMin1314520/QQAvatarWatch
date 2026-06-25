import hashlib
import json
import os
import time
from dataclasses import dataclass
from io import BytesIO
from typing import Optional, Tuple

import requests
from PIL import Image

from config import QQConfig


@dataclass
class AvatarState:
    hash: str
    timestamp: float
    image_data: bytes


class QQAvatarMonitor:
    AVATAR_URLS = [
        "https://q.qlogo.cn/headimg_dl?dst_uin={qq}&spec=640",
        "https://q1.qlogo.cn/g?b=qq&nk={qq}&s=640",
        "https://q2.qlogo.cn/headimg_dl?dst_uin={qq}&spec=640",
    ]

    def __init__(self, config: QQConfig, state_file: str):
        self.config = config
        self.state_file = state_file
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        })

    def _compute_hash(self, image_data: bytes) -> str:
        return hashlib.sha256(image_data).hexdigest()

    def _load_state(self) -> Optional[AvatarState]:
        if not os.path.exists(self.state_file):
            return None
        try:
            with open(self.state_file, "r") as f:
                data = json.load(f)
            return AvatarState(
                hash=data["hash"],
                timestamp=data["timestamp"],
                image_data=bytes.fromhex(data["image_data"]),
            )
        except Exception:
            return None

    def _save_state(self, state: AvatarState) -> None:
        data = {
            "hash": state.hash,
            "timestamp": state.timestamp,
            "image_data": state.image_data.hex(),
        }
        with open(self.state_file, "w") as f:
            json.dump(data, f)

    def fetch_avatar(self) -> Tuple[Optional[bytes], Optional[str]]:
        for url_template in self.AVATAR_URLS:
            url = url_template.format(qq=self.config.qq_number)
            try:
                resp = self.session.get(url, timeout=10)
                if resp.status_code == 200 and resp.content:
                    img = Image.open(BytesIO(resp.content))
                    if img.width > 10 and img.height > 10:
                        buf = BytesIO()
                        img.save(buf, format="PNG")
                        data = buf.getvalue()
                        return data, self._compute_hash(data)
            except Exception:
                continue
        return None, None

    def check_for_changes(self) -> Tuple[bool, Optional[bytes], Optional[str]]:
        image_data, new_hash = self.fetch_avatar()
        if not image_data or not new_hash:
            return False, None, None

        old_state = self._load_state()
        if old_state is None:
            self._save_state(
                AvatarState(hash=new_hash, timestamp=time.time(), image_data=image_data)
            )
            return True, image_data, new_hash

        if old_state.hash != new_hash:
            self._save_state(
                AvatarState(hash=new_hash, timestamp=time.time(), image_data=image_data)
            )
            return True, image_data, new_hash

        return False, None, None
