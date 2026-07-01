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
      type="text"
      :class="bem(baseClass, 'input')"
      :value="modelValue"
      @input="handleInput"
      :placeholder="placeholder"
      :required="required"
      :aria-invalid="formattedErrors ? 'true' : 'false'"
      :aria-describedby="formattedErrors ? `${id}-error` : undefined"
    />
    <div v-if="formattedErrors" :id="`${id}-error`" :class="bem(baseClass, 'error')">
      {{ formattedErrors }}
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import { bem } from '../../../../scripts/utils/bem';
  import './styles.scss';

  export interface TextFieldProps {
    modelValue: string;
    id: string;
    label?: string;
    hideLabel?: boolean;
    customClass?: string;
    placeholder?: string;
    required?: boolean;
    errors?: string[] | string;
  }

  const props = withDefaults(defineProps<TextFieldProps>(), {
    required: false,
    modelValue: '',
    hideLabel: false,
    customClass: '',
  });

  const emit = defineEmits(['update:modelValue']);

  const baseClass = 'text-field';

  const handleInput = (event: Event) => {
    if (event.target instanceof HTMLInputElement) {
      emit('update:modelValue', event.target.value);
    }
  };

  const formattedErrors = computed(() => {
    if (!props.errors) return '';
    if (Array.isArray(props.errors)) {
      return props.errors.join(', ');
    }
    return props.errors;
  });
</script>
