"""
라우트 템플릿 엔진
브루트포스를 방지하기 위해 미리 정의된 라우트 패턴을 생성합니다.
"""
from __future__ import annotations

from typing import List, Optional, Dict, Tuple
from app.services.flight_graph import FlightGraph


class RouteTemplateEngine:
    """
    라우트 템플릿 엔진
    제한된 패턴만 생성하여 조합 폭발을 방지합니다.
    """

    def __init__(self, graph: FlightGraph):
        self.graph = graph

    def generate_templates(
        self,
        departure: str,
        destination: str,
        allow_two_entries: bool = True,
    ) -> List[List[str]]:
        """
        라우트 템플릿 생성

        Args:
            departure: 출발 공항 (예: ICN)
            destination: 최종 목적지 (예: CTS)
            allow_two_entries: ENTRY 2개 경유(D) 생성 여부

        Returns:
            라우트 템플릿 리스트

        템플릿 패턴:
        A: DEP → DEST → DEP (직항)
        B: DEP → ENTRY → DEST → DEP
        C: DEP → ENTRY → DEST → EXIT → DEP
        D: DEP → ENTRY1 → ENTRY2 → DEST → EXIT → DEP (ENTRY 2개)
        """
        dep = departure.upper()
        dest = destination.upper()

        templates: List[List[str]] = []

        entries = [e.upper() for e in self.graph.get_entry_airports()]
        exits = [x.upper() for x in self.graph.get_exit_airports()]

        # 템플릿 A: 직항 왕복
        templates.append([dep, dest, dep])

        # 템플릿 B: 진입 공항 1개 경유
        for entry in entries:
            if entry == dest:
                continue
            templates.append([dep, entry, dest, dep])

        # 템플릿 C: 진입 공항 1개, 출구 공항 1개
        for entry in entries:
            if entry == dest:
                continue
            for exit_ in exits:
                # ENTRY/EXIT가 같아도 현실적으로 문제는 없지만
                # 중복 루프를 줄이기 위해 기본은 제외
                if entry == exit_:
                    continue
                templates.append([dep, entry, dest, exit_, dep])

        # 템플릿 D: 진입 공항 2개 (순서 고려!)
        if allow_two_entries and len(entries) >= 2:
            for entry1 in entries:
                if entry1 == dest:
                    continue
                for entry2 in entries:
                    if entry2 == dest or entry2 == entry1:
                        continue
                    for exit_ in exits:
                        templates.append([dep, entry1, entry2, dest, exit_, dep])

        return templates

    def validate_template(self, template: List[str], destination: Optional[str] = None) -> bool:
        """
        템플릿 유효성 검사

        - 출발지와 최종 도착지가 일치하는지(왕복)
        - 중간에 같은 공항이 반복되지 않는지
        - 최대 중간 도시 수 제한
        - (선택) 목적지가 실제 template에 포함되는지

        NOTE:
        - 템플릿 C: middle_airports 길이 3
        - 템플릿 D: middle_airports 길이 4
          => 기존 코드의 >3 제한 때문에 D가 전부 탈락했음
        """
        if not template or len(template) < 3:
            return False

        # 왕복 여부
        if template[0].upper() != template[-1].upper():
            return False

        middle_airports = [a.upper() for a in template[1:-1]]

        # 중간 공항 중복 금지
        if len(middle_airports) != len(set(middle_airports)):
            return False

        # 최대 중간 도시 수 제한:
        #   B: 2 (ENTRY, DEST)
        #   C: 3 (ENTRY, DEST, EXIT)
        #   D: 4 (ENTRY1, ENTRY2, DEST, EXIT)
        if len(middle_airports) > 4:
            return False

        # 목적지가 주어지면 포함 여부 확인
        if destination:
            dest = destination.upper()
            if dest not in middle_airports:
                return False

        return True

    def expand_template(
        self,
        template: List[str],
        available_segments: Optional[Dict[Tuple[str, str], bool]] = None,
    ) -> List[List[str]]:
        """
        템플릿을 실제 사용 가능한 세그먼트로 확장

        Args:
            template: 라우트 템플릿
            available_segments: {(from, to): bool}
                - None이면 그래프에서 has_edge로 직접 확인

        Returns:
            유효한 경우 [template], 아니면 []
        """
        if not template or len(template) < 2:
            return []

        # available_segments가 없으면 그래프에서 확인
        if available_segments is None:
            available_segments = {}

            for i in range(len(template) - 1):
                f = template[i].upper()
                t = template[i + 1].upper()
                available_segments[(f, t)] = self.graph.has_edge(f, t)

        # 템플릿의 모든 간선이 존재하는지 확인
        for i in range(len(template) - 1):
            f = template[i].upper()
            t = template[i + 1].upper()
            if not available_segments.get((f, t), False):
                return []

        return [template]
