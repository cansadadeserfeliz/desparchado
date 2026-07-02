import { onMounted, onBeforeUnmount, ComputedRef, Ref } from 'vue';

export interface IUseEventWizardLayoutProps {
  isDirty: ComputedRef<boolean>;
  showMobilePreview: Ref<boolean>;
}

export interface IUseEventWizardLayoutReturn {
  removeBeforeUnload: () => void;
}

/**
 * Composable responsible for managing window side effects, resizing height settings,
 * mobile drawer matches, and page unload prevention prompts.
 *
 * @param props - Layout dependency parameters: isDirty state and showMobilePreview flag.
 * @returns The cleanup function to remove beforeunload listeners.
 */
export const useEventWizardLayout = (
  props: IUseEventWizardLayoutProps,
): IUseEventWizardLayoutReturn => {
  const beforeUnloadHandler = (e: BeforeUnloadEvent): string | void => {
    if (props.isDirty.value) {
      e.preventDefault();
      return '';
    }
  };

  const removeBeforeUnload = (): void => {
    window.removeEventListener('beforeunload', beforeUnloadHandler);
  };

  const updateHeaderHeight = (): void => {
    requestAnimationFrame(() => {
      const header = document.getElementById('header');
      const height = header?.offsetHeight;
      if (height) {
        document.body.style.setProperty('--header-height', `${height}px`);
      }
    });
  };

  let mediaQueryList: MediaQueryList | null = null;

  const handleBreakpointChange = (e: MediaQueryListEvent | MediaQueryList): void => {
    if (e.matches) {
      props.showMobilePreview.value = false;
    }
  };

  onMounted(() => {
    window.addEventListener('beforeunload', beforeUnloadHandler);
    updateHeaderHeight();
    window.addEventListener('resize', updateHeaderHeight);

    if (typeof window !== 'undefined') {
      mediaQueryList = window.matchMedia('(min-width: 768px)');
      handleBreakpointChange(mediaQueryList);
      mediaQueryList.addEventListener('change', handleBreakpointChange);
    }
  });

  onBeforeUnmount(() => {
    window.removeEventListener('beforeunload', beforeUnloadHandler);
    window.removeEventListener('resize', updateHeaderHeight);

    if (mediaQueryList) {
      mediaQueryList.removeEventListener('change', handleBreakpointChange);
    }
  });

  return {
    removeBeforeUnload,
  };
};
