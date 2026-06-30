<script lang="ts" setup>
  import { computed } from 'vue';
  import { IWizardState, IEntityOption } from '../../../../../scripts/api/interfaces';
  import { bem } from '../../../../../scripts/utils/bem';
  import { sanitizeHtml } from '../../../../../scripts/utils/sanitize';
  import './styles.scss';

  const props = defineProps<{
    state: IWizardState;
    speakers?: IEntityOption[];
    organizers?: IEntityOption[];
    place?: { id: number; name: string } | null;
  }>();

  const baseClass = 'event-preview';

  const computedSpeakers = computed(() => {
    if (props.speakers && props.speakers.length > 0) {
      return props.speakers;
    }
    return [
      {
        id: -1,
        name: 'Aun no se han agregado presentadores',
      },
    ];
  });

  const computedOrganizers = computed(() => {
    if (props.organizers && props.organizers.length > 0) {
      return props.organizers;
    }
    return [
      {
        id: -1,
        name: 'Aun no se han agregado organizadores',
      },
    ];
  });

  const computedPlaceName = computed(() => {
    if (props.place?.name) {
      return props.place.name;
    }
    return 'Lugar por asignar';
  });

  const formatSpeakerNames = (speakersList: IEntityOption[]) => {
    if (speakersList.length === 0) return '';
    const names = speakersList.map((s) => s.name);
    if (names.length === 1) return names[0];
    if (names.length === 2) return `${names[0]} y ${names[1]}`;
    return `${names.slice(0, -1).join(', ')} y ${names[names.length - 1]}`;
  };

  const formattedOrganizers = computed(() => {
    return computedOrganizers.value.map((o) => o.name).join(', ');
  });

  const formattedDate = computed(() => {
    if (!props.state.eventDate) return 'Fecha no especificada';
    try {
      const dateStr = props.state.eventDate.includes('T')
        ? props.state.eventDate
        : props.state.eventDate.replace(' ', 'T');
      const date = new Date(dateStr);
      if (isNaN(date.getTime())) return props.state.eventDate;
      const weekday = date.toLocaleDateString('es-CO', { weekday: 'long' });
      const day = String(date.getDate()).padStart(2, '0');
      const monthRaw = date.toLocaleDateString('es-CO', { month: 'short' }).replace('.', '');
      const month = monthRaw.charAt(0).toUpperCase() + monthRaw.slice(1);
      const hour = String(date.getHours()).padStart(2, '0');
      const minute = String(date.getMinutes()).padStart(2, '0');
      const year = date.getFullYear();

      return `${weekday}, ${day} ${month} ${hour}:${minute}, ${year}`;
    } catch {
      return props.state.eventDate;
    }
  });

  const sanitizedDescription = computed(() => {
    return sanitizeHtml(props.state.description || '');
  });
</script>

<template>
  <div :class="bem(baseClass)">
    <div :class="bem(baseClass, 'container')">
      <div :class="bem(baseClass, 'badge')">Vista Previa</div>

      <div :class="bem(baseClass, 'card')" tabindex="0" aria-label="Vista previa del evento">
        <!-- 1. Presenters (Speakers) at Top -->
        <div v-if="computedSpeakers.length > 0" :class="bem(baseClass, 'presenters')">
          <div :class="bem(baseClass, 'avatars-row')">
            <div
              v-for="speaker in computedSpeakers"
              :key="speaker.id"
              :class="bem(baseClass, 'avatar-wrapper')"
            >
              <img
                v-if="speaker.image_url"
                :src="speaker.image_url"
                :alt="speaker.name"
                :class="bem(baseClass, 'avatar')"
              />
              <div v-else :class="bem(baseClass, 'avatar-placeholder')">
                {{ speaker.name.charAt(0) }}
              </div>
            </div>
          </div>
          <div :class="bem(baseClass, 'presenter-names')">
            {{ formatSpeakerNames(computedSpeakers) }}
          </div>
        </div>

        <!-- 2. The Image -->
        <div :class="bem(baseClass, 'image-wrapper')">
          <img
            v-if="state.imagePreviewUrl"
            :src="state.imagePreviewUrl"
            alt="Vista previa de imagen"
            :class="bem(baseClass, 'image')"
          />
          <div v-else :class="bem(baseClass, 'image-placeholder')">
            <span>Sin imagen seleccionada</span>
          </div>
        </div>

        <!-- 3. Content Area -->
        <div :class="bem(baseClass, 'content')">
          <!-- Organizer list separated by commas -->
          <div v-if="formattedOrganizers" :class="bem(baseClass, 'organizers')">
            {{ formattedOrganizers }}
          </div>

          <!-- Details section at the end -->
          <div :class="bem(baseClass, 'details-section')">
            <div :class="bem(baseClass, 'detail-item')">
              <div :class="bem(baseClass, 'detail-content')">
                <span :class="bem(baseClass, 'detail-label')">Fecha y Hora</span>
                <span :class="bem(baseClass, 'detail-value')">{{ formattedDate }}</span>
              </div>
            </div>

            <div :class="bem(baseClass, 'detail-item')">
              <div :class="bem(baseClass, 'detail-content')">
                <span :class="bem(baseClass, 'detail-label')">Lugar</span>
                <span :class="bem(baseClass, 'detail-value')">{{ computedPlaceName }}</span>
              </div>
            </div>

            <div :class="bem(baseClass, 'detail-item')">
              <div :class="bem(baseClass, 'detail-content')">
                <span :class="bem(baseClass, 'detail-label')">Costo</span>
                <span :class="bem(baseClass, 'detail-value')">{{
                  !state.price || Number(state.price) === 0 ? 'Gratuito' : `$ ${state.price} COP`
                }}</span>
              </div>
            </div>
          </div>

          <!-- Title -->
          <h3 :class="bem(baseClass, 'title')">
            {{ state.title || 'Título de tu Evento' }}
          </h3>

          <!-- Description -->
          <div
            v-if="sanitizedDescription"
            :class="bem(baseClass, 'description')"
            style="white-space: pre-wrap"
            v-html="sanitizedDescription"
          ></div>
          <div
            v-else
            :class="[bem(baseClass, 'description'), bem(baseClass, 'description', 'empty')]"
          >
            Sin descripción...
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
