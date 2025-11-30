"""
검색 컨트롤러
API 엔드포인트를 처리합니다.
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging
from app.models.itinerary import SearchRequest, SearchResponse
from app.services.search_engine import SearchEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["search"])

# 검색 엔진 인스턴스 (싱글톤 패턴)
search_engine = SearchEngine()


@router.post("/search", response_model=SearchResponse)
async def search_flights(request: SearchRequest) -> SearchResponse:
    """
    최저가 항공편 조합 검색
    
    Args:
        request: 검색 요청 (출발지, 목적지, 날짜 등)
    
    Returns:
        최저가 항공편 조합 정보
    
    Raises:
        HTTPException: 검색 실패 시
    """
    try:
        logger.info(f"검색 요청 수신: {request.departure} → {request.destination}")
        
        result = await search_engine.search(request)
        
        logger.info(f"검색 완료: 총 비용 {result.total_cost}원")
        
        return result
    
    except Exception as e:
        logger.error(f"검색 오류: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"검색 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """헬스 체크 엔드포인트"""
    return {"status": "healthy", "service": "Flown API"}

