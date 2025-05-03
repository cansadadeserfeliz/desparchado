<template>
  <component :is="link ? 'a' : 'button'" :href="link" :class="classes">
    <Typography
      tag="span"
      :customClass="bem('label')"
      type="body_highlight"
      weight="medium"
      :text="label"
    />
    <div :class="bem('hover-feature')" role="presentation" aria-hidden="true"></div>
  </component>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import Typography from '@presentational_components/foundation/typography/Typography.vue';
  import './styles.scss';

  type ButtonType = 'primary' | 'secondary' | 'tertiary';

  const baseClass = 'button';

  const types: Record<ButtonType, string> = {
    primary: `${baseClass}--primary`,
    secondary: `${baseClass}--secondary`,
    tertiary: `${baseClass}--tertiary`,
  };

  const props = withDefaults(
    defineProps<{
      label: string;
      type: ButtonType;
      condensed?: boolean;
      customClass?: string;
      link?: string;
    }>(),
    {
      condensed: false,
    },
  );

  const bem = (suffix?: string) => (suffix ? `${baseClass}__${suffix}` : baseClass);
  const classes = computed(() =>
    [bem(), types[props.type], props.customClass, props.condensed && `${baseClass}--condensed`]
      .filter(Boolean)
      .join(' '),
  );
</script>
