<template>
  <header :class="bem(baseClass)">
    <div :class="bem(baseClass, 'wrapper')">
      <a href="/" :class="bem(baseClass, 'logo')" :aria-label="props.brandName">
        <Logo type="imagotype" :customClass="bem(baseClass, 'logo', 'large')" />
        <Logo type="isotype" :customClass="bem(baseClass, 'logo', 'small')" />
      </a>
      <div :class="bem(baseClass, 'nav-group')">
        <NavItem
          v-for="(navItem, index) in props.navItems"
          :key="index"
          :label="navItem.label"
          :link="navItem.link"
          :highlight="navItem.highlight"
        />
      </div>
      <div :class="bem(baseClass, 'actions')">
        <MenuDropdown
          v-if="logged"
          :items="props.profileMenu.items"
          :customClass="bem(baseClass, 'profile')"
          :name="props.profileMenu.name"
        />
        <Button
          v-if="!logged"
          :type="props.login.type"
          :link="props.login.link"
          :label="props.login.label"
        />
        <Button
          :type="props.createEvent.type"
          :link="props.createEvent.link"
          :label="props.createEvent.label"
          customClass="excluded-from-mobile"
        />
      </div>
      <div :class="bem(baseClass, 'social')">
        <Button
          v-for="(social, index) in props.social"
          :key="index"
          type="tertiary"
          padding="balanced"
          radius="soft"
          :name="social.name"
          :customClass="bem(baseClass, 'social-item')"
          :icon="social.icon"
        />
      </div>
    </div>
    <div :class="[bem(baseClass, 'mobile-actions'), 'excluded-from-desktop']">
      <Button
        :type="props.createEvent.type"
        :link="props.createEvent.link"
        :label="props.createEvent.label"
        customClass="excluded-from-desktop"
      />
    </div>
  </header>
</template>

<script lang="ts" setup>
  import './styles.scss';
  import { bem } from '../../../../scripts/utils/bem';
  import NavItem, { NavItemProps } from '@presentational_components/atoms/nav-item/NavItem.vue';
  import Button, { ButtonProps } from '@presentational_components/atoms/button/Button.vue';
  import Logo from '@presentational_components/atoms/logo/Logo.vue';
  import MenuDropdown, {
    MenuDropdownProps,
  } from '@presentational_components/components/menu-dropdown/MenuDropdown.vue';

  export interface HeaderProps {
    brandName?: string;
    navItems: Array<NavItemProps>;
    social: Array<ButtonProps>;
    profileMenu: MenuDropdownProps;
    login: ButtonProps;
    createEvent: ButtonProps;
  }

  const logged = false; // This should be replaced with a prop or a store value in the future

  const props = defineProps<HeaderProps>();

  // -------- [Props] --------
  const baseClass = 'header';
</script>
