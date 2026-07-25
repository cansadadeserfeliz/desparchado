import { ref, watch, onUnmounted, Ref } from 'vue';
import { getData } from '../api/base';
import { IEntityOption, ISearchResponse } from '../api/interfaces';
import { MIN_SEARCH_QUERY_LENGTH, SEARCH_DEBOUNCE_MS } from '../constants';

export interface IUseEntitySearchOptions {
  searchUrl: string;
  minQueryLength?: number;
  debounceMs?: number;
}

export interface IUseEntitySearchReturn {
  query: Ref<string>;
  results: Ref<IEntityOption[]>;
  isLoading: Ref<boolean>;
  hasSearched: Ref<boolean>;
  searchError: Ref<string | null>;
  resetSearch: () => void;
  performSearch: (searchQuery: string) => Promise<void>;
}

export function useEntitySearch(
  searchUrlRef: Ref<string> | string,
  options?: { minQueryLength?: number; debounceMs?: number },
): IUseEntitySearchReturn {
  const query = ref('');
  const results = ref<IEntityOption[]>([]);
  const isLoading = ref(false);
  const hasSearched = ref(false);
  const searchError = ref<string | null>(null);

  const minQueryLength = options?.minQueryLength ?? MIN_SEARCH_QUERY_LENGTH;
  const debounceMs = options?.debounceMs ?? SEARCH_DEBOUNCE_MS;

  let debounceTimer: ReturnType<typeof setTimeout> | null = null;
  let activeAbortController: AbortController | null = null;

  const resetSearch = (): void => {
    if (debounceTimer) {
      clearTimeout(debounceTimer);
      debounceTimer = null;
    }
    if (activeAbortController) {
      activeAbortController.abort();
      activeAbortController = null;
    }
    query.value = '';
    results.value = [];
    isLoading.value = false;
    hasSearched.value = false;
    searchError.value = null;
  };

  onUnmounted(() => {
    if (debounceTimer) {
      clearTimeout(debounceTimer);
      debounceTimer = null;
    }
    if (activeAbortController) {
      activeAbortController.abort();
      activeAbortController = null;
    }
  });

  const performSearch = async (searchQuery: string): Promise<void> => {
    const trimmed = searchQuery.trim();

    // Queries with 1 character (or between 1 and minQueryLength - 1) are too short
    if (trimmed.length > 0 && trimmed.length < minQueryLength) {
      if (activeAbortController) {
        activeAbortController.abort();
        activeAbortController = null;
      }
      results.value = [];
      isLoading.value = false;
      hasSearched.value = false;
      searchError.value = null;
      return;
    }

    isLoading.value = true;
    searchError.value = null;

    if (activeAbortController) {
      activeAbortController.abort();
    }
    activeAbortController = new AbortController();
    const currentController = activeAbortController;

    const baseUrl = typeof searchUrlRef === 'string' ? searchUrlRef : searchUrlRef.value;
    const separator = baseUrl.includes('?') ? '&' : '?';
    const fullUrl = `${baseUrl}${separator}q=${encodeURIComponent(trimmed)}`;

    try {
      const response = await getData<ISearchResponse<IEntityOption>>(fullUrl, {
        signal: currentController.signal,
      });
      if (activeAbortController === currentController) {
        results.value = response?.results ?? [];
        hasSearched.value = true;
      }
    } catch (err: unknown) {
      if (err instanceof Error && (err.name === 'AbortError' || err.name === 'DOMException')) {
        return;
      }
      if (activeAbortController === currentController) {
        searchError.value = err instanceof Error ? err.message : 'Error al buscar resultados';
        results.value = [];
        hasSearched.value = true;
      }
    } finally {
      if (activeAbortController === currentController) {
        isLoading.value = false;
      }
    }
  };

  watch(query, (newQuery) => {
    if (debounceTimer) {
      clearTimeout(debounceTimer);
    }

    const trimmed = newQuery.trim();
    if (trimmed.length > 0 && trimmed.length < minQueryLength) {
      if (activeAbortController) {
        activeAbortController.abort();
        activeAbortController = null;
      }
      results.value = [];
      isLoading.value = false;
      hasSearched.value = false;
      searchError.value = null;
      return;
    }

    isLoading.value = true;
    debounceTimer = setTimeout(() => {
      void performSearch(newQuery);
    }, debounceMs);
  });

  return {
    query,
    results,
    isLoading,
    hasSearched,
    searchError,
    resetSearch,
    performSearch,
  };
}
