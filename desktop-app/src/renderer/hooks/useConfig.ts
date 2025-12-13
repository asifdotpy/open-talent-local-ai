import { useAppContainer } from '../AppContext';
import { ConfigManager } from '../../core/config-manager';

export function useConfig(): ConfigManager {
  const c = useAppContainer();
  return c.resolve<ConfigManager>('ConfigManager');
}
