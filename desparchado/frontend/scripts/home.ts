import '../styles/pages/home.scss';
import { EventContainer } from './event-container';
import { attachOnLoadListener } from './utils/page-load-listener';

const registry = new Map([['event-container', EventContainer]]);

attachOnLoadListener(registry);
