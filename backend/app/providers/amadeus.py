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
HTTP_TIMEOUT = 30.0  # 10초 타임아웃
MAX_RETRIES = 2  # 최대 재시도 횟수
RETRY_DELAY_BASE = 10.0  # 재시도 지연 시간 (초)


class AmadeusProvider:
    """Amadeus API 프로바이더"""
    
    def __init__(self):
        self.api_key = "8xRaCxhyujnqMdLZLgoWawd8aQqAcYfU"
        self.api_secret ="Xy2e31cWqZVGD5KE"
        self.base_url = "test.api.amadeus.com"
        self.access_token: Optional[str] = None
        
        # 초기화 로깅
        logger.info(f"🔧 AmadeusProvider 초기화: base_url={self.base_url}")
        logger.debug(f"API 키 존재: {bool(self.api_key)}, 시크릿 존재: {bool(self.api_secret)}")
        
        # API 키 검증
        if not self.api_key or not self.api_secret:
            logger.error("❌ Amadeus API 키가 설정되지 않았습니다. 환경 변수를 확인하세요.")
        # HTTP 클라이언트 (재사용)
        self.client = httpx.AsyncClient(
            timeout=HTTP_TIMEOUT,
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
        )
    
    async def _get_access_token(self) -> Optional[str]:
        """Amadeus API 액세스 토큰 획득"""
        if not self.access_token:
            try:
                # OAuth 2.0 토큰 요청
                token_url = f"{self.base_url}/v1/security/oauth2/token"
                data = {
                    "grant_type": "client_credentials",
                    "client_id": self.api_key,
                    "client_secret": self.api_secret
                }
                
                logger.info(f"🔑 토큰 요청: POST {token_url}")
                
                response = await self.client.post(token_url, data=data)
                
                logger.info(f"📥 토큰 응답: HTTP {response.status_code}")
                logger.debug(f"토큰 응답 헤더: {dict(response.headers)}")
                
                response.raise_for_status()
                token_data = response.json()
                self.access_token = token_data.get("access_token")
                
                if self.access_token:
                    logger.info(f"✅ Amadeus 액세스 토큰 획득 성공 (토큰 길이: {len(self.access_token)})")
                    logger.debug(f"토큰 (처음 20자): {self.access_token[:20]}...")
                else:
                    logger.error(f"❌ Amadeus 토큰 응답에 access_token이 없습니다. 응답: {token_data}")
                    
            except httpx.HTTPStatusError as e:
                error_response = e.response.text
                logger.error(f"❌ Amadeus 토큰 요청 실패 (HTTP {e.response.status_code}): {error_response}")
                # API 키가 비어있거나 잘못된 경우
                if e.response.status_code == 401:
                    logger.error("❌ Amadeus API 인증 실패. API 키와 시크릿을 확인하세요.")
                # 토큰 캐시 초기화
                self.access_token = None
            except Exception as e:
                logger.error(f"❌ Amadeus 토큰 요청 실패: {e}")
                self.access_token = None
        
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
        logger.info(f"Amadeus 검색: {origin} → {destination} ({departure_date})")
        
        try:
            # 액세스 토큰 획득
            token = await self._get_access_token()
            if not token or not token.strip():
                logger.error("❌ Amadeus 액세스 토큰이 없습니다. API 키를 확인하세요.")
                return []
            
            # Flight Offers Search API 호출
            search_url = f"{self.base_url}/v2/shopping/flight-offers"
            date_str = DateUtils.format_date_for_api(departure_date)
            
            params = {
                "originLocationCode": origin,
                "destinationLocationCode": destination,
                "departureDate": date_str,
                "adults": 1,
                "max": 5  # 최대 5개 결과
            }
            
            if return_date:
                params["returnDate"] = DateUtils.format_date_for_api(return_date)
            
            # Authorization 헤더 형식 확인
            token_clean = token.strip()
            if not token_clean:
                logger.error("❌ 토큰이 비어있습니다")
                return []
            
            auth_header = f"Bearer {token_clean}"
            # Amadeus API 요청 헤더 (curl 예제와 동일)
            headers = {
                "Authorization": auth_header,
                "Accept": "application/vnd.amadeus+json"
            }
            
            # 헤더 검증
            if "Authorization" not in headers or not headers["Authorization"].startswith("Bearer "):
                logger.error(f"❌ Authorization 헤더 형식 오류: {headers.get('Authorization', '없음')}")
                return []
            
            logger.info(f"🔍 Flight 검색 요청: GET {search_url}")
            logger.info(f"📤 요청 파라미터: {params}")
            logger.info(f"📤 요청 헤더: {headers}")  # 전체 헤더 로깅
            
            # httpx를 사용한 GET 요청 (헤더 명시적 전달)
            # curl과 동일한 형식: -H "Authorization: Bearer TOKEN"
            try:
                response = await self.client.get(
                    search_url,
                    params=params,
                    headers=headers,
                    follow_redirects=True
                )
            except Exception as e:
                logger.error(f"❌ HTTP 요청 실패: {e}")
                logger.error(f"요청 URL: {search_url}")
                logger.error(f"요청 헤더: {headers}")
                raise
            
            logger.info(f"📥 Flight 검색 응답: HTTP {response.status_code}")
            logger.debug(f"📥 응답 헤더: {dict(response.headers)}")
            
            # 실제 전송된 요청 확인 (디버깅용)
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"🔍 실제 요청 URL: {response.request.url}")
                logger.debug(f"🔍 실제 요청 헤더: {dict(response.request.headers)}")
            
            # 응답 본문 로깅 (에러인 경우)
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    logger.error(f"❌ API 에러 응답: {error_data}")
                except:
                    logger.error(f"❌ API 에러 응답 (텍스트): {response.text[:500]}")
            
            # 401 에러인 경우 토큰을 재발급 시도
            if response.status_code == 401:
                logger.warning("⚠️ 401 에러 발생, 토큰 재발급 시도")
                self.access_token = None  # 토큰 캐시 초기화
                token = await self._get_access_token()
                if token and token.strip():
                    token_clean = token.strip()
                    headers = {
                        "Authorization": f"Bearer {token_clean}",
                        "Accept": "application/vnd.amadeus+json"
                    }
                    logger.info(f"🔄 재요청: GET {search_url}")
                    logger.info(f"🔄 재요청 헤더: {headers}")
                    response = await self.client.get(
                        search_url,
                        params=params,
                        headers=headers
                    )
                    logger.info(f"📥 재요청 응답: HTTP {response.status_code}")
                    if response.status_code >= 400:
                        try:
                            error_data = response.json()
                            logger.error(f"❌ 재요청 API 에러 응답: {error_data}")
                        except:
                            logger.error(f"❌ 재요청 API 에러 응답 (텍스트): {response.text[:500]}")
                else:
                    logger.error("❌ 토큰 재발급 실패")
                    return []
            
            # 429 에러인 경우 (Rate Limit 초과)
            if response.status_code == 429:
                error_data = response.json() if response.text else {}
                logger.warning(f"⚠️ Rate Limit 초과 (429). 응답: {error_data}")
                # Rate limit 헤더 확인
                retry_after = response.headers.get("Retry-After")
                if retry_after:
                    wait_time = int(retry_after)
                    logger.info(f"⏳ {wait_time}초 후 재시도 예정")
                else:
                    logger.warning("⚠️ Retry-After 헤더가 없습니다. 기본 대기 시간 사용")
                return []  # Rate limit 초과 시 빈 결과 반환
            
            response.raise_for_status()
            data = response.json()
            
            # 성공 응답 로깅
            logger.info(f"✅ Flight 검색 성공: {len(data.get('data', []))}개 결과")
            logger.debug(f"응답 데이터 샘플: {str(data)[:500]}...")
            
            # API 응답을 FlightSegment로 변환
            segments = self.normalize_response(data)
            logger.info(f"📊 변환된 세그먼트 수: {len(segments)}")
            return segments
            
        except httpx.HTTPStatusError as e:
            error_status = e.response.status_code
            error_text = e.response.text
            
            # 429 에러는 이미 위에서 처리했지만, raise_for_status()에서 다시 발생할 수 있음
            if error_status == 429:
                logger.warning(f"⚠️ Rate Limit 초과 (429): {error_text}")
            elif error_status == 401:
                logger.error(f"❌ 인증 실패 (401): {error_text}")
                logger.error("API 키와 시크릿을 확인하세요.")
            else:
                logger.error(f"❌ Amadeus API 호출 실패 (HTTP {error_status}): {error_text}")
        except Exception as e:
            logger.error(f"❌ Amadeus API 호출 오류: {e}")
        
        return []
    
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
                    # 최저가 세그먼트 선택
                    cheapest = min(segments, key=lambda s: s.price)
                    logger.info(f"✅ 최저가 세그먼트 선택: {cheapest.from_airport} → {cheapest.to_airport}, 가격: {cheapest.price}원")
                    return cheapest
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
        
        Amadeus API 응답 구조:
        {
            "data": [
                {
                    "itineraries": [
                        {
                            "segments": [
                                {
                                    "departure": {
                                        "iataCode": "ICN",
                                        "at": "2025-01-01T09:00:00"
                                    },
                                    "arrival": {
                                        "iataCode": "KIX",
                                        "at": "2025-01-01T11:30:00"
                                    },
                                    "carrierCode": "KE",
                                    "number": "123"
                                }
                            ]
                        }
                    ],
                    "price": {
                        "total": "82000.00",
                        "currency": "KRW"
                    }
                }
            ]
        }
        """
        segments = []
        
        try:
            data = api_response.get("data", [])
            
            for offer in data:
                # 가격 정보 추출
                price_info = offer.get("price", {})
                # Amadeus API는 "total" 또는 "grandTotal"을 사용할 수 있음
                total_price = price_info.get("grandTotal") or price_info.get("total", "0")
                currency = price_info.get("currency", "KRW")
                
                logger.debug(f"🔍 가격 정보: total={price_info.get('total')}, grandTotal={price_info.get('grandTotal')}, currency={currency}")
                
                # 가격을 숫자로 변환 (문자열일 수 있음)
                try:
                    price_value = float(total_price)
                    logger.info(f"💰 Offer 전체 가격: {price_value} {currency}")
                    # KRW가 아니면 환율 변환 필요 (여기서는 KRW로 가정)
                    if currency == "USD":
                        price_value = price_value * 1467
                    elif currency == "JPY":
                        price_value = price_value * 10
                    elif currency == "CNY":
                        price_value = price_value * 210
                    elif currency == "EUR":
                        price_value = price_value * 1600
                    elif currency == "GBP":
                        price_value = price_value * 1800
                    elif currency == "AUD":
                        price_value = price_value * 1000
                    elif currency == "CAD":
                        price_value = price_value * 1100
                    elif currency == "CHF":
                        price_value = price_value * 1500
                    elif currency == "HKD":
                        price_value = price_value * 180
                    elif currency == "NZD":
                        price_value = price_value * 1000
                    elif currency == "SEK":
                        price_value = price_value * 100
                    elif currency != "KRW":
                        logger.warning(f"⚠️ 통화 변환 필요: {currency} → KRW")
                    price = int(price_value)
                except (ValueError, TypeError) as e:
                    logger.warning(f"⚠️ 가격 파싱 실패: {total_price}, {e}")
                    continue
                
                # 항공편 정보 추출
                itineraries = offer.get("itineraries", [])
                
                for itinerary in itineraries:
                    itinerary_segments = itinerary.get("segments", [])
                    
                    if len(itinerary_segments) == 0:
                        continue
                    
                    # ⚠️ 중요: Amadeus API의 price.total은 전체 여정의 총 가격입니다
                    # 각 세그먼트에 전체 가격을 할당하면 중복 계산됩니다
                    # 
                    # 해결 방법:
                    # 1. 세그먼트가 1개인 경우: 전체 가격을 그대로 사용
                    # 2. 세그먼트가 여러 개인 경우: 전체 가격을 세그먼트 수로 나눔
                    #    (실제로는 각 세그먼트를 개별 검색하는 것이 더 정확하지만,
                    #     현재 구조에서는 이 방법이 합리적입니다)
                    segment_count = len(itinerary_segments)
                    
                    if segment_count == 1:
                        # 단일 세그먼트: 전체 가격 사용
                        segment_price = price
                    else:
                        # 여러 세그먼트: 가격을 세그먼트 수로 나눔
                        segment_price = int(price / segment_count)
                    
                    logger.info(f"💰 Offer 가격: {price}원, 세그먼트 수: {segment_count}, 세그먼트당 가격: {segment_price}원")
                    
                    for idx, segment_data in enumerate(itinerary_segments):
                        departure = segment_data.get("departure", {})
                        arrival = segment_data.get("arrival", {})
                        
                        from_airport = departure.get("iataCode", "")
                        to_airport = arrival.get("iataCode", "")
                        
                        # 날짜 추출
                        departure_at = departure.get("at", "")
                        arrival_at = arrival.get("at", "")
                        
                        # 날짜 파싱 (ISO 8601 형식: "2025-01-01T09:00:00")
                        try:
                            if departure_at:
                                date_str = departure_at.split("T")[0]  # "2025-01-01"
                                flight_date = DateUtils.parse_api_date(date_str)
                            else:
                                logger.warning("⚠️ 출발 시간 정보 없음")
                                continue
                        except Exception as e:
                            logger.warning(f"⚠️ 날짜 파싱 실패: {departure_at}, {e}")
                            continue
                        
                        # 시간 추출
                        departure_time = None
                        arrival_time = None
                        if departure_at:
                            try:
                                departure_time = departure_at.split("T")[1].split(".")[0][:5]  # "09:00"
                            except:
                                pass
                        if arrival_at:
                            try:
                                arrival_time = arrival_at.split("T")[1].split(".")[0][:5]  # "11:30"
                            except:
                                pass
                        
                        # 항공편 번호
                        carrier_code = segment_data.get("carrierCode", "")
                        flight_number_str = segment_data.get("number", "")
                        flight_number = f"{carrier_code}{flight_number_str}" if carrier_code and flight_number_str else None
                        
                        # FlightSegment 생성
                        # 각 세그먼트의 가격 사용 (전체 가격을 세그먼트 수로 나눈 값)
                        segment = FlightSegment(
                            from_airport=from_airport,
                            to_airport=to_airport,
                            price=segment_price,  # 세그먼트당 가격
                            provider="Amadeus",
                            date=flight_date,
                            flight_number=flight_number,
                            departure_time=departure_time,
                            arrival_time=arrival_time
                        )
                        
                        logger.info(f"✈️ 세그먼트 [{idx+1}/{segment_count}] 생성: {from_airport} → {to_airport}, 가격: {segment_price}원, 날짜: {flight_date}")
                        
                        segments.append(segment)
                        
                        # 가격 검증
                        if segment_price <= 0:
                            logger.warning(f"⚠️ 세그먼트 가격이 0 이하입니다: {from_airport} → {to_airport}, 가격: {segment_price}")
                        
        except Exception as e:
            logger.error(f"❌ Amadeus API 응답 파싱 오류: {e}")
            logger.debug(f"응답 데이터: {api_response}")
        
        return segments
    
    async def close(self):
        """리소스 정리 (HTTP 클라이언트 종료)"""
        await self.client.aclose()

