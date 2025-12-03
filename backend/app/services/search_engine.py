"""
검색 엔진
전체 검색 프로세스를 조율합니다.
"""
from __future__ import annotations

import asyncio
import logging
from typing import List, Optional, Set, Tuple
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
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

        # 국제/국내 공항 셋 (국제선 판정용)
        self.korean_airports: Set[str] = {"ICN", "GMP", "PUS", "CJU"}
        self.japanese_airports: Set[str] = {
            "NRT", "HND", "KIX", "CTS", "FUK", "OKA", "NGO", "ITM"
        }

    async def search(self, request: SearchRequest) -> SearchResponse:
        """
        최저가 항공편 조합 검색

        Args:
            request: 검색 요청

        Returns:
            검색 응답 (최저가 일정)
        """
        dep = request.departure.upper()
        dest = request.destination.upper()

        logger.info(f"검색 시작: {dep} → {dest}")

        # 1. 그래프 초기화
        self.graph.clear()

        # 2. 라우트 템플릿 생성
        templates = self.template_engine.generate_templates(
            departure=dep,
            destination=dest,
            allow_two_entries=True,
        )
        logger.info(f"생성된 템플릿 수(초기): {len(templates)}")

        # 3. 필요한 세그먼트 수집 및 가격 조회
        await self._populate_graph(request, templates)

        # 3-1. 그래프 기반으로 entry/exit 후보 현실화
        # (그래프를 채운 뒤에 호출해야 의미 있음)
        self.graph.refresh_entry_exit_from_graph(
            korean_airports=self.korean_airports,
            japanese_airports=self.japanese_airports,
        )

        # entry/exit 후보가 바뀌었을 수 있으니 템플릿을 다시 생성
        templates = self.template_engine.generate_templates(
            departure=dep,
            destination=dest,
            allow_two_entries=True,
        )
        logger.info(f"생성된 템플릿 수(갱신후): {len(templates)}")

        # 4. 각 템플릿에 대해 일정 구성 및 가격 계산
        trip_nights = request.trip_nights or 3
        itineraries: List[Itinerary] = []

        # 날짜 조합은 템플릿마다 동일하므로 한 번만 계산
        date_pairs = self.date_utils.get_departure_return_pairs(
            request.start_date,
            request.end_date,
            trip_nights
        )
        candidate_pairs = date_pairs[:5]
        logger.info(f"📅 날짜 조합 수: {len(candidate_pairs)}개")

        for template in templates:
            if not self.template_engine.validate_template(template, destination=dest):
                logger.debug(f"템플릿 검증 실패: {' → '.join(template)}")
                continue

            # 템플릿 확장 (그래프에 실제 세그먼트가 있는지 확인)
            if not self.template_engine.expand_template(template):
                logger.debug(f"템플릿 스킵 (간선 없음): {' → '.join(template)}")
                continue

            # 날짜 조합별로 itinerary 구성
            for dep_date, ret_date in candidate_pairs:
                logger.debug(f"🔍 일정 구성 시도: 템플릿={' → '.join(template)}, 출발일={dep_date}, 귀국일={ret_date}")
                
                # 먼저 엄격한 날짜 매칭 시도
                itinerary = self.price_aggregator.build_itinerary_from_template(
                    template=template,
                    departure_date=dep_date,
                    return_date=ret_date,
                    destination=dest,
                    allow_same_day_transfer=False,   # 기본: 당일 환승 불허
                    strict_date_match=True,         # 기본: 날짜 엄격 매칭
                )
                
                # 엄격한 매칭 실패 시, 유연한 매칭 시도
                if not itinerary:
                    logger.debug(f"엄격한 날짜 매칭 실패, 유연한 매칭 시도: 템플릿={' → '.join(template)}")
                    itinerary = self.price_aggregator.build_itinerary_from_template(
                        template=template,
                        departure_date=dep_date,
                        return_date=ret_date,
                        destination=dest,
                        allow_same_day_transfer=False,
                        strict_date_match=False,    # 유연한 매칭: 날짜 없을 때 전체 최저가 사용
                    )
                
                if itinerary:
                    itineraries.append(itinerary)
                    logger.info(
                        f"✅ 일정 생성 성공: {itinerary.get_route_pattern()}, 비용: {itinerary.total_cost}원, 세그먼트 수: {len(itinerary.segments)}개"
                    )
                    for idx, seg in enumerate(itinerary.segments, 1):
                        logger.info(f"   [{idx}] {seg.from_airport} → {seg.to_airport}: {seg.price}원 (날짜: {seg.date})")
                else:
                    logger.warning(f"❌ 일정 구성 실패: 템플릿={' → '.join(template)}, 출발일={dep_date}, 귀국일={ret_date}")

        logger.info(f"📊 생성된 일정 수: {len(itineraries)}개")
        
        # 5. 최저가 일정 선택
        cheapest = self.price_aggregator.find_cheapest_itinerary(itineraries)
        if not cheapest:
            logger.warning("⚠️ 생성된 일정이 없음, 직항 응답 반환")
            return await self._create_direct_response(request)
        
        logger.info(f"💰 최저가 일정 선택: {cheapest.get_route_pattern()}, 비용: {cheapest.total_cost}원, 세그먼트 수: {len(cheapest.segments)}개")

        # 6. 직항 가격과 비교
        direct_cost = await self._get_direct_cost(request)
        cheaper_than_direct = self.price_aggregator.compare_with_direct(
            cheapest, direct_cost
        )

        # 7. 응답 생성 (segments 검증)
        # segments 배열에서 유효하지 않은 세그먼트 필터링
        valid_segments = [
            seg for seg in cheapest.segments 
            if seg and seg.date and seg.from_airport and seg.to_airport
        ]
        
        logger.info(f"🔍 세그먼트 검증: 원본 {len(cheapest.segments)}개 → 유효 {len(valid_segments)}개")
        
        if not valid_segments:
            logger.error(f"❌ 유효한 세그먼트가 없음! 원본 세그먼트 정보:")
            for idx, seg in enumerate(cheapest.segments, 1):
                logger.error(f"   [{idx}] 세그먼트: {seg}, date={seg.date if seg else 'None'}, from={seg.from_airport if seg else 'None'}, to={seg.to_airport if seg else 'None'}")
            logger.warning("⚠️ 직항 응답 반환")
            return await self._create_direct_response(request)
        
        return SearchResponse(
            total_cost=cheapest.total_cost,
            segments=valid_segments,
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

        # 템플릿에서 필요한 모든 간선 추출 (대문자 정규화)
        needed_segments: Set[Tuple[str, str]] = set()
        for template in templates:
            for i in range(len(template) - 1):
                f = template[i].upper()
                t = template[i + 1].upper()
                needed_segments.add((f, t))

        # 날짜 범위
        date_range = self.date_utils.get_date_range(
            request.start_date,
            request.end_date
        )
        date_range = date_range[:7]  # 최대 7일만 조회

        async def limited_fetch(fetch_coro):
            """세마포어로 동시성 제한"""
            async with self.semaphore:
                try:
                    return await fetch_coro
                except Exception as e:
                    logger.exception(f"세그먼트 조회 오류: {e}", exc_info=e)
                    return None

        tasks = []
        for from_airport, to_airport in needed_segments:
            for dep_date in date_range:
                is_international = self._is_international_route(from_airport, to_airport)

                if is_international:
                    coro = self._fetch_international_segment(
                        from_airport, to_airport, dep_date
                    )
                else:
                    coro = self._fetch_domestic_segment(
                        from_airport, to_airport, dep_date
                    )

                tasks.append(limited_fetch(coro))

        results = await asyncio.gather(*tasks, return_exceptions=True)

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
        f = from_airport.upper()
        t = to_airport.upper()

        from_kr = f in self.korean_airports
        to_kr = t in self.korean_airports
        from_jp = f in self.japanese_airports
        to_jp = t in self.japanese_airports

        # 한국 ↔ 일본 = 국제선
        if (from_kr and to_jp) or (from_jp and to_kr):
            return True

        # 일본 내 이동 = 국내선
        if from_jp and to_jp:
            return False

        # 한국 내 이동 등 알 수 없는 조합은 국내선 취급(False)
        return False

    async def _fetch_international_segment(
        self,
        from_airport: str,
        to_airport: str,
        departure_date: date
    ) -> Optional[FlightSegment]:
        """국제선 세그먼트 조회 (캐싱 포함, 직렬화 안전화)"""
        f = from_airport.upper()
        t = to_airport.upper()

        cache_key = self.cache.generate_key(
            "amadeus",
            from_airport=f,
            to_airport=t,
            date=DateUtils.format_date_for_api(departure_date)
        )

        cached = self.cache.get(cache_key)
        if cached:
            try:
                if isinstance(cached.get("date"), str):
                    cached["date"] = DateUtils.parse_api_date(cached["date"])
                return FlightSegment(**cached)
            except Exception as e:
                logger.warning(f"캐시 역직렬화 오류 (무시하고 API 호출): {e}")

        segment = await self.amadeus.search_one_way(
            origin=f,
            destination=t,
            departure_date=departure_date
        )

        if segment:
            to_cache = segment.model_dump()
            to_cache["date"] = DateUtils.format_date_for_api(segment.date)
            self.cache.set(cache_key, to_cache, ttl=10800)

        return segment

    async def _fetch_domestic_segment(
        self,
        from_airport: str,
        to_airport: str,
        departure_date: date
    ) -> Optional[FlightSegment]:
        """국내선 세그먼트 조회 (캐싱 포함, 직렬화 안전화)"""
        f = from_airport.upper()
        t = to_airport.upper()

        cache_key = self.cache.generate_key(
            "airlabs",
            from_airport=f,
            to_airport=t,
            date=DateUtils.format_date_for_api(departure_date)
        )

        cached = self.cache.get(cache_key)
        if cached:
            try:
                if isinstance(cached.get("date"), str):
                    cached["date"] = DateUtils.parse_api_date(cached["date"])
                return FlightSegment(**cached)
            except Exception as e:
                logger.warning(f"캐시 역직렬화 오류 (무시하고 API 호출): {e}")

        segment = await self.airlabs.search_peach_flight(
            origin=f,
            destination=t,
            departure_date=departure_date
        )

        if segment:
            to_cache = segment.model_dump()
            to_cache["date"] = DateUtils.format_date_for_api(segment.date)
            self.cache.set(cache_key, to_cache, ttl=21600)

        return segment

    async def _get_direct_cost(self, request: SearchRequest) -> Optional[int]:
        """직항 가격 조회"""
        dep = request.departure.upper()
        dest = request.destination.upper()

        outbound = await self._fetch_international_segment(
            dep, dest, request.start_date
        )

        return_date = self.date_utils.calculate_return_date(
            request.start_date,
            request.trip_nights or 3
        )

        inbound = await self._fetch_international_segment(
            dest, dep, return_date
        )

        if outbound and inbound:
            return outbound.price + inbound.price
        return None

    async def _create_direct_response(self, request: SearchRequest) -> SearchResponse:
        """직항만 있는 경우 응답 생성"""
        direct_cost = await self._get_direct_cost(request)
        dep = request.departure.upper()
        dest = request.destination.upper()

        return SearchResponse(
            total_cost=direct_cost or 0,
            segments=[],
            route_pattern=f"{dep} → {dest} → {dep}",
            cheaper_than_direct=False,
            direct_cost=direct_cost
        )
