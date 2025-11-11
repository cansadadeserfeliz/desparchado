<template>
  <component
    :is="link ? 'a' : 'button'"
    :href="link"
    :target="link && props.target ? props.target : undefined"
    :rel="link && props.target === '_blank' ? 'noopener noreferrer' : undefined"
    :type="link ? undefined : isActionSubmit ? 'submit' : ''"
    :aria-label="!props.label && props.name ? props.name : undefined"
    :class="[
      bem(baseClass),
      types[props.type],
      paddings[props.padding],
      radiuses[props.radius],
      props.customClass,
    ]"
    :style="props.name && `--button-name: '${props.name}'`"
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
      <Icon v-if="props.icon" :id="props.icon" size="regular" />
      <Typography
        v-if="props.label"
        tag="span"
        type="body_highlight"
        weight="medium"
        :customClass="bem(baseClass, 'label')"
        :text="props.label"
      />
      <div
        v-if="props.label"
        :class="bem(baseClass, 'hover-feature')"
        role="presentation"
        aria-hidden="true"
      ></div>
    </div>
  </component>
</template>

<script lang="ts" setup>
  import Typography from '@presentational_components/foundation/typography/Typography.vue';
  import Icon from '@presentational_components/foundation/icon/Icon.vue';
  import './styles.scss';
  import { bem } from '../../../../scripts/utils/bem';

  type ButtonType = 'primary' | 'secondary' | 'tertiary';
  type ButtonPadding = 'balanced-sm' | 'condensed' | 'balanced' | 'regular';
  type ButtonRadius = 'squared' | 'soft' | 'circular';

  const baseClass = 'button';

  const types: Record<ButtonType, string> = {
    primary: `${baseClass}--type-primary`,
    secondary: `${baseClass}--type-secondary`,
    tertiary: `${baseClass}--type-tertiary`,
  };

  const paddings: Record<ButtonPadding, string> = {
    'balanced-sm': `${baseClass}--padding-balanced-sm`,
    condensed: `${baseClass}--padding-condensed`,
    balanced: `${baseClass}--padding-balanced`,
    regular: `${baseClass}--padding-regular`,
  };

  const radiuses: Record<ButtonRadius, string> = {
    squared: `${baseClass}--radius-squared`,
    soft: `${baseClass}--radius-soft`,
    circular: `${baseClass}--radius-circular`,
  };

  export interface ButtonProps {
    label?: string; // text shown on the button
    name?: string; // labeled name of the button, use when label cannot be provided
    icon?: string;
    type: ButtonType;
    padding?: ButtonPadding;
    radius?: ButtonRadius;
    customClass?: string;
    link?: string;
    target?: '_blank' | '_self' | '_parent' | '_top';
    onClick?: () => void;
    actionId?: string;
    isActionSubmit?: boolean;
  }

  const props = withDefaults(defineProps<ButtonProps>(), {
    padding: 'regular',
    radius: 'circular',
  });

  const handleClick = (event: MouseEvent) => {
    if (!props.link && props.actionId) {
      const customEvent = new CustomEvent(`button:action:${props.actionId}`, {
        detail: { event, props },
      });
      window.dispatchEvent(customEvent);
    }

    if (props.onClick) {
      props.onClick();
    }
  };
</script>
