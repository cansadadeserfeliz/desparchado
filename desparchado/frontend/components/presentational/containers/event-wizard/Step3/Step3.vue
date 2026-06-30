<script lang="ts" setup>
  import { computed } from 'vue';
  import { IWizardState } from '../../../../../scripts/api/interfaces';
  import { bem } from '../../../../../scripts/utils/bem';

  const props = defineProps<{
    state: IWizardState;
    condensed: boolean;
    fieldErrors?: Record<string, string[]>;
  }>();
  props;

  const baseClass = 'event-wizard';
  const fieldClass = 'wizard-field';
  const formGroupClass = 'form-group';

  const isValid = computed(() => {
    return true;
  });

  defineExpose({
    isValid,
  });
</script>

<template>
  <div :class="bem(baseClass, 'step-content')">
    <!-- Category Group -->
    <div :class="bem(fieldClass)">
      <div :class="bem(fieldClass, 'details')">
        <label :class="bem(fieldClass, 'headline')" for="wizard-category">Categoría</label>
        <p :class="bem(fieldClass, 'subheadline')">Elige la que mejor encaje</p>
        <p :class="bem(fieldClass, 'description')">
          Selecciona la categoría que mejor represente tu evento para facilitar que otros
          entusiastas lo encuentren. Así, llegarás a un público que comparte tus intereses y
          garantizarás una experiencia más significativa para todos.
        </p>
      </div>
      <select id="wizard-category" :class="bem(fieldClass, 'select')" v-model="state.category">
        <option value="literature">Literatura</option>
        <option value="art">Arte</option>
        <option value="society">Sociedad</option>
        <option value="science">Ciencia</option>
        <option value="environment">Medio Ambiente</option>
        <option value="other">Otro</option>
      </select>
      <div v-if="fieldErrors?.category" :class="bem(fieldClass, 'error')">
        {{ fieldErrors.category.join(', ') }}
      </div>
    </div>

    <!-- Price Group -->
    <div :class="bem(fieldClass)">
      <div :class="bem(fieldClass, 'details')">
        <label :class="bem(fieldClass, 'headline')" for="wizard-price"> Precio (COP) </label>
        <p :class="bem(fieldClass, 'subheadline')">Deja en $0 para gratuito</p>
      </div>
      <input
        id="wizard-price"
        type="number"
        min="0"
        :class="bem(fieldClass, 'input')"
        v-model="state.price"
      />
      <div v-if="fieldErrors?.price" :class="bem(fieldClass, 'error')">
        {{ fieldErrors.price.join(', ') }}
      </div>
    </div>

    <!-- Event Source URL Group -->
    <div :class="bem(fieldClass)">
      <div :class="bem(fieldClass, 'details')">
        <label :class="bem(fieldClass, 'headline')" for="wizard-source-url">
          Enlace del evento (URL) *
        </label>
      </div>
      <input
        id="wizard-source-url"
        type="url"
        :class="bem(fieldClass, 'input')"
        v-model="state.eventSourceUrl"
        placeholder="https://ejemplo.com/evento"
        required
      />
      <div v-if="fieldErrors?.event_source_url" :class="bem(fieldClass, 'error')">
        {{ fieldErrors.event_source_url.join(', ') }}
      </div>
    </div>

    <!-- Is Published Group -->
    <div :class="bem(fieldClass)" style="flex-direction: row; align-items: center; gap: 8px">
      <input
        id="wizard-published"
        type="checkbox"
        v-model="state.isPublished"
        style="width: auto; cursor: pointer"
      />
      <label
        :class="bem(formGroupClass, 'label')"
        for="wizard-published"
        style="cursor: pointer; margin: 0"
      >
        Publicar evento inmediatamente
      </label>
      <div v-if="fieldErrors?.is_published" :class="bem(formGroupClass, 'error')">
        {{ fieldErrors.is_published.join(', ') }}
      </div>
    </div>
  </div>
</template>
