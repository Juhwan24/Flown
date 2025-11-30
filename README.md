# Flown - 최저가 항공편 조합 검색 시스템

한국에서 일본으로 가는 최저가 항공편 조합을 자동으로 찾는 백엔드 시스템입니다.

## 주요 기능

- 다중 항공사 API 통합 (Amadeus, AirLabs)
- 도시 그래프 기반 라우트 탐색
- 템플릿 기반 라우트 패턴 검색 (브루트포스 방지)
- 비동기 API 호출
- Redis 캐싱으로 API 호출 최소화
- FastAPI 기반 RESTful API

## 설치 및 실행

1. 의존성 설치:
```bash
pip install -r requirements.txt
```

2. 환경 변수 설정:
```bash
cp .env.example .env
# .env 파일에 API 키 입력
```

3. Redis 실행 (선택사항, 캐싱 사용 시):
```bash
redis-server
```

4. 애플리케이션 실행:
```bash
uvicorn main:app --reload
```

## API 사용법

### POST /search

최저가 항공편 조합 검색

**Request Body:**
```json
{
  "departure": "ICN",
  "destination": "CTS",
  "startDate": "2025-01-01",
  "endDate": "2025-01-10",
  "tripNights": 3
}
```

**Response:**
```json
{
  "totalCost": 512340,
  "segments": [
    {
      "from": "ICN",
      "to": "KIX",
      "price": 82000,
      "provider": "Amadeus",
      "date": "2025-01-01"
    }
  ],
  "routePattern": "ICN → KIX → CTS → FUK → ICN",
  "cheaperThanDirect": true
}
```

## 프로젝트 구조

```
/app
  /config          - 설정 관리
  /providers       - 외부 API 프로바이더
  /services        - 비즈니스 로직
  /controllers     - API 엔드포인트
  /utils           - 유틸리티 함수
  /models          - 데이터 모델
```

