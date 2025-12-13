export interface EventMap {
  'interview:started': { role: string; model?: string };
  'interview:question-answered': { question: number; answer: string };
  'interview:completed': { totalQuestions: number };
  'ai:error': { error: Error; context: string };
  'config:updated': { key: string; value: unknown };
}
