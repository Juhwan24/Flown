"""
항공편 그래프 모델
공항을 노드로, 항공편 가격을 엣지 가중치로 표현
"""
from typing import Dict, List, Optional, Tuple
from datetime import date
from app.models.flight_segment import FlightSegment


class FlightGraph:
    """
    항공편 그래프 클래스
    각 공항을 노드로, 항공편 세그먼트를 엣지로 표현
    """
    
    def __init__(self):
        """그래프 초기화"""
        # 그래프 구조: {from_airport: {to_airport: [FlightSegment, ...]}}
        self.graph: Dict[str, Dict[str, List[FlightSegment]]] = {}
        
        # 한국 → 일본 진입 공항 (제한된 후보)
        self.entry_airports = ["NRT", "KIX", "FUK"]
        
        # 일본 → 한국 출구 공항 (제한된 후보)
        self.exit_airports = ["NRT", "KIX", "FUK"]
    
    def add_segment(self, segment: FlightSegment) -> None:
        """그래프에 세그먼트 추가"""
        from_airport = segment.from_airport
        to_airport = segment.to_airport
        
        if from_airport not in self.graph:
            self.graph[from_airport] = {}
        
        if to_airport not in self.graph[from_airport]:
            self.graph[from_airport][to_airport] = []
        
        self.graph[from_airport][to_airport].append(segment)
    
    def add_segments(self, segments: List[FlightSegment]) -> None:
        """여러 세그먼트를 그래프에 추가"""
        for segment in segments:
            self.add_segment(segment)
    
    def get_cheapest_segment(
        self,
        from_airport: str,
        to_airport: str,
        date_filter: Optional[date] = None
    ) -> Optional[FlightSegment]:
        """
        두 공항 사이의 최저가 세그먼트 반환
        
        Args:
            from_airport: 출발 공항
            to_airport: 도착 공항
            date_filter: 날짜 필터 (선택사항)
        
        Returns:
            최저가 FlightSegment 또는 None
        """
        if from_airport not in self.graph:
            return None
        
        if to_airport not in self.graph[from_airport]:
            return None
        
        segments = self.graph[from_airport][to_airport]
        
        # 날짜 필터 적용
        if date_filter:
            segments = [s for s in segments if s.date == date_filter]
        
        if not segments:
            return None
        
        # 최저가 세그먼트 반환
        return min(segments, key=lambda s: s.price)
    
    def get_available_destinations(self, from_airport: str) -> List[str]:
        """특정 공항에서 갈 수 있는 모든 목적지 반환"""
        if from_airport not in self.graph:
            return []
        return list(self.graph[from_airport].keys())
    
    def is_entry_airport(self, airport: str) -> bool:
        """진입 공항인지 확인"""
        return airport in self.entry_airports
    
    def is_exit_airport(self, airport: str) -> bool:
        """출구 공항인지 확인"""
        return airport in self.exit_airports
    
    def get_entry_airports(self) -> List[str]:
        """진입 공항 리스트 반환"""
        return self.entry_airports.copy()
    
    def get_exit_airports(self) -> List[str]:
        """출구 공항 리스트 반환"""
        return self.exit_airports.copy()
    
    def clear(self) -> None:
        """그래프 초기화"""
        self.graph.clear()

