"""
가격 집계 모듈
여러 세그먼트의 가격을 합산하고 최적의 일정을 선택합니다.
"""
from __future__ import annotations

from typing import List, Optional
from datetime import date, timedelta

from app.models.flight_segment import FlightSegment
from app.models.itinerary import Itinerary
from app.services.flight_graph import FlightGraph


class PriceAggregator:
    """가격 집계 및 최적 일정 선택 클래스"""

    def __init__(self, graph: FlightGraph):
        self.graph = graph

    def calculate_total_cost(self, segments: List[FlightSegment]) -> int:
        """세그먼트 리스트의 총 가격 계산"""
        total = sum(segment.price for segment in segments)
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"💰 총 비용 계산: {len(segments)}개 세그먼트, 총액: {total}원")
        for idx, seg in enumerate(segments, 1):
            logger.info(f"   [{idx}] {seg.from_airport} → {seg.to_airport}: {seg.price}원")
        return total

    def build_itinerary_from_template(
        self,
        template: List[str],
        departure_date: date,
        return_date: date,
        destination: str,
        allow_same_day_transfer: bool = False,
        strict_date_match: bool = True,
    ) -> Optional[Itinerary]:
        """
        템플릿으로부터 실제 일정 구성

        Args:
            template: 공항 코드 리스트
                      예) ["ICN", "NRT", "CTS", "KIX", "ICN"]
            departure_date: 출발 날짜
            return_date: 귀국 날짜
            destination: 최종 목적지 공항 코드 (예: "CTS")
                         ⚠️ template[-2] 같은 추정 로직 금지
            allow_same_day_transfer: 당일 환승 허용 여부
            strict_date_match: True면 current_date에 해당하는 세그먼트만 사용.
                               False면 날짜 없을 때 전체 최저가 fallback 허용(권장X)

        Returns:
            Itinerary 객체 또는 None
        """
        if not template or len(template) < 3:
            return None

        segments: List[FlightSegment] = []
        current_date = departure_date
        final_destination = destination.upper()

        # 템플릿을 따라 세그먼트 구성
        for i in range(len(template) - 1):
            from_airport = template[i].upper()
            to_airport = template[i + 1].upper()

            # 1) 날짜 엄격 매칭
            if strict_date_match:
                segment = self.graph.get_cheapest_segment_strict(
                    from_airport=from_airport,
                    to_airport=to_airport,
                    flight_date=current_date,
                )
            else:
                segment = self.graph.get_cheapest_segment(
                    from_airport=from_airport,
                    to_airport=to_airport,
                    date_filter=current_date,
                ) or self.graph.get_cheapest_segment(
                    from_airport=from_airport,
                    to_airport=to_airport,
                )

            if not segment:
                # 해당 날짜/구간에 세그먼트가 없으면 일정 실패
                return None

            # 원본 세그먼트 불변성 유지 → 복사본 생성
            seg_dict = segment.model_dump()
            seg_dict["date"] = current_date
            segment_copy = FlightSegment(**seg_dict)
            segments.append(segment_copy)
            
            # 디버깅: 각 세그먼트 가격 로깅
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"🔗 일정 구성 세그먼트 [{len(segments)}]: {from_airport} → {to_airport}, 가격: {segment_copy.price}원, 날짜: {current_date}")

            # 다음 세그먼트 날짜 계산
            if to_airport == final_destination:
                # 최종 목적지 도착 → 귀국일로 점프
                current_date = return_date
            else:
                # 중간 경유지
                if allow_same_day_transfer:
                    # 당일 환승: 날짜 유지
                    pass
                else:
                    current_date += timedelta(days=1)

        total_cost = self.calculate_total_cost(segments)
        return Itinerary(segments=segments, total_cost=total_cost)

    def find_cheapest_itinerary(
        self,
        itineraries: List[Itinerary],
    ) -> Optional[Itinerary]:
        """여러 일정 중 최저가 일정 선택"""
        if not itineraries:
            return None
        return min(itineraries, key=lambda it: it.total_cost)

    def compare_with_direct(
        self,
        itinerary: Itinerary,
        direct_cost: Optional[int],
    ) -> bool:
        """직항 가격과 비교"""
        if not direct_cost:
            return True
        return itinerary.total_cost < direct_cost
