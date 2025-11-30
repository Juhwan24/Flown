import { useState } from 'react';
import { FloatLogo } from './components/FloatLogo';
import { FlightSearchCard } from './components/FlightSearchCard';
import { FlightResults } from './components/FlightResults';
import { ImageWithFallback } from './components/figma/ImageWithFallback';
import { SearchResponse } from './types/flight';

export default function App() {
  const [searchResult, setSearchResult] = useState<SearchResponse | null>(null);
  const [searchParams, setSearchParams] = useState<{
    departure: string;
    destination: string;
    startDate: string;
    endDate: string;
  } | null>(null);

  const handleSearchResult = (result: SearchResponse, params: {
    departure: string;
    destination: string;
    startDate: string;
    endDate: string;
  }) => {
    setSearchResult(result);
    setSearchParams(params);
  };

  const handleBack = () => {
    setSearchResult(null);
    setSearchParams(null);
  };

  // 검색 결과가 있으면 결과 페이지 표시
  if (searchResult && searchParams) {
    return <FlightResults result={searchResult} onBack={handleBack} searchParams={searchParams} />;
  }

  // 검색 페이지
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
            <FloatLogo className="h-10 text-white" />
            <div className="flex items-center gap-6">
              <button className="text-white hover:text-blue-200 transition-colors">
                항공권
              </button>
            </div>
          </nav>
        </header>

        {/* Hero section */}
        <main className="px-6 py-20">
          <div className="max-w-7xl mx-auto">
            <div className="text-center mb-12">
              <h1 className="text-white text-5xl md:text-6xl mb-4">
                세계 어디든, FLOWN와 함께
              </h1>
              <p className="text-white/90 text-xl">
                최저가 항공권을 비교하고 예약하세요
              </p>
            </div>

            {/* Search card */}
            <div className="flex justify-center">
              <FlightSearchCard 
                onSearchResult={(result, params) => handleSearchResult(result, params)}
              />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
