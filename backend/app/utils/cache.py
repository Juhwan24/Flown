"""
Redis 캐싱 관리 모듈
API 호출 결과를 캐싱하여 비용과 응답 시간을 최적화합니다.
"""
import json
import redis
from typing import Optional, Any
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """Redis 캐시 관리자"""
    
    def __init__(self):
        """Redis 연결 초기화"""
        try:
            self.redis_client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password,
                decode_responses=True
            )
            # 연결 테스트
            self.redis_client.ping()
            logger.info("Redis 연결 성공")
        except Exception as e:
            logger.warning(f"Redis 연결 실패: {e}. 캐싱이 비활성화됩니다.")
            self.redis_client = None
    
    def get(self, key: str) -> Optional[Any]:
        """캐시에서 값 가져오기"""
        if not self.redis_client:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f"캐시 읽기 오류: {e}")
        
        return None
    
    def set(self, key: str, value: Any, ttl: int) -> bool:
        """캐시에 값 저장하기"""
        if not self.redis_client:
            return False
        
        try:
            serialized = json.dumps(value, default=str)
            self.redis_client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.error(f"캐시 쓰기 오류: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """캐시에서 값 삭제하기"""
        if not self.redis_client:
            return False
        
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"캐시 삭제 오류: {e}")
            return False
    
    def generate_key(self, prefix: str, **kwargs) -> str:
        """캐시 키 생성"""
        parts = [prefix]
        for key, value in sorted(kwargs.items()):
            parts.append(f"{key}:{value}")
        return ":".join(parts)

