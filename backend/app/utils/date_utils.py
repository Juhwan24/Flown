"""
날짜 유틸리티 함수 모듈
"""
from datetime import date, timedelta
from typing import List, Tuple


class DateUtils:
    """날짜 관련 유틸리티 클래스"""
    
    @staticmethod
    def get_date_range(start_date: date, end_date: date) -> List[date]:
        """시작일과 종료일 사이의 모든 날짜 리스트 반환"""
        dates = []
        current = start_date
        while current <= end_date:
            dates.append(current)
            current += timedelta(days=1)
        return dates
    
    @staticmethod
    def calculate_return_date(departure_date: date, trip_nights: int) -> date:
        """출발일과 체류 일수로 귀국일 계산"""
        return departure_date + timedelta(days=trip_nights)
    
    @staticmethod
    def get_departure_return_pairs(
        start_date: date, 
        end_date: date, 
        trip_nights: int
    ) -> List[Tuple[date, date]]:
        """출발일과 귀국일 조합 리스트 생성"""
        pairs = []
        current = start_date
        
        while current <= end_date:
            return_date = DateUtils.calculate_return_date(current, trip_nights)
            if return_date <= end_date + timedelta(days=30):  # 귀국일이 너무 늦지 않도록 제한
                pairs.append((current, return_date))
            current += timedelta(days=1)
        
        return pairs
    
    @staticmethod
    def format_date_for_api(d: date) -> str:
        """API 요청용 날짜 포맷 (YYYY-MM-DD)"""
        return d.strftime("%Y-%m-%d")
    
    @staticmethod
    def parse_api_date(date_str: str) -> date:
        """API 응답에서 날짜 문자열을 date 객체로 파싱"""
        return date.fromisoformat(date_str)
    
    @staticmethod
    def compute_segment_dates_for_template(
        template: List[str],
        departure_date: date,
        return_date: date,
        allow_same_day_transfer: bool = False
    ) -> List[date]:
        """
        템플릿에 대한 각 세그먼트의 날짜 리스트 계산
        
        Args:
            template: 공항 코드 리스트
            departure_date: 출발 날짜
            return_date: 귀국 날짜
            allow_same_day_transfer: 당일 환승 허용 여부
        
        Returns:
            각 세그먼트의 날짜 리스트
        """
        dates = []
        current_date = departure_date
        final_destination = template[-2]
        
        for i in range(len(template) - 1):
            to_airport = template[i + 1]
            dates.append(current_date)
            
            if to_airport == final_destination:
                current_date = return_date
            else:
                if not allow_same_day_transfer:
                    current_date += timedelta(days=1)
        
        return dates

