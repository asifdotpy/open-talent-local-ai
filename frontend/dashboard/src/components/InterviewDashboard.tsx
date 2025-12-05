import { Briefcase, CheckCircle, Play, Users } from 'lucide-react';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useInterviewStore } from '../stores/interviewStore';

export const InterviewDashboard = () => {
  const navigate = useNavigate();
  const { createRoom, beginInterview, isLoading, error } = useInterviewStore();
  const [candidateId, setCandidateId] = useState('');
  const [jobRole, setJobRole] = useState('');

  const jobRoles = [
    'Software Engineer',
    'Frontend Developer',
    'Backend Developer',
    'Full Stack Developer',
    'DevOps Engineer',
    'Data Scientist',
    'Product Manager',
    'UI/UX Designer',
    'QA Engineer',
    'Technical Lead'
  ];

  const handleStartInterview = async () => {
    if (!candidateId.trim() || !jobRole) {
      return;
    }

    try {
      await createRoom(candidateId.trim(), jobRole);
      await beginInterview();
      navigate('/interview');
    } catch (err) {
      console.error('Failed to start interview:', err);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <div className="flex justify-center mb-6">
          <div className="bg-blue-100 p-4 rounded-full">
            <Users className="h-12 w-12 text-blue-600" />
          </div>
        </div>
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          AI-Powered Interview Experience
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Experience the future of recruitment with our avatar-powered interview platform.
          Professional, unbiased, and comprehensive assessments.
        </p>
      </div>

      {/* Interview Setup Card */}
      <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
        <div className="flex items-center mb-6">
          <Briefcase className="h-6 w-6 text-blue-600 mr-2" />
          <h2 className="text-2xl font-semibold text-gray-900">Start Your Interview</h2>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {/* Candidate ID Input */}
          <div>
            <label htmlFor="candidateId" className="block text-sm font-medium text-gray-700 mb-2">
              Candidate ID
            </label>
            <input
              type="text"
              id="candidateId"
              value={candidateId}
              onChange={(e) => setCandidateId(e.target.value)}
              placeholder="Enter your candidate ID"
              className="w-full px-4 py-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={isLoading}
            />
          </div>

          {/* Job Role Selection */}
          <div>
            <label htmlFor="jobRole" className="block text-sm font-medium text-gray-700 mb-2">
              Job Role
            </label>
            <select
              id="jobRole"
              value={jobRole}
              onChange={(e) => setJobRole(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={isLoading}
            >
              <option value="">Select a job role</option>
              {jobRoles.map((role) => (
                <option key={role} value={role}>
                  {role}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Start Interview Button */}
        <div className="text-center">
          <button
            onClick={handleStartInterview}
            disabled={!candidateId.trim() || !jobRole || isLoading}
            className="inline-flex items-center px-8 py-4 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 focus:ring-4 focus:ring-blue-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                Starting Interview...
              </>
            ) : (
              <>
                <Play className="h-5 w-5 mr-2" />
                Start AI Interview
              </>
            )}
          </button>
        </div>
      </div>

      {/* Features Section */}
      <div className="grid md:grid-cols-3 gap-6 mb-12">
        <div className="bg-white rounded-lg shadow p-6 text-center">
          <div className="bg-green-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle className="h-6 w-6 text-green-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Professional Assessment</h3>
          <p className="text-gray-600">
            Comprehensive evaluation using industry-standard interview techniques and AI analysis.
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6 text-center">
          <div className="bg-blue-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4">
            <Users className="h-6 w-6 text-blue-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Avatar Interaction</h3>
          <p className="text-gray-600">
            Engage with AI avatars that provide a natural, human-like interview experience.
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6 text-center">
          <div className="bg-purple-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4">
            <Briefcase className="h-6 w-6 text-purple-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Role-Specific Questions</h3>
          <p className="text-gray-600">
            Tailored interview questions based on your target job role and industry standards.
          </p>
        </div>
      </div>

      {/* How It Works Section */}
      <div className="bg-white rounded-lg shadow-lg p-8">
        <h2 className="text-2xl font-semibold text-gray-900 mb-6 text-center">How It Works</h2>
        <div className="grid md:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="bg-blue-100 w-8 h-8 rounded-full flex items-center justify-center mx-auto mb-3 text-sm font-semibold text-blue-600">
              1
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">Setup</h3>
            <p className="text-sm text-gray-600">Enter your details and select your target role</p>
          </div>
          <div className="text-center">
            <div className="bg-blue-100 w-8 h-8 rounded-full flex items-center justify-center mx-auto mb-3 text-sm font-semibold text-blue-600">
              2
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">Interview</h3>
            <p className="text-sm text-gray-600">Answer questions from our AI avatar interviewer</p>
          </div>
          <div className="text-center">
            <div className="bg-blue-100 w-8 h-8 rounded-full flex items-center justify-center mx-auto mb-3 text-sm font-semibold text-blue-600">
              3
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">Analysis</h3>
            <p className="text-sm text-gray-600">AI analyzes your responses and provides feedback</p>
          </div>
          <div className="text-center">
            <div className="bg-blue-100 w-8 h-8 rounded-full flex items-center justify-center mx-auto mb-3 text-sm font-semibold text-blue-600">
              4
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">Results</h3>
            <p className="text-sm text-gray-600">Receive comprehensive assessment and recommendations</p>
          </div>
        </div>
      </div>
    </div>
  );
};