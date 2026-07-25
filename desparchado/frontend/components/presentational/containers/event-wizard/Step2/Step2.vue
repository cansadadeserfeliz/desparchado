<script lang="ts" setup>
  import { computed, reactive } from 'vue';
  import { IWizardState, IEntityOption } from '../../../../../scripts/api/interfaces';
  import { bem } from '../../../../../scripts/utils/bem';
  import TimeField from '@presentational_components/components/TimeField/TimeField.vue';
  import SearchableCombobox from '@presentational_components/components/SearchableCombobox/SearchableCombobox.vue';

  const props = defineProps<{
    state: IWizardState;
    condensed: boolean;
    cities: { id: number; name: string }[];
    initialPlace?: IEntityOption[];
    fieldErrors?: Record<string, string[]>;
  }>();

  const emit = defineEmits<{
    'create-place': [];
    'update:selected-place': [place: { id: number; name: string } | null];
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
    const placeValid = typeof props.state.placeId === 'number' && props.state.placeId > 0;
    return !!props.state.eventDate && placeValid;
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
        <label :class="bem(fieldClass, 'headline')">Lugar, *</label>
        <p :class="bem(fieldClass, 'subheadline')">¿Dónde se va a hacer?</p>
        <p :class="bem(fieldClass, 'description')">
          Indica en donde se va a realizar el evento, búscalo en la lista de lugares, si no lo
          encuentras crea uno nuevo
        </p>
      </div>
      <SearchableCombobox
        id="wizard-place"
        label="Lugar"
        :hideLabel="true"
        placeholder="Buscar lugar por nombre..."
        emptyChipsText="No se ha seleccionado un lugar"
        searchUrl="/places/api/v1/places/search/"
        v-model="state.placeId"
        :initialOptions="initialPlace"
        :multiple="false"
        :required="true"
        :errors="fieldErrors?.place_id"
        @error="(msg) => handleFieldError('place_id', msg)"
        @create-new="emit('create-place')"
        @update:selected-options="(opts) => emit('update:selected-place', opts[0] || null)"
      />
    </div>
  </div>
</template>
