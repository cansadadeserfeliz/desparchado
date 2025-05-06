<template>
  <component :is="link ? 'a' : 'button'" :href="link" :class="classes">
    <Typography
      tag="span"
      type="nav_item"
      weight="medium"
      :text="label"
      :customClass="bem('label')"
    />
  </component>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import Typography from '@presentational_components/foundation/typography/Typography.vue';
  import './styles.scss';

  const baseClass = 'nav-item';

  const props = defineProps<{
    label: string;
    customClass?: string;
    active?: boolean;
    link?: string;
  }>();

  const bem = (suffix?: string) => (suffix ? `${baseClass}__${suffix}` : baseClass);
  const classes = computed(() =>
    [bem(), props.customClass, props.active && `${baseClass}--active`].filter(Boolean).join(' '),
  );
</script>
