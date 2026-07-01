<template>
  <div :class="[bem(baseClass), customClass]">
    <label
      v-if="label"
      :id="`${id}-label`"
      :class="[bem(baseClass, 'headline'), hideLabel ? 'visually-hidden' : '']"
      :for="id"
    >
      {{ label }}<span v-if="required">, *</span>
    </label>
    <div :class="bem(baseClass, 'editor-wrapper')">
      <div ref="editorEl" :class="bem(baseClass, 'editor')"></div>
    </div>
    <div v-if="formattedErrors" :id="`${id}-error`" :class="bem(baseClass, 'error')">
      {{ formattedErrors }}
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { ref, onMounted, onBeforeUnmount, watch, computed } from 'vue';
  import Quill from 'quill';
  import 'quill/dist/quill.snow.css';
  import { bem } from '../../../../scripts/utils/bem';
  import './styles.scss';

  export interface RichTextEditorProps {
    modelValue: string;
    id: string;
    label?: string;
    hideLabel?: boolean;
    customClass?: string;
    placeholder?: string;
    required?: boolean;
    errors?: string[] | string;
  }

  const props = withDefaults(defineProps<RichTextEditorProps>(), {
    required: false,
    modelValue: '',
    hideLabel: false,
    customClass: '',
  });

  const emit = defineEmits(['update:modelValue']);

  const baseClass = 'rich-text-editor';
  const editorEl = ref<HTMLElement | null>(null);
  let quillInstance: Quill | null = null;
  let isUpdating = false;

  const formattedErrors = computed(() => {
    if (!props.errors) return '';
    if (Array.isArray(props.errors)) {
      return props.errors.join(', ');
    }
    return props.errors;
  });

  /**
   * Handles text-change events from the Quill instance.
   * Extracts semantic HTML and emits the value if it represents meaningful content.
   */
  const onTextChange = () => {
    if (!quillInstance || isUpdating) return;
    isUpdating = true;

    let html = quillInstance.getSemanticHTML();
    const text = quillInstance.getText().trim();
    if (!text && (html === '<p><br></p>' || html === '<p></p>' || !html)) {
      html = '';
    }

    emit('update:modelValue', html);
    isUpdating = false;
  };

  /**
   * Initializes the Quill editor instance on mount.
   */
  onMounted(() => {
    if (!editorEl.value) return;

    quillInstance = new Quill(editorEl.value, {
      theme: 'snow',
      placeholder: props.placeholder || '',
      modules: {
        toolbar: [
          ['bold', 'italic', 'underline'],
          [{ list: 'ordered' }, { list: 'bullet' }],
          ['link'],
        ],
      },
    });

    const setupClipboardFilters = () => {
      quillInstance!.clipboard.addMatcher(Node.ELEMENT_NODE, (node, delta) => {
        delta.ops.forEach((op) => {
          if (op.attributes) {
            const allowed: {
              bold?: boolean;
              italic?: boolean;
              underline?: boolean;
              link?: string;
              list?: string;
            } = {};
            if (op.attributes.bold) allowed.bold = true;
            if (op.attributes.italic) allowed.italic = true;
            if (op.attributes.underline) allowed.underline = true;
            if (op.attributes.link) allowed.link = op.attributes.link as string;
            if (op.attributes.list) allowed.list = op.attributes.list as string;
            op.attributes = Object.keys(allowed).length > 0 ? allowed : undefined;
          }
        });
        return delta;
      });
    };

    setupClipboardFilters();

    if (props.modelValue) {
      quillInstance.clipboard.dangerouslyPasteHTML(props.modelValue);
    }

    if (quillInstance.root) {
      const rootEl = quillInstance.root;
      rootEl.setAttribute('id', props.id);

      if (props.label) {
        rootEl.setAttribute('aria-labelledby', `${props.id}-label`);
      }
      if (props.required) {
        rootEl.setAttribute('aria-required', 'true');
      }
      if (formattedErrors.value) {
        rootEl.setAttribute('aria-describedby', `${props.id}-error`);
      }
      const hasErrors =
        props.errors && (Array.isArray(props.errors) ? props.errors.length > 0 : !!props.errors);
      rootEl.setAttribute('aria-invalid', hasErrors ? 'true' : 'false');
    }

    quillInstance.on('text-change', onTextChange);
  });

  watch(
    () => formattedErrors.value,
    (newErrorsVal) => {
      if (quillInstance && quillInstance.root) {
        const rootEl = quillInstance.root;
        if (newErrorsVal) {
          rootEl.setAttribute('aria-describedby', `${props.id}-error`);
        } else {
          rootEl.removeAttribute('aria-describedby');
        }
      }
    },
  );

  watch(
    () => props.errors,
    (errorsProp) => {
      if (quillInstance && quillInstance.root) {
        const rootEl = quillInstance.root;
        const hasErrors =
          errorsProp && (Array.isArray(errorsProp) ? errorsProp.length > 0 : !!errorsProp);
        rootEl.setAttribute('aria-invalid', hasErrors ? 'true' : 'false');
      }
    },
  );

  watch(
    () => props.required,
    (requiredProp) => {
      if (quillInstance && quillInstance.root) {
        const rootEl = quillInstance.root;
        if (requiredProp) {
          rootEl.setAttribute('aria-required', 'true');
        } else {
          rootEl.removeAttribute('aria-required');
        }
      }
    },
  );

  /**
   * Watches props.modelValue to programmatically update Quill's content
   * when changed externally, preserving the selection state safely.
   */
  watch(
    () => props.modelValue,
    (newVal) => {
      if (quillInstance && !isUpdating) {
        const currentHtml = quillInstance.getSemanticHTML();
        const normalizedNewVal = newVal || '';
        const normalizedCurrentHtml =
          currentHtml === '<p><br></p>' || currentHtml === '<p></p>' ? '' : currentHtml;

        if (normalizedNewVal !== normalizedCurrentHtml) {
          isUpdating = true;
          const selection = quillInstance.getSelection();
          quillInstance.clipboard.dangerouslyPasteHTML(normalizedNewVal);

          if (selection) {
            const length = quillInstance.getLength();
            const index = Math.min(selection.index, length - 1);
            quillInstance.setSelection(index, Math.min(selection.length, length - 1 - index));
          }
          isUpdating = false;
        }
      }
    },
  );

  /**
   * Cleans up event listeners and references before unmounting.
   */
  onBeforeUnmount(() => {
    if (quillInstance) {
      quillInstance.off('text-change', onTextChange);
      quillInstance = null;
    }
  });
</script>
