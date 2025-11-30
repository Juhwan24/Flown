import { useState } from 'react';
import { Calendar, MapPin, Users, Search } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';

export function FlightSearchCard() {
  const [tripType, setTripType] = useState<'roundtrip' | 'oneway'>('roundtrip');

  return (
    <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-4xl w-full">
      {/* Trip type selector */}
      <div className="flex gap-4 mb-6">
        <button
          onClick={() => setTripType('roundtrip')}
          className={`px-4 py-2 rounded-lg transition-colors ${
            tripType === 'roundtrip'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          왕복
        </button>
        <button
          onClick={() => setTripType('oneway')}
          className={`px-4 py-2 rounded-lg transition-colors ${
            tripType === 'oneway'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          편도
        </button>
      </div>

      {/* Search inputs */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        {/* From */}
        <div className="relative">
          <label className="block text-sm text-gray-600 mb-2">출발지</label>
          <div className="relative">
            <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <Input
              type="text"
              placeholder="서울 (ICN)"
              className="pl-10 h-14 border-gray-300"
            />
          </div>
        </div>

        {/* To */}
        <div className="relative">
          <label className="block text-sm text-gray-600 mb-2">도착지</label>
          <div className="relative">
            <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <Input
              type="text"
              placeholder="도쿄 (NRT)"
              className="pl-10 h-14 border-gray-300"
            />
          </div>
        </div>

        {/* Departure date */}
        <div className="relative">
          <label className="block text-sm text-gray-600 mb-2">출발일</label>
          <div className="relative">
            <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <Input
              type="date"
              className="pl-10 h-14 border-gray-300"
            />
          </div>
        </div>

        {/* Return date */}
        {tripType === 'roundtrip' && (
          <div className="relative">
            <label className="block text-sm text-gray-600 mb-2">도착일</label>
            <div className="relative">
              <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <Input
                type="date"
                className="pl-10 h-14 border-gray-300"
              />
            </div>
          </div>
        )}

        {/* Passengers */}
        <div className="relative">
          <label className="block text-sm text-gray-600 mb-2">승객</label>
          <div className="relative">
            <Users className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <Input
              type="number"
              placeholder="1"
              min="1"
              defaultValue="1"
              className="pl-10 h-14 border-gray-300"
            />
          </div>
        </div>
      </div>

      {/* Search button */}
      <Button className="w-full h-14 bg-blue-600 hover:bg-blue-700 text-white mt-4">
        <Search className="w-5 h-5 mr-2" />
        항공권 검색
      </Button>
    </div>
  );
}
