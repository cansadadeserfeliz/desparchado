<template>
  <component :is="tag" :class="[props.customClass, bem(baseClass)]" :id="id">
    <div :class="bem(baseClass, 'container')" :aria-labelledby="headingId">
      <div :class="bem(baseClass, 'image')" role="presentation" aria-hidden="true">
        <div
          :class="bem(baseClass, 'image-asset')"
          :style="`--featured-event-card-img-url: url('${imageUrl}');`"
        ></div>
      </div>
      <div :class="bem(baseClass, 'wrapper')" :aria-labelledby="headingId">
        <div :class="bem(baseClass, 'details')" :aria-labelledby="headingId">
          <Typography
            tag="span"
            :customClass="bem(baseClass, 'location')"
            type="caption"
            :text="location"
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
        <Typography
          tag="p"
          :customClass="bem(baseClass, 'title')"
          type="h5"
          weight="medium"
          :text="title"
          :id="headingId"
        />
        <Typography
          tag="p"
          :customClass="bem(baseClass, 'description')"
          type="body_sm"
          weight="regular"
          :text="description"
        />
        <Button
          type="secondary"
          link="#"
          label="Leer más"
          padding="condensed"
          :customClass="bem(baseClass, 'cta')"
        />
      </div>
    </div>
  </component>
</template>

<script lang="ts" setup>
  import Typography from '@presentational_components/foundation/typography/Typography.vue';
  import { generateUID } from '../../../../scripts/utils/generate-uid';
  import './styles.scss';
  import { bem } from '../../../../scripts/utils/bem';
  import Button from '@presentational_components/atoms/button/Button.vue';

  // -------- [Types] --------
  type FeaturedEventTags = 'div' | 'li' | 'section' | 'article';

  // -------- [Props] --------
  const props = withDefaults(
    defineProps<{
      tag?: FeaturedEventTags;
      customClass?: string;
      location: string;
      title: string;
      description: string;
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
  const id = ['event-card', generateUID()].join('-');

  const baseClass = 'event-card';

  const headingId = [id, 'title'].join('-');
</script>
