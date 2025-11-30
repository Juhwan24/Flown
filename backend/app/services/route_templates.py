"""
라우트 템플릿 엔진
브루트포스를 방지하기 위해 미리 정의된 라우트 패턴을 생성합니다.
"""
from typing import List, Tuple, Optional
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
        destination: str
    ) -> List[List[str]]:
        """
        라우트 템플릿 생성
        
        Args:
            departure: 출발 공항 (예: ICN)
            destination: 최종 목적지 (예: CTS)
        
        Returns:
            라우트 템플릿 리스트 (각 템플릿은 공항 코드 리스트)
        
        템플릿 패턴:
        A: ICN → CTS → ICN (직항)
        B: ICN → ENTRY → CTS → ICN
        C: ICN → ENTRY → CTS → EXIT → ICN
        D: ICN → ENTRY1 → ENTRY2 → CTS → EXIT → ICN (최대 2개 중간 도시)
        """
        templates = []
        
        # 템플릿 A: 직항 왕복
        templates.append([departure, destination, departure])
        
        # 템플릿 B: 진입 공항 1개 경유
        for entry in self.graph.get_entry_airports():
            templates.append([departure, entry, destination, departure])
        
        # 템플릿 C: 진입 공항 1개, 출구 공항 1개
        for entry in self.graph.get_entry_airports():
            for exit in self.graph.get_exit_airports():
                if entry != exit:  # 같은 공항은 제외
                    templates.append([departure, entry, destination, exit, departure])
        
        # 템플릿 D: 진입 공항 2개 (최대 2개 중간 도시)
        entry_airports = self.graph.get_entry_airports()
        for i, entry1 in enumerate(entry_airports):
            for entry2 in entry_airports[i+1:]:
                for exit in self.graph.get_exit_airports():
                    templates.append([
                        departure,
                        entry1,
                        entry2,
                        destination,
                        exit,
                        departure
                    ])
        
        return templates
    
    def validate_template(self, template: List[str]) -> bool:
        """
        템플릿 유효성 검사
        
        - 출발지와 최종 도착지가 일치하는지
        - 중간에 같은 공항이 반복되지 않는지
        - 최대 중간 도시 수 제한 (2개)
        """
        if len(template) < 3:
            return False
        
        # 출발지와 최종 도착지가 일치해야 함 (왕복)
        if template[0] != template[-1]:
            return False
        
        # 중간 공항 중복 체크 (출발/도착 제외)
        middle_airports = template[1:-1]
        if len(middle_airports) != len(set(middle_airports)):
            return False
        
        # 최대 중간 도시 수: 3개 이하 (실제로는 2개 중간 도시 + 목적지)
        if len(middle_airports) > 3:
            return False
        
        return True
    
    def expand_template(
        self,
        template: List[str],
        available_segments: Optional[dict] = None
    ) -> List[List[str]]:
        """
        템플릿을 실제 사용 가능한 세그먼트로 확장
        
        Args:
            template: 라우트 템플릿
            available_segments: 사용 가능한 세그먼트 딕셔너리 {(from, to): bool}
                              None인 경우 그래프에서 확인
        
        Returns:
            확장된 라우트 리스트 (유효한 경우만)
        """
        # available_segments가 제공되지 않으면 그래프에서 확인
        if available_segments is None:
            available_segments = {}
            # 그래프에서 사용 가능한 세그먼트 확인
            for i in range(len(template) - 1):
                from_airport = template[i]
                to_airport = template[i + 1]
                # 그래프에 해당 세그먼트가 존재하는지 확인
                segment = self.graph.get_cheapest_segment(from_airport, to_airport)
                available_segments[(from_airport, to_airport)] = segment is not None
        
        # 템플릿의 모든 세그먼트가 사용 가능한지 확인
        for i in range(len(template) - 1):
            from_airport = template[i]
            to_airport = template[i + 1]
            segment_key = (from_airport, to_airport)
            
            # available_segments에 키가 없거나 False인 경우
            if not available_segments.get(segment_key, False):
                # 유효하지 않은 템플릿
                return []
        
        # 모든 세그먼트가 유효함
        return [template]

