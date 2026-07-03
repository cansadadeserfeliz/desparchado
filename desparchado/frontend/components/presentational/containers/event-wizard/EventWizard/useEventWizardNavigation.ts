import { ref, computed, Ref, ComputedRef } from 'vue';

export interface IStepRef {
  isValid: boolean;
}

export interface IUseEventWizardNavigationReturn {
  currentStep: Ref<number>;
  stepRefs: Ref<IStepRef[]>;
  isStepComponentInstance: (el: unknown) => el is IStepRef;
  isStepValid: (stepNumber: number) => boolean;
  isCurrentStepValid: ComputedRef<boolean>;
  handlePrev: () => void;
  handleNext: () => void;
}

/**
 * Composable responsible for managing Event Wizard multi-step navigation flow,
 * track components validations, and manage transition boundaries.
 *
 * @returns Ref steps, component instances checking, and handlers for step transitions.
 */
export const useEventWizardNavigation = (): IUseEventWizardNavigationReturn => {
  const currentStep = ref(1);
  const stepRefs = ref<IStepRef[]>([]);

  const isStepComponentInstance = (el: unknown): el is IStepRef => {
    return typeof el === 'object' && el !== null && 'isValid' in el;
  };

  const isStepValid = (stepNumber: number): boolean => {
    const stepIndex = stepNumber - 1;
    const stepInstance = stepRefs.value.at(stepIndex);
    return stepInstance?.isValid ?? false;
  };

  const isCurrentStepValid = computed((): boolean => {
    return isStepValid(currentStep.value);
  });

  const handlePrev = (): void => {
    if (currentStep.value > 1) {
      currentStep.value--;
    }
  };

  const handleNext = (): void => {
    if (!isCurrentStepValid.value) {
      return;
    }

    if (currentStep.value < 3) {
      currentStep.value++;
    }
  };

  return {
    currentStep,
    stepRefs,
    isStepComponentInstance,
    isStepValid,
    isCurrentStepValid,
    handlePrev,
    handleNext,
  };
};
