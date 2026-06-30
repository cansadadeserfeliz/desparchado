<script lang="ts" setup>
  import { computed } from 'vue';
  import { IWizardState } from '../../../../../scripts/api/interfaces';
  import { bem } from '../../../../../scripts/utils/bem';

  const props = defineProps<{
    state: IWizardState;
    condensed: boolean;
    cities: { id: number; name: string }[];
    fieldErrors?: Record<string, string[]>;
  }>();
  props;

  const baseClass = 'event-wizard';
  const fieldClass = 'wizard-field';

  const isValid = computed(() => {
    return true;
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
      <input
        id="wizard-date"
        type="datetime-local"
        :class="bem(fieldClass, 'input')"
        v-model="state.eventDate"
        required
      />
      <div v-if="fieldErrors?.event_date" :class="bem(fieldClass, 'error')">
        {{ fieldErrors.event_date.join(', ') }}
      </div>
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
      <div v-if="fieldErrors?.place" :class="bem(fieldClass, 'error')">
        {{ fieldErrors.place.join(', ') }}
      </div>
    </div>
  </div>
</template>
