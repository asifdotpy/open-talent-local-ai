import { useAppContainer } from '../AppContext';
import { EventBus } from '../../core/event-bus';

export function useEventBus(): EventBus {
  const c = useAppContainer();
  return c.resolve<EventBus>('EventBus');
}
