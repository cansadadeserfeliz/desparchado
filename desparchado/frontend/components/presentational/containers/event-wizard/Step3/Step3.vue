<script lang="ts" setup>
  import { ref, computed, watch, reactive } from 'vue';
  import { IWizardState } from '../../../../../scripts/api/interfaces';
  import { bem } from '../../../../../scripts/utils/bem';
  import TextField from '@presentational_components/components/TextField/TextField.vue';
  import NumberField from '@presentational_components/components/NumberField/NumberField.vue';
  import ToggleField from '@presentational_components/components/ToggleField/ToggleField.vue';
  import RadioCategoryField, {
    ChoiceOption,
  } from '@presentational_components/components/RadioCategoryField/RadioCategoryField.vue';

  const props = defineProps<{
    state: IWizardState;
    condensed: boolean;
    fieldErrors?: Record<string, string[]>;
  }>();

  const categoryChoices: ChoiceOption[] = [
    {
      value: 'literature',
      label: 'Literatura',
      description: 'Libros, lecturas, poesía, charlas literarias y clubes de lectura.',
      icon: 'book',
    },
    {
      value: 'art',
      label: 'Arte',
      description: 'Pintura, teatro, exposiciones, danza y talleres creativos.',
      icon: 'pencil',
    },
    {
      value: 'society',
      label: 'Sociedad',
      description: 'Debates, encuentros ciudadanos, ferias y causas comunitarias.',
      icon: 'codesandbox',
    },
    {
      value: 'science',
      label: 'Ciencia',
      description: 'Tecnología, astronomía, divulgación y conferencias científicas.',
      icon: 'loader',
    },
    {
      value: 'environment',
      label: 'Medio Ambiente',
      description: 'Sostenibilidad, ecología, jornadas de siembra y cuidado natural.',
      icon: 'feather',
    },
    {
      value: 'other',
      label: 'Otro',
      description: 'Cualquier evento que escape de las categorías tradicionales.',
      icon: 'ghost',
    },
  ];

  const baseClass = 'event-wizard';
  const fieldClass = 'wizard-field';
  const formGroupClass = 'form-group';

  const urlError = ref('');

  const isValidUrl = (val: string): boolean => {
    if (!val) return false;
    try {
      const url = new URL(val.trim());
      return url.protocol === 'http:' || url.protocol === 'https:';
    } catch {
      return false;
    }
  };

  const handleUrlBlur = () => {
    if (!props.state.eventSourceUrl) {
      urlError.value = 'Este campo es requerido';
      return;
    }
    if (!isValidUrl(props.state.eventSourceUrl)) {
      urlError.value = 'Formato de URL no válido';
      return;
    }
    urlError.value = '';
  };

  watch(
    () => props.state.eventSourceUrl,
    (newVal) => {
      if (!newVal) return;
      if (!isValidUrl(newVal)) return;
      urlError.value = '';
    },
  );

  const combinedUrlErrors = computed(() => {
    if (urlError.value) {
      return urlError.value;
    }
    return props.fieldErrors?.event_source_url || '';
  });

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
    if (urlError.value) return false;
    if (hasLocalErrors.value) return false;
    return isValidUrl(props.state.eventSourceUrl);
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
      <RadioCategoryField
        id="wizard-category"
        v-model="state.category"
        :choices="categoryChoices"
        :condensed="condensed"
      />
      <div v-if="fieldErrors?.category" :class="bem(fieldClass, 'error')">
        {{ fieldErrors.category.join(', ') }}
      </div>
    </div>

    <!-- Price Group -->
    <div :class="bem(fieldClass)">
      <div :class="bem(fieldClass, 'details')">
        <label :class="bem(fieldClass, 'headline')" for="wizard-price"> Precio </label>
        <p :class="bem(fieldClass, 'subheadline')">Deja en $0 para gratuito</p>
        <p :class="bem(fieldClass, 'description')">
          Indica el costo de ingreso. Si el evento es libre y sin costo, déjalo en cero. La moneda
          base se calcula en Pesos Colombianos.
        </p>
      </div>
      <NumberField
        id="wizard-price"
        v-model="state.price"
        min="0"
        placeholder="0"
        unit="COP"
        :errors="fieldErrors?.price"
        @error="(msg) => handleFieldError('price', msg)"
      />
    </div>

    <!-- Event Source URL Group -->
    <div :class="bem(fieldClass)">
      <div :class="bem(fieldClass, 'details')">
        <label :class="bem(fieldClass, 'headline')" for="wizard-source-url">
          Enlace del evento *
        </label>
        <p :class="bem(fieldClass, 'subheadline')">
          Ingresa una dirección web válida (ej. https://...)
        </p>
        <p :class="bem(fieldClass, 'description')">
          Proporcionar un enlace permite a los asistentes consultar la fuente oficial, obtener más
          detalles, comprar entradas directamente o confirmar su asistencia.
        </p>
      </div>
      <TextField
        id="wizard-source-url"
        type="url"
        v-model="state.eventSourceUrl"
        placeholder="https://ejemplo.com/evento"
        required
        @blur="handleUrlBlur"
        :errors="combinedUrlErrors"
      />
    </div>

    <!-- Is Published Group -->
    <div :class="bem(fieldClass)" style="flex-direction: row; align-items: center; gap: 8px">
      <ToggleField
        id="wizard-published"
        label="Publicar evento inmediatamente"
        v-model="state.isPublished"
      />
      <div v-if="fieldErrors?.is_published" :class="bem(formGroupClass, 'error')">
        {{ fieldErrors.is_published.join(', ') }}
      </div>
    </div>
  </div>
</template>
