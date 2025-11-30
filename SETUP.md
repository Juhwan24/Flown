# 실행 가이드

## 1. 의존성 설치

모든 의존성이 이미 설치되어 있습니다:
```bash
pip install -r requirements.txt
```

## 2. 환경 변수 설정 (선택사항)

`.env` 파일을 생성하여 API 키를 설정할 수 있습니다. 없어도 모의 데이터로 동작합니다.

```bash
# .env 파일 생성 (선택사항)
cp env.example .env
```

`.env` 파일 내용:
```
AMADEUS_API_KEY=your_amadeus_api_key
AMADEUS_API_SECRET=your_amadeus_api_secret
AIRLABS_API_KEY=your_airlabs_api_key
```

**참고**: `.env` 파일이 없어도 기본값(mock_key_for_testing)으로 동작합니다.

## 3. 서버 실행

```bash
python main.py
```

또는 uvicorn으로 직접 실행:
```bash
uvicorn main:app --reload
```

서버가 시작되면:
- API 문서: http://localhost:8000/docs
- 헬스 체크: http://localhost:8000/api/health
- 루트: http://localhost:8000/

## 4. API 테스트

### 검색 요청 예시:
```bash
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{
    "departure": "ICN",
    "destination": "CTS",
    "start_date": "2025-01-01",
    "end_date": "2025-01-10",
    "trip_nights": 3
  }'
```

## 5. 문제 해결

### ModuleNotFoundError: No module named 'app'
- `main.py`가 프로젝트 루트에서 실행되는지 확인
- `backend/` 디렉토리가 존재하는지 확인

### Redis 연결 오류
- Redis가 없어도 동작합니다 (캐싱만 비활성화됨)
- Redis를 사용하려면: `redis-server` 실행

### API 키 오류
- `.env` 파일이 없어도 기본값으로 동작합니다
- 실제 API를 사용하려면 `.env` 파일에 실제 키를 입력하세요

