import React, { useState } from 'react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import type { InterviewQuestion } from '../../stores/questionBuilderStore';
import { Brain, ChevronDown, ChevronUp, Lightbulb, Target, Users, Clock } from 'lucide-react';

interface ExplainableAIProps {
  questions: InterviewQuestion[];
  prompt?: string;
  templateUsed?: string;
}

export const ExplainableAI: React.FC<ExplainableAIProps> = ({
  questions,
  prompt,
  templateUsed
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  // Calculate insights
  const mustAskCount = questions.filter(q => q.priority === 'must_ask').length;
  const niceToAskCount = questions.filter(q => q.priority === 'nice_to_ask').length;
  const totalDuration = questions.reduce((total, q) => total + q.expected_duration, 0);
  const uniqueSkills = [...new Set(questions.flatMap(q => q.skill_assessed || []))];

  const getSkillFrequency = (skill: string) => {
    return questions.filter(q => q.skill_assessed?.includes(skill)).length;
  };

  const topSkills = uniqueSkills
    .map(skill => ({ skill, count: getSkillFrequency(skill) }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 5);

  return (
    <Card className="p-6">
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
              <Brain className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                AI Generation Insights
              </h3>
              <p className="text-sm text-gray-600">
                How the AI created these interview questions
              </p>
            </div>
          </div>

          <Button
            variant="outline"
            onClick={() => setIsExpanded(!isExpanded)}
            className="flex items-center gap-2"
          >
            {isExpanded ? (
              <>
                <ChevronUp className="w-4 h-4" />
                Hide Details
              </>
            ) : (
              <>
                <ChevronDown className="w-4 h-4" />
                Show Details
              </>
            )}
          </Button>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-blue-50 p-3 rounded-lg">
            <div className="flex items-center gap-2 mb-1">
              <Target className="w-4 h-4 text-blue-600" />
              <span className="text-sm font-medium text-blue-900">Questions</span>
            </div>
            <div className="text-2xl font-bold text-blue-700">{questions.length}</div>
          </div>

          <div className="bg-red-50 p-3 rounded-lg">
            <div className="flex items-center gap-2 mb-1">
              <Target className="w-4 h-4 text-red-600" />
              <span className="text-sm font-medium text-red-900">Must-Ask</span>
            </div>
            <div className="text-2xl font-bold text-red-700">{mustAskCount}</div>
          </div>

          <div className="bg-green-50 p-3 rounded-lg">
            <div className="flex items-center gap-2 mb-1">
              <Users className="w-4 h-4 text-green-600" />
              <span className="text-sm font-medium text-green-900">Nice-to-Ask</span>
            </div>
            <div className="text-2xl font-bold text-green-700">{niceToAskCount}</div>
          </div>

          <div className="bg-purple-50 p-3 rounded-lg">
            <div className="flex items-center gap-2 mb-1">
              <Clock className="w-4 h-4 text-purple-600" />
              <span className="text-sm font-medium text-purple-900">Duration</span>
            </div>
            <div className="text-2xl font-bold text-purple-700">{totalDuration}m</div>
          </div>
        </div>

        {/* Generation Method */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h4 className="font-medium text-gray-900 mb-2 flex items-center gap-2">
            <Lightbulb className="w-4 h-4" />
            Generation Method
          </h4>

          {templateUsed ? (
            <div className="space-y-2">
              <p className="text-sm text-gray-700">
                <span className="font-medium">Template Used:</span> {templateUsed}
              </p>
              <p className="text-sm text-gray-600">
                This template provided the structure and question patterns for generating
                targeted interview questions based on proven methodologies.
              </p>
            </div>
          ) : prompt ? (
            <div className="space-y-2">
              <p className="text-sm text-gray-700">
                <span className="font-medium">Natural Language Input:</span>
              </p>
              <p className="text-sm text-gray-600 bg-white p-2 rounded border italic">
                "{prompt}"
              </p>
              <p className="text-sm text-gray-600">
                The AI analyzed this description to understand the role requirements,
                candidate profile, and interview objectives.
              </p>
            </div>
          ) : (
            <p className="text-sm text-gray-600">
              Questions were generated using the default AI model with standard interview best practices.
            </p>
          )}
        </div>

        {/* Expanded Details */}
        {isExpanded && (
          <div className="space-y-4 border-t pt-4">
            {/* Skills Analysis */}
            <div>
              <h4 className="font-medium text-gray-900 mb-3 flex items-center gap-2">
                <Target className="w-4 h-4" />
                Skills Coverage Analysis
              </h4>

              <div className="space-y-2">
                <p className="text-sm text-gray-600 mb-3">
                  The AI identified and prioritized these key skills for assessment:
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {topSkills.map(({ skill, count }) => (
                    <div key={skill} className="flex items-center justify-between bg-white p-2 rounded border">
                      <span className="text-sm font-medium text-gray-900">{skill}</span>
                      <Badge variant="secondary" className="text-xs">
                        {count} question{count !== 1 ? 's' : ''}
                      </Badge>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Question Distribution */}
            <div>
              <h4 className="font-medium text-gray-900 mb-3 flex items-center gap-2">
                <Users className="w-4 h-4" />
                Question Distribution Strategy
              </h4>

              <div className="space-y-3">
                <div className="bg-red-50 p-3 rounded-lg">
                  <div className="flex items-center gap-2 mb-1">
                    <Target className="w-4 h-4 text-red-600" />
                    <span className="font-medium text-red-900">Must-Ask Questions ({mustAskCount})</span>
                  </div>
                  <p className="text-sm text-red-700">
                    Critical questions that assess core competencies and must be asked regardless
                    of time constraints. These evaluate the fundamental skills required for the role.
                  </p>
                </div>

                <div className="bg-green-50 p-3 rounded-lg">
                  <div className="flex items-center gap-2 mb-1">
                    <Users className="w-4 h-4 text-green-600" />
                    <span className="font-medium text-green-900">Nice-to-Ask Questions ({niceToAskCount})</span>
                  </div>
                  <p className="text-sm text-green-700">
                    Supplementary questions that provide additional insights but can be skipped
                    if time is limited. These explore deeper understanding and edge cases.
                  </p>
                </div>
              </div>
            </div>

            {/* AI Decision Process */}
            <div>
              <h4 className="font-medium text-gray-900 mb-3 flex items-center gap-2">
                <Brain className="w-4 h-4" />
                AI Decision Process
              </h4>

              <div className="space-y-2 text-sm text-gray-600">
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-xs font-medium text-blue-700">1</span>
                  </div>
                  <p>Analyzed the job requirements and candidate profile to identify key skills and competencies</p>
                </div>

                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-xs font-medium text-blue-700">2</span>
                  </div>
                  <p>Determined question priority based on skill importance and assessment criticality</p>
                </div>

                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-xs font-medium text-blue-700">3</span>
                  </div>
                  <p>Generated questions with expected answers and follow-up scenarios</p>
                </div>

                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-xs font-medium text-blue-700">4</span>
                  </div>
                  <p>Estimated time duration and assigned scoring criteria for evaluation</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* PeopleGPT Pattern Note */}
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <Brain className="w-5 h-5 text-purple-600 mt-0.5" />
            <div>
              <h4 className="font-medium text-purple-900 mb-1">
                PeopleGPT-Inspired Transparency
              </h4>
              <p className="text-sm text-purple-700">
                Like PeopleGPT's explainable AI recommendations, this section shows exactly how the AI
                analyzed your requirements and generated targeted interview questions. Understanding the
                AI's decision process helps you trust and refine the generated content.
              </p>
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
};
