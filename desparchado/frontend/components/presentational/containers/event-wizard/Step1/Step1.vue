<script lang="ts" setup>
  import { computed } from 'vue';
  import { IWizardState } from '../../../../../scripts/api/interfaces';
  import { bem } from '../../../../../scripts/utils/bem';

  const props = defineProps<{
    state: IWizardState;
    condensed: boolean;
    fieldErrors?: Record<string, string[]>;
  }>();
  props;

  const baseClass = 'event-wizard';
  const fieldClass = 'wizard-field';

  const isValid = computed(() => {
    return props.state.title.trim().length > 0;
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
      <input
        id="wizard-title"
        type="text"
        :class="bem(fieldClass, 'input')"
        v-model="state.title"
        placeholder="Ej. Concierto de Jazz en el Parque"
        required
      />
      <div v-if="fieldErrors?.title" :class="bem(fieldClass, 'error')">
        {{ fieldErrors.title.join(', ') }}
      </div>
    </div>

    <!-- Description Group -->
    <div :class="bem(fieldClass)">
      <div :class="bem(fieldClass, 'details')">
        <label :class="bem(fieldClass, 'headline')" for="wizard-description">Descripción,</label>
        <p :class="bem(fieldClass, 'subheadline')">Comparte la esencia de tu encuentro</p>
        <p :class="bem(fieldClass, 'description')">
          ¿De qué trata tu evento? Ayuda a tus invitados a entender de qué va el evento.
        </p>
      </div>
      <textarea
        id="wizard-description"
        :class="bem(fieldClass, 'textarea')"
        v-model="state.description"
        rows="5"
        placeholder="Describe de qué se trata el evento..."
      ></textarea>
      <div v-if="fieldErrors?.description" :class="bem(fieldClass, 'error')">
        {{ fieldErrors.description.join(', ') }}
      </div>
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
      <div v-if="fieldErrors?.organizers" :class="bem(fieldClass, 'error')">
        {{ fieldErrors.organizers.join(', ') }}
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
      <div v-if="fieldErrors?.speakers" :class="bem(fieldClass, 'error')">
        {{ fieldErrors.speakers.join(', ') }}
      </div>
    </div>
  </div>
</template>
