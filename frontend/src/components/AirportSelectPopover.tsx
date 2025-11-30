import React, { useState, useMemo } from 'react';
import { Search, X, Plane } from 'lucide-react';
import { Popover, PopoverContent, PopoverTrigger } from './ui/popover';
import { Input } from './ui/input';
import { airportGroups, Airport } from '../data/airports';

interface AirportSelectPopoverProps {
  children: React.ReactNode;
  onSelect: (airport: Airport) => void;
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
}

export function AirportSelectPopover({
  children,
  onSelect,
  open,
  onOpenChange,
}: AirportSelectPopoverProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCountry, setSelectedCountry] = useState<string>('KR');

  // 검색 필터링
  const filteredGroups = useMemo(() => {
    if (!searchQuery.trim()) {
      return airportGroups;
    }

    const query = searchQuery.toLowerCase();
    return airportGroups
      .map(group => ({
        ...group,
        airports: group.airports.filter(
          airport =>
            airport.code.toLowerCase().includes(query) ||
            airport.name.toLowerCase().includes(query) ||
            airport.city.toLowerCase().includes(query) ||
            airport.country.toLowerCase().includes(query)
        ),
      }))
      .filter(group => group.airports.length > 0);
  }, [searchQuery]);

  // 선택된 국가의 공항 리스트
  const selectedCountryAirports = useMemo(() => {
    if (searchQuery.trim()) {
      // 검색 중일 때는 필터링된 결과에서 선택된 국가의 공항만 표시
      const group = filteredGroups.find(g => g.countryCode === selectedCountry);
      return group?.airports || [];
    }
    const group = airportGroups.find(g => g.countryCode === selectedCountry);
    return group?.airports || [];
  }, [selectedCountry, searchQuery, filteredGroups]);

  const handleSelect = (airport: Airport) => {
    onSelect(airport);
    setSearchQuery('');
    onOpenChange?.(false);
  };

  return (
    <Popover open={open} onOpenChange={onOpenChange}>
      <PopoverTrigger asChild>
        {children}
      </PopoverTrigger>
      <PopoverContent 
        className="!w-[650px] max-w-[90vw] p-0 bg-white rounded-2xl shadow-2xl border border-gray-300 overflow-hidden"
        align="start"
        sideOffset={8}
        style={{ 
          zIndex: 9999,
          width: '400px',
          maxWidth: '90vw',
          backgroundColor: '#ffffff',
          borderRadius: '1rem',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
        }}
      >
        {/* Header with search and close */}
        <div className="flex justify-end p-4 mb-4">
        </div>

        {/* Two column layout */}
        <div className="flex h-[300px] min-h-0">
          {/* Left panel: Country list */}
          <div 
            className="flex-shrink-0 border-r border-gray-200 overflow-y-auto bg-gray-50"
            style={{ 
              width: '180px',
              borderRightWidth: '1px',
              borderRightColor: '#e5e7eb',
              borderRightStyle: 'solid'
            }}
          >
            <div className="p-2">
              {airportGroups.map((group) => (
                <button
                  key={group.countryCode}
                  onClick={() => {
                    setSelectedCountry(group.countryCode);
                    setSearchQuery('');
                  }}
                  className={`w-full text-left px-4 py-3 transition-all mb-2 ${
                    selectedCountry === group.countryCode
                      ? 'bg-white font-semibold text-gray-900 shadow-sm'
                      : 'text-gray-600 hover:bg-white hover:text-gray-900'
                  }`}
                  type="button"
                >
                  <span className="block truncate">{group.country}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Right panel: Airport list */}
          <div 
            className="flex-1 min-w-0 overflow-y-auto"
            style={{ width: 'calc(650px - 180px)' }}
          >
            <div className="p-4">
              {selectedCountryAirports.length === 0 ? (
                <div className="text-center py-12 text-gray-500 text-sm">
                  검색 결과가 없습니다.
                </div>
              ) : (
                <div className="space-y-4">
                  {selectedCountryAirports.map((airport) => (
                    <button
                      key={airport.code}
                      onClick={() => handleSelect(airport)}
                      className="w-full text-left flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 active:bg-gray-100 transition-colors group mb-2"
                      type="button"
                    >
                      <div className="flex items-center gap-3 flex-1 min-w-0">
                        <div className="flex-shrink-0">
                          <span className="text-sm font-mono text-white whitespace-nowrap">
                            ㅁ
                          </span>
                        </div>
                        <div className="flex-shrink-0">
                          <Plane className="w-4 h-4 text-gray-400" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-0.5">
                            <span className="font-medium text-gray-900 text-sm whitespace-nowrap">
                              {airport.city}
                            </span>
                            <span className="text-xs font-mono text-gray-500 whitespace-nowrap">
                              {airport.code}
                            </span>
                          </div>

                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
}
