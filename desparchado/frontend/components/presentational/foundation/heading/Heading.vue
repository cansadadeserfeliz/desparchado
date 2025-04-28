<template>
  <component :is="tag" :class="classes" :id="id">
    {{ text }}
  </component>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';

  // -------- [Types] --------
  type HeadingTypes = 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 's1';
  type WeightValues = 'regular' | 'medium' | 'bold';

  const weights: Record<WeightValues, string> = {
    regular: 'text-regular',
    medium: 'text-medium',
    bold: 'text-bold',
  };

  const types: Record<HeadingTypes, string> = {
    h1: 'text-heading-1',
    h2: 'text-heading-2',
    h3: 'text-heading-3',
    h4: 'text-heading-4',
    h5: 'text-heading-5',
    s1: 'text-subtitle-1',
  };

  // -------- [Props] --------
  const props = withDefaults(
    defineProps<{
      tag?: HeadingTypes;
      type?: HeadingTypes;
      weight?: WeightValues;
      text: string;
      id: string;
      customClass?: string;
    }>(),
    {
      tag: 'h1',
      type: 'h1',
      weight: 'regular',
    },
  );
  const tag = props.tag;

  const classes = computed(() =>
    [types[props.type], weights[props.weight], props.customClass].filter(Boolean).join(' '),
  );
</script>
