export interface IApiPaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface IEvent {
  title: string;
  slug: string;
  url: string;
  event_date: string;
  formatted_hour: string;
  formatted_day: string;
  place: {
    name: string;
    slug: string;
  };
  image_url: string;
  description: string;
  truncated_description: string;
  is_recurrent: boolean;
}
