/**
 * 항공편 세그먼트 데이터 모델
 * 각 구간(출발지 → 도착지)의 정보를 담습니다.
 * 
 * 사용 예시:
 * - segment.from_airport: "ICN" (출발 공항 코드)
 * - segment.to_airport: "KIX" (도착 공항 코드)
 * - segment.date: "2025-01-15" (출발 날짜, YYYY-MM-DD 형식)
 * - segment.price: 82000 (해당 구간 가격, 원화 기준)
 * - segment.provider: "Amadeus" 또는 "Peach" (항공사/프로바이더 이름)
 * - segment.flight_number: "KE123" (항공편 번호, 선택사항)
 * - segment.departure_time: "09:00" (출발 시간, HH:MM 형식, 선택사항)
 * - segment.arrival_time: "11:30" (도착 시간, HH:MM 형식, 선택사항)
 */
export interface FlightSegment {
  /** 출발 공항 코드 (3자리 IATA 코드, 예: "ICN", "KIX", "CTS") */
  from_airport: string;
  
  /** 도착 공항 코드 (3자리 IATA 코드, 예: "ICN", "KIX", "CTS") */
  to_airport: string;
  
  /** 출발 날짜 (ISO 8601 형식 문자열: "YYYY-MM-DD", 예: "2025-01-15") */
  date: string;
  
  /** 해당 구간의 가격 (원화 기준 정수, 예: 82000) */
  price: number;
  
  /** 항공사/프로바이더 이름 (예: "Amadeus", "Peach") */
  provider: string;
  
  /** 항공편 번호 (선택사항, 예: "KE123", "MM123") */
  flight_number?: string;
  
  /** 출발 시간 (선택사항, HH:MM 형식, 예: "09:00") */
  departure_time?: string;
  
  /** 도착 시간 (선택사항, HH:MM 형식, 예: "11:30") */
  arrival_time?: string;
}

/**
 * 검색 요청 모델
 * API에 전송하는 검색 파라미터입니다.
 * 
 * 사용 예시:
 * const request: SearchRequest = {
 *   departure: "ICN",
 *   destination: "CTS",
 *   start_date: "2025-01-15",
 *   end_date: "2025-01-20",
 *   trip_nights: 3
 * };
 */
export interface SearchRequest {
  /** 출발 공항 코드 (3자리 IATA 코드, 필수) */
  departure: string;
  
  /** 최종 목적지 공항 코드 (3자리 IATA 코드, 필수) */
  destination: string;
  
  /** 출발 가능한 시작 날짜 (ISO 8601 형식: "YYYY-MM-DD", 필수) */
  start_date: string;
  
  /** 출발 가능한 종료 날짜 (ISO 8601 형식: "YYYY-MM-DD", 필수) */
  end_date: string;
  
  /** 체류 일수 (선택사항, 기본값: 3일) */
  trip_nights?: number;
}

/**
 * 검색 응답 모델
 * API로부터 받아오는 검색 결과 데이터입니다.
 * 
 * 사용 예시:
 * - result.total_cost: 164000 (전체 여정 총 비용)
 * - result.segments: [FlightSegment, ...] (각 구간별 상세 정보 배열)
 * - result.route_pattern: "ICN → KIX → CTS → KIX → ICN" (경로 패턴 문자열)
 * - result.cheaper_than_direct: true (직항보다 저렴한지 여부)
 * - result.direct_cost: 200000 (직항 가격, 비교용)
 * 
 * UI 표시 예시:
 * - 총 비용: result.total_cost를 formatPrice()로 포맷팅
 * - 경로: result.route_pattern을 그대로 표시
 * - 기간: result.segments[0].date와 result.segments[마지막].date 차이 계산
 * - 각 세그먼트: result.segments 배열을 map()으로 순회하여 표시
 * - 절약 금액: result.direct_cost - result.total_cost (cheaper_than_direct가 true일 때)
 */
export interface SearchResponse {
  /** 전체 여정의 총 비용 (원화 기준 정수, 모든 segments의 price 합계) */
  total_cost: number;
  
  /** 항공편 세그먼트 목록 (각 구간별 상세 정보)
   * 
   * 배열 순서: 출발 → 경유지1 → 경유지2 → 목적지 → 귀국
   * 예: [
   *   { from_airport: "ICN", to_airport: "KIX", ... },  // 출발
   *   { from_airport: "KIX", to_airport: "CTS", ... },  // 경유
   *   { from_airport: "CTS", to_airport: "KIX", ... },  // 귀국 경유
   *   { from_airport: "KIX", to_airport: "ICN", ... }  // 귀국
   * ]
   * 
   * 활용 방법:
   * - 첫 세그먼트: result.segments[0] → 출발 정보
   * - 마지막 세그먼트: result.segments[result.segments.length - 1] → 귀국 정보
   * - 모든 세그먼트: result.segments.map() → 전체 경로 상세 표시
   * - 날짜 계산: result.segments[0].date와 result.segments[마지막].date로 기간 계산
   */
  segments: FlightSegment[];
  
  /** 경로 패턴 문자열 (공항 코드를 " → "로 연결한 형태)
   * 
   * 예시:
   * - "ICN → KIX → CTS → KIX → ICN" (경유 1곳)
   * - "ICN → NRT → CTS → FUK → ICN" (경유 2곳)
   * 
   * 활용 방법:
   * - UI에 그대로 표시 가능
   * - Plane 아이콘과 함께 표시하면 시각적으로 명확
   */
  route_pattern: string;
  
  /** 직항보다 저렴한지 여부 (boolean)
   * 
   * true: 경유 일정이 직항보다 저렴함
   * false: 경유 일정이 직항보다 비쌈 (또는 직항 가격 정보 없음)
   * 
   * 활용 방법:
   * - result.cheaper_than_direct && result.direct_cost가 있을 때만 절약 금액 표시
   * - 조건부 렌더링: {result.cheaper_than_direct && <절약금액표시 />}
   */
  cheaper_than_direct: boolean;
  
  /** 직항 가격 (원화 기준 정수, 선택사항)
   * 
   * 활용 방법:
   * - 절약 금액 계산: result.direct_cost - result.total_cost
   * - 비교 표시: "직항 대비 {절약금액}원 절약"
   * - result.cheaper_than_direct가 true일 때만 표시 권장
   * 
   * 주의:
   * - undefined일 수 있으므로 옵셔널 체이닝 사용: result.direct_cost?.toLocaleString()
   */
  direct_cost?: number;
}

