import { EventBus } from '../event-bus';
import { EventMap } from '../event-types';

describe('EventBus', () => {
  it('calls listeners when events are emitted', () => {
    const bus = new EventBus();
    let called = 0;
    const listener = () => {
      called += 1;
    };
    bus.on('interview:started', listener as (data: EventMap['interview:started']) => void);
    bus.emit('interview:started', { role: 'Software Engineer', model: 'granite-code:3b' });
    expect(called).toBe(1);
  });

  it('removes listeners with off()', () => {
    const bus = new EventBus();
    let called = 0;
    const listener = () => {
      called += 1;
    };
    const typedListener = listener as (data: EventMap['interview:completed']) => void;
    bus.on('interview:completed', typedListener);
    bus.off('interview:completed', typedListener);
    bus.emit('interview:completed', { totalQuestions: 5 });
    expect(called).toBe(0);
  });
});
