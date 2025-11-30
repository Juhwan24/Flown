export interface FlightSegment {
  from_airport: string;
  to_airport: string;
  date: string;
  price: number;
  provider: string;
  departure_time?: string;
  arrival_time?: string;
}

export interface SearchRequest {
  departure: string;
  destination: string;
  start_date: string;
  end_date: string;
  trip_nights?: number;
}

export interface SearchResponse {
  total_cost: number;
  segments: FlightSegment[];
  route_pattern: string;
  cheaper_than_direct: boolean;
  direct_cost?: number;
}

