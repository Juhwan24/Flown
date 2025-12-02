/**
 * FlightResults 컴포넌트
 * 
 * API 응답 데이터(SearchResponse)를 활용하여 항공편 검색 결과를 표시합니다.
 * 
 * 사용 가능한 데이터 구조:
 * 
 * 1. result.total_cost (number)
 *    - 전체 여정의 총 비용 (원화)
 *    - 사용: formatPrice(result.total_cost)로 포맷팅하여 표시
 * 
 * 2. result.segments (FlightSegment[])
 *    - 각 구간별 상세 정보 배열
 *    - result.segments[0]: 첫 번째 세그먼트 (출발)
 *    - result.segments[result.segments.length - 1]: 마지막 세그먼트 (귀국)
 *    - 각 segment의 사용 가능한 필드:
 *      * segment.from_airport: 출발 공항 코드 (예: "ICN")
 *      * segment.to_airport: 도착 공항 코드 (예: "KIX")
 *      * segment.date: 출발 날짜 (예: "2025-01-15")
 *      * segment.price: 구간 가격 (예: 82000)
 *      * segment.provider: 프로바이더 이름 (예: "Amadeus", "Peach")
 *      * segment.flight_number: 항공편 번호 (선택사항, 예: "KE123")
 *      * segment.departure_time: 출발 시간 (선택사항, 예: "09:00")
 *      * segment.arrival_time: 도착 시간 (선택사항, 예: "11:30")
 * 
 * 3. result.route_pattern (string)
 *    - 경로 패턴 문자열 (예: "ICN → KIX → CTS → KIX → ICN")
 *    - 사용: 그대로 표시 가능
 * 
 * 4. result.cheaper_than_direct (boolean)
 *    - 직항보다 저렴한지 여부
 *    - 사용: 조건부 렌더링 {result.cheaper_than_direct && <절약금액 />}
 * 
 * 5. result.direct_cost (number | undefined)
 *    - 직항 가격 (선택사항)
 *    - 사용: 절약 금액 계산 = result.direct_cost - result.total_cost
 *    - 주의: undefined 체크 필요
 * 
 * 계산 예시:
 * - 기간 계산: 첫 세그먼트 날짜와 마지막 세그먼트 날짜 차이
 *   const firstDate = new Date(result.segments[0].date);
 *   const lastDate = new Date(result.segments[result.segments.length - 1].date);
 *   const daysDiff = Math.ceil((lastDate - firstDate) / (1000 * 60 * 60 * 24));
 * 
 * - 출발일: result.segments[0].date
 * - 귀국일: result.segments[result.segments.length - 1].date
 * 
 * - 절약 금액: result.direct_cost && result.cheaper_than_direct 
 *   ? result.direct_cost - result.total_cost 
 *   : null
 */
import { ArrowLeft, Plane, Calendar } from 'lucide-react';
import { Button } from './ui/button';
import { SearchResponse } from '../types/flight';
import { ImageWithFallback } from './figma/ImageWithFallback';

interface FlightResultsProps {
  /** API로부터 받아온 검색 결과 데이터 (모든 필드 활용 가능) */
  result: SearchResponse;
  
  /** 뒤로가기 버튼 클릭 핸들러 */
  onBack: () => void;
  
  /** 검색 파라미터 (현재는 사용하지 않지만 참고용으로 유지) */
  searchParams: {
    departure: string;
    destination: string;
    startDate: string;
    endDate: string;
  };
}

