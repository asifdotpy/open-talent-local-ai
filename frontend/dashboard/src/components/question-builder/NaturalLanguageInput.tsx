import React from 'react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { Textarea } from '../ui/Textarea';
import { Input } from '../ui/Input';
import { Badge } from '../ui/Badge';
import { ChevronDown, ChevronUp, Plus, X } from 'lucide-react';
import type { NaturalLanguagePrompt } from '../../stores/questionBuilderStore';

interface NaturalLanguageInputProps {
  prompt: NaturalLanguagePrompt;
  onPromptChange: (updates: Partial<NaturalLanguagePrompt>) => void;
  isLoading: boolean;
  showAdvanced: boolean;
  onToggleAdvanced: () => void;
}

const EXAMPLE_PROMPTS = [
  "Create questions to assess system design skills for senior backend engineer",
  "Generate behavioral questions for a product manager focused on stakeholder management",
  "Design technical questions for a data scientist with ML experience",
  "Build questions to evaluate leadership skills for engineering managers",
  "Create questions for assessing frontend development skills with React"
];

const DIFFICULTY_OPTIONS = [
  { value: 'junior', label: 'Junior (0-2 years)' },
  { value: 'mid_level', label: 'Mid-Level (3-5 years)' },
  { value: 'senior', label: 'Senior (5-8 years)' },
  { value: 'principal', label: 'Principal (8+ years)' },
  { value: 'executive', label: 'Executive' }
];

export const NaturalLanguageInput: React.FC<NaturalLanguageInputProps> = ({
  prompt,
  onPromptChange,
  isLoading,
  showAdvanced,
  onToggleAdvanced
}) => {
  const handleSkillAdd = (skill: string) => {
    if (skill.trim() && !prompt.required_skills?.includes(skill.trim())) {
      onPromptChange({
        required_skills: [...(prompt.required_skills || []), skill.trim()]
      });
    }
  };

  const handleSkillRemove = (skill: string) => {
    onPromptChange({
      required_skills: prompt.required_skills?.filter(s => s !== skill) || []
    });
  };

  const handleCultureAdd = (culture: string) => {
    if (culture.trim() && !prompt.company_culture?.includes(culture.trim())) {
      onPromptChange({
        company_culture: [...(prompt.company_culture || []), culture.trim()]
      });
    }
  };

  const handleCultureRemove = (culture: string) => {
    onPromptChange({
      company_culture: prompt.company_culture?.filter(c => c !== culture) || []
    });
  };

  return (
    <Card className="p-6">
      <div className="space-y-6">
        {/* Main Prompt Input */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Describe what you want to assess
          </label>
          <Textarea
            value={prompt.prompt}
            onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => onPromptChange({ prompt: e.target.value })}
            placeholder="e.g., Create questions to assess system design skills for senior backend engineers..."
            className="min-h-24 resize-none"
            disabled={isLoading}
          />

          {/* Example Prompts */}
          <div className="mt-3">
            <p className="text-sm text-gray-500 mb-2">Try these examples:</p>
            <div className="flex flex-wrap gap-2">
              {EXAMPLE_PROMPTS.slice(0, 3).map((example, index) => (
                <button
                  key={index}
                  onClick={() => onPromptChange({ prompt: example })}
                  className="text-xs bg-blue-50 text-blue-700 px-3 py-1 rounded-full hover:bg-blue-100 transition-colors"
                  disabled={isLoading}
                >
                  {example}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Advanced Options Toggle */}
        <div className="border-t pt-4">
          <button
            onClick={onToggleAdvanced}
            className="flex items-center gap-2 text-sm font-medium text-gray-700 hover:text-gray-900"
          >
            {showAdvanced ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            Advanced Options
          </button>
        </div>

        {/* Advanced Options */}
        {showAdvanced && (
          <div className="space-y-4 border-t pt-4">
            {/* Job Title */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Job Title (Optional)
              </label>
              <Input
                value={prompt.job_title || ''}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => onPromptChange({ job_title: e.target.value })}
                placeholder="e.g., Senior Backend Engineer"
                disabled={isLoading}
              />
            </div>

            {/* Required Skills */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Required Skills
              </label>
              <div className="flex gap-2 mb-2">
                <Input
                  placeholder="Add a skill..."
                  onKeyPress={(e: React.KeyboardEvent<HTMLInputElement>) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      const input = e.target as HTMLInputElement;
                      handleSkillAdd(input.value);
                      input.value = '';
                    }
                  }}
                  disabled={isLoading}
                  className="flex-1"
                />
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    const input = document.querySelector('input[placeholder="Add a skill..."]') as HTMLInputElement;
                    if (input?.value) {
                      handleSkillAdd(input.value);
                      input.value = '';
                    }
                  }}
                  disabled={isLoading}
                >
                  <Plus className="w-4 h-4" />
                </Button>
              </div>
              <div className="flex flex-wrap gap-2">
                {prompt.required_skills?.map((skill) => (
                  <Badge key={skill} variant="secondary" className="flex items-center gap-1">
                    {skill}
                    <button
                      onClick={() => handleSkillRemove(skill)}
                      className="ml-1 hover:bg-gray-200 rounded-full p-0.5"
                      disabled={isLoading}
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </Badge>
                ))}
              </div>
            </div>

            {/* Company Culture */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Company Culture
              </label>
              <div className="flex gap-2 mb-2">
                <Input
                  placeholder="Add culture value..."
                  onKeyPress={(e: React.KeyboardEvent<HTMLInputElement>) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      const input = e.target as HTMLInputElement;
                      handleCultureAdd(input.value);
                      input.value = '';
                    }
                  }}
                  disabled={isLoading}
                  className="flex-1"
                />
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    const input = document.querySelector('input[placeholder="Add culture value..."]') as HTMLInputElement;
                    if (input?.value) {
                      handleCultureAdd(input.value);
                      input.value = '';
                    }
                  }}
                  disabled={isLoading}
                >
                  <Plus className="w-4 h-4" />
                </Button>
              </div>
              <div className="flex flex-wrap gap-2">
                {prompt.company_culture?.map((culture) => (
                  <Badge key={culture} variant="outline" className="flex items-center gap-1">
                    {culture}
                    <button
                      onClick={() => handleCultureRemove(culture)}
                      className="ml-1 hover:bg-gray-200 rounded-full p-0.5"
                      disabled={isLoading}
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </Badge>
                ))}
              </div>
            </div>

            {/* Number of Questions & Difficulty */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Number of Questions
                </label>
                <Input
                  type="number"
                  min="1"
                  max="20"
                  value={prompt.num_questions || 5}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => onPromptChange({ num_questions: parseInt(e.target.value) || 5 })}
                  disabled={isLoading}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Difficulty Level
                </label>
                <select
                  value={prompt.difficulty || 'mid_level'}
                  onChange={(e) => onPromptChange({ difficulty: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isLoading}
                >
                  {DIFFICULTY_OPTIONS.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Interview Duration */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Interview Duration (minutes)
              </label>
              <Input
                type="number"
                min="15"
                max="120"
                value={prompt.interview_duration || 45}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => onPromptChange({ interview_duration: parseInt(e.target.value) || 45 })}
                disabled={isLoading}
              />
            </div>
          </div>
        )}
      </div>
    </Card>
  );
};