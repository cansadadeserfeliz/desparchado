<script lang="ts" setup>
  import { computed, reactive } from 'vue';
  import { IWizardState, IEntityOption } from '../../../../../scripts/api/interfaces';
  import { bem } from '../../../../../scripts/utils/bem';
  import TextField from '@presentational_components/components/TextField/TextField.vue';
  import RichTextEditor from '@presentational_components/components/RichTextEditor/RichTextEditor.vue';
  import SearchableCombobox from '@presentational_components/components/SearchableCombobox/SearchableCombobox.vue';

  const props = defineProps<{
    state: IWizardState;
    condensed: boolean;
    initialOrganizers?: IEntityOption[];
    initialSpeakers?: IEntityOption[];
    fieldErrors?: Record<string, string[]>;
  }>();

  const emit = defineEmits<{
    'create-organizer': [];
    'create-speaker': [];
    'update:selected-organizers': [options: IEntityOption[]];
    'update:selected-speakers': [options: IEntityOption[]];
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
    const organizersValid =
      Array.isArray(props.state.organizerIds) && props.state.organizerIds.length >= 1;
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

    <!-- Organizers Group -->
    <div :class="bem(fieldClass)">
      <div :class="bem(fieldClass, 'details')">
        <label :class="bem(fieldClass, 'headline')">Organizadores, *</label>
        <p :class="bem(fieldClass, 'subheadline')">¿Quién está detrás?</p>
        <p :class="bem(fieldClass, 'description')">
          Indica quién(es) está(n) a cargo de la planificación y qué experiencia o credenciales
          respaldan el encuentro. Busca tu organizador, si no se ha creado todavía el organizador
          que buscas crea uno nuevo.
        </p>
      </div>
      <SearchableCombobox
        id="wizard-organizers"
        label="Organizadores"
        :hideLabel="true"
        placeholder="Buscar organizador por nombre..."
        emptyChipsText="No has seleccionado ningún organizador aún"
        searchUrl="/events/api/v1/organizers/search/"
        v-model="state.organizerIds"
        :initialOptions="initialOrganizers"
        :multiple="true"
        :required="true"
        :errors="fieldErrors?.organizer_ids"
        @error="(msg) => handleFieldError('organizer_ids', msg)"
        @create-new="emit('create-organizer')"
        @update:selected-options="(opts) => emit('update:selected-organizers', opts)"
      />
    </div>

    <!-- Speakers Group -->
    <div :class="bem(fieldClass)">
      <div :class="bem(fieldClass, 'details')">
        <label :class="bem(fieldClass, 'headline')">Invitados/Ponentes</label>
        <p :class="bem(fieldClass, 'subheadline')">¿Quién o quiénes participan?</p>
        <p :class="bem(fieldClass, 'description')">
          Indica quién(es) está(n) a cargo de la exponer, presentar, hablar o de permitir que la
          experiencia funcione. Busca si el presentador ha sido agregado antes, si no se ha agregado
          todavía, agrega uno nuevo.
        </p>
      </div>
      <SearchableCombobox
        id="wizard-speakers"
        label="Invitados/Ponentes"
        :hideLabel="true"
        placeholder="Buscar invitado o ponente..."
        emptyChipsText="No has seleccionado ningún ponente aún"
        searchUrl="/events/api/v1/speakers/search/"
        v-model="state.speakerIds"
        :initialOptions="initialSpeakers"
        :multiple="true"
        :required="false"
        :errors="fieldErrors?.speaker_ids"
        @error="(msg) => handleFieldError('speaker_ids', msg)"
        @create-new="emit('create-speaker')"
        @update:selected-options="(opts) => emit('update:selected-speakers', opts)"
      />
    </div>
  </div>
</template>
