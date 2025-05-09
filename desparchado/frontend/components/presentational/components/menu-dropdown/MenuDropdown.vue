<template>
  <div :class="[bem(baseClass), isOpen && bem(baseClass, '', 'open')]" ref="wrapperRef">
    <Button
      type="primary"
      padding="balanced"
      :onClick="toggleMenu"
      ref="triggerRef"
      :custom-class="bem(baseClass, 'trigger')"
    >
      <template #icon>
        <Icon id="user" size="regular" />
      </template>
    </Button>

    <Transition name="slide-fade">
      <div
        v-if="isOpen"
        :class="[
          bem(baseClass, 'content'),
          bem(baseClass, 'content', contentPositionX),
          bem(baseClass, 'content', contentPositionY),
        ]"
        role="menu"
        :aria-label="props.ariaLabel || 'Dropdown Menu'"
      >
        <ul>
          <li v-for="(item, index) in items" :key="index" role="menuitem">
            <Button
              type="tertiary"
              padding="condensed"
              radius="squared"
              :label="item.label"
              :link="item.url"
              :custom-class="bem(baseClass, 'item')"
            ></Button>
          </li>
        </ul>
      </div>
    </Transition>
  </div>
</template>

<script lang="ts" setup>
  import { ref, onMounted, onBeforeUnmount } from 'vue';

  import Button from '@presentational_components/atoms/button/Button.vue';
  import Icon from '@presentational_components/foundation/icon/Icon.vue';
  import './styles.scss';
  import { bem } from '../../../../scripts/utils/bem';

  // -------- [Interfaces] --------
  export interface MenuItem {
    label: string;
    url: string;
  }

  // -------- [Class] --------
  const baseClass = 'menu-dropdown';

  // -------- [Variables] --------
  const contentPositionX = ref('');
  const contentPositionY = ref('');
  const triggerRef = ref<typeof Button | null>(null);
  const wrapperRef = ref<typeof Button | null>(null);
  const props = defineProps<{ items: Array<MenuItem>; ariaLabel?: string }>();
  const isOpen = ref(false);

  // -------- [Functions] --------
  const toggleMenu = () => {
    const triggerElement = triggerRef.value?.$el || triggerRef.value;

    if (triggerElement instanceof HTMLElement) {
      const { left, bottom } = triggerElement.getBoundingClientRect();
      const viewportHeight = window.innerHeight;

      const hasSpaceBottom = viewportHeight - bottom > 100;
      const hasSpaceLeft = left > 100;

      contentPositionY.value = hasSpaceBottom ? 'bottom' : 'top';
      contentPositionX.value = hasSpaceLeft ? 'left' : 'right';
    }

    isOpen.value = !isOpen.value;
  };

  const handleClickOutside = (event: MouseEvent) => {
    if (wrapperRef.value && !wrapperRef.value.contains(event.target as Node)) {
      isOpen.value = false;
    }
  };

  const handleScrollOutside = () => {
    if (isOpen.value) {
      isOpen.value = false;
    }
  };

  // -------- [Lifecycle] --------
  onMounted(() => {
    document.addEventListener('click', handleClickOutside);
    document.addEventListener('scroll', handleScrollOutside, true);
  });

  onBeforeUnmount(() => {
    document.removeEventListener('click', handleClickOutside);
    document.removeEventListener('scroll', handleScrollOutside, true);
  });
</script>
