<template>
  <div v-html="sprite" style="display: none" aria-hidden="true"></div>
  <svg :class="classes">
    <use :xlink:href="`#${props.id}`" />
  </svg>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import siteSvgs from '@assets/icons.svg?raw';

  const spriteContent = siteSvgs;
  const sprite = computed(() => spriteContent);

  type IconSizeType = 'unset' | 'small' | 'regular' | 'large';

  const sizes: Record<IconSizeType, string> = {
    unset: '',
    small: 'icon--small',
    regular: 'icon--regular',
    large: 'icon--large',
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

  .icon--large {
    height: 40px;
    width: 40px;
  }
</style>
