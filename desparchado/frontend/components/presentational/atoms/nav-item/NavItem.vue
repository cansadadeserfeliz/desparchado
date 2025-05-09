<template>
  <component
    :is="link ? 'a' : 'button'"
    :href="link"
    :class="[bem(baseClass), props.customClass, props.active && bem(baseClass, '', 'active')]"
  >
    <Typography
      tag="span"
      type="nav_item"
      weight="medium"
      :text="label"
      :customClass="bem(baseClass, 'label')"
    />
  </component>
</template>

<script lang="ts" setup>
  import Typography from '@presentational_components/foundation/typography/Typography.vue';
  import './styles.scss';
  import { bem } from '../../../../scripts/utils/bem';

  const baseClass = 'nav-item';

  const props = defineProps<{
    label: string;
    customClass?: string;
    active?: boolean;
    link?: string;
  }>();
</script>
