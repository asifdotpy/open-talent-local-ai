import { AlertCircle, CheckCircle, Clock, Download, RefreshCw, Star, Target, Trophy, XCircle } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useInterviewStore } from '../stores/interviewStore';

interface AssessmentResult {
  category: string;
  score: number;
  maxScore: number;
  feedback: string;
  strengths: string[];
  improvements: string[];
}

export const ResultsPage = () => {
  const navigate = useNavigate();
  const { currentRoom, getInterviewResults, isLoading, error } = useInterviewStore();
  const [results, setResults] = useState<AssessmentResult[] | null>(null);

  useEffect(() => {
    const loadResults = async () => {
      if (!currentRoom) {
        navigate('/');
        return;
      }

      try {
        const interviewResults = await getInterviewResults();
        setResults(interviewResults);
      } catch (err) {
        console.error('Failed to load results:', err);
      }
    };

    loadResults();
  }, [currentRoom, getInterviewResults, navigate]);

  const handleStartNewInterview = () => {
    navigate('/');
  };

  const handleDownloadReport = () => {
    // TODO: Implement PDF report generation
    console.log('Downloading report...');
  };

  if (!currentRoom) {
    return (
      <div className="max-w-4xl mx-auto text-center py-12">
        <p className="text-gray-600">No interview results available. Please start a new interview.</p>
      </div>
    );
  }

  const overallScore = results ? Math.round(results.reduce((sum, r) => sum + (r.score / r.maxScore), 0) / results.length * 100) : 0;
  const totalQuestions = currentRoom.questions.length;
  const answeredQuestions = currentRoom.answers.length;

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
          <CheckCircle className="h-8 w-8 text-green-600" />
        </div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Interview Complete!</h1>
        <p className="text-lg text-gray-600">
          Thank you for completing your {currentRoom.job_role} interview assessment
        </p>
      </div>

      {/* Overall Score Card */}
      <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-24 h-24 bg-blue-100 rounded-full mb-4">
            <Trophy className="h-12 w-12 text-blue-600" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Overall Score</h2>
          <div className="text-6xl font-bold text-blue-600 mb-4">{overallScore}%</div>
          <div className="flex items-center justify-center space-x-6 text-sm text-gray-600">
            <div className="flex items-center">
              <Target className="h-4 w-4 mr-1" />
              <span>{answeredQuestions}/{totalQuestions} Questions Answered</span>
            </div>
            <div className="flex items-center">
              <Clock className="h-4 w-4 mr-1" />
              <span>Completed in {Math.round(currentRoom.duration / 60)} minutes</span>
            </div>
          </div>
        </div>
      </div>

      {/* Detailed Results */}
      {results && (
        <div className="grid lg:grid-cols-2 gap-8 mb-8">
          {results.map((result, index) => (
            <div key={index} className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">{result.category}</h3>
                <div className="flex items-center">
                  <Star className="h-5 w-5 text-yellow-400 mr-1" />
                  <span className="text-lg font-bold text-gray-900">
                    {result.score}/{result.maxScore}
                  </span>
                </div>
              </div>

              <div className="mb-4">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full"
                    style={{ width: `${(result.score / result.maxScore) * 100}%` }}
                  ></div>
                </div>
                <p className="text-sm text-gray-600 mt-1">
                  {Math.round((result.score / result.maxScore) * 100)}% score
                </p>
              </div>

              <p className="text-gray-700 mb-4">{result.feedback}</p>

              {/* Strengths */}
              {result.strengths.length > 0 && (
                <div className="mb-4">
                  <h4 className="text-sm font-semibold text-green-700 mb-2 flex items-center">
                    <CheckCircle className="h-4 w-4 mr-1" />
                    Strengths
                  </h4>
                  <ul className="space-y-1">
                    {result.strengths.map((strength, i) => (
                      <li key={i} className="text-sm text-green-700 flex items-start">
                        <span className="w-1.5 h-1.5 bg-green-500 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                        {strength}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Areas for Improvement */}
              {result.improvements.length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold text-orange-700 mb-2 flex items-center">
                    <AlertCircle className="h-4 w-4 mr-1" />
                    Areas for Improvement
                  </h4>
                  <ul className="space-y-1">
                    {result.improvements.map((improvement, i) => (
                      <li key={i} className="text-sm text-orange-700 flex items-start">
                        <span className="w-1.5 h-1.5 bg-orange-500 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                        {improvement}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Loading State */}
      {isLoading && !results && (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Generating your assessment results...</p>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 mb-8">
          <div className="flex items-center">
            <XCircle className="h-5 w-5 text-red-500 mr-3" />
            <div>
              <h3 className="text-sm font-medium text-red-800">Error Loading Results</h3>
              <p className="text-sm text-red-700 mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-4 justify-center">
        <button
          onClick={handleStartNewInterview}
          className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
        >
          <RefreshCw className="h-5 w-5 mr-2" />
          Start New Interview
        </button>

        <button
          onClick={handleDownloadReport}
          disabled={!results}
          className="inline-flex items-center px-6 py-3 bg-gray-200 text-gray-700 font-semibold rounded-lg hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <Download className="h-5 w-5 mr-2" />
          Download Report
        </button>
      </div>

      {/* Next Steps */}
      <div className="mt-12 bg-blue-50 rounded-lg p-8">
        <h3 className="text-xl font-semibold text-blue-900 mb-4">What's Next?</h3>
        <div className="grid md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <span className="text-blue-600 font-bold">1</span>
            </div>
            <h4 className="font-semibold text-blue-900 mb-2">Review Feedback</h4>
            <p className="text-sm text-blue-700">
              Take time to review your detailed feedback and identify areas for growth
            </p>
          </div>

          <div className="text-center">
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <span className="text-blue-600 font-bold">2</span>
            </div>
            <h4 className="font-semibold text-blue-900 mb-2">Practice More</h4>
            <p className="text-sm text-blue-700">
              Consider taking additional practice interviews to improve your skills
            </p>
          </div>

          <div className="text-center">
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <span className="text-blue-600 font-bold">3</span>
            </div>
            <h4 className="font-semibold text-blue-900 mb-2">Apply Your Skills</h4>
            <p className="text-sm text-blue-700">
              Use what you've learned in real job interviews and professional situations
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