export function FlightResults({ result, onBack, searchParams }: FlightResultsProps) {
  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('ko-KR').format(price);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  return (
    <div className="min-h-screen relative">
      {/* Background image */}
      <div className="absolute inset-0 z-0">
        <ImageWithFallback
          src="https://images.unsplash.com/photo-1715526239919-af51497b77e9?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxhaXJwbGFuZSUyMHNreSUyMHRyYXZlbHxlbnwxfHx8fDE3NjAyNDk5MjV8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
          alt="Airplane background"
          className="w-full h-full object-cover"
        />
        {/* Dark overlay */}
        <div className="absolute inset-0 bg-gradient-to-b from-black/50 via-black/40 to-black/60" />
      </div>

      {/* Content */}
      <div className="relative z-10">
        {/* Header */}
        <header className="px-6 py-6">
          <nav className="max-w-7xl mx-auto flex items-center justify-between">
            <Button
              onClick={onBack}
              variant="ghost"
              className="text-white hover:text-blue-200 hover:bg-white/10"
            >
              <ArrowLeft className="w-5 h-5 mr-2" />
              다시 검색
            </Button>
          </nav>
        </header>

        {/* Results section */}
        <main className="px-6 py-12">
          <div className="max-w-4xl mx-auto">
            {/* Flight result card */}
            <div className="bg-white rounded-2xl shadow-2xl p-8">
              {/* 경로 */}
              <div className="mb-6 pb-6 border-b border-gray-200">
                <h4 className="text-sm font-semibold text-gray-600 mb-3">경로</h4>
                <div className="flex items-center gap-2 text-lg font-medium text-gray-900">
                  <Plane className="w-5 h-5 text-blue-600" />
                  <span>{result.route_pattern}</span>
                </div>
              </div>

              {/* 기간 */}
              {result.segments.length > 0 && (() => {
                const firstDate = new Date(result.segments[0].date);
                const lastDate = new Date(result.segments[result.segments.length - 1].date);
                const daysDiff = Math.ceil((lastDate.getTime() - firstDate.getTime()) / (1000 * 60 * 60 * 24));
                return (
                  <div className="mb-6 -pb6 border-b border-gray-200">
                    <h4 className="text-sm font-semibold text-gray-600 mb-3">기간</h4>
                    <p className="text-lg font-medium text-gray-900">
                      {daysDiff}박 {daysDiff + 1}일
                    </p>
                  </div>
                );
              })()}

              {/* 날짜 */}
              {result.segments.length > 0 && (
                <div className="mb-6 pb-6 border-b border-gray-200">
                  <h4 className="text-sm font-semibold text-gray-600 mb-3">날짜</h4>
                  <div className="flex items-center gap-4 text-lg font-medium text-gray-900">
                    <div className="flex items-center gap-2">
                      <Calendar className="w-5 h-5 text-blue-600" />
                      <span>출발: {formatDate(result.segments[0].date)}</span>
                    </div>
                    <span className="text-gray-400">→</span>
                    <div className="flex items-center gap-2">
                      <Calendar className="w-5 h-5 text-blue-600" />
                      <span>귀국: {formatDate(result.segments[result.segments.length - 1].date)}</span>
                    </div>
                  </div>
                </div>
              )}

              {/* 가격 */}
              <div className="mb-6 pb-6 border-b border-gray-200">
                <h4 className="text-sm font-semibold text-gray-600 mb-3">가격</h4>
                <div className="flex items-center justify-between">
                  <p className="text-3xl font-bold text-blue-600">
                    {formatPrice(result.total_cost)}원
                  </p>
                  {result.cheaper_than_direct && result.direct_cost && (
                    <div className="text-right">
                      <p className="text-sm text-gray-600">직항 대비</p>
                      <p className="text-lg font-semibold text-green-600">
                        {formatPrice(result.direct_cost - result.total_cost)}원 절약
                      </p>
                    </div>
                  )}
                </div>
              </div>

              {/* 항공편 상세 정보 - 모든 세그먼트 표시 */}
              {result.segments.length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-600 mb-4">항공편 상세</h4>
                  <div className="space-y-4">
                    {result.segments.map((segment, index) => (
                      <div
                        key={index}
                        className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors"
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-4 flex-1">
                            <div className="flex-shrink-0">
                              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                                <Plane className="w-6 h-6 text-blue-600" />
                              </div>
                            </div>
                            <div className="flex-1">
                              {/* 출발지 → 도착지 */}
                              <div className="flex items-center gap-3 mb-2">
                                <span className="text-xl font-bold text-gray-900">
                                  {segment.from_airport}
                                </span>
                                <span className="text-gray-400">→</span>
                                <span className="text-xl font-bold text-gray-900">
                                  {segment.to_airport}
                                </span>
                              </div>
                              
                              {/* 날짜 및 시간 정보 */}
                              <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600">
                                <div className="flex items-center gap-1">
                                  <Calendar className="w-4 h-4" />
                                  <span>{formatDate(segment.date)}</span>
                                </div>
                                {segment.departure_time && (
                                  <div className="flex items-center gap-1">
                                    <span className="font-medium">출발:</span>
                                    <span>{segment.departure_time}</span>
                                  </div>
                                )}
                                {segment.arrival_time && (
                                  <div className="flex items-center gap-1">
                                    <span className="font-medium">도착:</span>
                                    <span>{segment.arrival_time}</span>
                                  </div>
                                )}
                                {segment.flight_number && (
                                  <div className="flex items-center gap-1">
                                    <span className="font-medium">편명:</span>
                                    <span>{segment.flight_number}</span>
                                  </div>
                                )}
                              </div>
                              
                              
                            </div>
                          </div>
                          
                          {/* 가격 정보 */}
                          <div className="text-right">
                            <p className="text-sm text-gray-600 mb-1"></p>
                            <p className="text-xl font-bold text-blue-600">
                              {formatPrice(segment.price)}원
                            </p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

