import React from 'react';
import { Card } from '../ui/Card';
import { QuestionCard } from './QuestionCard';
import type { InterviewQuestion } from '../../stores/questionBuilderStore';
import { CheckCircle, Clock, Users } from 'lucide-react';

interface QuestionListProps {
  questions: InterviewQuestion[];
  onPinQuestion: (index: number) => void;
  onUnpinQuestion: (index: number) => void;
}

export const QuestionList: React.FC<QuestionListProps> = ({
  questions,
  onPinQuestion,
  onUnpinQuestion
}) => {
  const mustAskCount = questions.filter(q => q.priority === 'must_ask').length;
  const niceToAskCount = questions.filter(q => q.priority === 'nice_to_ask').length;
  const totalDuration = questions.reduce((total, q) => total + q.expected_duration, 0);

  return (
    <Card className="p-6">
      <div className="space-y-6">
        {/* Header with Stats */}
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              Generated Questions
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              Review and customize your interview questions
            </p>
          </div>

          <div className="flex items-center gap-4 text-sm text-gray-600">
            <div className="flex items-center gap-1">
              <CheckCircle className="w-4 h-4 text-red-500" />
              <span className="font-medium">{mustAskCount}</span> must-ask
            </div>
            <div className="flex items-center gap-1">
              <Users className="w-4 h-4 text-green-500" />
              <span className="font-medium">{niceToAskCount}</span> nice-to-ask
            </div>
            <div className="flex items-center gap-1">
              <Clock className="w-4 h-4 text-blue-500" />
              <span className="font-medium">{totalDuration}</span> min total
            </div>
          </div>
        </div>

        {/* Questions List */}
        <div className="space-y-4">
          {questions.map((question, index) => (
            <QuestionCard
              key={index}
              question={question}
              index={index}
              onPin={() => onPinQuestion(index)}
              onUnpin={() => onUnpinQuestion(index)}
            />
          ))}
        </div>

        {/* Summary */}
        {questions.length > 0 && (
          <div className="border-t pt-4">
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-2">Interview Summary</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <div className="text-gray-500">Total Questions</div>
                  <div className="font-semibold text-gray-900">{questions.length}</div>
                </div>
                <div>
                  <div className="text-gray-500">Must-Ask</div>
                  <div className="font-semibold text-red-600">{mustAskCount}</div>
                </div>
                <div>
                  <div className="text-gray-500">Nice-to-Ask</div>
                  <div className="font-semibold text-green-600">{niceToAskCount}</div>
                </div>
                <div>
                  <div className="text-gray-500">Duration</div>
                  <div className="font-semibold text-blue-600">{totalDuration} min</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* PeopleGPT Pattern Note */}
        <div className="border-t pt-4">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-blue-600 mt-0.5" />
              <div>
                <h4 className="font-medium text-blue-900 mb-1">
                  PeopleGPT-Inspired Pinning
                </h4>
                <p className="text-sm text-blue-700">
                  Like PeopleGPT's pinned skills, questions marked as "must-ask" are prioritized during interviews.
                  These are the critical questions that assess core competencies and must be asked regardless of time constraints.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
};