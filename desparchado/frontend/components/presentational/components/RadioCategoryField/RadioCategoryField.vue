<template>
  <div :class="[bem(baseClass), props.condensed ? `${baseClass}--condensed` : '', customClass]">
    <div :class="bem(baseClass, 'grid')">
      <label
        v-for="choice in props.choices"
        :key="choice.value"
        :class="[
          bem(baseClass, 'card'),
          modelValue === choice.value ? bem(baseClass, 'card', 'selected') : '',
        ]"
        :for="`${id}-${choice.value}`"
      >
        <input
          type="radio"
          :id="`${id}-${choice.value}`"
          :name="id"
          :value="choice.value"
          :checked="modelValue === choice.value"
          @click="handleClick(choice.value)"
          :class="[bem(baseClass, 'radio-input'), 'visually-hidden']"
        />
        <div :class="bem(baseClass, 'card-content')">
          <div :class="bem(baseClass, 'card-header')">
            <span :class="bem(baseClass, 'card-label')">{{ choice.label }}</span>
            <div :class="bem(baseClass, 'icon-wrapper')">
              <Icon :id="choice.icon" size="regular" />
            </div>
          </div>
          <div v-if="!props.condensed" :class="bem(baseClass, 'card-body')">
            <span :class="bem(baseClass, 'card-description')">{{ choice.description }}</span>
          </div>
        </div>
      </label>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { bem } from '../../../../scripts/utils/bem';
  import Icon from '../../foundation/icon/Icon.vue';
  import './styles.scss';

  export interface ChoiceOption {
    value: string;
    label: string;
    description: string;
    icon: string;
  }

  export interface RadioCategoryFieldProps {
    modelValue: string;
    id: string;
    choices: ChoiceOption[];
    customClass?: string;
    condensed?: boolean;
  }

  const props = withDefaults(defineProps<RadioCategoryFieldProps>(), {
    modelValue: 'other',
    customClass: '',
    condensed: false,
  });

  const emit = defineEmits(['update:modelValue']);

  const baseClass = 'radio-category-field';

  const handleClick = (value: string) => {
    if (props.modelValue === value) {
      emit('update:modelValue', 'other');
      return;
    }
    emit('update:modelValue', value);
  };
</script>
