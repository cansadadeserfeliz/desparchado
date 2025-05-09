export const bem = (baseClass: string, suffix?: string, modifier?: string): string => {
  let className = suffix ? `${baseClass}__${suffix}` : baseClass;
  if (modifier) {
    className += `--${modifier}`;
  }
  return className;
};
