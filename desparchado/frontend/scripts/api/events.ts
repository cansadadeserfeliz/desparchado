import { IApiPaginatedResponse, IEvent } from './interfaces';

export async function getEventList(url: string): Promise<IApiPaginatedResponse<IEvent>> {
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`);
  }
  const eventPaginatedResponse: IApiPaginatedResponse<IEvent> = await res.json();

  return eventPaginatedResponse;
}
