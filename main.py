"""
Flown - 최저가 항공편 조합 검색 시스템
FastAPI 메인 애플리케이션
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.controllers.search_controller import router as search_router
from app.config import settings

# 로깅 설정
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="Flown API",
    description="한국-일본 최저가 항공편 조합 검색 시스템",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(search_router)


@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행"""
    logger.info("Flown API 서버 시작")
    logger.info(f"Debug 모드: {settings.debug}")


@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 실행"""
    logger.info("Flown API 서버 종료")
    # Provider 리소스 정리
    from app.controllers.search_controller import search_engine
    await search_engine.amadeus.close()
    await search_engine.airlabs.close()


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "Flown API에 오신 것을 환영합니다",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )

