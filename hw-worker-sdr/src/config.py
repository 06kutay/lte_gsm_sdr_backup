import os
from enum import Enum
try:
    from pydantic_settings import BaseSettings
    from pydantic import Field
except ImportError:
    try:
        from pydantic import BaseSettings, Field
    except ImportError:
        # Fallback to simple settings if pydantic is not installed during compile
        class BaseSettings:
            pass
        def Field(default, env=None):
            return default

class SdrType(str, Enum):
    LIMESDR = "limesdr"
    USRP = "usrp"

class SdrRole(str, Enum):
    HIGH = "high"
    LOW = "low"

class Settings(BaseSettings):
    GRPC_PORT: int = 50051
    ZMQ_PUB_PORT: int = 5556
    BACKEND_GRPC_ADDR: str = "localhost:50050"
    SDR_TYPE: SdrType = SdrType.LIMESDR
    SDR_SERIAL: str = ""
    SDR_ROLE: SdrRole = SdrRole.HIGH
    SDR_ANTENNA: str = ""  # If set, overrides the auto-derived antenna port
    FREQ_THRESHOLD_MHZ: float = 1500.0
    DEFAULT_GAIN: int = 40
    DEFAULT_TIMEOUT: int = 20
    DEFAULT_EXTRA_TIMEOUT: int = 10
    DEVICE_PATH: str = "/dev/sdr_device_1"
    GSM_TIMEOUT_PER_ARFCN: int = 15
    GSM_UDP_PORT: int = 4729
    GSM_DEFAULT_BAND: str = "GSM900"

    # Support loading from environment variables directly in standard Python
    def __init__(self, **values):
        # Override fields from env variables if present
        annotations = self.__class__.__annotations__ if hasattr(self.__class__, "__annotations__") else {}
        for key in annotations:
            env_val = os.environ.get(key)
            if env_val is not None:
                # Type conversion
                field_type = annotations[key]
                try:
                    if field_type == int:
                        values[key] = int(env_val)
                    elif field_type == float:
                        values[key] = float(env_val)
                    elif field_type == bool:
                        values[key] = env_val.lower() in ("true", "1", "yes")
                    elif field_type == SdrType:
                        values[key] = SdrType(env_val.lower())
                    elif field_type == SdrRole:
                        values[key] = SdrRole(env_val.lower())
                    else:
                        values[key] = env_val
                except Exception:
                    pass
        super().__init__(**values)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def driver(self) -> str:
        if self.SDR_TYPE == SdrType.LIMESDR:
            return "soapy"
        else:
            return "UHD"

    @property
    def antenna(self) -> str:
        if self.SDR_ANTENNA:
            return self.SDR_ANTENNA
        if self.SDR_TYPE == SdrType.LIMESDR:
            return "LNAH" if self.SDR_ROLE == SdrRole.HIGH else "LNAW"
        else:
            return "TX/RX" if self.SDR_ROLE == SdrRole.HIGH else "RX2"

settings = Settings()
