import { OrbitControls, PerspectiveCamera } from '@react-three/drei';
import { Canvas } from '@react-three/fiber';
import { Mic, MicOff, Send, SkipForward, Video } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useInterviewStore } from '../stores/interviewStore';
import { Avatar } from './Avatar';
import { AvatarSelector } from './AvatarSelector';
import { LiveTranscription } from './LiveTranscription';

export const InterviewInterface = () => {
  const navigate = useNavigate();
  const {
    currentRoom,
    currentQuestion,
    getNextQuestion,
    submitAnswer,
    completeInterview,
    initializeWebRTC,
    startWebRTC,
    isWebRTCConnected,
    isLoading,
    error,
    currentAvatar,
    initializeAvatars,
    isAvatarLoading,
    avatarError
  } = useInterviewStore();

  const [answer, setAnswer] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [audioUrl, _setAudioUrl] = useState<string | null>(null);

  useEffect(() => {
    // Initialize avatars when component mounts
    if (!currentAvatar && !isAvatarLoading) {
      initializeAvatars();
    }

    // Initialize WebRTC when room is created
    if (currentRoom && !isWebRTCConnected) {
      initializeWebRTC().then(() => {
        startWebRTC();
      });
    }

    // Load first question when room begins
    if (currentRoom && currentRoom.status === 'in_progress' && !currentQuestion && !isLoading) {
      getNextQuestion();
    }
  }, [currentRoom, currentQuestion, isLoading, getNextQuestion, currentAvatar, isAvatarLoading, initializeAvatars, isWebRTCConnected, initializeWebRTC, startWebRTC]);

  const handleSubmitAnswer = async () => {
    if (!answer.trim() || !currentQuestion || !currentRoom) return;

    try {
      await submitAnswer(answer.trim());
      setAnswer('');

      // Check if this was the last question
      const currentIndex = currentRoom.current_question_index;
      if (currentIndex >= currentRoom.questions.length) {
        // Interview complete
        await completeInterview();
        navigate('/results');
      } else {
        // Get next question
        await getNextQuestion();
      }
    } catch (err) {
      console.error('Failed to submit answer:', err);
    }
  };

  const handleSkipQuestion = async () => {
    if (!currentRoom) return;

    try {
      await submitAnswer(''); // Submit empty answer for skip

      const currentIndex = currentRoom.current_question_index;
      if (currentIndex >= currentRoom.questions.length) {
        await completeInterview();
        navigate('/results');
      } else {
        await getNextQuestion();
      }
    } catch (err) {
      console.error('Failed to skip question:', err);
    }
  };

  const toggleRecording = () => {
    setIsRecording(!isRecording);
    // TODO: Implement actual audio recording
    console.log('Recording toggled:', !isRecording);
  };

  if (!currentRoom) {
    return (
      <div className="max-w-4xl mx-auto text-center py-12">
        <p className="text-gray-600">No active interview room. Please start a new interview.</p>
      </div>
    );
  }

  const progress = ((currentRoom.current_question_index) / currentRoom.questions.length) * 100;

  return (
    <div className="max-w-6xl mx-auto">
      {/* Progress Bar */}
      <div className="mb-8">
        <div className="flex justify-between items-center mb-2">
          <h1 className="text-2xl font-bold text-gray-900">Interview in Progress</h1>
          <span className="text-sm text-gray-600">
            Question {currentRoom.current_question_index} of {currentRoom.questions.length}
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-8">
        {/* Video/Avatar Section */}
        <div className="space-y-6">
          <div className="bg-black rounded-lg overflow-hidden aspect-video relative">
            {currentAvatar ? (
              <Canvas
                camera={{ position: [0, 0, 2], fov: 50 }}
                style={{ width: '100%', height: '100%' }}
              >
                <PerspectiveCamera makeDefault position={[0, 0, 2]} />
                <OrbitControls enableZoom={false} enablePan={false} />
                <ambientLight intensity={0.6} />
                <directionalLight position={[10, 10, 5]} intensity={1} />
                <Avatar avatarUrl={currentAvatar.url} />
              </Canvas>
            ) : (
              <div className="w-full h-full bg-gray-900 flex items-center justify-center">
                <div className="text-center text-white">
                  <Video className="h-16 w-16 mx-auto mb-4 opacity-50" />
                  <p className="text-lg">Loading Avatar...</p>
                  {avatarError && (
                    <p className="text-sm opacity-75 text-red-400">{avatarError}</p>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Avatar Selector */}
          <div className="bg-white rounded-lg shadow p-6">
            <AvatarSelector />
          </div>

          {/* Interviewer Info */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">AI Interviewer</h3>
            <p className="text-gray-600 mb-4">
              Professional AI interviewer conducting your {currentRoom.job_role} assessment
            </p>
            <div className="flex items-center space-x-4 text-sm text-gray-500">
              <span>Status: {currentRoom.status}</span>
              <span>•</span>
              <span>Voice: {isWebRTCConnected ? 'Connected' : 'Connecting...'}</span>
              <span>•</span>
              <span>Avatar: {currentAvatar ? '3D Model' : 'Loading...'}</span>
            </div>
          </div>
        </div>

        {/* Question & Response Section */}
        <div className="space-y-6">
          {/* Live Transcription */}
          <LiveTranscription
            roomId={currentRoom.room_id}
            isRecording={isRecording}
            className="mb-6"
          />

          {/* Current Question */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Current Question</h2>

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-4">
                <p className="text-red-800">{error}</p>
              </div>
            )}

            {currentQuestion ? (
              <div className="space-y-4">
                <p className="text-gray-800 text-lg leading-relaxed">
                  {currentQuestion.text}
                </p>

                {/* Audio Playback */}
                {audioUrl && (
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-sm text-gray-600 mb-2">Question Audio:</p>
                    <audio controls className="w-full">
                      <source src={audioUrl} type="audio/mpeg" />
                      Your browser does not support the audio element.
                    </audio>
                  </div>
                )}
              </div>
            ) : isLoading ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <span className="ml-3 text-gray-600">Loading question...</span>
              </div>
            ) : (
              <p className="text-gray-500">No question available</p>
            )}
          </div>

          {/* Answer Input */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Your Answer</h3>

            <div className="space-y-4">
              {/* Recording Controls */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <button
                    onClick={toggleRecording}
                    className={`inline-flex items-center px-4 py-2 rounded-md font-medium ${
                      isRecording
                        ? 'bg-red-600 text-white hover:bg-red-700'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    {isRecording ? (
                      <>
                        <MicOff className="h-4 w-4 mr-2" />
                        Stop Recording
                      </>
                    ) : (
                      <>
                        <Mic className="h-4 w-4 mr-2" />
                        Start Recording
                      </>
                    )}
                  </button>
                  {isRecording && (
                    <div className="flex items-center text-red-600">
                      <div className="animate-pulse w-2 h-2 bg-red-600 rounded-full mr-2"></div>
                      Recording...
                    </div>
                  )}
                </div>

                <div className="text-sm text-gray-500">
                  {answer.length} characters
                </div>
              </div>

              {/* Text Input */}
              <textarea
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
                placeholder="Type your answer here, or use voice recording above..."
                className="w-full px-4 py-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                rows={6}
                disabled={isLoading}
              />

              {/* Action Buttons */}
              <div className="flex items-center justify-between">
                <button
                  onClick={handleSkipQuestion}
                  disabled={isLoading}
                  className="inline-flex items-center px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <SkipForward className="h-4 w-4 mr-2" />
                  Skip Question
                </button>

                <button
                  onClick={handleSubmitAnswer}
                  disabled={!answer.trim() || isLoading}
                  className="inline-flex items-center px-6 py-2 bg-blue-600 text-white font-semibold rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Submitting...
                    </>
                  ) : (
                    <>
                      <Send className="h-4 w-4 mr-2" />
                      Submit Answer
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Interview Tips */}
          <div className="bg-blue-50 rounded-lg p-6">
            <h4 className="text-lg font-semibold text-blue-900 mb-3">Interview Tips</h4>
            <ul className="space-y-2 text-blue-800">
              <li className="flex items-start">
                <span className="w-2 h-2 bg-blue-600 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                Take your time to think before answering
              </li>
              <li className="flex items-start">
                <span className="w-2 h-2 bg-blue-600 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                Be specific and provide examples from your experience
              </li>
              <li className="flex items-start">
                <span className="w-2 h-2 bg-blue-600 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                Use the voice recording feature if you prefer speaking
              </li>
              <li className="flex items-start">
                <span className="w-2 h-2 bg-blue-600 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                You can skip questions if needed, but try to answer all
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};
