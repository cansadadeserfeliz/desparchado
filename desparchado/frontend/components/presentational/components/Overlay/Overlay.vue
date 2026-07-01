<template>
  <Transition name="overlay-fade">
    <div
      v-if="show"
      ref="overlayRef"
      :class="[bem(baseClass), customClass]"
      @click.self="emit('close')"
      tabindex="-1"
      role="dialog"
      aria-modal="true"
      :aria-label="dialogLabel || undefined"
      :aria-labelledby="labelledBy || undefined"
    >
      <div :class="bem(baseClass, 'content')" ref="contentRef">
        <button
          type="button"
          :class="bem(baseClass, 'close')"
          @click="emit('close')"
          :aria-label="closeLabel"
          ref="closeButtonRef"
        >
          &times;
        </button>
        <slot></slot>
      </div>
    </div>
  </Transition>
</template>

<script lang="ts" setup>
  import { watch, onBeforeUnmount, ref } from 'vue';
  import { bem } from '../../../../scripts/utils/bem';
  import './styles.scss';

  export interface OverlayProps {
    show: boolean;
    closeLabel?: string;
    customClass?: string;
    dialogLabel?: string;
    labelledBy?: string;
  }

  const props = withDefaults(defineProps<OverlayProps>(), {
    show: false,
    closeLabel: 'Cerrar',
    customClass: '',
  });

  const emit = defineEmits(['close']);

  const baseClass = 'overlay';
  const overlayRef = ref<HTMLElement | null>(null);
  const contentRef = ref<HTMLElement | null>(null);
  const closeButtonRef = ref<HTMLElement | null>(null);

  /**
   * Focus trap and Escape key listener for keyboard navigation.
   */
  const handleKeydown = (e: KeyboardEvent) => {
    if (!props.show) return;

    if (e.key === 'Escape') {
      emit('close');
      return;
    }

    const trapFocus = () => {
      if (!contentRef.value) return;
      const focusableElements = contentRef.value.querySelectorAll<HTMLElement>(
        'a[href], area[href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), button:not([disabled]), iframe, object, embed, [tabindex="0"], [contenteditable]',
      );
      if (focusableElements.length === 0) return;

      const firstEl = focusableElements[0];
      const lastEl = focusableElements[focusableElements.length - 1];

      if (e.shiftKey) {
        if (document.activeElement === firstEl) {
          lastEl.focus();
          e.preventDefault();
        }
      } else {
        if (document.activeElement === lastEl) {
          firstEl.focus();
          e.preventDefault();
        }
      }
    };

    if (e.key === 'Tab') {
      trapFocus();
    }
  };

  let previousActiveElement: HTMLElement | null = null;
  let previousBodyOverflow: string | null = null;

  /**
   * Watches show prop to toggle body scroll locking, keydown listeners, and initial focus state.
   */
  watch(
    () => props.show,
    (val) => {
      if (typeof document === 'undefined') return;

      if (val) {
        previousActiveElement = document.activeElement as HTMLElement;
        previousBodyOverflow = document.body.style.overflow;
        document.body.style.overflow = 'hidden';
        window.addEventListener('keydown', handleKeydown);

        const focusFirstElement = () => {
          if (contentRef.value) {
            const focusable = contentRef.value.querySelectorAll<HTMLElement>(
              'a[href], area[href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), button:not([disabled]), iframe, object, embed, [tabindex="0"], [contenteditable]',
            );
            if (focusable.length > 0) {
              focusable[0].focus();
            } else if (overlayRef.value) {
              overlayRef.value.focus();
            }
          }
        };

        setTimeout(focusFirstElement, 50);
      } else {
        if (previousBodyOverflow !== null) {
          document.body.style.overflow = previousBodyOverflow;
          previousBodyOverflow = null;
        }
        window.removeEventListener('keydown', handleKeydown);
        if (previousActiveElement) {
          previousActiveElement.focus();
        }
      }
    },
    { immediate: true },
  );

  /**
   * Cleans up scroll locking and listeners on unmount.
   */
  onBeforeUnmount(() => {
    if (typeof document !== 'undefined') {
      if (previousBodyOverflow !== null) {
        document.body.style.overflow = previousBodyOverflow;
        previousBodyOverflow = null;
      }
      window.removeEventListener('keydown', handleKeydown);
    }
  });
</script>
