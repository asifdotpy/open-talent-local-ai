import React from 'react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { FileText, Users, Clock, Sparkles, Loader2 } from 'lucide-react';
import type { QuestionTemplate } from '../../stores/questionBuilderStore';

interface TemplateSelectorProps {
  templates: QuestionTemplate[];
  selectedTemplateId: string | null;
  onSelectTemplate: (templateId: string) => void;
  isLoading: boolean;
}

export const TemplateSelector: React.FC<TemplateSelectorProps> = ({
  templates,
  selectedTemplateId,
  onSelectTemplate,
  isLoading
}) => {
  return (
    <Card className="p-6">
      <div className="space-y-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2 flex items-center gap-2">
            <FileText className="w-5 h-5" />
            Question Templates
          </h3>
          <p className="text-gray-600 text-sm">
            Choose from pre-built templates designed for common roles and scenarios.
            Templates are inspired by PeopleGPT's "General Presets" pattern.
          </p>
        </div>

        {templates.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>No templates available</p>
          </div>
        ) : (
          <div className="grid gap-4">
            {templates.map((template) => (
              <div
                key={template.template_id}
                className={`border rounded-lg p-4 cursor-pointer transition-all ${
                  selectedTemplateId === template.template_id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => onSelectTemplate(template.template_id)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 mb-1">
                      {template.template_name}
                    </h4>
                    <p className="text-sm text-gray-600 mb-3">
                      {template.description}
                    </p>

                    <div className="flex items-center gap-4 text-xs text-gray-500 mb-3">
                      <div className="flex items-center gap-1">
                        <Users className="w-3 h-3" />
                        {template.questions.length} questions
                      </div>
                      <div className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {template.questions.reduce((total, q) => total + q.expected_duration, 0)} min
                      </div>
                      <div className="flex items-center gap-1">
                        <Sparkles className="w-3 h-3" />
                        Used {template.usage_count} times
                      </div>
                    </div>

                    <div className="flex flex-wrap gap-1">
                      {template.job_roles.slice(0, 3).map((role) => (
                        <Badge key={role} variant="outline" className="text-xs">
                          {role}
                        </Badge>
                      ))}
                      {template.job_roles.length > 3 && (
                        <Badge variant="outline" className="text-xs">
                          +{template.job_roles.length - 3} more
                        </Badge>
                      )}
                    </div>
                  </div>

                  <div className="ml-4">
                    <Button
                      size="sm"
                      variant={selectedTemplateId === template.template_id ? "default" : "outline"}
                      disabled={isLoading}
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectTemplate(template.template_id);
                      }}
                      className="flex items-center gap-2"
                    >
                      {isLoading && selectedTemplateId === template.template_id ? (
                        <Loader2 className="w-3 h-3 animate-spin" />
                      ) : (
                        <FileText className="w-3 h-3" />
                      )}
                      {selectedTemplateId === template.template_id ? 'Selected' : 'Select'}
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="border-t pt-4 mt-6">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <Sparkles className="w-5 h-5 text-blue-600 mt-0.5" />
              <div>
                <h4 className="font-medium text-blue-900 mb-1">
                  PeopleGPT-Inspired Templates
                </h4>
                <p className="text-sm text-blue-700">
                  These templates follow the same pattern as PeopleGPT's "B2B Startups", "Fortune 50", and "Enterprise SaaS" presets.
                  Each template is optimized for specific roles and experience levels.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
};