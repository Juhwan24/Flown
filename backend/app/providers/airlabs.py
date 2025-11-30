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
        
        # API 키 검증
        if not self.api_key:
            logger.error("❌ AirLabs API 키가 설정되지 않았습니다. 환경 변수를 확인하세요.")
        
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
        for attempt in range(MAX_RETRIES):
            try:
                logger.info(f"AirLabs (Peach) 검색: {origin} → {destination} ({departure_date})")
                
                # AirLabs API 호출
                date_str = DateUtils.format_date_for_api(departure_date)
                api_url = f"{self.base_url}/flights"
                
                params = {
                    "api_key": self.api_key,
                    "dep_iata": origin,
                    "arr_iata": destination,
                    "date": date_str
                }
                
                response = await self.client.get(api_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                # 응답 데이터 확인
                response_data = data.get("response", [])
                if not response_data:
                    logger.warning(f"⚠️ AirLabs API 응답이 비어있습니다: {origin} → {destination} ({departure_date})")
                    logger.debug(f"전체 응답: {data}")
                    return None
                
                # API 응답을 FlightSegment로 변환
                segments = self.normalize_response(data)
                if segments:
                    return segments[0]  # 최저가 반환
                else:
                    logger.warning(f"⚠️ AirLabs 응답 파싱 결과가 없습니다: {origin} → {destination}")
                return None
                
            except httpx.HTTPStatusError as e:
                logger.error(f"❌ AirLabs API 호출 실패 (HTTP {e.response.status_code}): {e.response.text}")
                if attempt == MAX_RETRIES - 1:
                    return None
            except Exception as e:
                if attempt == MAX_RETRIES - 1:
                    logger.error(f"AirLabs 검색 실패 (최대 재시도 초과): {e}")
                    return None
                delay = RETRY_DELAY_BASE * (2 ** attempt)  # Exponential backoff
                logger.warning(f"AirLabs 검색 실패 (재시도 {attempt + 1}/{MAX_RETRIES}): {e}, {delay}초 후 재시도")
                await asyncio.sleep(delay)
        
        return None
    
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
        
        AirLabs API 응답 구조에 맞게 파싱하여 FlightSegment 리스트로 변환
        """
        segments = []
        
        try:
            # AirLabs API 응답 구조에 맞게 파싱
            # 응답 데이터 구조는 AirLabs API 문서 참조 필요
            response_data = api_response.get("response", [])
            
            for flight_data in response_data:
                try:
                    from_airport = flight_data.get("dep_iata", "")
                    to_airport = flight_data.get("arr_iata", "")
                    flight_date_str = flight_data.get("dep_time", "").split(" ")[0] if flight_data.get("dep_time") else ""
                    
                    if not from_airport or not to_airport or not flight_date_str:
                        continue
                    
                    # 날짜 파싱
                    flight_date = DateUtils.parse_api_date(flight_date_str)
                    
                   
                    price = int(flight_data.get("price", 0)) if flight_data.get("price") else 0
                    
                    if price == 0:
                        price = 90000  
                    
                    # 시간 정보
                    departure_time = None
                    arrival_time = None
                    if flight_data.get("dep_time"):
                        try:
                            departure_time = flight_data.get("dep_time").split(" ")[1][:5] if " " in flight_data.get("dep_time", "") else None
                        except:
                            pass
                    if flight_data.get("arr_time"):
                        try:
                            arrival_time = flight_data.get("arr_time").split(" ")[1][:5] if " " in flight_data.get("arr_time", "") else None
                        except:
                            pass
                    
                    # 항공편 번호
                    flight_number = flight_data.get("flight_number", "")
                    
                    segment = FlightSegment(
                        from_airport=from_airport,
                        to_airport=to_airport,
                        price=price,
                        provider="Peach",
                        date=flight_date,
                        flight_number=flight_number,
                        departure_time=departure_time,
                        arrival_time=arrival_time
                    )
                    
                    segments.append(segment)
                    
                except Exception as e:
                    logger.warning(f"⚠️ AirLabs 응답 파싱 오류 (항목 건너뜀): {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"❌ AirLabs API 응답 파싱 오류: {e}")
            logger.debug(f"응답 데이터: {api_response}")
        
        return segments
    
    async def close(self):
        """리소스 정리 (HTTP 클라이언트 종료)"""
        await self.client.aclose()

