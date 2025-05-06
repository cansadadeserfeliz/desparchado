<template>
  <svg :class="classes">
    <use :xlink:href="`${siteSvgs}#${types[props.type]}`"></use>
  </svg>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import siteSvgs from '@assets/logo.svg';

  type LogoType = 'isotype' | 'imagotype' | 'isologo';

  const types: Record<LogoType, string> = {
    isotype: 'logo-isotype',
    imagotype: 'logo-imagotype',
    isologo: 'logo-isologo',
  };

  // Props
  const props = withDefaults(
    defineProps<{
      customClass?: string;
      type?: LogoType;
    }>(),
    {
      type: 'isotype',
    },
  );

  const classes = computed(() => [props.customClass].filter(Boolean).join(' '));
</script>
