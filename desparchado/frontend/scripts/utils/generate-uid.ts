export const generateUID = (): string => 'uid-' + Math.random().toString(36).slice(2, 11);
