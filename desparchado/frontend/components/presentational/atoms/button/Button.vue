<template>
  <component :is="link ? 'a' : 'button'" :href="link" :class="classes">
    <slot name="icon" :class="bem('icon')"></slot>
    <Typography
      tag="span"
      v-if="label"
      :customClass="bem('label')"
      type="body_highlight"
      weight="medium"
      :text="label"
    />
    <div v-if="label" :class="bem('hover-feature')" role="presentation" aria-hidden="true"></div>
  </component>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import Typography from '@presentational_components/foundation/typography/Typography.vue';
  import './styles.scss';

  type ButtonType = 'primary' | 'secondary' | 'tertiary';
  type ButtonPadding = 'condensed' | 'balanced' | 'regular';

  const baseClass = 'button';

  const types: Record<ButtonType, string> = {
    primary: `${baseClass}--type-primary`,
    secondary: `${baseClass}--type-secondary`,
    tertiary: `${baseClass}--type-tertiary`,
  };

  const paddings: Record<ButtonPadding, string> = {
    condensed: `${baseClass}--padding-condensed`,
    balanced: `${baseClass}--padding-balanced`,
    regular: `${baseClass}--padding-regular`,
  };

  const props = withDefaults(
    defineProps<{
      label?: string;
      type: ButtonType;
      padding?: ButtonPadding;
      customClass?: string;
      link?: string;
    }>(),
    {
      padding: 'regular',
    },
  );

  const bem = (suffix?: string) => (suffix ? `${baseClass}__${suffix}` : baseClass);
  const classes = computed(() =>
    [bem(), types[props.type], paddings[props.padding], props.customClass]
      .filter(Boolean)
      .join(' '),
  );
</script>
