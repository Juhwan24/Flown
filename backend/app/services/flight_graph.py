"""
항공편 그래프 모델
공항을 노드로, 항공편 가격을 엣지 가중치로 표현
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple, Iterable, Set
from datetime import date
from app.models.flight_segment import FlightSegment


class FlightGraph:
    """
    항공편 그래프 클래스
    각 공항을 노드로, 항공편 세그먼트를 엣지로 표현

    graph 구조:
      {
        "ICN": {
          "NRT": [FlightSegment(...), ...],
          "KIX": [...]
        },
        ...
      }
    """

    DEFAULT_ENTRY_AIRPORTS = ["NRT", "KIX", "FUK"]
    DEFAULT_EXIT_AIRPORTS = ["NRT", "KIX", "FUK"]

    def __init__(
        self,
        entry_airports: Optional[Iterable[str]] = None,
        exit_airports: Optional[Iterable[str]] = None,
    ):
        """그래프 초기화"""
        self.graph: Dict[str, Dict[str, List[FlightSegment]]] = {}

        # 한국 → 일본 진입 공항 (제한된 후보)
        self.entry_airports: List[str] = [
            a.upper() for a in (entry_airports or self.DEFAULT_ENTRY_AIRPORTS)
        ]

        # 일본 → 한국 출구 공항 (제한된 후보)
        self.exit_airports: List[str] = [
            a.upper() for a in (exit_airports or self.DEFAULT_EXIT_AIRPORTS)
        ]

    # -----------------------
    # Graph mutation
    # -----------------------
    def add_segment(self, segment: FlightSegment) -> None:
        """그래프에 세그먼트 추가"""
        if not segment:
            return

        from_airport = (segment.from_airport or "").upper()
        to_airport = (segment.to_airport or "").upper()

        if not from_airport or not to_airport:
            return

        self.graph.setdefault(from_airport, {}).setdefault(to_airport, []).append(segment)

    def add_segments(self, segments: List[FlightSegment]) -> None:
        """여러 세그먼트를 그래프에 추가"""
        for segment in segments:
            self.add_segment(segment)

    def clear(self) -> None:
        """그래프 초기화"""
        self.graph.clear()

    # -----------------------
    # Query helpers
    # -----------------------
    def has_edge(self, from_airport: str, to_airport: str) -> bool:
        """해당 간선이 존재하는지 확인"""
        f = from_airport.upper()
        t = to_airport.upper()
        return f in self.graph and t in self.graph[f] and bool(self.graph[f][t])

    def get_segments(
        self,
        from_airport: str,
        to_airport: str,
        date_filter: Optional[date] = None,
    ) -> List[FlightSegment]:
        """
        두 공항 사이의 세그먼트 리스트 반환 (필요 시 날짜 필터)
        """
        f = from_airport.upper()
        t = to_airport.upper()

        if f not in self.graph or t not in self.graph[f]:
            return []

        segments = self.graph[f][t]

        if date_filter is not None:
            segments = [s for s in segments if s.date == date_filter]

        return segments

    def get_cheapest_segment(
        self,
        from_airport: str,
        to_airport: str,
        date_filter: Optional[date] = None,
    ) -> Optional[FlightSegment]:
        """
        두 공항 사이의 최저가 세그먼트 반환

        ⚠️ 주의:
        - date_filter가 주어지면 "해당 날짜" 내에서만 최저가를 반환
        - date_filter가 None이면 "전체 날짜" 중 최저가를 반환
        """
        segments = self.get_segments(from_airport, to_airport, date_filter)
        if not segments:
            return None
        return min(segments, key=lambda s: s.price)

    def get_cheapest_segment_strict(
        self,
        from_airport: str,
        to_airport: str,
        flight_date: date,
    ) -> Optional[FlightSegment]:
        """
        특정 날짜에서만 최저가 세그먼트 반환 (fallback 없음)
        - PriceAggregator/SearchEngine에서 날짜 꼬임 방지용으로 사용 권장
        """
        segment = self.get_cheapest_segment(from_airport, to_airport, date_filter=flight_date)
        if segment:
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f"🔍 그래프에서 세그먼트 조회: {from_airport} → {to_airport}, 날짜: {flight_date}, 가격: {segment.price}원")
        return segment

    def get_available_destinations(self, from_airport: str) -> List[str]:
        """특정 공항에서 갈 수 있는 모든 목적지 반환"""
        f = from_airport.upper()
        if f not in self.graph:
            return []
        return list(self.graph[f].keys())

    def get_available_origins(self) -> List[str]:
        """그래프에 존재하는 출발 공항 목록"""
        return list(self.graph.keys())

    def get_all_edges(self) -> Set[Tuple[str, str]]:
        """그래프에 존재하는 모든 간선(from,to) 집합"""
        edges: Set[Tuple[str, str]] = set()
        for f, tos in self.graph.items():
            for t, segs in tos.items():
                if segs:
                    edges.add((f, t))
        return edges

    # -----------------------
    # Entry/Exit airports
    # -----------------------
    def is_entry_airport(self, airport: str) -> bool:
        """진입 공항인지 확인"""
        return airport.upper() in self.entry_airports

    def is_exit_airport(self, airport: str) -> bool:
        """출구 공항인지 확인"""
        return airport.upper() in self.exit_airports

    def get_entry_airports(self) -> List[str]:
        """진입 공항 리스트 반환"""
        return self.entry_airports.copy()

    def get_exit_airports(self) -> List[str]:
        """출구 공항 리스트 반환"""
        return self.exit_airports.copy()

    def set_entry_airports(self, airports: Iterable[str]) -> None:
        """진입 공항 후보를 외부에서 교체/설정"""
        self.entry_airports = [a.upper() for a in airports if a]

    def set_exit_airports(self, airports: Iterable[str]) -> None:
        """출구 공항 후보를 외부에서 교체/설정"""
        self.exit_airports = [a.upper() for a in airports if a]

    def refresh_entry_exit_from_graph(
        self,
        korean_airports: Optional[Set[str]] = None,
        japanese_airports: Optional[Set[str]] = None,
    ) -> None:
        """
        그래프에 실제 존재하는 국제선 간선을 보고 entry/exit 후보를 갱신.
        (SearchEngine에서 그래프 채운 직후 호출하면 후보가 현실적으로 정리됨)

        기본 후보군이 없으면 기존 DEFAULT를 유지.
        """
        if korean_airports is None:
            korean_airports = {"ICN", "GMP", "PUS", "CJU"}
        if japanese_airports is None:
            japanese_airports = {
                "NRT", "HND", "KIX", "CTS", "FUK", "OKA", "NGO", "ITM"
            }

        entries: Set[str] = set()
        exits: Set[str] = set()

        for f, t in self.get_all_edges():
            if f in korean_airports and t in japanese_airports:
                entries.add(t)
            if f in japanese_airports and t in korean_airports:
                exits.add(f)

        if entries:
            self.entry_airports = sorted(entries)
        if exits:
            self.exit_airports = sorted(exits)
