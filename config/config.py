import sys
from pathlib import Path

class Config:
    @staticmethod
    def resource_path(relative_path):
        if hasattr(sys, '_MEIPASS'):
            return Path(sys._MEIPASS) / relative_path
        return Path(relative_path)

    LOGO_PATH = resource_path("assets/favicon.ico")
    LOG_PATH = resource_path("assets/logs.txt")
    MODEL_PATH = resource_path("assets/model.onnx")
    
    SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
    VIDEO_ID_PATTERN = r"(?:v=|\/)([0-9A-Za-z_-]{11})"