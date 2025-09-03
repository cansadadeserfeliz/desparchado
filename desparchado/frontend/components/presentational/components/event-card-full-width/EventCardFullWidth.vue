<template>
  <component :is="tag" :class="[props.customClass, bem(baseClass)]" :id="id">
    <div :class="bem(baseClass, 'container')" :aria-labelledby="headingId">
      <div :class="bem(baseClass, 'date')">
        <Typography
          tag="span"
          :customClass="bem(baseClass, 'natural-day')"
          type="body_highlight"
          weight="bold"
          :text="dateCopy + ''"
        />
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
      <div :class="bem(baseClass, 'image')" role="presentation" aria-hidden="true">
        <div
          :class="bem(baseClass, 'image-asset')"
          :style="`--featured-event-card-img-url: url('${imageUrl}');`"
        ></div>
      </div>
      <div :class="bem(baseClass, 'wrapper')">
        <div :class="bem(baseClass, 'speakers')">
          <a
            :class="bem(baseClass, 'speaker-item')"
            v-for="(speaker, index) in props.speakers"
            :key="index"
            :href="speaker.link"
          >
            <img
              :class="bem(baseClass, 'speaker-avatar')"
              :src="speaker.imageUrl"
              width="30"
              role="presentation"
              aria-hidden="true"
            />
            <Typography
              tag="span"
              :customClass="bem(baseClass, 'speaker-name')"
              type="body_sm"
              :text="speaker.name"
            />
          </a>
        </div>

        <div :class="bem(baseClass, 'title')">
          <Typography
            tag="span"
            :customClass="bem(baseClass, 'location')"
            type="h5"
            :text="location"
          />
          <Typography
            tag="p"
            :customClass="bem(baseClass, 'title')"
            type="h3"
            weight="medium"
            :text="title"
            :id="headingId"
          />
        </div>
        <div :class="bem(baseClass, 'description')">
          <div class="text-body-md rich-text-description" v-html="description" />
        </div>
        <div :class="bem(baseClass, 'actions')">
          <Button
            type="secondary"
            :link="link"
            label="Ver evento"
            padding="condensed"
            :customClass="bem(baseClass, 'cta')"
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
  import Button from '@presentational_components/atoms/button/Button.vue';

  // -------- [Types] --------
  export type EventCardFullWidthTags = 'div' | 'li' | 'section' | 'article';

  export interface Speaker {
    imageUrl: string;
    name: string;
    link: string;
  }

  export interface EventCardProps {
    tag?: EventCardFullWidthTags;
    customClass?: string;
    location: string;
    title: string;
    description: string;
    day: string;
    time: string;
    // number is allowed in case the provided prop is a number from html
    dateCopy?: string | number;
    imageUrl?: string;
    link?: string;
    speakers?: Speaker[] | string;
  }

  // -------- [Props] --------
  const props = withDefaults(defineProps<EventCardProps>(), {
    tag: 'div',
  });

  const tag = props.tag;
  const id = ['event-card-full-width', generateUID()].join('-');
  const baseClass = 'event-card-full-width';
  const headingId = [id, 'title'].join('-');
</script>
