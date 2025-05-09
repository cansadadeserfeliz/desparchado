<template>
  <component
    :is="link ? 'a' : 'button'"
    :href="link"
    :class="[
      bem(baseClass),
      types[props.type],
      paddings[props.padding],
      radiuses[props.radius],
      props.customClass,
    ]"
    @click="handleClick"
  >
    <div
      :class="[
        bem(baseClass, 'content'),
        types[props.type],
        paddings[props.padding],
        radiuses[props.radius],
        props.customClass,
      ]"
    >
      <slot name="icon" :class="bem(baseClass, 'icon')"></slot>
      <Typography
        v-if="label"
        tag="span"
        type="body_highlight"
        weight="medium"
        :customClass="bem(baseClass, 'label')"
        :text="label"
      />
      <div
        v-if="label"
        :class="bem(baseClass, 'hover-feature')"
        role="presentation"
        aria-hidden="true"
      ></div>
    </div>
  </component>
</template>

<script lang="ts" setup>
  import Typography from '@presentational_components/foundation/typography/Typography.vue';
  import './styles.scss';
  import { bem } from '../../../../scripts/utils/bem';

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

  const handleClick = () => {
    if (props.onClick) {
      props.onClick();
    }
  };
</script>
