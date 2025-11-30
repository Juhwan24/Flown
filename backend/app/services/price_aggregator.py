"""
가격 집계 모듈
여러 세그먼트의 가격을 합산하고 최적의 일정을 선택합니다.
"""
from typing import List, Optional
from datetime import date, timedelta
from copy import deepcopy
from app.models.flight_segment import FlightSegment
from app.models.itinerary import Itinerary
from app.services.flight_graph import FlightGraph


class PriceAggregator:
    """가격 집계 및 최적 일정 선택 클래스"""
    
    def __init__(self, graph: FlightGraph):
        self.graph = graph
    
    def calculate_total_cost(self, segments: List[FlightSegment]) -> int:
        """세그먼트 리스트의 총 가격 계산"""
        return sum(segment.price for segment in segments)
    
    def build_itinerary_from_template(
        self,
        template: List[str],
        departure_date: date,
        return_date: date,
        trip_nights: int,
        allow_same_day_transfer: bool = False
    ) -> Optional[Itinerary]:
        """
        템플릿으로부터 실제 일정 구성
        
        Args:
            template: 공항 코드 리스트 (예: ["ICN", "KIX", "CTS", "ICN"])
            departure_date: 출발 날짜
            return_date: 귀국 날짜
            trip_nights: 체류 일수
            allow_same_day_transfer: 당일 환승 허용 여부
        
        Returns:
            Itinerary 객체 또는 None (세그먼트를 찾을 수 없는 경우)
        """
        segments = []
        current_date = departure_date
        
        # 최종 목적지 명시적 변수 (의도 분명화)
        final_destination = template[-2]
        
        # 템플릿을 따라 세그먼트 구성
        for i in range(len(template) - 1):
            from_airport = template[i]
            to_airport = template[i + 1]
            
            # 최저가 세그먼트 찾기
            segment = self.graph.get_cheapest_segment(
                from_airport=from_airport,
                to_airport=to_airport,
                date_filter=current_date
            )
            
            if not segment:
                # 날짜 필터 없이 다시 시도
                segment = self.graph.get_cheapest_segment(
                    from_airport=from_airport,
                    to_airport=to_airport
                )
            
            if not segment:
                # 세그먼트를 찾을 수 없음
                return None
            
            # 중요: 원본 세그먼트를 수정하지 않고 복사본 생성
            # Pydantic 모델의 경우 model_dump() 사용
            seg_dict = segment.model_dump()
            seg_dict["date"] = current_date
            segment_copy = FlightSegment(**seg_dict)
            segments.append(segment_copy)
            
            # 다음 세그먼트 날짜 계산
            if to_airport == final_destination:
                # 최종 목적지 도착 → 귀국일로 설정
                current_date = return_date
            else:
                # 중간 경유지: 환승 허용 여부에 따라 날짜 증가
                if allow_same_day_transfer:
                    # 당일 환승 허용: 날짜 유지 (0일 증가)
                    pass
                else:
                    # 다음날 출발: 1일 증가
                    current_date += timedelta(days=1)
        
        total_cost = self.calculate_total_cost(segments)
        return Itinerary(segments=segments, total_cost=total_cost)
    
    def find_cheapest_itinerary(
        self,
        itineraries: List[Itinerary]
    ) -> Optional[Itinerary]:
        """여러 일정 중 최저가 일정 선택"""
        if not itineraries:
            return None
        
        return min(itineraries, key=lambda it: it.total_cost)
    
    def compare_with_direct(
        self,
        itinerary: Itinerary,
        direct_cost: Optional[int]
    ) -> bool:
        """직항 가격과 비교"""
        if not direct_cost:
            return True
        
        return itinerary.total_cost < direct_cost

