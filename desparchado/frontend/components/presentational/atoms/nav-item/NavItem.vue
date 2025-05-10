<template>
  <component
    :is="link ? 'a' : 'button'"
    :href="link"
    :class="[
      bem(baseClass),
      props.customClass,
      props.active && bem(baseClass, '', 'active'),
      props.highlight && bem(baseClass, '', 'highlight'),
    ]"
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

  export interface NavItemProps {
    label: string;
    highlight?: boolean;
    customClass?: string;
    active?: boolean;
    link?: string;
  }
  const baseClass = 'nav-item';

  const props = defineProps<NavItemProps>();
</script>
