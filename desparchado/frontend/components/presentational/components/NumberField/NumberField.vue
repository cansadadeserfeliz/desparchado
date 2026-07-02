<template>
  <div :class="[bem(baseClass), customClass]">
    <label
      v-if="label"
      :class="[bem(baseClass, 'headline'), hideLabel ? 'visually-hidden' : '']"
      :for="id"
    >
      {{ label }}<span v-if="required">, *</span>
    </label>
    <div :class="bem(baseClass, 'input-container')">
      <input
        :id="id"
        type="number"
        :min="min"
        :class="bem(baseClass, 'input')"
        :value="modelValue"
        @input="handleInput"
        @blur="handleBlur"
        :placeholder="placeholder"
        :required="required"
        :aria-invalid="displayError ? 'true' : 'false'"
        :aria-describedby="displayError ? `${id}-error` : undefined"
      />
      <span v-if="unit" :class="bem(baseClass, 'unit')">{{ unit }}</span>
    </div>
    <div v-if="displayError" :id="`${id}-error`" :class="bem(baseClass, 'error')">
      {{ displayError }}
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { ref, computed, watch } from 'vue';
  import { bem } from '../../../../scripts/utils/bem';
  import './styles.scss';

  export interface NumberFieldProps {
    modelValue: string | number;
    id: string;
    label?: string;
    hideLabel?: boolean;
    customClass?: string;
    placeholder?: string;
    required?: boolean;
    min?: number | string;
    unit?: string;
    errors?: string[] | string;
  }

  const props = withDefaults(defineProps<NumberFieldProps>(), {
    required: false,
    modelValue: '',
    hideLabel: false,
    customClass: '',
  });

  const emit = defineEmits(['update:modelValue', 'blur', 'error']);

  const baseClass = 'number-field';
  const localError = ref('');

  watch(localError, (val) => {
    emit('error', val);
  });

  const handleInput = (event: Event) => {
    if (!(event.target instanceof HTMLInputElement)) return;
    const val = event.target.value;
    if (val !== '') {
      localError.value = '';
    }
    emit('update:modelValue', val);
  };

  const handleBlur = (event: FocusEvent) => {
    emit('blur', event);
    const input = event.target as HTMLInputElement;
    if (!input) return;

    const valStr = input.value;
    if (valStr !== '') {
      const valNum = parseFloat(valStr);
      if (props.min !== undefined && Number(props.min) >= 0 && valNum < 0) {
        localError.value = '';
        input.value = '0';
        emit('update:modelValue', '0');
        return;
      }
    }

    if (!input.validity.valid) {
      localError.value = 'Valor no válido';
      return;
    }

    if (valStr === '') {
      localError.value = props.required ? 'Este campo es requerido' : '';
      return;
    }

    localError.value = '';
  };

  watch(
    () => props.modelValue,
    () => {
      localError.value = '';
    },
  );

  const displayError = computed(() => {
    if (!props.errors) {
      return localError.value;
    }
    if (Array.isArray(props.errors)) {
      return props.errors.join(', ');
    }
    return props.errors;
  });
</script>
