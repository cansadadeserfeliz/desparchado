import { ref, reactive, Ref } from 'vue';
import {
  IWizardState,
  IEntityOption,
  IEventDetailResponse,
} from '../../../../../scripts/api/interfaces';
import { toBogotaLocalDateTimeString } from '../../../../../scripts/utils/date';

/**
 * Helper to serialize the wizard state for initial capture and dirty state tracking.
 *
 * @param state - The current wizard state object.
 * @returns The JSON serialized string representation of the state.
 */
export const serializeWizardState = (state: IWizardState): string => {
  const normalizeDateTime = (dateStr: string): string => {
    return toBogotaLocalDateTimeString(dateStr) || dateStr;
  };

  return JSON.stringify({
    title: state.title,
    description: state.description,
    organizerIds: state.organizerIds,
    speakerIds: state.speakerIds,
    placeId: state.placeId,
    eventDate: normalizeDateTime(state.eventDate),
    category: state.category,
    price: state.price,
    eventSourceUrl: state.eventSourceUrl,
    isPublished: state.isPublished,
  });
};

export interface IUseEventWizardStateReturn {
  state: IWizardState;
  selectedSpeakers: Ref<IEntityOption[]>;
  selectedOrganizers: Ref<IEntityOption[]>;
  selectedPlace: Ref<{ id: number; name: string } | null>;
  initialSerializedState: Ref<string>;
  captureInitialState: () => void;
  hydrateWizardState: (data: IEventDetailResponse) => void;
}

/**
 * Composable responsible for managing the reactive state of the Event Wizard,
 * handling initial state capture, and performing state hydration for editing.
 *
 * @param mode - The current wizard mode, either 'create' or 'edit'.
 * @param initialData - Optional initial event details for editing mode.
 * @returns The reactive wizard state, selected entity refs, and state utility functions.
 */
export const useEventWizardState = (
  mode: 'create' | 'edit',
  initialData?: IEventDetailResponse,
): IUseEventWizardStateReturn => {
  const state = reactive<IWizardState>({
    title: initialData?.title || '',
    description: initialData?.description || '',
    image: null,
    imagePreviewUrl: initialData?.image_url || '',
    organizerIds: initialData ? initialData.organizers.map((o) => o.id) : [],
    speakerIds: initialData ? initialData.speakers.map((s) => s.id) : [],
    placeId: initialData ? initialData.place?.id || null : null,
    eventDate: initialData ? toBogotaLocalDateTimeString(initialData.event_date) : '',
    category: initialData?.category || 'other',
    price: initialData ? String(initialData.price) : '0',
    eventSourceUrl: initialData?.event_source_url || '',
    isPublished: initialData?.is_published || false,
  });

  const selectedSpeakers = ref<IEntityOption[]>([]);
  const selectedOrganizers = ref<IEntityOption[]>([]);
  const selectedPlace = ref<{ id: number; name: string } | null>(null);

  const initialSerializedState = ref('');

  const captureInitialState = (): void => {
    initialSerializedState.value = serializeWizardState(state);
  };

  const hydrateWizardState = (data: IEventDetailResponse): void => {
    state.title = data.title;
    state.description = data.description;
    state.category = data.category || 'other';
    state.price = String(data.price);
    state.eventSourceUrl = data.event_source_url;
    state.isPublished = data.is_published;
    state.eventDate = toBogotaLocalDateTimeString(data.event_date);
    state.organizerIds = data.organizers.map((o) => o.id);
    state.speakerIds = data.speakers.map((s) => s.id);
    state.placeId = data.place ? data.place.id : null;
    if (data.image_url) {
      state.imagePreviewUrl = data.image_url;
    }

    selectedSpeakers.value = data.speakers;
    selectedOrganizers.value = data.organizers;
    selectedPlace.value = data.place;
  };

  return {
    state,
    selectedSpeakers,
    selectedOrganizers,
    selectedPlace,
    initialSerializedState,
    captureInitialState,
    hydrateWizardState,
  };
};
