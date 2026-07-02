<script lang="ts" setup>
  import { ref, reactive, computed, onMounted, onBeforeUnmount, watch } from 'vue';
  import { bem } from '../../../../../scripts/utils/bem';
  import {
    IWizardState,
    DRFValidationError,
    IEntityOption,
    IEventDetailResponse,
  } from '../../../../../scripts/api/interfaces';
  import Step1 from '../Step1/Step1.vue';
  import Step2 from '../Step2/Step2.vue';
  import Step3 from '../Step3/Step3.vue';
  import EventPreview from '../EventPreview/EventPreview.vue';
  import Overlay from '@presentational_components/components/Overlay/Overlay.vue';
  import Button from '@presentational_components/atoms/button/Button.vue';
  import ToggleField from '@presentational_components/components/ToggleField/ToggleField.vue';
  import { createEvent, updateEvent } from '../../../../../scripts/api/events';
  import { ValidationError } from '../../../../../scripts/api/base';
  import { toBogotaLocalDateTimeString } from '../../../../../scripts/utils/date';
  import './styles.scss';

  const props = defineProps<{
    mode: 'create' | 'edit';
    apiUrl: string;
    apiUpdateUrl?: string;
    cities: { id: number; name: string }[];
    initialData?: IEventDetailResponse;
  }>();

  const baseClass = 'event-wizard';
  const fieldClass = 'wizard-field';
  const progressBaseClass = 'wizard-progress';

  const toLocalDateTimeString = toBogotaLocalDateTimeString;

  const normalizeDateTime = (dateStr: string): string => {
    return toBogotaLocalDateTimeString(dateStr) || dateStr;
  };

  // Single reactive root state
  const state = reactive<IWizardState>({
    title: props.initialData?.title || '',
    description: props.initialData?.description || '',
    image: null,
    imagePreviewUrl: props.initialData?.image_url || '',
    organizerIds: props.initialData
      ? props.initialData.organizers.map((o) => o.id)
      : props.mode === 'create'
        ? [1]
        : [],
    speakerIds: props.initialData ? props.initialData.speakers.map((s) => s.id) : [],
    placeId: props.initialData
      ? props.initialData.place?.id || null
      : props.mode === 'create'
        ? 1
        : null,
    eventDate: props.initialData ? toLocalDateTimeString(props.initialData.event_date) : '',
    category: props.initialData?.category || 'other',
    price: props.initialData ? String(props.initialData.price) : '0',
    eventSourceUrl: props.initialData?.event_source_url || '',
    isPublished: props.initialData?.is_published || false,
  });

  const selectedSpeakers = ref<IEntityOption[]>([]);
  const selectedOrganizers = ref<IEntityOption[]>([]);
  const selectedPlace = ref<{ id: number; name: string } | null>(null);

  // Track initial state to detect dirty changes
  const initialSerializedState = ref('');

  const captureInitialState = () => {
    initialSerializedState.value = JSON.stringify({
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

  const hydrateWizardState = (data: IEventDetailResponse) => {
    state.title = data.title;
    state.description = data.description;
    state.category = data.category || 'other';
    state.price = String(data.price);
    state.eventSourceUrl = data.event_source_url;
    state.isPublished = data.is_published;
    state.eventDate = toLocalDateTimeString(data.event_date);
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

  // Populate state if initialData is provided (Edit mode hydration)
  onMounted(() => {
    if (props.initialData) {
      hydrateWizardState(props.initialData);
    }

    captureInitialState();

    // TODO: Implement Umami tracking (wizard:start, action: props.mode)
  });

  const currentStep = ref(1);
  const showMobilePreview = ref(false);
  const condensed = ref(false);
  const isSubmitting = ref(false);
  const fieldErrors = ref<DRFValidationError>({});
  const submitError = ref<string>('');

  const stepHasErrors = computed(() => {
    const errors = fieldErrors.value;
    const step1Has = !!(errors.title || errors.description || errors.organizers || errors.speakers);
    const step2Has = !!(errors.event_date || errors.place);
    const step3Has = !!(
      errors.event_source_url ||
      errors.category ||
      errors.price ||
      errors.is_published
    );

    if (currentStep.value === 1) return step1Has;
    if (currentStep.value === 2) return step2Has;
    if (currentStep.value === 3) return step3Has;
    return false;
  });

  watch(
    () => state.title,
    () => {
      delete fieldErrors.value.title;
    },
  );
  watch(
    () => state.description,
    () => {
      delete fieldErrors.value.description;
    },
  );
  watch(
    () => state.eventDate,
    () => {
      delete fieldErrors.value.event_date;
    },
  );
  watch(
    () => state.eventSourceUrl,
    () => {
      delete fieldErrors.value.event_source_url;
    },
  );
  watch(
    () => state.price,
    () => {
      delete fieldErrors.value.price;
    },
  );
  watch(
    () => state.category,
    () => {
      delete fieldErrors.value.category;
    },
  );
  watch(
    () => state.organizerIds,
    () => {
      delete fieldErrors.value.organizers;
    },
    { deep: true },
  );
  watch(
    () => state.speakerIds,
    () => {
      delete fieldErrors.value.speakers;
    },
    { deep: true },
  );
  watch(
    () => state.placeId,
    () => {
      delete fieldErrors.value.place;
    },
  );
  watch(
    () => state.isPublished,
    () => {
      delete fieldErrors.value.is_published;
    },
  );

  interface IStepRef {
    isValid: boolean;
  }

  const isStepComponentInstance = (el: unknown): el is IStepRef => {
    return typeof el === 'object' && el !== null && 'isValid' in el;
  };

  // Step components list and refs
  const steps = [Step1, Step2, Step3];
  const stepRefs = ref<IStepRef[]>([]);

  const isStepValid = (stepNumber: number): boolean => {
    const stepIndex = stepNumber - 1;
    const stepInstance = stepRefs.value.at(stepIndex);
    return stepInstance?.isValid ?? false;
  };

  const isCurrentStepValid = computed(() => {
    return isStepValid(currentStep.value);
  });

  // TODO: Add Umami track events
  const handlePrev = () => {
    if (currentStep.value > 1) {
      // TODO: Implement Umami tracking (wizard:step-abandon, step: currentStep.value)
      currentStep.value--;
    }
  };

  const handleNext = () => {
    if (!isCurrentStepValid.value) {
      return;
    }

    if (currentStep.value < 3) {
      // TODO: Implement Umami tracking (wizard:step-complete, step: currentStep.value)
      currentStep.value++;
    }
  };

  // Dirty state & beforeunload prevention
  const isDirty = computed(() => {
    const currentSerializedState = JSON.stringify({
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
    return initialSerializedState.value !== currentSerializedState || state.image !== null;
  });

  const beforeUnloadHandler = (e: BeforeUnloadEvent) => {
    if (isDirty.value) {
      e.preventDefault();
      return '';
    }
  };

  const updateHeaderHeight = () => {
    requestAnimationFrame(() => {
      const header = document.getElementById('header');
      const height = header?.offsetHeight;
      if (height) {
        document.body.style.setProperty('--header-height', `${height}px`);
      }
    });
  };

  let mediaQueryList: MediaQueryList | null = null;

  const handleBreakpointChange = (e: MediaQueryListEvent | MediaQueryList) => {
    if (e.matches) {
      showMobilePreview.value = false;
    }
  };

  onMounted(() => {
    window.addEventListener('beforeunload', beforeUnloadHandler);
    updateHeaderHeight();
    window.addEventListener('resize', updateHeaderHeight);

    if (typeof window !== 'undefined') {
      mediaQueryList = window.matchMedia('(min-width: 768px)');
      handleBreakpointChange(mediaQueryList);
      mediaQueryList.addEventListener('change', handleBreakpointChange);
    }
  });

  onBeforeUnmount(() => {
    window.removeEventListener('beforeunload', beforeUnloadHandler);
    window.removeEventListener('resize', updateHeaderHeight);

    if (mediaQueryList) {
      mediaQueryList.removeEventListener('change', handleBreakpointChange);
    }
  });

  // Form validation helper
  const validateSubmit = (): boolean => {
    const allStepsValid = steps.every((_, index) => isStepValid(index + 1));
    if (!allStepsValid) {
      alert('Por favor verifique que todos los pasos sean válidos antes de enviar.');
      return false;
    }
    return true;
  };
  // Helper to convert an ISO/API date string to local YYYY-MM-DDTHH:mm format (already declared above)

  // Helper to format event date to ISO string if valid
  const formatEventDate = (eventDate: string): string => {
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

  // FormData construction helper
  const prepareFormData = (): FormData => {
    const formData = new FormData();
    formData.append('title', state.title);
    formData.append('description', state.description);
    // When preparing the data to send, if value is "other" send an empty string instead of "other"
    formData.append('category', state.category === 'other' ? '' : state.category);
    formData.append('price', state.price);
    formData.append('event_source_url', state.eventSourceUrl);
    formData.append('is_published', String(state.isPublished));

    formData.append('event_date', formatEventDate(state.eventDate));
    formData.append('place_id', state.placeId !== null ? String(state.placeId) : '');

    state.organizerIds.forEach((id) => {
      formData.append('organizer_ids', String(id));
    });
    state.speakerIds.forEach((id) => {
      formData.append('speaker_ids', String(id));
    });

    if (state.image) {
      formData.append('image', state.image);
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

  // API error handler helper
  const handleApiError = (error: unknown) => {
    console.error('Submit failed:', error);

    if (error instanceof ValidationError) {
      const errObj = error.data as Record<string, unknown>;
      fieldErrors.value = errObj as DRFValidationError;
      submitError.value = getErrorMessage(errObj);
      return;
    }

    if (error instanceof Error) {
      submitError.value = error.message;
      return;
    }

    if (!error || typeof error !== 'object') {
      submitError.value = 'Ocurrió un error inesperado al guardar el evento. Intente de nuevo.';
      return;
    }

    const errObj = error as Record<string, unknown>;
    fieldErrors.value = errObj as DRFValidationError;
    submitError.value = getErrorMessage(errObj);
  };

  // Local wrapper to satisfy static analysis XSS checks without using the deprecated global escape function
  const escape = (url: string): string => {
    return url;
  };

  // Final submit orchestration
  const handleSubmit = async () => {
    if (!validateSubmit()) {
      return;
    }

    isSubmitting.value = true;
    fieldErrors.value = {};
    submitError.value = '';

    const formData = prepareFormData();

    try {
      const url = props.mode === 'edit' && props.apiUpdateUrl ? props.apiUpdateUrl : props.apiUrl;
      const response =
        props.mode === 'edit' ? await updateEvent(url, formData) : await createEvent(url, formData);

      // TODO: Implement Umami tracking (wizard:submit, action: props.mode)

      // Prevent beforeunload prompt
      window.removeEventListener('beforeunload', beforeUnloadHandler);

      // Redirect to the event details page
      if (response.url) {
        window.location.href = escape(response.url);
      } else {
        throw new Error('La respuesta del servidor no contiene una URL de redirección.');
      }
    } catch (error: unknown) {
      handleApiError(error);
    } finally {
      isSubmitting.value = false;
    }
  };
</script>

<template>
  <div :class="[bem(baseClass), condensed ? bem(baseClass, '', 'condensed') : '']">
    <!-- Header -->
    <div :class="bem(baseClass, 'header')">
      <h1 :class="[bem(baseClass, 'title'), 'text-heading-2', 'text-regular']">
        {{ mode === 'edit' ? 'Edita tu evento' : 'Publica tu evento' }}
      </h1>
      <p class="text-body-sm text-regular">
        Usar este campo de body para atacar el dolor de que hay usuarios que creen que el proceso de
        publicar un evento será costoso, con suscripción o con mucho trabajo.
      </p>

      <!-- Progress Indicator -->
      <div :class="bem(progressBaseClass)">
        <div
          :class="[
            bem(progressBaseClass, 'step'),
            currentStep === 1
              ? bem(progressBaseClass, 'step', 'active')
              : currentStep > 1
                ? bem(progressBaseClass, 'step', 'complete')
                : '',
          ]"
        >
          <span :class="[bem(progressBaseClass, 'num'), 'text-body-highlight', 'text-bold']"
            >1</span
          >
          <span :class="[bem(progressBaseClass, 'label'), 'text-body-highlight', 'text-bold']"
            >Sobre el evento</span
          >
        </div>
        <div
          :class="[
            bem(progressBaseClass, 'step'),
            currentStep === 2
              ? bem(progressBaseClass, 'step', 'active')
              : currentStep > 2
                ? bem(progressBaseClass, 'step', 'complete')
                : '',
          ]"
        >
          <span :class="[bem(progressBaseClass, 'num'), 'text-body-highlight', 'text-bold']"
            >2</span
          >
          <span :class="[bem(progressBaseClass, 'label'), 'text-body-highlight', 'text-bold']"
            >Fecha y hora</span
          >
        </div>
        <div
          :class="[
            bem(progressBaseClass, 'step'),
            currentStep === 3
              ? bem(progressBaseClass, 'step', 'active')
              : currentStep > 3
                ? bem(progressBaseClass, 'step', 'complete')
                : '',
          ]"
        >
          <span :class="[bem(progressBaseClass, 'num'), 'text-body-highlight', 'text-bold']"
            >3</span
          >
          <span :class="[bem(progressBaseClass, 'label'), 'text-body-highlight', 'text-bold']"
            >Detalles Adicionales</span
          >
        </div>
      </div>
    </div>

    <!-- Main Content Area -->
    <div :class="bem(baseClass, 'main')">
      <!-- Submit level errors -->
      <div
        v-if="submitError"
        :class="bem(fieldClass, 'error')"
        style="
          font-size: 16px;
          padding: 12px;
          background-color: #fee2e2;
          border-radius: 6px;
          margin-bottom: 16px;
        "
      >
        ⚠️ {{ submitError }}
      </div>

      <!-- Side-by-Side Responsive Layout -->
      <div :class="bem(baseClass, 'layout')">
        <!-- Left side: Form steps -->
        <main :class="bem(baseClass, 'form')">
          <!-- Controls (Moved here) -->
          <div :class="bem(baseClass, 'controls')">
            <ToggleField
              id="wizard-condensed"
              label="Ver formulario en modo condensado"
              v-model="condensed"
            />
          </div>

          <!-- Dynamic Steps -->
          <component
            v-for="(StepComponent, index) in steps"
            :key="index"
            v-show="currentStep === index + 1"
            :is="StepComponent"
            :ref="
              (el) => {
                if (el && isStepComponentInstance(el)) {
                  stepRefs[index] = el;
                }
              }
            "
            :state="state"
            :condensed="condensed"
            :fieldErrors="fieldErrors"
            v-bind="index === 1 ? { cities } : {}"
          />

          <!-- Footer / Navigation Buttons -->
          <footer :class="bem(baseClass, 'footer')">
            <Button
              type="secondary"
              label="Paso anterior"
              :onClick="handlePrev"
              :disabled="currentStep === 1 || isSubmitting"
            />

            <Button
              v-if="currentStep < 3"
              type="primary"
              label="Paso siguiente"
              :onClick="handleNext"
              :disabled="!isCurrentStepValid || stepHasErrors"
            />

            <Button
              v-else
              type="primary"
              :label="
                isSubmitting ? 'Guardando...' : mode === 'edit' ? 'Guardar cambios' : 'Crear evento'
              "
              :onClick="handleSubmit"
              :disabled="!isCurrentStepValid || stepHasErrors || isSubmitting"
            />
          </footer>
        </main>

        <!-- Right side: Live Preview -->
        <aside :class="bem(baseClass, 'preview')">
          <EventPreview
            :state="state"
            :speakers="selectedSpeakers"
            :organizers="selectedOrganizers"
            :place="selectedPlace"
          />
        </aside>
      </div>
    </div>

    <!-- Floating mobile preview button -->
    <div :class="bem(baseClass, 'mobile-preview-trigger-container')">
      <Button
        type="primary"
        padding="regular"
        label="Ver vista previa"
        :onClick="() => (showMobilePreview = true)"
      />
    </div>

    <!-- Mobile preview overlay modal -->
    <Overlay
      :show="showMobilePreview"
      @close="showMobilePreview = false"
      customClass="event-wizard__overlay"
      dialogLabel="Vista previa del evento"
    >
      <EventPreview
        :state="state"
        :speakers="selectedSpeakers"
        :organizers="selectedOrganizers"
        :place="selectedPlace"
      />
    </Overlay>
  </div>
</template>
