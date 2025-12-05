import React, { useState } from 'react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import type { InterviewQuestion } from '../../stores/questionBuilderStore';
import { Pin, PinOff, Clock, MessageSquare, Edit, Trash2 } from 'lucide-react';

interface QuestionCardProps {
  question: InterviewQuestion;
  index: number;
  onPin: () => void;
  onUnpin: () => void;
}

export const QuestionCard: React.FC<QuestionCardProps> = ({
  question,
  index,
  onPin,
  onUnpin
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'must_ask':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'nice_to_ask':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'must_ask':
        return <Pin className="w-3 h-3" />;
      case 'nice_to_ask':
        return <MessageSquare className="w-3 h-3" />;
      default:
        return null;
    }
  };

  return (
    <Card className="p-4 hover:shadow-md transition-shadow">
      <div className="space-y-3">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-3 flex-1">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                <span className="text-sm font-medium text-blue-700">
                  {index + 1}
                </span>
              </div>
            </div>

            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-2">
                <Badge
                  variant="outline"
                  className={getPriorityColor(question.priority)}
                >
                  {getPriorityIcon(question.priority)}
                  <span className="ml-1 capitalize">
                    {question.priority.replace('_', '-')}
                  </span>
                </Badge>

                <div className="flex items-center gap-1 text-sm text-gray-500">
                  <Clock className="w-4 h-4" />
                  <span>{question.expected_duration} min</span>
                </div>
              </div>

              <h4 className="font-medium text-gray-900 mb-1">
                {question.question_text}
              </h4>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-1 ml-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={question.priority === 'must_ask' ? onUnpin : onPin}
              className="h-8 w-8 p-0"
            >
              {question.priority === 'must_ask' ? (
                <PinOff className="w-4 h-4 text-red-500" />
              ) : (
                <Pin className="w-4 h-4 text-gray-400" />
              )}
            </Button>

            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsExpanded(!isExpanded)}
              className="h-8 w-8 p-0"
            >
              <Edit className="w-4 h-4" />
            </Button>

            <Button
              variant="ghost"
              size="sm"
              className="h-8 w-8 p-0 text-red-500 hover:text-red-700"
            >
              <Trash2 className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Expanded Content */}
        {isExpanded && (
          <div className="border-t pt-3 mt-3">
            <div className="space-y-3">
              {/* Skills */}
              {question.skill_assessed && question.skill_assessed.length > 0 && (
                <div>
                  <label className="text-sm font-medium text-gray-700 mb-1 block">
                    Skills Assessed
                  </label>
                  <div className="flex flex-wrap gap-1">
                    {question.skill_assessed.map((skill, skillIndex) => (
                      <Badge key={skillIndex} variant="secondary" className="text-xs">
                        {skill}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* Follow-up Questions */}
              {question.follow_up_questions && question.follow_up_questions.length > 0 && (
                <div>
                  <label className="text-sm font-medium text-gray-700 mb-1 block">
                    Follow-up Questions
                  </label>
                  <ul className="text-sm text-gray-600 space-y-1">
                    {question.follow_up_questions.map((followUp, followUpIndex) => (
                      <li key={followUpIndex} className="flex items-start gap-2">
                        <span className="text-gray-400 mt-1">•</span>
                        <span>{followUp}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Evaluation Criteria */}
              {question.evaluation_criteria && question.evaluation_criteria.length > 0 && (
                <div>
                  <label className="text-sm font-medium text-gray-700 mb-1 block">
                    Evaluation Criteria
                  </label>
                  <ul className="text-sm text-gray-600 space-y-1">
                    {question.evaluation_criteria.map((criteria, criteriaIndex) => (
                      <li key={criteriaIndex} className="flex items-start gap-2">
                        <span className="text-gray-400 mt-1">•</span>
                        <span>{criteria}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}

        {/* PeopleGPT Pattern Note */}
        {question.priority === 'must_ask' && (
          <div className="bg-red-50 border border-red-200 rounded p-2 mt-3">
            <div className="flex items-center gap-2">
              <Pin className="w-4 h-4 text-red-600" />
              <span className="text-sm text-red-700">
                This question is pinned as "must-ask" - it will be prioritized during the interview
              </span>
            </div>
          </div>
        )}
      </div>
    </Card>
  );
};