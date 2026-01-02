import React, { useEffect, useState } from 'react';
import { useQuestionBuilderStore } from '../../stores/questionBuilderStore';
import { NaturalLanguageInput } from './NaturalLanguageInput';
import { TemplateSelector } from './TemplateSelector';
import { QuestionList } from './QuestionList';
import { ExplainableAI } from './ExplainableAI';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';
import { Loader2, Sparkles, FileText, Settings } from 'lucide-react';

export const QuestionBuilder: React.FC = () => {
  const {
    templates,
    generatedQuestions,
    isLoading,
    error,
    selectedTemplateId,
    showAdvancedOptions,
    loadTemplates,
    generateQuestions,
    useTemplate,
    pinQuestion,
    unpinQuestion,
    resetQuestions,
    toggleAdvancedOptions,
    naturalLanguagePrompt,
    updatePrompt
  } = useQuestionBuilderStore();

  const [activeTab, setActiveTab] = useState<'natural' | 'templates'>('natural');

  // Load templates on mount
  useEffect(() => {
    loadTemplates();
  }, [loadTemplates]);

  const handleGenerateFromPrompt = async () => {
    if (!naturalLanguagePrompt.prompt.trim()) return;

    await generateQuestions(naturalLanguagePrompt);
  };

  const handleUseTemplate = async (templateId: string) => {
    await useTemplate(templateId);
    setActiveTab('templates');
  };

  const handleReset = () => {
    resetQuestions();
    updatePrompt({
      prompt: '',
      job_title: '',
      required_skills: [],
      company_culture: [],
      num_questions: 5,
      difficulty: 'mid_level',
      interview_duration: 45
    });
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center justify-center gap-2">
          <Sparkles className="w-8 h-8 text-blue-600" />
          AI Question Builder
        </h1>
        <p className="text-gray-600 max-w-2xl mx-auto">
          Create high-quality interview questions using natural language, inspired by PeopleGPT's conversational search paradigm.
          Generate questions that assess specific skills and competencies for any role.
        </p>
      </div>

      {/* Error Display */}
      {error && (
        <Card className="border-red-200 bg-red-50">
          <div className="text-red-800 p-4">
            <strong>Error:</strong> {error}
          </div>
        </Card>
      )}

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Panel - Input */}
        <div className="lg:col-span-2 space-y-6">
          {/* Tab Navigation */}
          <div className="flex border-b border-gray-200">
            <button
              onClick={() => setActiveTab('natural')}
              className={`flex items-center gap-2 px-4 py-2 border-b-2 font-medium text-sm ${
                activeTab === 'natural'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <Sparkles className="w-4 h-4" />
              Natural Language
            </button>
            <button
              onClick={() => setActiveTab('templates')}
              className={`flex items-center gap-2 px-4 py-2 border-b-2 font-medium text-sm ${
                activeTab === 'templates'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <FileText className="w-4 h-4" />
              Templates
            </button>
          </div>

          {/* Input Section */}
          {activeTab === 'natural' ? (
            <NaturalLanguageInput
              prompt={naturalLanguagePrompt}
              onPromptChange={updatePrompt}
              isLoading={isLoading}
              showAdvanced={showAdvancedOptions}
              onToggleAdvanced={toggleAdvancedOptions}
            />
          ) : (
            <TemplateSelector
              templates={templates}
              selectedTemplateId={selectedTemplateId}
              onSelectTemplate={handleUseTemplate}
              isLoading={isLoading}
            />
          )}

          {/* Action Buttons */}
          <div className="flex gap-3">
            <Button
              onClick={activeTab === 'natural' ? handleGenerateFromPrompt : () => selectedTemplateId && handleUseTemplate(selectedTemplateId)}
              disabled={isLoading || (activeTab === 'natural' && !naturalLanguagePrompt.prompt.trim()) || (activeTab === 'templates' && !selectedTemplateId)}
              className="flex items-center gap-2"
            >
              {isLoading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Sparkles className="w-4 h-4" />
              )}
              {isLoading ? 'Generating...' : 'Generate Questions'}
            </Button>

            {(generatedQuestions.length > 0 || selectedTemplateId) && (
              <Button
                variant="outline"
                onClick={handleReset}
                className="flex items-center gap-2"
              >
                <Settings className="w-4 h-4" />
                Reset
              </Button>
            )}
          </div>
        </div>

        {/* Right Panel - Explainable AI */}
        <div className="lg:col-span-1">
          <ExplainableAI
            questions={generatedQuestions}
            prompt={activeTab === 'natural' ? naturalLanguagePrompt.prompt : undefined}
            templateUsed={activeTab === 'templates' && selectedTemplateId ?
              templates.find(t => t.template_id === selectedTemplateId)?.template_name : undefined}
          />
        </div>
      </div>

      {/* Questions Display */}
      {generatedQuestions.length > 0 && (
        <QuestionList
          questions={generatedQuestions}
          onPinQuestion={pinQuestion}
          onUnpinQuestion={unpinQuestion}
        />
      )}
    </div>
  );
};
