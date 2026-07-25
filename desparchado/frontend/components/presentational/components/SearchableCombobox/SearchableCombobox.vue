<script lang="ts" setup>
  import { ref, computed, watch, onMounted, onUnmounted, toRef } from 'vue';
  import { bem } from '../../../../scripts/utils/bem';
  import { IEntityOption } from '../../../../scripts/api/interfaces';
  import { useEntitySearch } from '../../../../scripts/composables/useEntitySearch';
  import './styles.scss';

  export interface SearchableComboboxProps {
    id: string;
    label: string;
    searchUrl: string;
    modelValue: number | number[] | string | null;
    initialOptions?: IEntityOption[];
    multiple?: boolean;
    required?: boolean;
    hideLabel?: boolean;
    placeholder?: string;
    emptyChipsText?: string;
    errors?: string[] | string;
    customClass?: string;
  }

  const props = withDefaults(defineProps<SearchableComboboxProps>(), {
    multiple: false,
    required: false,
    hideLabel: false,
    placeholder: 'Buscar u opción...',
    emptyChipsText: 'No has seleccionado nada todavía',
    initialOptions: () => [],
    customClass: '',
  });

  const emit = defineEmits<{
    'update:modelValue': [value: number | number[] | string | null];
    'update:selectedOptions': [options: IEntityOption[]];
    'create-new': [];
    error: [message: string];
    blur: [event: FocusEvent];
  }>();

  const baseClass = 'searchable-combobox';
  const containerRef = ref<HTMLElement | null>(null);
  const isDropdownOpen = ref(false);
  const activeIndex = ref(-1);

  // Selected Entities Registry
  const knownOptionsMap = new Map<number, IEntityOption>();
  (props.initialOptions || []).forEach((opt) => knownOptionsMap.set(opt.id, opt));

  const selectedEntities = ref<IEntityOption[]>([]);

  const emitSelectedOptions = () => {
    emit('update:selectedOptions', [...selectedEntities.value]);
  };

  const syncSelectedEntities = () => {
    if (props.multiple) {
      const ids = Array.isArray(props.modelValue) ? props.modelValue : [];
      selectedEntities.value = ids
        .map((id) => knownOptionsMap.get(id) || { id, name: `ID #${id}` })
        .filter(Boolean);
    } else {
      const id = typeof props.modelValue === 'number' ? props.modelValue : null;
      if (id !== null) {
        const entity = knownOptionsMap.get(id) || { id, name: `ID #${id}` };
        selectedEntities.value = [entity];
      } else {
        selectedEntities.value = [];
      }
    }
    emitSelectedOptions();
  };

  syncSelectedEntities();

  watch(
    () => props.initialOptions,
    (newOpts) => {
      if (newOpts && newOpts.length > 0) {
        newOpts.forEach((opt) => knownOptionsMap.set(opt.id, opt));
        syncSelectedEntities();
      }
    },
    { immediate: true, deep: true },
  );

  watch(
    () => props.modelValue,
    () => {
      syncSelectedEntities();
    },
    { deep: true },
  );

  // Composable Search
  const searchUrlRef = toRef(props, 'searchUrl');
  const { query, results, isLoading, hasSearched, resetSearch, performSearch } =
    useEntitySearch(searchUrlRef);

  watch(results, (newResults) => {
    newResults.forEach((opt) => knownOptionsMap.set(opt.id, opt));
    if (!isDropdownOpen.value && (newResults.length > 0 || hasSearched.value)) {
      isDropdownOpen.value = true;
    }
    activeIndex.value = -1;
  });

  // Loading Label Text & Option State
  const loadingLabel = computed(() => {
    const trimmed = query.value.trim();
    return trimmed.length > 0 ? `Buscando por: "${trimmed}"` : 'Buscando...';
  });

  const showLoadingOption = computed(() => isLoading.value);

  // Filter out already selected items in multi-select mode
  const filteredResults = computed(() => {
    if (!props.multiple) return results.value;
    const selectedIds = new Set(selectedEntities.value.map((item) => item.id));
    return results.value.filter((item) => !selectedIds.has(item.id));
  });

  // Zero Unselected Results Condition
  const showCreateNewOption = computed(
    () =>
      hasSearched.value &&
      !isLoading.value &&
      filteredResults.value.length === 0 &&
      query.value.trim().length >= 2,
  );

  const totalDropdownItems = computed(() => {
    return (
      filteredResults.value.length +
      (showCreateNewOption.value ? 1 : 0) +
      (showLoadingOption.value ? 1 : 0)
    );
  });

  // Selection Logic
  const selectEntity = (item: IEntityOption) => {
    knownOptionsMap.set(item.id, item);

    if (props.multiple) {
      if (!selectedEntities.value.some((e) => e.id === item.id)) {
        selectedEntities.value.push(item);
      }
      const updatedIds = selectedEntities.value.map((e) => e.id);
      emit('update:modelValue', updatedIds);
      emitSelectedOptions();
    } else {
      selectedEntities.value = [item];
      emit('update:modelValue', item.id);
      emitSelectedOptions();
      closeDropdown();
      resetSearch();
    }
  };

  const removeEntity = (id: number) => {
    if (props.multiple) {
      selectedEntities.value = selectedEntities.value.filter((e) => e.id !== id);
      const updatedIds = selectedEntities.value.map((e) => e.id);
      emit('update:modelValue', updatedIds);
      emitSelectedOptions();
    } else {
      selectedEntities.value = [];
      emit('update:modelValue', null);
      emitSelectedOptions();
    }
  };

  const handleCreateNew = () => {
    closeDropdown();
    resetSearch();
    emit('create-new');
  };

  const isDisabled = computed(() => !props.multiple && selectedEntities.value.length > 0);

  // Dropdown Controls & Keyboard Navigation
  const handleFocus = () => {
    if (isDisabled.value) {
      return;
    }
    if (isDropdownOpen.value) {
      return;
    }
    if (!hasSearched.value) {
      void performSearch(query.value);
    }
    isDropdownOpen.value = true;
  };

  const closeDropdown = () => {
    isDropdownOpen.value = false;
    activeIndex.value = -1;
  };

  const handleKeyDown = (event: KeyboardEvent): void => {
    switch (event.key) {
      case 'ArrowDown': {
        event.preventDefault();
        if (!isDropdownOpen.value) {
          handleFocus();
          return;
        }
        if (totalDropdownItems.value > 0) {
          activeIndex.value = (activeIndex.value + 1) % totalDropdownItems.value;
        }
        break;
      }
      case 'ArrowUp': {
        event.preventDefault();
        if (!isDropdownOpen.value || totalDropdownItems.value === 0) {
          return;
        }
        activeIndex.value =
          (activeIndex.value - 1 + totalDropdownItems.value) % totalDropdownItems.value;
        break;
      }
      case 'Enter': {
        if (!isDropdownOpen.value) {
          return;
        }
        event.preventDefault();
        if (activeIndex.value < 0) {
          return;
        }
        if (showCreateNewOption.value && activeIndex.value === filteredResults.value.length) {
          handleCreateNew();
          return;
        }
        if (activeIndex.value < filteredResults.value.length) {
          selectEntity(filteredResults.value[activeIndex.value]);
        }
        break;
      }
      case 'Escape': {
        event.preventDefault();
        closeDropdown();
        break;
      }
    }
  };

  // Click Outside Handler
  const handleClickOutside = (event: MouseEvent) => {
    if (containerRef.value && !containerRef.value.contains(event.target as Node)) {
      closeDropdown();
    }
  };

  onMounted(() => {
    document.addEventListener('click', handleClickOutside);
  });

  onUnmounted(() => {
    document.removeEventListener('click', handleClickOutside);
  });

  // Local Errors & Display Errors
  const localError = ref('');

  const handleBlur = (event: FocusEvent) => {
    emit('blur', event);

    if (
      containerRef.value &&
      event.relatedTarget &&
      containerRef.value.contains(event.relatedTarget as Node)
    ) {
      return;
    }

    closeDropdown();

    if (props.required) {
      const isEmpty = props.multiple
        ? !Array.isArray(props.modelValue) || props.modelValue.length === 0
        : props.modelValue === null || props.modelValue === undefined || props.modelValue === '';
      if (isEmpty) {
        localError.value = 'Este campo es requerido';
        emit('error', localError.value);
        return;
      }
    }
    localError.value = '';
    emit('error', '');
  };

  const displayError = computed(() => {
    if (!props.errors) {
      return localError.value;
    }
    if (Array.isArray(props.errors)) {
      return props.errors.join(', ');
    }
    return props.errors;
  });

  const srStatusMessage = computed(() => {
    if (!isDropdownOpen.value) {
      return '';
    }
    if (isLoading.value) {
      return 'Buscando opciones...';
    }
    if (filteredResults.value.length > 0) {
      return `${filteredResults.value.length} ${
        filteredResults.value.length === 1 ? 'opción disponible' : 'opciones disponibles'
      }. Usa las flechas arriba y abajo para navegar.`;
    }
    if (showCreateNewOption.value) {
      return 'No se encontraron resultados. Opción de crear nuevo disponible.';
    }
    return '';
  });
