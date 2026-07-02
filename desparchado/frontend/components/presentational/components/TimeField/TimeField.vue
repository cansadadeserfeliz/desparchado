<template>
  <div :class="[bem(baseClass), customClass]">
    <label
      v-if="label"
      :class="[bem(baseClass, 'headline'), hideLabel ? 'visually-hidden' : '']"
      :for="id"
    >
      {{ label }}<span v-if="required">, *</span>
    </label>
    <input
      :id="id"
      type="datetime-local"
      :class="bem(baseClass, 'input')"
      :value="localInputValue"
      @input="handleInput"
      @blur="handleBlur"
      :required="required"
      :aria-invalid="displayError ? 'true' : 'false'"
      :aria-describedby="displayError ? `${id}-error` : undefined"
    />
    <div v-if="displayError" :id="`${id}-error`" :class="bem(baseClass, 'error')">
      {{ displayError }}
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { ref, computed, watch } from 'vue';
  import { bem } from '../../../../scripts/utils/bem';
  import {
    toBogotaLocalDateTimeString,
    fromInputToBogotaIso,
  } from '../../../../scripts/utils/date';
  import './styles.scss';

  export interface TimeFieldProps {
    modelValue: string;
    id: string;
    label?: string;
    hideLabel?: boolean;
    customClass?: string;
    required?: boolean;
    errors?: string[] | string;
  }

  const props = withDefaults(defineProps<TimeFieldProps>(), {
    required: false,
    modelValue: '',
    hideLabel: false,
    customClass: '',
  });

  const emit = defineEmits(['update:modelValue', 'blur', 'error']);

  const baseClass = 'time-field';
  const localError = ref('');

  watch(localError, (val) => {
    emit('error', val);
  });

  const localInputValue = computed(() => toBogotaLocalDateTimeString(props.modelValue));

  const handleInput = (event: Event) => {
    if (!(event.target instanceof HTMLInputElement)) return;
    const val = event.target.value;
    if (val) {
      localError.value = '';
    }
    emit('update:modelValue', fromInputToBogotaIso(val));
  };

  const handleBlur = (event: FocusEvent) => {
    emit('blur', event);
    if (props.required && !props.modelValue) {
      localError.value = 'Este campo es requerido';
      return;
    }
    localError.value = '';
  };

  // Watch modelValue to clear localError if it changes externally
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
