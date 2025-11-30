import { useState, useMemo } from 'react';
import { Search, X } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { Input } from './ui/input';
import { airportGroups, Airport } from '../data/airports';

interface AirportSelectModalProps {
  open: boolean;
  onClose: () => void;
  onSelect: (airport: Airport) => void;
  title: string;
}

export function AirportSelectModal({
  open,
  onClose,
  onSelect,
  title,
}: AirportSelectModalProps) {
  const [searchQuery, setSearchQuery] = useState('');

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

  const handleSelect = (airport: Airport) => {
    onSelect(airport);
    setSearchQuery('');
    onClose();
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-hidden flex flex-col p-0">
        <DialogHeader className="px-6 pt-6 pb-4 border-b">
          <DialogTitle className="text-2xl font-semibold">{title}</DialogTitle>
        </DialogHeader>

        {/* Search bar */}
        <div className="px-6 pt-4 pb-2">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <Input
              type="text"
              placeholder="공항명, 도시명, 코드로 검색..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 pr-10 h-12"
              autoFocus
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>

        {/* Airport list */}
        <div className="flex-1 overflow-y-auto px-6 pb-6">
          {filteredGroups.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              검색 결과가 없습니다.
            </div>
          ) : (
            <div className="space-y-6 pt-4">
              {filteredGroups.map((group) => (
                <div key={group.countryCode} className="space-y-3">
                  {/* Country header */}
                  <div className="flex items-center gap-2 text-lg font-semibold text-gray-800 sticky top-0 bg-white py-2 z-10">
                    <span className="text-2xl">{group.flag}</span>
                    <span>{group.country}</span>
                  </div>

                  {/* Airports */}
                  <div className="space-y-1 ml-2">
                    {group.airports.map((airport) => (
                      <button
                        key={airport.code}
                        onClick={() => handleSelect(airport)}
                        className="w-full text-left p-4 rounded-lg hover:bg-gray-50 transition-colors border border-transparent hover:border-gray-200 group"
                      >
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="font-semibold text-gray-900">
                                {airport.city}
                              </span>
                              <span className="text-sm font-mono text-blue-600 bg-blue-50 px-2 py-0.5 rounded">
                                {airport.code}
                              </span>
                            </div>
                            <div className="text-sm text-gray-600 truncate">
                              {airport.name}
                            </div>
                            <div className="text-xs text-gray-400 mt-1">
                              {airport.fullName}
                            </div>
                          </div>
                          <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                            <div className="w-2 h-2 rounded-full bg-blue-600"></div>
                          </div>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}

