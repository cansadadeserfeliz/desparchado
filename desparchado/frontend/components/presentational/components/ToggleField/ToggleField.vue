<template>
  <div :class="[bem(baseClass), customClass]">
    <label :class="bem(baseClass, 'label')" :for="id">
      <input
        :id="id"
        type="checkbox"
        :class="[bem(baseClass, 'input'), 'visually-hidden']"
        :checked="modelValue"
        @change="handleChange"
        @blur="handleBlur"
      />
      <span :class="bem(baseClass, 'switch')"></span>
      <span v-if="label" :class="bem(baseClass, 'text')">{{ label }}</span>
    </label>
  </div>
</template>

<script lang="ts" setup>
  import { bem } from '../../../../scripts/utils/bem';
  import './styles.scss';

  export interface ToggleFieldProps {
    modelValue: boolean;
    id: string;
    label?: string;
    customClass?: string;
  }

  withDefaults(defineProps<ToggleFieldProps>(), {
    modelValue: false,
    customClass: '',
  });

  const emit = defineEmits(['update:modelValue', 'blur']);

  const baseClass = 'toggle-field';

  const handleChange = (event: Event) => {
    if (!(event.target instanceof HTMLInputElement)) return;
    emit('update:modelValue', event.target.checked);
  };

  const handleBlur = (event: FocusEvent) => {
    emit('blur', event);
  };
</script>