</script>

<template>
  <div
    ref="containerRef"
    :class="[bem(baseClass), isDropdownOpen ? bem(baseClass, '', 'open') : '', customClass]"
  >
    <label v-if="label" :class="[bem(baseClass, 'headline'), hideLabel ? 'visually-hidden' : '']">
      {{ label }}<span v-if="required">, *</span>
    </label>

    <!-- Render Selected Chips / Empty Chips State -->
    <div :class="bem(baseClass, 'chips')">
      <TransitionGroup name="chip-slide">
        <button
          v-for="item in selectedEntities"
          :key="item.id"
          type="button"
          :class="bem(baseClass, 'chip')"
          :aria-label="`Eliminar ${item.name}`"
          @click="removeEntity(item.id)"
        >
          <img
            v-if="item.image_url"
            :src="item.image_url"
            :alt="item.name"
            :class="bem(baseClass, 'chip-image')"
          />
          <span>{{ item.name }}</span>
          <span :class="bem(baseClass, 'chip-remove')" aria-hidden="true">&times;</span>
        </button>

        <div
          v-if="selectedEntities.length === 0"
          key="empty-chips-alert"
          :class="bem(baseClass, 'empty-chip')"
        >
          {{ emptyChipsText }}
        </div>
      </TransitionGroup>
    </div>

    <!-- Screen Reader Live Status Region -->
    <div class="visually-hidden" role="status" aria-live="polite" aria-atomic="true">
      {{ srStatusMessage }}
    </div>

    <!-- Input Search Field -->
    <div :class="bem(baseClass, 'input-container')">
      <input
        :id="id"
        type="text"
        :class="[bem(baseClass, 'input'), isDisabled ? bem(baseClass, 'input', 'disabled') : '']"
        v-model="query"
        :placeholder="isDisabled ? 'Opción seleccionada' : placeholder"
        :readonly="isDisabled"
        autocomplete="off"
        spellcheck="false"
        role="combobox"
        aria-haspopup="listbox"
        :aria-expanded="isDropdownOpen"
        :aria-controls="isDropdownOpen ? `${id}-dropdown` : undefined"
        :aria-activedescendant="
          showLoadingOption
            ? `${id}-option-loading`
            : activeIndex >= 0
              ? `${id}-option-${activeIndex}`
              : undefined
        "
        aria-autocomplete="list"
        @focus="handleFocus"
        @blur="handleBlur"
        @keydown="handleKeyDown"
      />
      <div v-if="isLoading" :class="bem(baseClass, 'spinner')" aria-label="Cargando..."></div>

      <!-- Results, Loading & Zero Results Dropdown -->
      <Transition name="slide-fade">
        <ul
          v-if="
            isDropdownOpen &&
            (filteredResults.length > 0 || showCreateNewOption || showLoadingOption)
          "
          :id="`${id}-dropdown`"
          :class="bem(baseClass, 'dropdown')"
          role="listbox"
        >
          <!-- Loading State Option -->
          <li
            v-if="showLoadingOption"
            :id="`${id}-option-loading`"
            :class="[bem(baseClass, 'option'), bem(baseClass, 'option', 'loading')]"
            role="option"
            aria-disabled="true"
          >
            <span>{{ loadingLabel }}</span>
          </li>

          <!-- Filtered Results & Zero Results (hidden while loading) -->
          <template v-if="!showLoadingOption">
            <li
              v-for="(item, index) in filteredResults"
              :key="item.id"
              :id="`${id}-option-${index}`"
              :class="[
                bem(baseClass, 'option'),
                activeIndex === index ? bem(baseClass, 'option', 'active') : '',
              ]"
              role="option"
              :aria-selected="activeIndex === index"
              @mousedown.prevent="selectEntity(item)"
            >
              <img
                v-if="item.image_url"
                :src="item.image_url"
                :alt="item.name"
                :class="bem(baseClass, 'option-image')"
              />
              <span>{{ item.name }}</span>
            </li>

            <!-- Zero Results / Create New Option -->
            <li
              v-if="showCreateNewOption"
              :id="`${id}-option-${filteredResults.length}`"
              :class="[
                bem(baseClass, 'option'),
                bem(baseClass, 'option', 'create-new'),
                activeIndex === filteredResults.length ? bem(baseClass, 'option', 'active') : '',
              ]"
              role="option"
              :aria-selected="activeIndex === filteredResults.length"
              @mousedown.prevent="handleCreateNew"
            >
              <span :class="bem(baseClass, 'create-new-label')">
                ¿No encontraste el que buscabas?
              </span>
              <span :class="bem(baseClass, 'create-new-button')"> Crear nuevo </span>
            </li>
          </template>
        </ul>
      </Transition>
    </div>

    <!-- Error Display -->
    <div v-if="displayError" :id="`${id}-error`" :class="bem(baseClass, 'error')">
      {{ displayError }}
    </div>
  </div>
</template>
