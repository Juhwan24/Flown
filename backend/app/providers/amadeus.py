"""
Amadeus API 프로바이더 모듈
한국 ↔ 일본 국제선 항공편 검색
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


class AmadeusProvider:
    """Amadeus API 프로바이더"""
    
    def __init__(self):
        self.api_key = settings.amadeus_api_key
        self.api_secret = settings.amadeus_api_secret
        self.base_url = settings.amadeus_base_url
        self.access_token: Optional[str] = None
        # HTTP 클라이언트 (재사용)
        self.client = httpx.AsyncClient(
            timeout=HTTP_TIMEOUT,
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
        )
    
    async def _get_access_token(self) -> Optional[str]:
        """Amadeus API 액세스 토큰 획득"""
        # 실제 구현 시 OAuth 2.0 토큰 요청
        # 여기서는 모의 토큰 반환
        if not self.access_token:
            # 실제 API 호출 대신 모의 응답
            logger.info("Amadeus 액세스 토큰 획득 (모의)")
            self.access_token = "mock_access_token"
        return self.access_token
    
    async def search_flight(
        self,
        origin: str,
        destination: str,
        departure_date: date,
        return_date: Optional[date] = None
    ) -> List[FlightSegment]:
        """
        항공편 검색
        
        Args:
            origin: 출발 공항 코드
            destination: 도착 공항 코드
            departure_date: 출발 날짜
            return_date: 귀국 날짜 (편도인 경우 None)
        
        Returns:
            FlightSegment 리스트
        """
        # 실제 구현 시 Amadeus API 호출
        # 여기서는 모의 데이터 반환
        
        logger.info(f"Amadeus 검색: {origin} → {destination} ({departure_date})")
        
        # 모의 응답 데이터
        segments = []
        
        # 편도 검색
        outbound_segment = self._create_mock_segment(
            origin=origin,
            destination=destination,
            date=departure_date,
            base_price=80000 if origin == "ICN" else 70000
        )
        segments.append(outbound_segment)
        
        # 왕복 검색
        if return_date:
            return_segment = self._create_mock_segment(
                origin=destination,
                destination=origin,
                date=return_date,
                base_price=85000 if destination == "ICN" else 75000
            )
            segments.append(return_segment)
        
        return segments
    
    def _create_mock_segment(
        self,
        origin: str,
        destination: str,
        date: date,
        base_price: int
    ) -> FlightSegment:
        """모의 세그먼트 생성 (테스트용)"""
        # 실제 가격 변동 시뮬레이션
        import random
        price_variation = random.randint(-10000, 20000)
        final_price = max(50000, base_price + price_variation)
        
        return FlightSegment(
            from_airport=origin,
            to_airport=destination,
            price=final_price,
            provider="Amadeus",
            date=date,
            flight_number=f"KE{random.randint(100, 999)}",
            departure_time="09:00",
            arrival_time="11:30"
        )
    
    async def search_one_way(
        self,
        origin: str,
        destination: str,
        departure_date: date
    ) -> Optional[FlightSegment]:
        """편도 항공편 검색 (최저가만 반환, 재시도 포함)"""
        for attempt in range(MAX_RETRIES):
            try:
                segments = await self.search_flight(origin, destination, departure_date)
                if segments:
                    return segments[0]
                return None
            except Exception as e:
                if attempt == MAX_RETRIES - 1:
                    logger.error(f"Amadeus 검색 실패 (최대 재시도 초과): {e}")
                    raise
                delay = RETRY_DELAY_BASE * (2 ** attempt)  # Exponential backoff
                logger.warning(f"Amadeus 검색 실패 (재시도 {attempt + 1}/{MAX_RETRIES}): {e}, {delay}초 후 재시도")
                await asyncio.sleep(delay)
        
        return None
    
    def normalize_response(self, api_response: Dict[str, Any]) -> List[FlightSegment]:
        """
        Amadeus API 응답을 표준 FlightSegment 형식으로 변환
        
        실제 구현 시 API 응답 구조에 맞게 파싱
        """
        # 실제 구현 필요
        segments = []
        # 예시 파싱 로직 (실제 API 응답 구조에 맞게 수정 필요)
        # for offer in api_response.get("data", []):
        #     segment = FlightSegment(...)
        #     segments.append(segment)
        return segments
    
    async def close(self):
        """리소스 정리 (HTTP 클라이언트 종료)"""
        await self.client.aclose()

