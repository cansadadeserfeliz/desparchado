<script lang="ts" setup>
  import { ref, onMounted } from 'vue';
  import EventWizard from '../EventWizard/EventWizard.vue';
  import { getEventDetail } from '../../../../../scripts/api/events';
  import { IEventDetailResponse } from '../../../../../scripts/api/interfaces';
  import { bem } from '../../../../../scripts/utils/bem';
  import './styles.scss';

  const props = defineProps<{
    apiUrl: string;
    apiUpdateUrl: string;
    cities: { id: number; name: string }[];
  }>();

  const isLoading = ref(true);
  const eventData = ref<IEventDetailResponse | null>(null);
  const loadError = ref<string>('');

  const loadingClass = 'event-wizard-loading';
  const errorClass = 'event-wizard-error';

  onMounted(async () => {
    try {
      eventData.value = await getEventDetail(props.apiUrl);
    } catch (error) {
      console.error('Failed to load event details for editing:', error);
      loadError.value = 'No se pudo cargar la información del evento. Intente de nuevo.';
    } finally {
      isLoading.value = false;
    }
  });
</script>

<template>
  <div v-if="isLoading" :class="bem(loadingClass)">
    <div :class="bem(loadingClass, 'spinner')"></div>
    Cargando información del evento...
  </div>

  <div v-else-if="loadError" :class="bem(errorClass)">⚠️ {{ loadError }}</div>

  <EventWizard
    v-else
    mode="edit"
    :apiUrl="apiUrl"
    :apiUpdateUrl="apiUpdateUrl"
    :cities="cities"
    :initialData="eventData"
  />
</template>
