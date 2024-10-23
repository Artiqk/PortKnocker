import os

class Config:
    DEBUG = os.getenv("DEBUG", "False") == "True"

class DebugConfig(Config):
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    MAX_PORTS = 128

class ReleaseConfig(Config):
    DEBUG = False
    LOG_LEVEL = "INFO"
    MAX_PORTS = 128
