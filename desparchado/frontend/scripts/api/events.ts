import { getData, handleResponse, submitData } from './base';
import {
  IApiPaginatedResponse,
  IEvent,
  IEventDetailResponse,
  IEventWriteResponse,
} from './interfaces';

export async function getEventList(url: string): Promise<IApiPaginatedResponse<IEvent>> {
  const res = await fetch(url);
  return handleResponse<IApiPaginatedResponse<IEvent>>(res);
}

export async function getEventDetail(url: string): Promise<IEventDetailResponse> {
  return getData<IEventDetailResponse>(url);
}

export async function createEvent(url: string, data: FormData): Promise<IEventWriteResponse> {
  const res = await submitData(url, data, 'POST');
  return handleResponse<IEventWriteResponse>(
    res,
  );
}

export async function updateEvent(url: string, data: FormData): Promise<IEventWriteResponse> {
  const res = await submitData(url, data, 'PATCH');
  return handleResponse<IEventWriteResponse>(
    res,
  );
}
