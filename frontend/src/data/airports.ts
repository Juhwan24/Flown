export interface Airport {
  code: string;
  name: string;
  city: string;
  country: string;
  countryCode: string;
  fullName: string;
}

export interface AirportGroup {
  country: string;
  countryCode: string;
  flag: string;
  airports: Airport[];
}

export const airportGroups: AirportGroup[] = [
  {
    country: '대한민국',
    countryCode: 'KR',
    flag: '🇰🇷',
    airports: [
      {
        code: 'ICN',
        name: 'Incheon International Airport',
        city: '서울 / 인천',
        country: '대한민국',
        countryCode: 'KR',
        fullName: 'Incheon International Airport · 대한민국',
      },
      {
        code: 'GMP',
        name: 'Gimpo International Airport',
        city: '서울 / 김포',
        country: '대한민국',
        countryCode: 'KR',
        fullName: 'Gimpo International Airport · 대한민국',
      },
      {
        code: 'PUS',
        name: 'Gimhae International Airport',
        city: '부산 / 김해',
        country: '대한민국',
        countryCode: 'KR',
        fullName: 'Gimhae International Airport · 대한민국',
      },
      {
        code: 'CJU',
        name: 'Jeju International Airport',
        city: '제주',
        country: '대한민국',
        countryCode: 'KR',
        fullName: 'Jeju International Airport · 대한민국',
      },
      {
        code: 'TAE',
        name: 'Daegu International Airport',
        city: '대구',
        country: '대한민국',
        countryCode: 'KR',
        fullName: 'Daegu International Airport · 대한민국',
      },
    ],
  },
  {
    country: '일본',
    countryCode: 'JP',
    flag: '🇯🇵',
    airports: [
      {
        code: 'NRT',
        name: 'Narita International Airport',
        city: '도쿄 / 나리타',
        country: '일본',
        countryCode: 'JP',
        fullName: 'Narita International Airport · 일본',
      },
      {
        code: 'HND',
        name: 'Haneda Airport',
        city: '도쿄 / 하네다',
        country: '일본',
        countryCode: 'JP',
        fullName: 'Haneda Airport · 일본',
      },
      {
        code: 'KIX',
        name: 'Kansai International Airport',
        city: '오사카 / 간사이',
        country: '일본',
        countryCode: 'JP',
        fullName: 'Kansai International Airport · 일본',
      },
      {
        code: 'CTS',
        name: 'New Chitose Airport',
        city: '삿포로 / 신치토세',
        country: '일본',
        countryCode: 'JP',
        fullName: 'New Chitose Airport · 일본',
      },
      {
        code: 'FUK',
        name: 'Fukuoka Airport',
        city: '후쿠오카',
        country: '일본',
        countryCode: 'JP',
        fullName: 'Fukuoka Airport · 일본',
      },
      {
        code: 'OKA',
        name: 'Naha Airport',
        city: '오키나와 / 나하',
        country: '일본',
        countryCode: 'JP',
        fullName: 'Naha Airport · 일본',
      },
    ],
  },
  {
    country: '미국',
    countryCode: 'US',
    flag: '🇺🇸',
    airports: [
      {
        code: 'LAX',
        name: 'Los Angeles International Airport',
        city: '로스앤젤레스',
        country: '미국',
        countryCode: 'US',
        fullName: 'Los Angeles International Airport · 미국',
      },
      {
        code: 'JFK',
        name: 'John F. Kennedy International Airport',
        city: '뉴욕 / JFK',
        country: '미국',
        countryCode: 'US',
        fullName: 'John F. Kennedy International Airport · 미국',
      },
      {
        code: 'SFO',
        name: 'San Francisco International Airport',
        city: '샌프란시스코',
        country: '미국',
        countryCode: 'US',
        fullName: 'San Francisco International Airport · 미국',
      },
      {
        code: 'SEA',
        name: 'Seattle–Tacoma International Airport',
        city: '시애틀',
        country: '미국',
        countryCode: 'US',
        fullName: 'Seattle–Tacoma International Airport · 미국',
      },
    ],
  },
  {
    country: '중국',
    countryCode: 'CN',
    flag: '🇨🇳',
    airports: [
      {
        code: 'PVG',
        name: 'Shanghai Pudong International Airport',
        city: '상하이 / 푸동',
        country: '중국',
        countryCode: 'CN',
        fullName: 'Shanghai Pudong International Airport · 중국',
      },
      {
        code: 'PEK',
        name: 'Beijing Capital International Airport',
        city: '베이징 / 수도',
        country: '중국',
        countryCode: 'CN',
        fullName: 'Beijing Capital International Airport · 중국',
      },
      {
        code: 'TAO',
        name: 'Qingdao Jiaodong International Airport',
        city: '칭다오',
        country: '중국',
        countryCode: 'CN',
        fullName: 'Qingdao Jiaodong International Airport · 중국',
      },
    ],
  },
  {
    country: '대만',
    countryCode: 'TW',
    flag: '🇹🇼',
    airports: [
      {
        code: 'TPE',
        name: 'Taiwan Taoyuan International Airport',
        city: '타이베이 / 타오위안',
        country: '대만',
        countryCode: 'TW',
        fullName: 'Taiwan Taoyuan International Airport · 대만',
      },
      {
        code: 'KHH',
        name: 'Kaohsiung International Airport',
        city: '가오슝',
        country: '대만',
        countryCode: 'TW',
        fullName: 'Kaohsiung International Airport · 대만',
      },
    ],
  },
  {
    country: '태국',
    countryCode: 'TH',
    flag: '🇹🇭',
    airports: [
      {
        code: 'BKK',
        name: 'Suvarnabhumi Airport',
        city: '방콕 / 수완나품',
        country: '태국',
        countryCode: 'TH',
        fullName: 'Suvarnabhumi Airport · 태국',
      },
      {
        code: 'DMK',
        name: 'Don Mueang International Airport',
        city: '방콕 / 돈므앙',
        country: '태국',
        countryCode: 'TH',
        fullName: 'Don Mueang International Airport · 태국',
      },
      {
        code: 'HKT',
        name: 'Phuket International Airport',
        city: '푸켓',
        country: '태국',
        countryCode: 'TH',
        fullName: 'Phuket International Airport · 태국',
      },
    ],
  },
];

// 모든 공항을 하나의 배열로 반환하는 헬퍼 함수
export const getAllAirports = (): Airport[] => {
  return airportGroups.flatMap(group => group.airports);
};

// 코드로 공항 찾기
export const findAirportByCode = (code: string): Airport | undefined => {
  return getAllAirports().find(airport => airport.code === code);
};

