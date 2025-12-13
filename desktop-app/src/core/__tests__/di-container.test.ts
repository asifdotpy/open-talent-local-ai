import { DIContainer } from '../di-container';

describe('DIContainer', () => {
  it('resolves a registered factory and caches instance', () => {
    const c = new DIContainer();
    const obj = { name: 'test' };
    c.register('S', () => obj);

    const a = c.resolve<typeof obj>('S');
    const b = c.resolve<typeof obj>('S');
    expect(a).toBe(obj);
    expect(b).toBe(obj);
  });

  it('resolves a registered singleton', () => {
    const c = new DIContainer();
    const singleton = { id: 1 };
    c.registerSingleton('One', singleton);
    expect(c.resolve<typeof singleton>('One')).toBe(singleton);
  });

  it('throws when resolving unknown service', () => {
    const c = new DIContainer();
    expect(() => c.resolve('Unknown')).toThrow('Service not registered: Unknown');
  });
});
