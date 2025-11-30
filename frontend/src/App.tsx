import { FloatLogo } from './components/FloatLogo';
import { FlightSearchCard } from './components/FlightSearchCard';
import { ImageWithFallback } from './components/figma/ImageWithFallback';

export default function App() {
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
                세계 어디든, FLOWN과 함께
              </h1>
              <p className="text-white/90 text-xl">
                최저가 항공권을 비교하고 예약하세요
              </p>
            </div>

            {/* Search card */}
            <div className="flex justify-center">
              <FlightSearchCard />
            </div>
          </div>
        </main>

        {/* Features */}
        <section className="px-6 py-16 bg-white/5 backdrop-blur-sm">
          <div className="max-w-7xl mx-auto">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="text-center p-6">
                <div className="w-16 h-16 bg-blue-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-blue-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h3 className="text-white text-xl mb-2">최저가 보장</h3>
                <p className="text-white/80">수백 개 항공사의 가격을 실시간 비교</p>
              </div>

              <div className="text-center p-6">
                <div className="w-16 h-16 bg-blue-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-blue-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <h3 className="text-white text-xl mb-2">빠른 검색</h3>
                <p className="text-white/80">몇 초 만에 최적의 항공편 찾기</p>
              </div>

              <div className="text-center p-6">
                <div className="w-16 h-16 bg-blue-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-blue-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                </div>
                <h3 className="text-white text-xl mb-2">안전한 예약</h3>
                <p className="text-white/80">신뢰할 수 있는 보안 시스템</p>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
