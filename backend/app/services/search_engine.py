"""
검색 엔진
전체 검색 프로세스를 조율합니다.
"""
import asyncio
import logging
from typing import List, Optional
from datetime import date
from app.models.itinerary import Itinerary, SearchRequest, SearchResponse
from app.models.flight_segment import FlightSegment
from app.services.flight_graph import FlightGraph
from app.services.route_templates import RouteTemplateEngine
from app.services.price_aggregator import PriceAggregator
from app.providers.amadeus import AmadeusProvider
from app.providers.airlabs import AirLabsProvider
from app.utils.cache import CacheManager
from app.utils.date_utils import DateUtils

logger = logging.getLogger(__name__)

# 동시성 제한 설정
MAX_CONCURRENT_REQUESTS = 20  # 동시 최대 요청 수


class SearchEngine:
    """항공편 검색 엔진"""
    
    def __init__(self):
        self.graph = FlightGraph()
        self.template_engine = RouteTemplateEngine(self.graph)
        self.price_aggregator = PriceAggregator(self.graph)
        self.amadeus = AmadeusProvider()
        self.airlabs = AirLabsProvider()
        self.cache = CacheManager()
        self.date_utils = DateUtils()
        # 동시성 제한을 위한 세마포어
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    
    async def search(self, request: SearchRequest) -> SearchResponse:
        """
        최저가 항공편 조합 검색
        
        Args:
            request: 검색 요청
        
        Returns:
            검색 응답 (최저가 일정)
        """
        logger.info(f"검색 시작: {request.departure} → {request.destination}")
        
        # 1. 그래프 초기화
        self.graph.clear()
        
        # 2. 라우트 템플릿 생성
        templates = self.template_engine.generate_templates(
            departure=request.departure,
            destination=request.destination
        )
        
        logger.info(f"생성된 템플릿 수: {len(templates)}")
        
        # 3. 필요한 세그먼트 수집 및 가격 조회
        await self._populate_graph(request, templates)
        
        # 4. 각 템플릿에 대해 일정 구성 및 가격 계산
        trip_nights = request.trip_nights or 3
        itineraries = []
        
        for template in templates:
            if not self.template_engine.validate_template(template):
                continue
            
            # 템플릿 확장 (그래프에 실제 세그먼트가 있는지 확인)
            expanded = self.template_engine.expand_template(template)
            if not expanded:
                # 유효하지 않은 템플릿 스킵
                logger.debug(f"템플릿 스킵 (세그먼트 없음): {' → '.join(template)}")
                continue
            
            # 여러 날짜 조합 시도
            date_pairs = self.date_utils.get_departure_return_pairs(
                request.start_date,
                request.end_date,
                trip_nights
            )
            
            # 날짜 조합을 우선순위로 정렬 (휴리스틱: 주말/평일 고려)
            # 간단히 처음 5개만 선택 (향후 개선 가능)
            for dep_date, ret_date in date_pairs[:5]:
                itinerary = self.price_aggregator.build_itinerary_from_template(
                    template=template,
                    departure_date=dep_date,
                    return_date=ret_date,
                    trip_nights=trip_nights,
                    allow_same_day_transfer=False  # 당일 환승 불허 (기본값)
                )
                
                if itinerary:
                    itineraries.append(itinerary)
                    logger.debug(f"일정 생성 성공: {itinerary.get_route_pattern()}, 비용: {itinerary.total_cost}원")
        
        # 5. 최저가 일정 선택
        cheapest = self.price_aggregator.find_cheapest_itinerary(itineraries)
        
        if not cheapest:
            # 직항만 반환
            return await self._create_direct_response(request)
        
        # 6. 직항 가격과 비교
        direct_cost = await self._get_direct_cost(request)
        cheaper_than_direct = self.price_aggregator.compare_with_direct(
            cheapest,
            direct_cost
        )
        
        # 7. 응답 생성
        return SearchResponse(
            total_cost=cheapest.total_cost,
            segments=cheapest.segments,
            route_pattern=cheapest.get_route_pattern(),
            cheaper_than_direct=cheaper_than_direct,
            direct_cost=direct_cost
        )
    
    async def _populate_graph(
        self,
        request: SearchRequest,
        templates: List[List[str]]
    ) -> None:
        """그래프에 필요한 세그먼트 데이터 채우기 (동시성 제한 적용)"""
        # 템플릿에서 필요한 모든 세그먼트 추출
        needed_segments = set()
        for template in templates:
            for i in range(len(template) - 1):
                needed_segments.add((template[i], template[i + 1]))
        
        # 날짜 범위
        date_range = self.date_utils.get_date_range(
            request.start_date,
            request.end_date
        )
        
        # 동시성 제한 래퍼 함수
        async def limited_fetch(fetch_coro):
            """세마포어로 동시성 제한"""
            async with self.semaphore:
                try:
                    return await fetch_coro
                except Exception as e:
                    logger.exception(f"세그먼트 조회 오류: {e}", exc_info=e)
                    return None
        
        # 세그먼트별로 가격 조회 (비동기 병렬 처리, 동시성 제한)
        tasks = []
        for from_airport, to_airport in needed_segments:
            for dep_date in date_range[:7]:  # 최대 7일만 조회
                # 국제선인지 국내선인지 판단
                is_international = self._is_international_route(
                    from_airport,
                    to_airport
                )
                
                if is_international:
                    coro = self._fetch_international_segment(
                        from_airport,
                        to_airport,
                        dep_date
                    )
                else:
                    coro = self._fetch_domestic_segment(
                        from_airport,
                        to_airport,
                        dep_date
                    )
                
                # 동시성 제한 적용
                tasks.append(limited_fetch(coro))
        
        # 모든 세그먼트 병렬 조회 (동시성 제한 적용)
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 결과를 그래프에 추가
        success_count = 0
        error_count = 0
        for result in results:
            if isinstance(result, Exception):
                error_count += 1
                logger.error(f"세그먼트 조회 오류: {result}")
                continue
            
            if result:
                self.graph.add_segment(result)
                success_count += 1
        
        logger.info(f"그래프 채우기 완료: 성공 {success_count}개, 실패 {error_count}개")
    
    def _is_international_route(self, from_airport: str, to_airport: str) -> bool:
        """국제선인지 국내선인지 판단"""
        korean_airports = {"ICN", "GMP", "PUS", "CJU"}
        japanese_airports = {
            "NRT", "HND", "KIX", "CTS", "FUK", "OKA", "NGO", "ITM"
        }
        
        from_kr = from_airport in korean_airports
        to_kr = to_airport in korean_airports
        from_jp = from_airport in japanese_airports
        to_jp = to_airport in japanese_airports
        
        # 한국 ↔ 일본 = 국제선
        if (from_kr and to_jp) or (from_jp and to_kr):
            return True
        
        # 일본 내 이동 = 국내선
        if from_jp and to_jp:
            return False
        
        # 한국 내 이동 = 국내선 (일반적으로는 국제선 API 사용 안 함)
        # 알 수 없는 조합은 False로 처리 (안전한 기본값)
        return False
    
    async def _fetch_international_segment(
        self,
        from_airport: str,
        to_airport: str,
        departure_date: date
    ) -> Optional[FlightSegment]:
        """국제선 세그먼트 조회 (캐싱 포함, 직렬화 안전화)"""
        # 캐시 키 생성
        cache_key = self.cache.generate_key(
            "amadeus",
            from_airport=from_airport,
            to_airport=to_airport,
            date=DateUtils.format_date_for_api(departure_date)
        )
        
        # 캐시 확인
        cached = self.cache.get(cache_key)
        if cached:
            try:
                # 날짜 문자열을 date 객체로 파싱
                if isinstance(cached.get("date"), str):
                    cached["date"] = DateUtils.parse_api_date(cached["date"])
                # 캐시된 데이터를 FlightSegment로 변환
                return FlightSegment(**cached)
            except Exception as e:
                logger.warning(f"캐시 역직렬화 오류 (무시하고 API 호출): {e}")
                # 캐시 오류 시 API 호출로 폴백
        
        # API 호출
        segment = await self.amadeus.search_one_way(
            origin=from_airport,
            destination=to_airport,
            departure_date=departure_date
        )
        
        # 캐시 저장 (직렬화 안전화)
        if segment:
            to_cache = segment.model_dump()
            # date 객체를 문자열로 변환
            to_cache["date"] = DateUtils.format_date_for_api(segment.date)
            self.cache.set(
                cache_key,
                to_cache,
                ttl=10800  # 3시간
            )
        
        return segment
    
    async def _fetch_domestic_segment(
        self,
        from_airport: str,
        to_airport: str,
        departure_date: date
    ) -> Optional[FlightSegment]:
        """국내선 세그먼트 조회 (캐싱 포함, 직렬화 안전화)"""
        # 캐시 키 생성
        cache_key = self.cache.generate_key(
            "airlabs",
            from_airport=from_airport,
            to_airport=to_airport,
            date=DateUtils.format_date_for_api(departure_date)
        )
        
        # 캐시 확인
        cached = self.cache.get(cache_key)
        if cached:
            try:
                # 날짜 문자열을 date 객체로 파싱
                if isinstance(cached.get("date"), str):
                    cached["date"] = DateUtils.parse_api_date(cached["date"])
                return FlightSegment(**cached)
            except Exception as e:
                logger.warning(f"캐시 역직렬화 오류 (무시하고 API 호출): {e}")
                # 캐시 오류 시 API 호출로 폴백
        
        # API 호출
        segment = await self.airlabs.search_peach_flight(
            origin=from_airport,
            destination=to_airport,
            departure_date=departure_date
        )
        
        # 캐시 저장 (직렬화 안전화)
        if segment:
            to_cache = segment.model_dump()
            # date 객체를 문자열로 변환
            to_cache["date"] = DateUtils.format_date_for_api(segment.date)
            self.cache.set(
                cache_key,
                to_cache,
                ttl=21600  # 6시간
            )
        
        return segment
    
    async def _get_direct_cost(self, request: SearchRequest) -> Optional[int]:
        """직항 가격 조회"""
        # 직항 왕복 가격 조회
        outbound = await self._fetch_international_segment(
            request.departure,
            request.destination,
            request.start_date
        )
        
        return_date = self.date_utils.calculate_return_date(
            request.start_date,
            request.trip_nights or 3
        )
        
        inbound = await self._fetch_international_segment(
            request.destination,
            request.departure,
            return_date
        )
        
        if outbound and inbound:
            return outbound.price + inbound.price
        
        return None
    
    async def _create_direct_response(
        self,
        request: SearchRequest
    ) -> SearchResponse:
        """직항만 있는 경우 응답 생성"""
        direct_cost = await self._get_direct_cost(request)
        
        return SearchResponse(
            total_cost=direct_cost or 0,
            segments=[],
            route_pattern=f"{request.departure} → {request.destination} → {request.departure}",
            cheaper_than_direct=False,
            direct_cost=direct_cost
        )

