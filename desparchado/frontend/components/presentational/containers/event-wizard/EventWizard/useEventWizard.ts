import { ref, computed, onMounted, Ref, ComputedRef } from 'vue';
import {
  IWizardState,
  DRFValidationError,
  IEntityOption,
  IEventDetailResponse,
} from '../../../../../scripts/api/interfaces';
import { useEventWizardState, serializeWizardState } from './useEventWizardState';
import { useEventWizardNavigation } from './useEventWizardNavigation';
import type { IStepRef } from './useEventWizardNavigation';
import { useEventWizardValidation } from './useEventWizardValidation';
import { useEventWizardLayout } from './useEventWizardLayout';
import { useEventWizardSubmit } from './useEventWizardSubmit';

export type { IStepRef };

export interface IUseEventWizardProps {
  mode: 'create' | 'edit';
  apiUrl: string;
  apiUpdateUrl?: string;
  cities: Array<{ id: number; name: string }>;
  initialData?: IEventDetailResponse;
}

export interface IUseEventWizardReturn {
  state: IWizardState;
  selectedSpeakers: Ref<IEntityOption[]>;
  selectedOrganizers: Ref<IEntityOption[]>;
  selectedPlace: Ref<{ id: number; name: string } | null>;
  currentStep: Ref<number>;
  showMobilePreview: Ref<boolean>;
  condensed: Ref<boolean>;
  isSubmitting: Ref<boolean>;
  fieldErrors: Ref<DRFValidationError>;
  submitError: Ref<string>;
  stepRefs: Ref<IStepRef[]>;
  isStepComponentInstance: (el: unknown) => el is IStepRef;
  isStepValid: (stepNumber: number) => boolean;
  isCurrentStepValid: ComputedRef<boolean>;
  stepHasErrors: ComputedRef<boolean>;
  isDirty: ComputedRef<boolean>;
  handlePrev: () => void;
  handleNext: () => void;
  handleSubmit: () => Promise<void>;
}

/**
 * Orchestrating Composition composable for the Event Wizard. Combines isolated sub-composables
 * for state, navigation, validation, layout effects, and submission logic.
 *
 * @param props - Root component configuration properties.
 * @returns Combined reactive states and action callbacks for EventWizard view.
 */
export const useEventWizard = (props: IUseEventWizardProps): IUseEventWizardReturn => {
  // 1. Core State Management
  const {
    state,
    selectedSpeakers,
    selectedOrganizers,
    selectedPlace,
    initialSerializedState,
    captureInitialState,
  } = useEventWizardState(props.mode, props.initialData);

  // 2. Multi-step Navigation
  const {
    currentStep,
    stepRefs,
    isStepComponentInstance,
    isStepValid,
    isCurrentStepValid,
    handlePrev,
    handleNext,
  } = useEventWizardNavigation();

  // 3. Validation and Dynamic Error Cleansing
  const { fieldErrors, submitError, stepHasErrors, setupErrorWatchers, navigateToErrorField } =
    useEventWizardValidation(state, currentStep);

  // 4. Dirty State Computation & Browser Layout Synchronization
  const isDirty = computed((): boolean => {
    const currentSerializedState = serializeWizardState(state);
    return initialSerializedState.value !== currentSerializedState || state.image !== null;
  });

  const showMobilePreview = ref(false);
  const condensed = ref(false);

  const { removeBeforeUnload } = useEventWizardLayout({
    isDirty,
    showMobilePreview,
  });

  // 5. Submit Orchestration
  const { isSubmitting, handleSubmit } = useEventWizardSubmit({
    props,
    state,
    fieldErrors,
    submitError,
    removeBeforeUnload,
    navigateToErrorField,
    validateSubmit: (): boolean => {
      const totalSteps = 3;
      let allStepsValid = true;
      for (let i = 1; i <= totalSteps; i++) {
        if (!isStepValid(i)) {
          allStepsValid = false;
          break;
        }
      }
      if (!allStepsValid) {
        alert('Por favor verifique que todos los pasos sean válidos antes de enviar.');
        return false;
      }
      return true;
    },
  });

  // Setup error watchers and trigger capture initial state on mounted
  setupErrorWatchers();

  onMounted((): void => {
    captureInitialState();
  });

  return {
    state,
    selectedSpeakers,
    selectedOrganizers,
    selectedPlace,
    currentStep,
    showMobilePreview,
    condensed,
    isSubmitting,
    fieldErrors,
    submitError,
    stepRefs,
    isStepComponentInstance,
    isStepValid,
    isCurrentStepValid,
    stepHasErrors,
    isDirty,
    handlePrev,
    handleNext,
    handleSubmit,
  };
};
