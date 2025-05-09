<template>
  <component :is="link ? 'a' : 'button'" :href="link" :class="classes" @click="handleClick">
    <div :class="bem('content')">
      <slot name="icon" :class="bem('icon')"></slot>
      <Typography
        v-if="label"
        tag="span"
        type="body_highlight"
        weight="medium"
        :customClass="bem('label')"
        :text="label"
      />
      <div v-if="label" :class="bem('hover-feature')" role="presentation" aria-hidden="true"></div>
    </div>
  </component>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import Typography from '@presentational_components/foundation/typography/Typography.vue';
  import './styles.scss';

  type ButtonType = 'primary' | 'secondary' | 'tertiary';
  type ButtonPadding = 'condensed' | 'balanced' | 'regular';
  type ButtonRadius = 'squared' | 'soft' | 'circular';

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

  const radiuses: Record<ButtonRadius, string> = {
    squared: `${baseClass}--radius-squared`,
    soft: `${baseClass}--radius-soft`,
    circular: `${baseClass}--radius-circular`,
  };

  const props = withDefaults(
    defineProps<{
      label?: string;
      type: ButtonType;
      padding?: ButtonPadding;
      radius?: ButtonRadius;
      customClass?: string;
      link?: string;
      onClick?: () => void;
    }>(),
    {
      padding: 'regular',
      radius: 'circular',
    },
  );

  const bem = (suffix?: string) => (suffix ? `${baseClass}__${suffix}` : baseClass);
  const classes = computed(() =>
    [bem(), types[props.type], paddings[props.padding], radiuses[props.radius], props.customClass]
      .filter(Boolean)
      .join(' '),
  );

  const handleClick = () => {
    if (props.onClick) {
      props.onClick();
    }
  };
</script>
