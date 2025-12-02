import { useState } from 'react';
import { Calendar, MapPin, Search, Loader2 } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { AirportSelectPopover } from './AirportSelectPopover';
import { Airport } from '../data/airports';
import { searchFlights } from '../services/flightApi';
import { SearchResponse } from '../types/flight';

interface FlightSearchCardProps {
  onSearchResult?: (result: SearchResponse, params: {
    departure: string;
    destination: string;
    startDate: string;
    endDate: string;
  }) => void;
}

export function FlightSearchCard({ onSearchResult }: FlightSearchCardProps) {
  const [tripType, setTripType] = useState<'roundtrip' | 'oneway'>('roundtrip');
  const [fromAirport, setFromAirport] = useState<Airport | null>(null);
  const [toAirport, setToAirport] = useState<Airport | null>(null);
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [tripNights, setTripNights] = useState<string>('');
  const [fromPopoverOpen, setFromPopoverOpen] = useState(false);
  const [toPopoverOpen, setToPopoverOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 여행 기간 계산 및 검증
  const calculateMaxNights = (): number => {
    if (!startDate || !endDate) return 0;
    const start = new Date(startDate);
    const end = new Date(endDate);
    const diffTime = end.getTime() - start.getTime();
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    return Math.max(0, diffDays);
  };

  const handleStartDateChange = (value: string) => {
    setStartDate(value);
    // 시작일이 변경되면 여행 기간 재검증
    if (value && endDate && tripNights) {
      const maxNights = calculateMaxNights();
      const nights = parseInt(tripNights);
      if (nights > maxNights) {
        setTripNights(maxNights.toString());
      }
    }
  };

  const handleEndDateChange = (value: string) => {
    setEndDate(value);
    // 종료일이 변경되면 여행 기간 재검증
    if (startDate && value && tripNights) {
      const maxNights = calculateMaxNights();
      const nights = parseInt(tripNights);
      if (nights > maxNights) {
        setTripNights(maxNights.toString());
      }
    }
  };

  const handleTripNightsChange = (value: string) => {
    const nights = parseInt(value);
    if (isNaN(nights) || nights < 0) {
      setTripNights('');
      return;
    }
    
    const maxNights = calculateMaxNights();
    if (maxNights > 0 && nights > maxNights) {
      setError(`여행 기간은 최대 ${maxNights}박까지 가능합니다.`);
      setTripNights(maxNights.toString());
      return;
    }
    
    setError(null);
    setTripNights(value);
  };

  const formatAirportDisplay = (airport: Airport | null) => {
    if (!airport) return '';
    return `${airport.city} (${airport.code})`;
  };

  const handleSearch = async () => {
    if (!fromAirport || !toAirport || !startDate || !endDate) {
      setError('모든 필드를 입력해주세요.');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const result = await searchFlights({
        departure: fromAirport.code,
        destination: toAirport.code,
        start_date: startDate,
        end_date: endDate,
        trip_nights: tripNights ? parseInt(tripNights) : undefined,
      });

      if (onSearchResult) {
        onSearchResult(result, {
          departure: fromAirport.code,
          destination: toAirport.code,
          startDate,
          endDate,
        });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '검색 중 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-4xl w-full">

      {/* Search inputs */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        {/* From */}
        <div className="relative">
          <label className="block text-sm text-gray-600 mb-2">출국장소</label>
          <AirportSelectPopover
            open={fromPopoverOpen}
            onOpenChange={setFromPopoverOpen}
            onSelect={(airport) => {
              setFromAirport(airport);
              setFromPopoverOpen(false);
            }}
          >
            <div className="relative">
              <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 z-10 pointer-events-none" />
              <Input
                type="text"
                placeholder="서울 (ICN)"
                value={formatAirportDisplay(fromAirport)}
                readOnly
                className="pl-10 h-14 border-gray-300 cursor-pointer hover:border-blue-400 transition-colors"
              />
            </div>
          </AirportSelectPopover>
        </div>

        {/* To */}
        <div className="relative">
          <label className="block text-sm text-gray-600 mb-2">입국장소</label>
          <AirportSelectPopover
            open={toPopoverOpen}
            onOpenChange={setToPopoverOpen}
            onSelect={(airport) => {
              setToAirport(airport);
              setToPopoverOpen(false);
            }}
          >
            <div className="relative">
              <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 z-10 pointer-events-none" />
              <Input
                type="text"
                placeholder="도쿄 (NRT)"
                value={formatAirportDisplay(toAirport)}
                readOnly
                className="pl-10 h-14 border-gray-300 cursor-pointer hover:border-blue-400 transition-colors"
              />
            </div>
          </AirportSelectPopover>
        </div>

      </div>

      {/* Date and trip nights row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        {/* Start date */}
        <div className="relative">
          <label className="block text-sm text-gray-600 mb-2">후보기간</label>
          <div className="relative">
            <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <Input
              type="date"
              value={startDate}
              onChange={(e) => handleStartDateChange(e.target.value)}
              className="pl-10 h-14 border-gray-300"
            />
          </div>
        </div>

        {/* End date */}
        <div className="relative">
          <label className="block text-sm text-white mb-2">.</label>
          <div className="relative">
            <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <Input
              type="date"
              value={endDate}
              onChange={(e) => handleEndDateChange(e.target.value)}
              min={startDate || undefined}
              className="pl-10 h-14 border-gray-300"
            />
          </div>
        </div>

        {/* Trip nights */}
        <div className="relative">
          <label className="block text-sm text-gray-600 mb-2">여행 일자</label>
          <div className="relative">
            <Input
              type="number"
              placeholder="박"
              value={tripNights}
              onChange={(e) => handleTripNightsChange(e.target.value)}
              min="0"
              max={calculateMaxNights() || undefined}
              className="h-14 border-gray-300 pr-12"
            />
            <span className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 text-sm">
              
            </span>
          </div>
        </div>
      </div>

      {/* Error message */}
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
          {error}
        </div>
      )}

      {/* Search button */}
      <Button 
        className="w-full h-14 bg-blue-600 hover:bg-blue-700 text-white mt-4 disabled:opacity-50 disabled:cursor-not-allowed"
        onClick={handleSearch}
        disabled={isLoading || !fromAirport || !toAirport || !startDate || !endDate}
      >
        {isLoading ? (
          <>
            <Loader2 className="w-5 h-5 mr-2 animate-spin" />
            검색 중...
          </>
        ) : (
          <>
            <Search className="w-5 h-5 mr-2" />
            항공권 검색
          </>
        )}
      </Button>
    </div>
  );
}
