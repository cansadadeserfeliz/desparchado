<template>
  <div
    :class="[
      bem(baseClass),
      condensed ? bem(baseClass, '', 'condensed') : '',
      isDragging ? bem(baseClass, '', 'dragging') : '',
      disabled ? bem(baseClass, '', 'disabled') : '',
      hasErrors ? bem(baseClass, '', 'error') : '',
      customClass,
    ]"
  >
    <label
      v-if="!hideLabel && label"
      :for="id"
      :class="[bem(baseClass, 'label'), 'text-body-highlight', 'text-bold']"
    >
      {{ label }}
      <span v-if="required" :class="bem(baseClass, 'required-star')">*</span>
    </label>

    <div
      :class="bem(baseClass, 'drop-zone')"
      tabindex="0"
      role="button"
      :aria-label="label || 'Subir imagen del evento'"
      @dragover.prevent="handleDragOver"
      @dragleave.prevent="handleDragLeave"
      @drop.prevent="handleDrop"
      @click="triggerFileInput"
      @keydown.enter.prevent="triggerFileInput"
      @keydown.space.prevent="triggerFileInput"
    >
      <input
        :id="id"
        ref="fileInputRef"
        type="file"
        accept="image/*"
        :disabled="disabled"
        :class="bem(baseClass, 'file-input')"
        @change="handleFileChange"
        @blur="emit('blur')"
      />

      <!-- Preview State when an image is selected -->
      <div v-if="previewUrl" :class="bem(baseClass, 'preview-container')">
        <div :class="bem(baseClass, 'preview-wrapper')">
          <img
            :src="previewUrl"
            alt="Vista previa de la imagen cargada"
            :class="bem(baseClass, 'preview-image')"
          />
          <button
            type="button"
            :class="bem(baseClass, 'remove-button')"
            @click.stop="handleRemoveImage"
            aria-label="Quitar imagen"
            title="Quitar imagen"
          >
            <Icon id="close" size="small" />
          </button>
        </div>
        <div :class="bem(baseClass, 'preview-info')">
          <span v-if="modelValue?.name" :class="[bem(baseClass, 'filename'), 'text-body-sm']">
            {{ modelValue.name }}
          </span>
          <span :class="[bem(baseClass, 'change-prompt'), 'text-caption']">
            Haz clic o arrastra otra imagen para cambiarla
          </span>
        </div>
      </div>

      <!-- Empty / Upload Prompt State -->
      <div v-else :class="bem(baseClass, 'prompt-container')">
        <div :class="bem(baseClass, 'upload-icon')" aria-hidden="true">
          <svg
            width="32"
            height="32"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
            <circle cx="8.5" cy="8.5" r="1.5" />
            <polyline points="21 15 16 10 5 21" />
          </svg>
        </div>
        <div :class="bem(baseClass, 'prompt-text')">
          <span :class="[bem(baseClass, 'prompt-primary'), 'text-body-highlight', 'text-bold']">
            Arrastra tu imagen aquí
          </span>
          <span :class="[bem(baseClass, 'prompt-secondary'), 'text-body-sm']">
            o haz clic para examinar desde tu equipo
          </span>
        </div>
        <span :class="[bem(baseClass, 'size-limit'), 'text-caption']">
          Límite máximo: {{ maxSizeMb }}MB (PNG, JPG, WEBP)
        </span>
      </div>
    </div>

    <!-- Error Messaging -->
    <div
      v-if="displayErrorMessage"
      :class="[bem(baseClass, 'error-message'), 'text-body-sm']"
      role="alert"
    >
      {{ displayErrorMessage }}
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { ref, computed, onBeforeUnmount } from 'vue';
  import { bem } from '../../../../scripts/utils/bem';
  import { MAX_IMAGE_SIZE_MB } from '../../../../scripts/constants';
  import Icon from '@presentational_components/foundation/icon/Icon.vue';
  import './styles.scss';

  export interface ImageUploadProps {
    id: string;
    label: string;
    hideLabel?: boolean;
    modelValue: File | null;
    previewUrl?: string;
    maxSizeMb?: number;
    errors?: string[] | string;
    disabled?: boolean;
    condensed?: boolean;
    required?: boolean;
    customClass?: string;
  }

  const props = withDefaults(defineProps<ImageUploadProps>(), {
    hideLabel: false,
    previewUrl: '',
    maxSizeMb: MAX_IMAGE_SIZE_MB,
    disabled: false,
    condensed: false,
    required: false,
    customClass: '',
  });

  const emit = defineEmits<{
    'update:modelValue': [value: File | null];
    'update:previewUrl': [url: string];
    error: [message: string];
    blur: [];
  }>();

  const baseClass = 'image-upload';
  const fileInputRef = ref<HTMLInputElement | null>(null);
  const isDragging = ref(false);
  const localError = ref('');
  let createdObjectUrl: string | null = null;

  const displayErrorMessage = computed(() => {
    if (localError.value) return localError.value;
    if (props.errors) {
      if (Array.isArray(props.errors)) {
        return props.errors[0] || '';
      }
      return props.errors;
    }
    return '';
  });

  const hasErrors = computed(() => !!displayErrorMessage.value);

  const triggerFileInput = () => {
    if (props.disabled) return;
    fileInputRef.value?.click();
  };

  const handleDragOver = () => {
    if (props.disabled) return;
    isDragging.value = true;
  };

  const handleDragLeave = () => {
    isDragging.value = false;
  };

  const revokeCurrentObjectUrl = () => {
    if (createdObjectUrl) {
      URL.revokeObjectURL(createdObjectUrl);
      createdObjectUrl = null;
    }
  };

  const processFile = (file: File | undefined) => {
    localError.value = '';

    if (!file) return;

    // Check file type
    if (!file.type.startsWith('image/')) {
      const msg = 'El archivo seleccionado debe ser una imagen.';
      localError.value = msg;
      emit('error', msg);
      return;
    }

    // Check size limit (maxSizeMb in MB)
    const maxSizeBytes = props.maxSizeMb * 1024 * 1024;
    if (file.size > maxSizeBytes) {
      const msg = `La imagen supera el límite de ${props.maxSizeMb}MB.`;
      localError.value = msg;
      emit('error', msg);
      return;
    }

    // Revoke previous object URL if managed locally
    revokeCurrentObjectUrl();

    // Create local object URL for preview
    const newPreviewUrl = URL.createObjectURL(file);
    createdObjectUrl = newPreviewUrl;

    emit('update:modelValue', file);
    emit('update:previewUrl', newPreviewUrl);
    emit('error', '');
  };

  const handleFileChange = (e: Event) => {
    const input = e.target as HTMLInputElement;
    const file = input.files?.[0];
    processFile(file);
  };

  const handleDrop = (e: DragEvent) => {
    isDragging.value = false;
    if (props.disabled) return;
    const file = e.dataTransfer?.files?.[0];
    processFile(file);
  };

  const handleRemoveImage = () => {
    revokeCurrentObjectUrl();
    localError.value = '';

    if (fileInputRef.value) {
      fileInputRef.value.value = '';
    }

    emit('update:modelValue', null);
    emit('update:previewUrl', '');
    emit('error', '');
  };

  onBeforeUnmount(() => {
    revokeCurrentObjectUrl();
  });
</script>
