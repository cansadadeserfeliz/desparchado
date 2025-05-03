<template>
  <svg :class="classes">
    <use :xlink:href="`${siteSvgs}#${props.id}`"></use>
  </svg>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import siteSvgs from '@assets/site.svg';

  type IconSizeType = 'unset' | 'small' | 'regular';

  const sizes: Record<IconSizeType, string> = {
    unset: '',
    small: 'icon--small',
    regular: 'icon--regular',
  };

  // Props
  const props = withDefaults(
    defineProps<{
      customClass?: string;
      id: string;
      size?: IconSizeType;
    }>(),
    {
      size: 'regular',
    },
  );

  const classes = computed(() => [props.customClass, sizes[props.size]].filter(Boolean).join(' '));
</script>

<style lang="scss" scoped>
  .icon--small {
    height: 20px;
    width: 20px;
  }

  .icon--regular {
    height: 24px;
    width: 24px;
  }
</style>
