<script lang="ts" setup>
  import { computed, reactive } from 'vue';
  import { IWizardState } from '../../../../../scripts/api/interfaces';
  import { bem } from '../../../../../scripts/utils/bem';
  import TimeField from '@presentational_components/components/TimeField/TimeField.vue';

  const props = defineProps<{
    state: IWizardState;
    condensed: boolean;
    cities: { id: number; name: string }[];
    fieldErrors?: Record<string, string[]>;
  }>();

  const baseClass = 'event-wizard';
  const fieldClass = 'wizard-field';

  const localErrors = reactive<Record<string, string>>({});
  const handleFieldError = (field: string, errorMsg: string) => {
    if (!errorMsg) {
      delete localErrors[field];
      return;
    }
    localErrors[field] = errorMsg;
  };
  const hasLocalErrors = computed(() => Object.keys(localErrors).length > 0);

  const isValid = computed(() => {
    if (hasLocalErrors.value) return false;
    return !!props.state.eventDate && !!props.state.placeId;
  });

  defineExpose({
    isValid,
  });
</script>

<template>
  <div :class="bem(baseClass, 'step-content')">
    <!-- Date Group -->
    <div :class="bem(fieldClass)">
      <div :class="bem(fieldClass, 'details')">
        <label :class="bem(fieldClass, 'headline')" for="wizard-date">Fecha y Hora *</label>
        <p :class="bem(fieldClass, 'subheadline')">¿Cuándo se va a realizar el evento?</p>
        <p :class="bem(fieldClass, 'description')">
          Selecciona la fecha en las que se va a realizar el evento.
        </p>
      </div>
      <TimeField
        id="wizard-date"
        label="Fecha y Hora"
        :hideLabel="true"
        customClass="wizard-field"
        v-model="state.eventDate"
        required
        :errors="fieldErrors?.event_date"
        @error="(msg) => handleFieldError('event_date', msg)"
      />
    </div>

    <!-- Place Group -->
    <div :class="bem(fieldClass)">
      <div :class="bem(fieldClass, 'details')">
        <span :class="bem(fieldClass, 'headline')">Lugar (Próximamente mapa y combobox)</span>
        <p :class="bem(fieldClass, 'subheadline')">¿Dónde se va a hacer?</p>
        <p :class="bem(fieldClass, 'description')">
          Indica en donde se va a realizar el evento, búscalo en la lista de lugares, si no lo
          encuentras crea uno nuevo
        </p>
      </div>
      <div v-if="fieldErrors?.place_id" :class="bem(fieldClass, 'error')">
        {{ fieldErrors.place_id.join(', ') }}
      </div>
    </div>
  </div>
</template>
