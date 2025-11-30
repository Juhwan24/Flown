import { ArrowLeft, Plane, Calendar, DollarSign } from 'lucide-react';
import { Button } from './ui/button';
import { SearchResponse } from '../types/flight';
import { ImageWithFallback } from './figma/ImageWithFallback';

interface FlightResultsProps {
  result: SearchResponse;
  onBack: () => void;
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
            {/* Search summary */}
            <div className="bg-white rounded-2xl shadow-2xl p-6 mb-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">검색 결과</h2>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">출발지</span>
                  <p className="font-semibold text-gray-900">{searchParams.departure}</p>
                </div>
                <div>
                  <span className="text-gray-600">도착지</span>
                  <p className="font-semibold text-gray-900">{searchParams.destination}</p>
                </div>
                <div>
                  <span className="text-gray-600">시작일</span>
                  <p className="font-semibold text-gray-900">{formatDate(searchParams.startDate)}</p>
                </div>
                <div>
                  <span className="text-gray-600">종료일</span>
                  <p className="font-semibold text-gray-900">{formatDate(searchParams.endDate)}</p>
                </div>
              </div>
            </div>

            {/* Flight result card */}
            <div className="bg-white rounded-2xl shadow-2xl p-8">
              {/* Total cost */}
              <div className="flex items-center justify-between mb-6 pb-6 border-b border-gray-200">
                <div>
                  <h3 className="text-lg font-semibold text-gray-600 mb-1">총 비용</h3>
                  <p className="text-3xl font-bold text-blue-600">
                    {formatPrice(result.total_cost)}원
                  </p>
                </div>
                {result.cheaper_than_direct && result.direct_cost && (
                  <div className="text-right">
                    <p className="text-sm text-gray-600">직항 대비</p>
                    <p className="text-lg font-semibold text-green-600">
                      {formatPrice(result.direct_cost - result.total_cost)}원 절약
                    </p>
                  </div>
                )}
              </div>

              {/* Route pattern */}
              <div className="mb-6">
                <h4 className="text-sm font-semibold text-gray-600 mb-3">경로</h4>
                <div className="flex items-center gap-2 text-lg font-medium text-gray-900">
                  <Plane className="w-5 h-5 text-blue-600" />
                  <span>{result.route_pattern}</span>
                </div>
              </div>

              {/* Flight segments */}
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
                            <div className="flex items-center gap-3 mb-2">
                              <span className="text-xl font-bold text-gray-900">
                                {segment.from_airport}
                              </span>
                              <span className="text-gray-400">→</span>
                              <span className="text-xl font-bold text-gray-900">
                                {segment.to_airport}
                              </span>
                            </div>
                            <div className="flex items-center gap-4 text-sm text-gray-600">
                              <div className="flex items-center gap-1">
                                <Calendar className="w-4 h-4" />
                                <span>{formatDate(segment.date)}</span>
                              </div>
                              {segment.departure_time && (
                                <div className="flex items-center gap-1">
                                  <span>출발: {segment.departure_time}</span>
                                </div>
                              )}
                              {segment.arrival_time && (
                                <div className="flex items-center gap-1">
                                  <span>도착: {segment.arrival_time}</span>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-sm text-gray-600 mb-1">가격</p>
                          <p className="text-xl font-bold text-blue-600">
                            {formatPrice(segment.price)}원
                          </p>
                          <p className="text-xs text-gray-500 mt-1">{segment.provider}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

