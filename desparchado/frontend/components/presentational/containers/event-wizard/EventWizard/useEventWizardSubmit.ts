import { ref, Ref } from 'vue';
import {
  IWizardState,
  DRFValidationError,
  IEventWriteResponse,
  IEventDetailResponse,
} from '../../../../../scripts/api/interfaces';
import { createEvent, updateEvent } from '../../../../../scripts/api/events';
import { ValidationError } from '../../../../../scripts/api/base';

export interface IUseEventWizardSubmitProps {
  mode: 'create' | 'edit';
  apiUrl: string;
  apiUpdateUrl?: string;
  cities: Array<{ id: number; name: string }>;
  initialData?: IEventDetailResponse;
}

export interface IUseEventWizardSubmitParams {
  props: IUseEventWizardSubmitProps;
  state: IWizardState;
  fieldErrors: Ref<DRFValidationError>;
  submitError: Ref<string>;
  removeBeforeUnload: () => void;
  navigateToErrorField: (firstErrorKey: string) => Promise<void>;
  validateSubmit: () => boolean;
}

export interface IUseEventWizardSubmitReturn {
  isSubmitting: Ref<boolean>;
  handleSubmit: () => Promise<void>;
}

/**
 * Validates that a redirect URL is a safe relative path starting with a single slash
 * or matches the current window's origin to prevent open redirect vulnerabilities.
 *
 * @param url - The URL to validate.
 * @returns True if the URL is safe to navigate to.
 */
export const isValidRedirectUrl = (url: string): boolean => {
  if (!url || typeof url !== 'string') {
    return false;
  }
  // Enforce relative paths starting with '/' but reject '//' or '/\'
  if (url.startsWith('/')) {
    return !url.startsWith('//') && !url.startsWith('/\\');
  }

  // Verify absolute URL matches the current window origin
  try {
    const parsed = new URL(url, window.location.origin);
    return parsed.origin === window.location.origin;
  } catch {
    return false;
  }
};

/**
 * Helper to format event date to ISO string if valid.
 *
 * @param eventDate - Raw date string.
 * @returns ISO string format or original string if invalid/empty.
 */
export const formatEventDate = (eventDate: string): string => {
  if (!eventDate) {
    return '';
  }
  try {
    const date = new Date(eventDate);
    return !isNaN(date.getTime()) ? date.toISOString() : eventDate;
  } catch {
    return eventDate;
  }
};

/**
 * Composable responsible for orchestrating the Event Wizard data submission payload,
 * parsing validation or quota errors, and managing post-submit success window redirects.
 *
 * @param params - Configuration parameters: props, state, error refs, and callbacks.
 * @returns Submission indicator ref and submit handler callback.
 */
export const useEventWizardSubmit = (
  params: IUseEventWizardSubmitParams,
): IUseEventWizardSubmitReturn => {
  const isSubmitting = ref(false);

  const prepareFormData = (): FormData => {
    const formData = new FormData();
    formData.append('title', params.state.title);
    formData.append('description', params.state.description);
    // When preparing the data to send, if value is "other" send an empty string instead of "other"
    formData.append('category', params.state.category === 'other' ? '' : params.state.category);
    formData.append('price', params.state.price);
    formData.append('event_source_url', params.state.eventSourceUrl);
    formData.append('is_published', String(params.state.isPublished));

    formData.append('event_date', formatEventDate(params.state.eventDate));
    formData.append('place_id', params.state.placeId !== null ? String(params.state.placeId) : '');

    params.state.organizerIds.forEach((id) => {
      formData.append('organizer_ids', String(id));
    });
    params.state.speakerIds.forEach((id) => {
      formData.append('speaker_ids', String(id));
    });

    if (params.state.image) {
      formData.append('image', params.state.image);
    }

    return formData;
  };

  const getErrorMessage = (errObj: Record<string, unknown>): string => {
    if (errObj.non_field_errors) {
      return Array.isArray(errObj.non_field_errors)
        ? errObj.non_field_errors.join(', ')
        : String(errObj.non_field_errors);
    }
    if (errObj.detail) return String(errObj.detail);
    if (errObj.message) return String(errObj.message);

    const hasOtherErrors = Object.keys(errObj).some((k) => k !== 'non_field_errors');
    return hasOtherErrors
      ? 'Ocurrió un error al guardar el evento. Revise los campos.'
      : 'Ocurrió un error al guardar el evento. Intente de nuevo.';
  };

  const handleApiError = (error: unknown): void => {
    console.error('Submit failed:', error);

    if (error instanceof ValidationError) {
      if (error.status === 403) {
        // TODO: Implement Umami tracking (quota:hit, resource: 'event')
      }
      const errObj = error.data as Record<string, unknown>;
      params.fieldErrors.value = errObj as DRFValidationError;
      params.submitError.value = getErrorMessage(errObj);
      return;
    }

    if (error instanceof Error) {
      params.submitError.value = error.message;
      return;
    }

    if (!error || typeof error !== 'object') {
      params.submitError.value =
        'Ocurrió un error inesperado al guardar el evento. Intente de nuevo.';
      return;
    }

    const errObj = error as Record<string, unknown>;
    params.fieldErrors.value = errObj as DRFValidationError;
    params.submitError.value = getErrorMessage(errObj);
  };

  const submitFormPayload = async (formData: FormData): Promise<IEventWriteResponse> => {
    const url =
      params.props.mode === 'edit' && params.props.apiUpdateUrl
        ? params.props.apiUpdateUrl
        : params.props.apiUrl;
    return params.props.mode === 'edit' ? updateEvent(url, formData) : createEvent(url, formData);
  };

  const handleSuccessfulSubmit = (response: IEventWriteResponse): void => {
    // TODO: Implement Umami tracking (wizard:submit, action: params.props.mode)

    // Prevent beforeunload prompt using the cleanup handler
    params.removeBeforeUnload();

    // Redirect to the event details page after validation
    if (response.url) {
      if (isValidRedirectUrl(response.url)) {
        window.location.href = response.url;
      } else {
        throw new Error('La URL de redirección no es válida o segura.');
      }
    } else {
      throw new Error('La respuesta del servidor no contiene una URL de redirección.');
    }
  };

  const handleSubmit = async (): Promise<void> => {
    if (!params.validateSubmit()) {
      return;
    }

    isSubmitting.value = true;
    params.fieldErrors.value = {};
    params.submitError.value = '';

    const formData = prepareFormData();

    try {
      const response = await submitFormPayload(formData);
      handleSuccessfulSubmit(response);
    } catch (error: unknown) {
      handleApiError(error);

      const keys = Object.keys(params.fieldErrors.value);
      if (keys.length > 0) {
        await params.navigateToErrorField(keys[0]);
      }
    } finally {
      isSubmitting.value = false;
    }
  };

  return {
    isSubmitting,
    handleSubmit,
  };
};
