"""
항공편 세그먼트 데이터 모델
각 구간(출발지 → 도착지)의 정보를 담습니다.
"""
from pydantic import BaseModel, Field
from datetime import date as date_type
from typing import Optional


class FlightSegment(BaseModel):
    """항공편 세그먼트 모델"""
    
    from_airport: str = Field(..., description="출발 공항 코드 (예: ICN)")
    to_airport: str = Field(..., description="도착 공항 코드 (예: KIX)")
    price: int = Field(..., description="가격 (원화 기준)")
    provider: str = Field(..., description="프로바이더 이름 (Amadeus, Peach 등)")
    date: date_type = Field(..., description="출발 날짜")
    flight_number: Optional[str] = Field(None, description="항공편 번호")
    departure_time: Optional[str] = Field(None, description="출발 시간")
    arrival_time: Optional[str] = Field(None, description="도착 시간")

