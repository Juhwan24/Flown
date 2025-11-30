"""
여행 일정 및 검색 요청/응답 모델
"""
from pydantic import BaseModel, Field
from datetime import date
from typing import List, Optional
from .flight_segment import FlightSegment


class SearchRequest(BaseModel):
    """검색 요청 모델"""
    
    departure: str = Field(..., description="출발 공항 코드 (예: ICN)", min_length=3, max_length=3)
    destination: str = Field(..., description="최종 목적지 공항 코드 (예: CTS)", min_length=3, max_length=3)
    start_date: date = Field(..., description="출발 시작 날짜")
    end_date: date = Field(..., description="출발 종료 날짜")
    trip_nights: Optional[int] = Field(None, description="체류 일수 (선택사항)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "departure": "ICN",
                "destination": "CTS",
                "start_date": "2025-01-01",
                "end_date": "2025-01-10",
                "trip_nights": 3
            }
        }


class Itinerary(BaseModel):
    """여행 일정 모델"""
    
    segments: List[FlightSegment] = Field(..., description="항공편 세그먼트 목록")
    total_cost: int = Field(..., description="총 비용")
    
    def get_route_pattern(self) -> str:
        """라우트 패턴 문자열 생성 (예: ICN → KIX → CTS → FUK → ICN)"""
        airports = [seg.from_airport for seg in self.segments]
        if self.segments:
            airports.append(self.segments[-1].to_airport)
        return " → ".join(airports)
    
    def get_direct_route_pattern(self, departure: str, destination: str) -> str:
        """직항 라우트 패턴 (비교용)"""
        return f"{departure} → {destination} → {departure}"


class SearchResponse(BaseModel):
    """검색 응답 모델"""
    
    total_cost: int = Field(..., description="총 비용")
    segments: List[FlightSegment] = Field(..., description="항공편 세그먼트 목록")
    route_pattern: str = Field(..., description="라우트 패턴 문자열")
    cheaper_than_direct: bool = Field(..., description="직항보다 저렴한지 여부")
    direct_cost: Optional[int] = Field(None, description="직항 가격 (비교용)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_cost": 512340,
                "segments": [
                    {
                        "from_airport": "ICN",
                        "to_airport": "KIX",
                        "price": 82000,
                        "provider": "Amadeus",
                        "date": "2025-01-01"
                    }
                ],
                "route_pattern": "ICN → KIX → CTS → FUK → ICN",
                "cheaper_than_direct": True,
                "direct_cost": 800000
            }
        }

