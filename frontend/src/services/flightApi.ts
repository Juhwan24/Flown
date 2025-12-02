import { SearchRequest, SearchResponse } from '../types/flight';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://flown-production.up.railway.app/';

export async function searchFlights(request: SearchRequest): Promise<SearchResponse> {
  const response = await fetch(`${API_BASE_URL}/api/search`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '검색 중 오류가 발생했습니다.' }));
    throw new Error(error.detail || '검색 중 오류가 발생했습니다.');
  }

  return response.json();
}

