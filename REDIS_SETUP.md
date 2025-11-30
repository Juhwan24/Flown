# Redis 설정 가이드

## Redis란?

**Redis**는 **인메모리 데이터베이스**로, 이 프로젝트에서는 **캐싱** 목적으로 사용됩니다.

### 왜 Redis를 사용하나요?

1. **API 호출 비용 절감**: 같은 검색 결과를 캐싱하여 중복 API 호출 방지
2. **응답 속도 향상**: 캐시된 데이터는 즉시 반환 (수 밀리초)
3. **API Rate Limit 방지**: 외부 API 호출 횟수 제한 회피

### Redis 없이도 동작하나요?

**네, Redis 없이도 정상 동작합니다!** 
- Redis가 없으면 캐싱 없이 매번 API를 직접 호출합니다
- 성능은 느려지지만 기능은 정상 작동합니다

---

## Redis 설치 방법

### Windows

#### 방법 1: WSL2 사용 (권장)

```bash
# WSL2에서 Ubuntu 실행
wsl

# Redis 설치
sudo apt update
sudo apt install redis-server

# Redis 시작
sudo service redis-server start

# Redis 상태 확인
redis-cli ping
# 응답: PONG
```

#### 방법 2: Docker 사용

```bash
# Docker Desktop 설치 후
docker run -d -p 6379:6379 --name redis redis:latest

# Redis 상태 확인
docker exec -it redis redis-cli ping
```

#### 방법 3: Memurai (Windows 네이티브)

1. [Memurai 다운로드](https://www.memurai.com/get-memurai)
2. 설치 후 자동으로 서비스로 실행됨
3. 기본 포트: 6379

### macOS

```bash
# Homebrew로 설치
brew install redis

# Redis 시작
brew services start redis

# 또는 수동 시작
redis-server

# Redis 상태 확인
redis-cli ping
```

### Linux

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server

# CentOS/RHEL
sudo yum install redis
sudo systemctl start redis
sudo systemctl enable redis

# Redis 상태 확인
redis-cli ping
```

---

## 프로젝트 설정

### 1. `.env` 파일 설정

프로젝트 루트에 `.env` 파일을 생성하고 다음 내용을 추가하세요:

```env
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
```

### 2. 기본 설정 설명

| 설정 | 설명 | 기본값 |
|------|------|--------|
| `REDIS_HOST` | Redis 서버 주소 | `localhost` |
| `REDIS_PORT` | Redis 서버 포트 | `6379` |
| `REDIS_DB` | Redis 데이터베이스 번호 (0-15) | `0` |
| `REDIS_PASSWORD` | Redis 비밀번호 (없으면 빈 문자열) | (없음) |

### 3. 원격 Redis 서버 사용

클라우드 Redis 서비스 (AWS ElastiCache, Redis Cloud 등)를 사용하는 경우:

```env
REDIS_HOST=your-redis-host.redis.cache.amazonaws.com
REDIS_PORT=6379
REDIS_PASSWORD=your-password-here
```

---

## Redis 동작 확인

### 1. 서버 실행 확인

```bash
# Redis CLI로 연결
redis-cli

# 또는 원격 서버인 경우
redis-cli -h localhost -p 6379

# 연결 테스트
ping
# 응답: PONG
```

### 2. 애플리케이션 로그 확인

서버 시작 시 다음 메시지가 보이면 성공:

```
INFO - Redis 연결 성공: localhost:6379
```

Redis가 없으면:

```
WARNING - Redis 연결 실패: ... 캐싱이 비활성화됩니다.
```

### 3. 캐시 데이터 확인

```bash
# Redis CLI에서
redis-cli

# 모든 키 조회
KEYS *

# 특정 키 조회 (예: amadeus 관련)
KEYS amadeus:*

# 키 값 확인
GET "amadeus:from_airport:ICN:to_airport:KIX:date:2025-01-01"

# 모든 캐시 삭제 (주의!)
FLUSHDB
```

---

## 캐싱 전략

### TTL (Time To Live)

프로젝트에서 사용하는 캐시 만료 시간:

| 데이터 타입 | TTL | 이유 |
|------------|-----|------|
| 국제선 (Amadeus) | 3시간 (10800초) | 항공권 가격 변동이 잦음 |
| 국내선 (AirLabs) | 6시간 (21600초) | 가격 변동이 상대적으로 적음 |

### 캐시 키 형식

```
{provider}:{param1}:{value1}:{param2}:{value2}:...

예시:
- amadeus:from_airport:ICN:to_airport:KIX:date:2025-01-01
- airlabs:from_airport:NRT:to_airport:CTS:date:2025-01-02
```

---

## 문제 해결

### Redis 연결 실패

**증상**: `Redis 연결 실패: Connection refused`

**해결 방법**:
1. Redis 서버가 실행 중인지 확인
   ```bash
   redis-cli ping
   ```
2. 포트가 올바른지 확인 (기본: 6379)
3. 방화벽 설정 확인

### Redis 비밀번호 오류

**증상**: `Redis 연결 실패: NOAUTH Authentication required`

**해결 방법**:
1. `.env` 파일에 `REDIS_PASSWORD` 설정
2. Redis 서버의 비밀번호와 일치하는지 확인

### 메모리 부족

**증상**: Redis가 데이터를 저장하지 못함

**해결 방법**:
1. Redis 메모리 사용량 확인
   ```bash
   redis-cli INFO memory
   ```
2. 오래된 캐시 삭제
   ```bash
   redis-cli FLUSHDB
   ```
3. Redis 메모리 제한 설정 (`redis.conf`)

---

## 성능 최적화

### Redis 없이 사용 시

- 모든 API 호출이 실시간으로 실행됨
- 응답 시간: 2-5초 (API 호출 시간에 따라)
- API 호출 비용 증가

### Redis 사용 시

- 첫 검색: 2-5초 (API 호출)
- 이후 동일 검색: 10-50ms (캐시에서 조회)
- API 호출 비용 대폭 감소

---

## 추가 리소스

- [Redis 공식 문서](https://redis.io/docs/)
- [Python redis 라이브러리](https://redis-py.readthedocs.io/)
- [Redis 명령어 참조](https://redis.io/commands/)

