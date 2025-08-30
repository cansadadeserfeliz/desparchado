<template>
  <component :is="link ? 'a' : tag" :href="link" :class="[props.customClass, bem(baseClass)]" :id="id">
    <div :class="bem(baseClass, 'container')" :aria-labelledby="headingId">
      <div :class="bem(baseClass, 'image')" role="presentation" aria-hidden="true">
        <div
          :class="bem(baseClass, 'image-asset')"
          :style="`--featured-event-card-img-url: url('${imageUrl}');`"
        ></div>
      </div>
      <div :class="bem(baseClass, 'wrapper')" :aria-labelledby="headingId">
        <Typography
          tag="span"
          :customClass="bem(baseClass, 'location')"
          type="caption"
          :text="location"
        />
        <Typography
          tag="span"
          :customClass="bem(baseClass, 'date-copy')"
          type="caption"
          :text="dateCopy"
        />
        <Typography
          tag="p"
          :customClass="bem(baseClass, 'title')"
          type="h5"
          weight="medium"
          :text="title"
          :id="headingId"
        />
        <div :class="bem(baseClass, 'date')">
          <Typography
            tag="span"
            :customClass="bem(baseClass, 'day')"
            type="body_highlight"
            weight="bold"
            :text="day"
          />
          <Typography
            tag="span"
            :customClass="bem(baseClass, 'time')"
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
  import Typography from '@presentational_components/foundation/typography/Typography.vue';
  import { generateUID } from '../../../../scripts/utils/generate-uid';
  import './styles.scss';
  import { bem } from '../../../../scripts/utils/bem';

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
      link?: string;
      dateCopy?: string;
    }>(),
    {
      tag: 'div',
      imageUrl: 'https://desparchado.co/media/events/images_6.jpeg',
    },
  );
  const tag = props.tag;
  const id = ['feature-event-card', generateUID()].join('-');

  const baseClass = 'featured-event-card';

  const headingId = [id, 'title'].join('-');
</script>
