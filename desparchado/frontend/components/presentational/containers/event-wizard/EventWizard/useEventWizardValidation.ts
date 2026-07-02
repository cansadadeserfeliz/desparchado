import { ref, computed, watch, nextTick, Ref, ComputedRef } from 'vue';
import { DRFValidationError, IWizardState } from '../../../../../scripts/api/interfaces';

// Maps for error navigation & element focus
const FIELD_STEP_MAP: Record<string, number> = {
  title: 1,
  description: 1,
  organizers: 1,
  organizer_ids: 1,
  speakers: 1,
  speaker_ids: 1,
  event_date: 2,
  place: 2,
  place_id: 2,
  event_source_url: 3,
  category: 3,
  price: 3,
  is_published: 3,
};

const FIELD_ELEMENT_ID_MAP: Record<string, string> = {
  title: 'wizard-title',
  description: 'wizard-description',
  event_date: 'wizard-date',
  event_source_url: 'wizard-source-url',
  price: 'wizard-price',
  category: 'wizard-category-literature',
  is_published: 'wizard-published',
};

const STEP_ERRORS_MAP: Record<number, string[]> = {
  1: ['title', 'description', 'organizer_ids', 'speaker_ids'],
  2: ['event_date', 'place_id'],
  3: ['event_source_url', 'category', 'price', 'is_published'],
};

// DRY watchers setup to clear field-specific errors dynamically
const FIELD_ERROR_KEYS: Record<string, string> = {
  title: 'title',
  description: 'description',
  eventDate: 'event_date',
  eventSourceUrl: 'event_source_url',
  price: 'price',
  category: 'category',
  organizerIds: 'organizer_ids',
  speakerIds: 'speaker_ids',
  placeId: 'place_id',
  isPublished: 'is_published',
};

export interface IUseEventWizardValidationReturn {
  fieldErrors: Ref<DRFValidationError>;
  submitError: Ref<string>;
  stepHasErrors: ComputedRef<boolean>;
  setupErrorWatchers: () => void;
  navigateToErrorField: (firstErrorKey: string) => Promise<void>;
}

/**
 * Composable responsible for managing form validations, dynamic error clearing watchers,
 * and element-focus navigation when API/form validation errors are encountered.
 *
 * @param state - The reactive wizard state object.
 * @param currentStep - Reactive reference to the current step number.
 * @returns Validation error refs, step error checkers, error focus navigator, and watch hooks.
 */
export const useEventWizardValidation = (
  state: IWizardState,
  currentStep: Ref<number>,
): IUseEventWizardValidationReturn => {
  const fieldErrors = ref<DRFValidationError>({});
  const submitError = ref<string>('');

  const stepHasErrors = computed((): boolean => {
    const fields = STEP_ERRORS_MAP[currentStep.value] || [];
    return fields.some((field) => !!fieldErrors.value[field]);
  });

  const setupErrorWatchers = (): void => {
    Object.entries(FIELD_ERROR_KEYS).forEach(([stateKey, errorKey]) => {
      watch(
        () => state[stateKey as keyof IWizardState],
        () => {
          delete fieldErrors.value[errorKey];
        },
        { deep: true },
      );
    });
  };

  const navigateToErrorField = async (firstErrorKey: string): Promise<void> => {
    const targetStep = FIELD_STEP_MAP[firstErrorKey];
    if (targetStep !== undefined) {
      currentStep.value = targetStep;
    }

    await nextTick();

    const elementId = FIELD_ELEMENT_ID_MAP[firstErrorKey];
    if (elementId) {
      const el = document.getElementById(elementId);
      if (el) {
        el.focus();
      }
    }
  };

  return {
    fieldErrors,
    submitError,
    stepHasErrors,
    setupErrorWatchers,
    navigateToErrorField,
  };
};
