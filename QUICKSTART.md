# 빠른 시작 가이드

## ✅ 의존성 설치 완료

모든 Python 패키지가 이미 설치되어 있습니다:
- FastAPI 0.104.1
- Uvicorn 0.24.0
- Pydantic 2.5.0
- Redis 5.0.1
- httpx 0.25.2
- 기타 모든 의존성

## 🚀 서버 실행

### 방법 1: Python 직접 실행
```bash
python main.py
```

### 방법 2: Uvicorn 직접 실행
```bash
uvicorn main:app --reload
```

### 방법 3: 배치 파일 사용 (Windows)
```bash
run.bat
```

## 📝 환경 변수 (선택사항)

`.env` 파일이 없어도 기본값으로 동작합니다. 실제 API를 사용하려면:

1. `env.example`을 `.env`로 복사
2. 실제 API 키 입력

## 🔍 확인 사항

서버가 시작되면:
- API 문서: http://localhost:8000/docs
- 헬스 체크: http://localhost:8000/api/health

## ⚠️ 문제 해결

### Pydantic 오류 발생 시
- Python 버전 확인 (3.8 이상 필요)
- 가상환경 사용 권장

### Redis 연결 오류
- Redis 없이도 동작합니다 (캐싱만 비활성화)
- Redis 사용 시: `redis-server` 실행

## 📚 자세한 내용

`SETUP.md` 파일을 참고하세요.

