<script lang="ts" setup>
  import EventWizard from '../EventWizard/EventWizard.vue';

  const props = defineProps<{
    apiUrl: string;
    cities: { id: number; name: string }[];
  }>();
  props;
</script>

<template>
  <EventWizard mode="create" :apiUrl="apiUrl" :cities="cities" />
</template>
