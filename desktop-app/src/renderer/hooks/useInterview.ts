import { useAppContainer } from '../AppContext';
import InterviewService from '../../services/interview-service';

export function useInterview(): InterviewService {
  const c = useAppContainer();
  return c.resolve<InterviewService>('InterviewService');
}
