"""
애플리케이션 설정 관리 모듈
환경 변수에서 API 키 및 설정을 로드합니다.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """애플리케이션 설정 클래스"""
    
    # Amadeus API 설정
    amadeus_api_key: str
    amadeus_api_secret: str
    amadeus_base_url: str = "https://test.api.amadeus.com"
    
    # AirLabs API 설정
    airlabs_api_key: str
    airlabs_base_url: str = "https://airlabs.co/api/v9"
    
    # Redis 설정
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    
    # 애플리케이션 설정
    debug: bool = True
    log_level: str = "INFO"
    
    # 캐싱 TTL (초 단위)
    cache_ttl_international: int = 10800  # 3시간
    cache_ttl_domestic: int = 21600  # 6시간
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

