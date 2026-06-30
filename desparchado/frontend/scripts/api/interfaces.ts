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

export interface IEntityOption {
  id: number;
  name: string;
  image_url?: string;
}

export interface IWizardState {
  title: string;
  description: string;
  image: File | null;
  imagePreviewUrl: string;
  organizerIds: number[];
  speakerIds: number[];
  placeId: number | null;
  eventDate: string;
  category: string;
  price: string;
  eventSourceUrl: string;
  isPublished: boolean;
}

export interface IEventDetailResponse {
  title: string;
  description: string;
  image_url: string | null;
  event_date: string;
  category: string;
  price: string;
  event_source_url: string;
  is_published: boolean;
  organizers: IEntityOption[];
  speakers: IEntityOption[];
  place: {
    id: number;
    name: string;
    city?: number | null;
    city_id?: number | null;
  } | null;
}

export interface IEventWriteResponse {
  url: string;
}

export interface ISearchResponse<T> {
  results: T[];
}

export type DRFValidationError = Record<string, string[]>;
