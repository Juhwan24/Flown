"""
Redis 캐싱 관리 모듈

API 호출 결과를 Redis에 캐싱하여 비용과 응답 시간을 최적화합니다.
Redis가 없어도 동작하며, 이 경우 캐싱 없이 API를 직접 호출합니다.

사용 예시:
    cache = CacheManager()
    cache.set("key", {"data": "value"}, ttl=3600)
    value = cache.get("key")
"""
import json
import redis
from typing import Optional, Any
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Redis 캐시 관리자
    
    Redis를 사용하여 API 호출 결과를 캐싱합니다.
    Redis 연결 실패 시 자동으로 캐싱 없이 동작합니다 (graceful degradation).
    """
    
    def __init__(self):
        """
        Redis 연결 초기화
        
        Redis 서버가 없거나 연결에 실패해도 애플리케이션은 정상 동작합니다.
        """
        self.redis_client: Optional[redis.Redis] = None
        self._connect()
    
    def _connect(self) -> None:
        """Redis 서버에 연결 시도"""
        try:
            self.redis_client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password,
                decode_responses=True,
                socket_connect_timeout=2,  # 2초 타임아웃
                socket_timeout=2
            )
            # 연결 테스트
            self.redis_client.ping()
            logger.info(f"Redis 연결 성공: {settings.redis_host}:{settings.redis_port}")
        except redis.ConnectionError as e:
            logger.warning(f"Redis 연결 실패: {e}. 캐싱이 비활성화됩니다.")
            self.redis_client = None
        except Exception as e:
            logger.warning(f"Redis 초기화 오류: {e}. 캐싱이 비활성화됩니다.")
            self.redis_client = None
    
    def is_available(self) -> bool:
        """Redis 사용 가능 여부 확인"""
        return self.redis_client is not None
    
    def get(self, key: str) -> Optional[Any]:
        """
        캐시에서 값 가져오기
        
        Args:
            key: 캐시 키
            
        Returns:
            캐시된 값 (없으면 None)
        """
        if not self.redis_client:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
        except json.JSONDecodeError as e:
            logger.error(f"캐시 JSON 파싱 오류 (키: {key}): {e}")
        except Exception as e:
            logger.error(f"캐시 읽기 오류 (키: {key}): {e}")
        
        return None
    
    def set(self, key: str, value: Any, ttl: int) -> bool:
        """
        캐시에 값 저장하기
        
        Args:
            key: 캐시 키
            value: 저장할 값 (JSON 직렬화 가능해야 함)
            ttl: Time To Live (초 단위)
            
        Returns:
            저장 성공 여부
        """
        if not self.redis_client:
            return False
        
        try:
            serialized = json.dumps(value, default=str, ensure_ascii=False)
            self.redis_client.setex(key, ttl, serialized)
            return True
        except (TypeError, ValueError) as e:
            logger.error(f"캐시 직렬화 오류 (키: {key}): {e}")
        except Exception as e:
            logger.error(f"캐시 쓰기 오류 (키: {key}): {e}")
        
        return False
    
    def delete(self, key: str) -> bool:
        """
        캐시에서 값 삭제하기
        
        Args:
            key: 삭제할 캐시 키
            
        Returns:
            삭제 성공 여부
        """
        if not self.redis_client:
            return False
        
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"캐시 삭제 오류 (키: {key}): {e}")
            return False
    
    def generate_key(self, prefix: str, **kwargs) -> str:
        """
        캐시 키 생성
        
        Args:
            prefix: 키 접두사 (예: "amadeus", "airlabs")
            **kwargs: 키에 포함할 파라미터들
            
        Returns:
            생성된 캐시 키 (예: "amadeus:from_airport:ICN:to_airport:KIX:date:2025-01-01")
        """
        parts = [prefix]
        for key, value in sorted(kwargs.items()):
            parts.append(f"{key}:{value}")
        return ":".join(parts)

