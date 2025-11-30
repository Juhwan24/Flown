"""
AirLabs API 프로바이더 모듈
일본 국내선 항공편 검색 (Peach Aviation 등)
"""
import httpx
import asyncio
from typing import List, Optional, Dict, Any
from datetime import date
import logging
import time
from app.config import settings
from app.models.flight_segment import FlightSegment
from app.utils.date_utils import DateUtils

logger = logging.getLogger(__name__)

# HTTP 클라이언트 설정
HTTP_TIMEOUT = 10.0  # 10초 타임아웃
MAX_RETRIES = 3  # 최대 재시도 횟수
RETRY_DELAY_BASE = 1.0  # 재시도 지연 시간 (초)


class AirLabsProvider:
    """AirLabs API 프로바이더 (Peach Aviation 검색)"""
    
    def __init__(self):
        self.api_key = settings.airlabs_api_key
        self.base_url = settings.airlabs_base_url
        # HTTP 클라이언트 (재사용)
        self.client = httpx.AsyncClient(
            timeout=HTTP_TIMEOUT,
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
        )
    
    async def search_peach_flight(
        self,
        origin: str,
        destination: str,
        departure_date: date
    ) -> Optional[FlightSegment]:
        """
        Peach Aviation 항공편 검색 (재시도 포함)
        
        Args:
            origin: 출발 공항 코드
            destination: 도착 공항 코드
            departure_date: 출발 날짜
        
        Returns:
            최저가 FlightSegment 또는 None
        """
        # 실제 구현 시 AirLabs API 호출
        # 여기서는 모의 데이터 반환
        
        for attempt in range(MAX_RETRIES):
            try:
                logger.info(f"AirLabs (Peach) 검색: {origin} → {destination} ({departure_date})")
                
                # 일본 국내선 가격은 훨씬 저렴함
                return self._create_mock_segment(
                    origin=origin,
                    destination=destination,
                    date=departure_date
                )
            except Exception as e:
                if attempt == MAX_RETRIES - 1:
                    logger.error(f"AirLabs 검색 실패 (최대 재시도 초과): {e}")
                    raise
                delay = RETRY_DELAY_BASE * (2 ** attempt)  # Exponential backoff
                logger.warning(f"AirLabs 검색 실패 (재시도 {attempt + 1}/{MAX_RETRIES}): {e}, {delay}초 후 재시도")
                await asyncio.sleep(delay)
        
        return None
    
    def _create_mock_segment(
        self,
        origin: str,
        destination: str,
        date: date
    ) -> FlightSegment:
        """모의 세그먼트 생성 (테스트용)"""
        import random
        
        # 일본 국내선 가격 범위: 5,000 ~ 15,000원
        base_prices = {
            ("KIX", "CTS"): 12000,
            ("CTS", "KIX"): 11000,
            ("KIX", "FUK"): 8000,
            ("FUK", "KIX"): 7500,
            ("NRT", "CTS"): 15000,
            ("CTS", "NRT"): 14000,
            ("NRT", "FUK"): 9000,
            ("FUK", "NRT"): 8500,
            ("KIX", "OKA"): 10000,
            ("OKA", "KIX"): 9500,
            ("CTS", "FUK"): 18000,
            ("FUK", "CTS"): 17000,
        }
        
        key = (origin, destination)
        base_price = base_prices.get(key, 10000)
        price_variation = random.randint(-2000, 3000)
        final_price = max(5000, base_price + price_variation)
        
        return FlightSegment(
            from_airport=origin,
            to_airport=destination,
            price=final_price,
            provider="Peach",
            date=date,
            flight_number=f"MM{random.randint(100, 999)}",
            departure_time="14:00",
            arrival_time="15:30"
        )
    
    async def search_multiple_routes(
        self,
        routes: List[tuple[str, str, date]]
    ) -> List[Optional[FlightSegment]]:
        """여러 경로 동시 검색"""
        tasks = [
            self.search_peach_flight(origin, dest, dep_date)
            for origin, dest, dep_date in routes
        ]
        results = await asyncio.gather(*tasks)
        return results
    
    def normalize_response(self, api_response: Dict[str, Any]) -> List[FlightSegment]:
        """
        AirLabs API 응답을 표준 FlightSegment 형식으로 변환
        
        실제 구현 시 API 응답 구조에 맞게 파싱
        """
        # 실제 구현 필요
        segments = []
        # 예시 파싱 로직 (실제 API 응답 구조에 맞게 수정 필요)
        return segments
    
    async def close(self):
        """리소스 정리 (HTTP 클라이언트 종료)"""
        await self.client.aclose()

