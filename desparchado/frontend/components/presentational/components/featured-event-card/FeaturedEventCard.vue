<template>
  <component :is="tag" :class="classes" :id="id">
    <div :class="bem()" :aria-labelledby="headingId">
      <div :class="bem('image')" role="presentation" aria-hidden="true">
        <img :src="imageUrl" />
      </div>
      <div :class="bem('wrapper')" :aria-labelledby="headingId">
        <Typography tag="span" :customClass="bem('location')" type="caption" :text="location" />
        <Typography tag="span" :customClass="bem('date-copy')" type="caption" :text="dateCopy" />
        <Typography
          tag="p"
          :customClass="bem('title')"
          type="h5"
          weight="medium"
          :text="title"
          :id="headingId"
        />
        <div :class="bem('date')">
          <Typography
            tag="span"
            :customClass="bem('day')"
            type="body_highlight"
            weight="bold"
            :text="day"
          />
          <Typography
            tag="span"
            :customClass="bem('time')"
            type="body_highlight"
            weight="medium"
            :text="time"
          />
        </div>
      </div>
    </div>
  </component>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import Typography from '@presentational_components/foundation/typography/Typography.vue';
  import { generateUID } from '../../../../scripts/utils/generate-uid';
  import './styles.scss';

  // -------- [Types] --------
  type FeaturedEventTags = 'div' | 'li' | 'section' | 'article';

  // -------- [Props] --------
  const props = withDefaults(
    defineProps<{
      tag?: FeaturedEventTags;
      customClass?: string;
      location: string;
      title: string;
      day: string;
      time: string;
      imageUrl?: string;
    }>(),
    {
      tag: 'div',
      imageUrl: 'https://desparchado.co/media/events/images_6.jpeg',
    },
  );
  const tag = props.tag;
  const id = ['feature-event-card', generateUID()].join('-');

  const baseClass = 'featured-event-card';
  const bem = (suffix?: string) => (suffix ? `${baseClass}__${suffix}` : baseClass);
  const classes = computed(() => [props.customClass].filter(Boolean).join(' '));

  const headingId = [id, 'title'].join('-');
  const dateCopy = 'Proximo mes';
</script>
