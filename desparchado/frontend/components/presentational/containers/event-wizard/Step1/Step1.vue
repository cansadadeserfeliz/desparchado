<script lang="ts" setup>
  import { computed, reactive } from 'vue';
  import { IWizardState } from '../../../../../scripts/api/interfaces';
  import { bem } from '../../../../../scripts/utils/bem';
  import TextField from '@presentational_components/components/TextField/TextField.vue';
  import RichTextEditor from '@presentational_components/components/RichTextEditor/RichTextEditor.vue';

  const props = defineProps<{
    state: IWizardState;
    condensed: boolean;
    fieldErrors?: Record<string, string[]>;
  }>();

  const baseClass = 'event-wizard';
  const fieldClass = 'wizard-field';

  const localErrors = reactive<Record<string, string>>({});
  const handleFieldError = (field: string, errorMsg: string) => {
    if (!errorMsg) {
      delete localErrors[field];
      return;
    }
    localErrors[field] = errorMsg;
  };
  const hasLocalErrors = computed(() => Object.keys(localErrors).length > 0);

  const isValid = computed(() => {
    if (hasLocalErrors.value) return false;
    const titleValid = props.state.title.trim().length > 0;
    const desc = props.state.description || '';
    const descText = desc.replace(/<[^>]*>/g, '').trim();
    const organizersValid = props.state.organizerIds.length >= 1;
    return titleValid && descText.length > 0 && organizersValid;
  });

  defineExpose({
    isValid,
  });
</script>

<template>
  <div :class="bem(baseClass, 'step-content')">
    <!-- Title Group -->
    <div :class="bem(fieldClass)">
      <div :class="bem(fieldClass, 'details')">
        <label :class="bem(fieldClass, 'headline')" for="wizard-title">Título, *</label>
        <p :class="bem(fieldClass, 'subheadline')">Ponle un nombre que inspire</p>
        <p :class="bem(fieldClass, 'description')">
          El título es tu carta de presentación: debe ser atractivo, breve y evocar la esencia de la
          experiencia que ofreces. Piensa en cómo conectar con tu público desde el primer vistazo.
        </p>
      </div>
      <TextField
        id="wizard-title"
        label="Título"
        :hideLabel="true"
        customClass="wizard-field"
        placeholder="Ej. Concierto de Jazz en el Parque"
        v-model="state.title"
        required
        :errors="fieldErrors?.title"
        @error="(msg) => handleFieldError('title', msg)"
      />
    </div>

    <!-- Description Group -->
    <div :class="bem(fieldClass)">
      <div :class="bem(fieldClass, 'details')">
        <label :class="bem(fieldClass, 'headline')" for="wizard-description">Descripción, *</label>
        <p :class="bem(fieldClass, 'subheadline')">Comparte la esencia de tu encuentro</p>
        <p :class="bem(fieldClass, 'description')">
          ¿De qué trata tu evento? Ayuda a tus invitados a entender de qué va el evento.
        </p>
      </div>
      <RichTextEditor
        id="wizard-description"
        label="Descripción"
        :hideLabel="true"
        customClass="wizard-field"
        placeholder="Describe de qué se trata el evento..."
        v-model="state.description"
        required
        :errors="fieldErrors?.description"
        @error="(msg) => handleFieldError('description', msg)"
      />
    </div>

    <!-- Organizers & Speakers Stubs -->
    <div :class="bem(fieldClass)">
      <div :class="bem(fieldClass, 'details')">
        <span :class="bem(fieldClass, 'headline')">Organizadores (Próximamente combobox)</span>
        <p :class="bem(fieldClass, 'subheadline')">¿Quién está detrás?</p>
        <p :class="bem(fieldClass, 'description')">
          Indica quién(es) está(n) a cargo de la planificación y qué experiencia o credenciales
          respaldan el encuentro. Busca tu organizador, si no se ha creado todavía el organizador
          que buscas crea uno nuevo.
        </p>
      </div>
      <div v-if="fieldErrors?.organizer_ids" :class="bem(fieldClass, 'error')">
        {{ fieldErrors.organizer_ids.join(', ') }}
      </div>
    </div>

    <div :class="bem(fieldClass)">
      <div :class="bem(fieldClass, 'details')">
        <span :class="bem(fieldClass, 'headline')">Invitados/Ponentes (Próximamente combobox)</span>
        <p :class="bem(fieldClass, 'subheadline')">¿Quién o quiénes participan?</p>
        <p :class="bem(fieldClass, 'description')">
          Indica quién(es) está(n) a cargo de la exponer, presentar, hablar o de permitir que la
          experiencia funcione. Busca si el presentador ha sido agregado antes, si no se ha agregado
          todavía, agrega uno nuevo.
        </p>
      </div>
      <div v-if="fieldErrors?.speaker_ids" :class="bem(fieldClass, 'error')">
        {{ fieldErrors.speaker_ids.join(', ') }}
      </div>
    </div>
  </div>
</template>
