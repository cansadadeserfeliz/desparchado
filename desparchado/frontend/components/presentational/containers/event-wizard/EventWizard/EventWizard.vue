<script lang="ts" setup>
  import { computed } from 'vue';
  import { bem } from '../../../../../scripts/utils/bem';
  import { IEventDetailResponse, IEntityOption } from '../../../../../scripts/api/interfaces';
  import Step1 from '../Step1/Step1.vue';
  import Step2 from '../Step2/Step2.vue';
  import Step3 from '../Step3/Step3.vue';
  import EventPreview from '../EventPreview/EventPreview.vue';
  import Overlay from '@presentational_components/components/Overlay/Overlay.vue';
  import Button from '@presentational_components/atoms/button/Button.vue';
  import ToggleField from '@presentational_components/components/ToggleField/ToggleField.vue';
  import { useEventWizard } from './useEventWizard';
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

  const {
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
    isCurrentStepValid,
    stepHasErrors,
    handlePrev,
    handleNext,
    handleSubmit,
  } = useEventWizard(props);

  const steps = computed(() => [
    {
      component: Step1,
      props: {},
      on: {
        'update:selected-organizers': (opts: IEntityOption[]) => {
          selectedOrganizers.value = opts;
        },
        'update:selected-speakers': (opts: IEntityOption[]) => {
          selectedSpeakers.value = opts;
        },
      },
    },
    {
      component: Step2,
      props: { cities: props.cities },
      on: {
        'update:selected-place': (place: { id: number; name: string } | null) => {
          selectedPlace.value = place;
        },
      },
    },
    {
      component: Step3,
      props: {},
      on: {},
    },
  ]);
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
            v-for="(stepConfig, index) in steps"
            :key="index"
            v-show="currentStep === index + 1"
            :is="stepConfig.component"
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
            v-bind="stepConfig.props"
            v-on="stepConfig.on"
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

    <!-- Submitting overlay -->
    <Overlay
      :show="isSubmitting"
      loading
      loadingText="Guardando evento..."
      dialogLabel="Guardando cambios"
    />
  </div>
</template>
