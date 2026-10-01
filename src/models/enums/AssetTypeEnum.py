from enum import Enum

class AssetTypeEnum(str, Enum):
    FILE = "file"
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"