<template>
  <component :is="tag" :class="classes" :id="id">
    {{ text }}
  </component>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';

  // -------- [Types] --------
  type HeadingTags = 'span' | 'p' | 'h1' | 'h2' | 'h3' | 'h4' | 'h5';
  type HeadingTypes =
    | 'body_sm'
    | 'body_md'
    | 'body_lg'
    | 'body_highlight'
    | 'caption'
    | 'header_item'
    | 'h1'
    | 'h2'
    | 'h3'
    | 'h4'
    | 'h5'
    | 's1';
  type WeightValues = 'regular' | 'medium' | 'bold';

  const weights: Record<WeightValues, string> = {
    regular: 'text-regular',
    medium: 'text-medium',
    bold: 'text-bold',
  };

  const types: Record<HeadingTypes, string> = {
    body_sm: 'text-body-sm',
    body_md: 'text-body-md',
    body_lg: 'text-body-lg',
    body_highlight: 'text-body-highlight',
    caption: 'text-caption',
    header_item: 'text-header-item',
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
      tag?: HeadingTags;
      type?: HeadingTypes;
      weight?: WeightValues;
      text: string;
      id?: string;
      customClass?: string;
    }>(),
    {
      tag: 'p',
      type: 'body_md',
      weight: 'regular',
    },
  );
  const tag = props.tag;

  const classes = computed(() =>
    [types[props.type], weights[props.weight], props.customClass].filter(Boolean).join(' '),
  );
</script>
