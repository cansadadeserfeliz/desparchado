<template>
  <header :class="bem(baseClass)">
    <div :class="bem(baseClass, 'wrapper')">
      <Typography tag="span" :customClass="bem(baseClass, 'location')" type="caption" text="text" />
    </div>
  </header>
</template>

<script lang="ts" setup>
  import Typography from '@presentational_components/foundation/typography/Typography.vue';
  import './styles.scss';
  import { bem } from '../../../../scripts/utils/bem';

  // -------- [Props] --------
  const baseClass = 'featured-event-card';
</script>
