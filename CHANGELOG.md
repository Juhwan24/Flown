# 변경 사항 (Changelog)

## 주요 수정 사항 (2025-01-XX)

### 🔴 치명적 버그 수정

#### 1. FlightSegment 객체 뮤테이션 방지
**문제**: `PriceAggregator.build_itinerary_from_template`에서 그래프에 저장된 `FlightSegment` 인스턴스를 직접 수정하여 공유 객체 오염 위험

**수정**:
- `segment.model_dump()`로 복사본 생성 후 날짜 수정
- 각 일정에 독립적인 세그먼트 인스턴스 사용

**파일**: `backend/app/services/price_aggregator.py`

#### 2. 동시성 제한 추가
**문제**: `_populate_graph`에서 모든 세그먼트를 무제한 병렬 호출하여 Rate limit 및 메모리 문제 발생 가능

**수정**:
- `asyncio.Semaphore(20)`로 동시 최대 20개 요청 제한
- `limited_fetch` 래퍼 함수로 모든 API 호출 보호
- 성공/실패 카운트 로깅 추가

**파일**: `backend/app/services/search_engine.py`

#### 3. 캐시 직렬화/역직렬화 안전화
**문제**: 캐시에 저장된 날짜가 문자열로 변환되어 역직렬화 시 타입 오류 가능

**수정**:
- 저장 시: `date` 객체를 `format_date_for_api()`로 문자열 변환
- 로드 시: 문자열을 `parse_api_date()`로 `date` 객체로 파싱
- 예외 처리 추가 (캐시 오류 시 API 호출로 폴백)

**파일**: 
- `backend/app/services/search_engine.py`
- `backend/app/utils/date_utils.py` (새 함수 추가)

### 🟡 논리/알고리즘 개선

#### 4. 날짜 논리 명확화
**수정**:
- `final_destination` 변수로 최종 목적지 명시적 표시
- `allow_same_day_transfer` 파라미터 추가 (당일 환승 허용 여부)
- `DateUtils.compute_segment_dates_for_template()` 헬퍼 함수 추가

**파일**: 
- `backend/app/services/price_aggregator.py`
- `backend/app/utils/date_utils.py`

#### 5. RouteTemplateEngine.expand_template 구현
**수정**:
- 그래프에 실제 세그먼트가 존재하는지 확인
- 유효하지 않은 템플릿은 빈 리스트 반환하여 스킵
- `available_segments` 딕셔너리 지원

**파일**: `backend/app/services/route_templates.py`

#### 6. _is_international_route 기본값 수정
**문제**: 알 수 없는 조합을 `True`(국제선)로 처리하여 오류 가능

**수정**: 알 수 없는 조합은 `False`로 처리 (안전한 기본값)

**파일**: `backend/app/services/search_engine.py`

### 🟢 안정성 개선

#### 7. 재시도 로직 추가 (Exponential Backoff)
**추가**:
- `MAX_RETRIES = 3`: 최대 3회 재시도
- `RETRY_DELAY_BASE = 1.0`: 지수 백오프 (1초, 2초, 4초)
- 모든 Provider API 호출에 적용

**파일**: 
- `backend/app/providers/amadeus.py`
- `backend/app/providers/airlabs.py`

#### 8. HTTP 타임아웃 및 연결 풀 설정
**추가**:
- `HTTP_TIMEOUT = 10.0`: 10초 타임아웃
- `httpx.AsyncClient` 재사용 (연결 풀 최적화)
- `max_keepalive_connections=20`, `max_connections=100`

**파일**: 
- `backend/app/providers/amadeus.py`
- `backend/app/providers/airlabs.py`

#### 9. 리소스 정리
**추가**:
- Provider에 `close()` 메서드 추가
- 애플리케이션 shutdown 시 HTTP 클라이언트 정리

**파일**: 
- `backend/app/providers/amadeus.py`
- `backend/app/providers/airlabs.py`
- `main.py`

#### 10. 로깅 강화
**추가**:
- 템플릿별 시도 로그 (성공/실패)
- 그래프 채우기 통계 (성공/실패 카운트)
- 일정 생성 성공 로그

**파일**: `backend/app/services/search_engine.py`

## 향후 개선 사항

1. **휴리스틱 기반 날짜 선택**: 주말/평일, 가격 변동성 고려
2. **부분 결합 전략**: 국제선 먼저 선택 후 국내선 조합
3. **동적 후보 확장**: 실패 시 후보 공항 추가
4. **비용 민감도 필터**: 사용자 설정 (직항 대비 X% 이상 저렴할 때만)

## 테스트 권장 사항

1. **단위 테스트**:
   - `PriceAggregator.build_itinerary_from_template`: 세그먼트 복사 확인
   - `RouteTemplateEngine.expand_template`: 유효성 검사 확인
   - 캐시 직렬화/역직렬화 테스트

2. **통합 테스트**:
   - 동시성 제한 동작 확인
   - 재시도 로직 동작 확인
   - Rate limit 시뮬레이션

3. **성능 테스트**:
   - 동시 요청 처리 능력
   - 메모리 사용량 모니터링
   - API 호출 수 최적화 확인

