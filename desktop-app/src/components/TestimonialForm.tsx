/**
 * Testimonial Form Component
 * Multi-step form for recording and submitting testimonials
 * Part of Day 5-6 implementation
 */

import React, { useState, useEffect } from 'react';
import {
  voiceInputService,
  VoiceSession,
  VoiceInputConfig,
} from '../services/voice-input';
import {
  transcriptionService,
  TranscriptionResult,
} from '../services/transcription-service';
import {
  testimonialDatabase,
  TestimonialData,
  ViolationType,
} from '../services/testimonial-database';
import { avatarRenderer, AvatarConfig, AvatarGender, AvatarSkinTone } from '../services/avatar-renderer';
import './TestimonialForm.css';

type FormStep = 'recording' | 'privacy' | 'details' | 'review';

interface FormState {
  recordingBlob: Blob | null;
  recordingDuration: number;
  transcription: string;
  incidentType: ViolationType;
  incidentDate: string;
  location: string;
  witnesses: string[];
  context: string;
  anonymous: boolean;
  shareWithResearchers: boolean;
  locationPrecision: 'exact' | 'city' | 'country';
  protectWitnesses: boolean;
}

const VIOLATION_TYPES = [
  { value: ViolationType.ASSAULT, label: 'Physical Assault' },
  { value: ViolationType.HARASSMENT, label: 'Harassment' },
  { value: ViolationType.DISCRIMINATION, label: 'Discrimination' },
  { value: ViolationType.HUMAN_TRAFFICKING, label: 'Human Trafficking' },
  { value: ViolationType.FORCED_LABOR, label: 'Forced Labor' },
  { value: ViolationType.CHILD_ABUSE, label: 'Child Abuse' },
  { value: ViolationType.SEXUAL_VIOLENCE, label: 'Sexual Violence' },
  { value: ViolationType.EXTORTION, label: 'Extortion' },
  { value: ViolationType.UNLAWFUL_DETENTION, label: 'Unlawful Detention' },
  { value: ViolationType.DENIAL_OF_SERVICES, label: 'Denial of Services' },
  { value: ViolationType.PROPERTY_THEFT, label: 'Property Theft' },
  { value: ViolationType.WAGE_THEFT, label: 'Wage Theft' },
  { value: ViolationType.DOCUMENT_WITHHOLDING, label: 'Document Withholding' },
  { value: ViolationType.MOVEMENT_RESTRICTION, label: 'Movement Restriction' },
  { value: ViolationType.THREATS, label: 'Threats' },
  { value: ViolationType.OTHER, label: 'Other' },
];

const DEFAULT_FORM_STATE: FormState = {
  recordingBlob: null,
  recordingDuration: 0,
  transcription: '',
  incidentType: ViolationType.OTHER,
  incidentDate: new Date().toISOString().split('T')[0],
  location: '',
  witnesses: [],
  context: '',
  anonymous: false,
  shareWithResearchers: true,
  locationPrecision: 'exact',
  protectWitnesses: true,
};

interface TestimonialFormProps {
  onComplete?: (id: string) => void;
  onCancel?: () => void;
}

export const TestimonialForm: React.FC<TestimonialFormProps> = ({
  onComplete,
  onCancel,
}) => {
  const [step, setStep] = useState<FormStep>('recording');
  const [form, setForm] = useState<FormState>(DEFAULT_FORM_STATE);
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [audioLevel, setAudioLevel] = useState(0);
  const [currentSession, setCurrentSession] = useState<VoiceSession | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Audio level visualization
  useEffect(() => {
    if (!isRecording) return;

    const interval = setInterval(() => {
      const level = voiceInputService.getAudioLevel();
      setAudioLevel(level);
    }, 50);

    return () => clearInterval(interval);
  }, [isRecording]);

  /**
   * Step 1: Start/stop recording
   */
  const handleStartRecording = async () => {
    try {
      setError(null);

      // Check microphone permission
      const { permitted } = await voiceInputService.checkMicrophoneAccess();
      if (!permitted) {
        const hasAccess = await voiceInputService.requestMicrophoneAccess();
        if (!hasAccess) {
          setError('Microphone access denied. Please check permissions.');
          return;
        }
      }

      // Start recording
      const config: VoiceInputConfig = {
        sampleRate: 16000,
        channelCount: 1,
        vadThreshold: 0.5,
        maxDuration: 5 * 60 * 1000, // 5 minutes
        autoStopSilence: 2000, // 2 seconds silence
      };

      const session = await voiceInputService.startRecording(config);
      setCurrentSession(session);
      setIsRecording(true);

      console.log('✅ Recording started');
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to start recording';
      setError(errorMsg);
      console.error('Recording error:', err);
    }
  };

  const handleStopRecording = async () => {
    try {
      setIsRecording(false);
      const audioBlob = await voiceInputService.stopRecording();

      // Convert to WAV format
      const wavBlob = await voiceInputService.convertToWav(audioBlob);

      setForm((prev) => ({
        ...prev,
        recordingBlob: wavBlob,
        recordingDuration: currentSession?.duration || 0,
      }));

      // Auto-transcribe
      setIsTranscribing(true);
      await transcribeAudio(wavBlob);
      setIsTranscribing(false);

      console.log('✅ Recording stopped, transcription started');
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to stop recording';
      setError(errorMsg);
      console.error('Stop recording error:', err);
    }
  };

  /**
   * Transcribe recorded audio
   */
  const transcribeAudio = async (audioBlob: Blob) => {
    try {
      setIsTranscribing(true);

      // Initialize transcriber if needed
      if (!transcriptionService.isReady()) {
        console.log('Initializing Whisper model (this may take a moment)...');
        await transcriptionService.initialize({ modelSize: 'tiny', language: 'en' });
      }

      // Transcribe
      const result = await transcriptionService.transcribe(audioBlob);

      setForm((prev) => ({
        ...prev,
        transcription: result.text,
      }));

      console.log('✅ Transcription complete:', result.text.substring(0, 100) + '...');
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to transcribe audio';
      setError(errorMsg);
      console.error('Transcription error:', err);
    } finally {
      setIsTranscribing(false);
    }
  };

  /**
   * Re-record audio
   */
  const handleReRecord = () => {
    voiceInputService.dispose();
    setForm((prev) => ({
      ...prev,
      recordingBlob: null,
      recordingDuration: 0,
      transcription: '',
    }));
    setAudioLevel(0);
    setCurrentSession(null);
  };

  /**
   * Handle form field changes
   */
  const handleFormChange = (
    field: keyof FormState,
    value: any
  ) => {
    setForm((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  /**
   * Add witness
   */
  const handleAddWitness = (name: string) => {
    if (name.trim()) {
      setForm((prev) => ({
        ...prev,
        witnesses: [...prev.witnesses, name],
      }));
    }
  };

  /**
   * Remove witness
   */
  const handleRemoveWitness = (index: number) => {
    setForm((prev) => ({
      ...prev,
      witnesses: prev.witnesses.filter((_, i) => i !== index),
    }));
  };

  /**
   * Submit form
   */
  const handleSubmit = async () => {
    try {
      // Validation
      if (!form.recordingBlob) {
        setError('Recording is required');
        return;
      }
      if (!form.location.trim()) {
        setError('Location is required');
        return;
      }

      setIsSubmitting(true);
      setError(null);

      // Prepare data
      const testimonialData: TestimonialData = {
        id: `testimonial-${Date.now()}`,
        recordingBlob: form.recordingBlob,
        recording: {
          duration: form.recordingDuration,
          audioUrl: URL.createObjectURL(form.recordingBlob),
        },
        privacy: {
          anonymous: form.anonymous,
          shareWithResearchers: form.shareWithResearchers,
          locationPrecision: form.locationPrecision,
          protectWitnesses: form.protectWitnesses,
        },
        incident: {
          type: form.incidentType,
          date: new Date(form.incidentDate),
          location: form.location,
          witnesses: form.witnesses,
          context: form.context,
        },
        metadata: {
          recordedAt: new Date(),
          audioLanguage: 'en',
          version: '1.0',
        },
      };

      // Save to database
      await testimonialDatabase.initialize();
      const id = await testimonialDatabase.saveTestimonial(testimonialData);

      setSuccessMessage(
        '✅ Testimonial saved successfully! Thank you for sharing your story.'
      );

      // Reset form
      setTimeout(() => {
        setForm(DEFAULT_FORM_STATE);
        setStep('recording');
        if (onComplete) {
          onComplete(id);
        }
      }, 2000);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to submit testimonial';
      setError(errorMsg);
      console.error('Submit error:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  /**
   * Validate step before proceeding
   */
  const canProceedToNextStep = (): boolean => {
    switch (step) {
      case 'recording':
        return form.recordingBlob !== null && form.transcription !== '';
      case 'privacy':
        return true;
      case 'details':
        return form.location.trim() !== '';
      case 'review':
        return true;
      default:
        return false;
    }
  };

  const handleNextStep = () => {
    if (!canProceedToNextStep()) {
      setError('Please complete required fields');
      return;
    }

    const steps: FormStep[] = ['recording', 'privacy', 'details', 'review'];
    const currentIndex = steps.indexOf(step);
    if (currentIndex < steps.length - 1) {
      setStep(steps[currentIndex + 1]);
      setError(null);
    }
  };

  const handlePreviousStep = () => {
    const steps: FormStep[] = ['recording', 'privacy', 'details', 'review'];
    const currentIndex = steps.indexOf(step);
    if (currentIndex > 0) {
      setStep(steps[currentIndex - 1]);
      setError(null);
    }
  };

  return (
    <div className="testimonial-form">
      <div className="form-header">
        <h1>Share Your Testimonial</h1>
        <p>Help us document human rights violations safely and securely</p>
        <div className="step-indicator">
          <div className={`step ${step === 'recording' ? 'active' : 'complete'}`}>1. Record</div>
          <div className={`step ${step === 'privacy' ? 'active' : step === 'details' || step === 'review' ? 'complete' : ''}`}>2. Privacy</div>
          <div className={`step ${step === 'details' ? 'active' : step === 'review' ? 'complete' : ''}`}>3. Details</div>
          <div className={`step ${step === 'review' ? 'active' : ''}`}>4. Review</div>
        </div>
      </div>

      {successMessage && (
        <div className="success-message">
          <p>{successMessage}</p>
        </div>
      )}

      {error && (
        <div className="error-message">
          <p>❌ {error}</p>
        </div>
      )}

      {/* Step 1: Recording */}
      {step === 'recording' && (
        <div className="form-step">
          <h2>📹 Record Your Testimonial</h2>
          <p>Tell us what happened in your own words. Speak clearly and take your time.</p>

          {!form.recordingBlob ? (
            <>
              <div className="audio-visualizer">
                <div className="level-bars">
                  {Array.from({ length: 10 }).map((_, i) => (
                    <div
                      key={i}
                      className="bar"
                      style={{
                        height: `${Math.max(5, (audioLevel * (i + 1)) / 10)}%`,
                      }}
                    />
                  ))}
                </div>
                <p className="level-text">{audioLevel}%</p>
              </div>

              {!isRecording ? (
                <button
                  className="btn btn-primary"
                  onClick={handleStartRecording}
                  disabled={isRecording}
                >
                  🎤 Start Recording
                </button>
              ) : (
                <div className="recording-controls">
                  <div className="recording-indicator">
                    <span className="pulse"></span>
                    Recording...
                  </div>
                  <button
                    className="btn btn-danger"
                    onClick={handleStopRecording}
                  >
                    ⏹️ Stop Recording
                  </button>
                </div>
              )}
            </>
          ) : (
            <>
              <div className="recording-complete">
                <p>✅ Recording complete!</p>
                <p className="duration">Duration: {(form.recordingDuration / 1000).toFixed(1)} seconds</p>

                <div className="transcription-preview">
                  <h3>Transcription:</h3>
                  <p className="transcription-text">
                    {form.transcription || '(Processing...)'}
                  </p>
                </div>

                <button
                  className="btn btn-secondary"
                  onClick={handleReRecord}
                  disabled={isTranscribing}
                >
                  🔄 Re-Record
                </button>
              </div>
            </>
          )}
        </div>
      )}

      {/* Step 2: Privacy Settings */}
      {step === 'privacy' && (
        <div className="form-step">
          <h2>🔒 Privacy Settings</h2>
          <p>Control how your information is handled and protected</p>

          <div className="privacy-options">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={form.anonymous}
                onChange={(e) => handleFormChange('anonymous', e.target.checked)}
              />
              <span>Record as Anonymous</span>
              <small>Your name will not be stored with your testimonial</small>
            </label>

            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={form.shareWithResearchers}
                onChange={(e) => handleFormChange('shareWithResearchers', e.target.checked)}
              />
              <span>Share Encrypted Data with Researchers</span>
              <small>Help human rights organizations document violations</small>
            </label>

            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={form.protectWitnesses}
                onChange={(e) => handleFormChange('protectWitnesses', e.target.checked)}
              />
              <span>Protect Witness Names</span>
              <small>Witness names will be masked in reports</small>
            </label>

            <div className="location-precision">
              <label>Location Precision:</label>
              <select
                value={form.locationPrecision}
                onChange={(e) => handleFormChange('locationPrecision', e.target.value as any)}
              >
                <option value="exact">Exact Location (Street Address)</option>
                <option value="city">City/Region Only</option>
                <option value="country">Country Only</option>
              </select>
            </div>
          </div>
        </div>
      )}

      {/* Step 3: Incident Details */}
      {step === 'details' && (
        <div className="form-step">
          <h2>📝 Incident Details</h2>
          <p>Provide information about what happened</p>

          <div className="form-fields">
            <div className="form-group">
              <label>Type of Violation:</label>
              <select
                value={form.incidentType}
                onChange={(e) => handleFormChange('incidentType', e.target.value)}
              >
                {VIOLATION_TYPES.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Date of Incident:</label>
              <input
                type="date"
                value={form.incidentDate}
                onChange={(e) => handleFormChange('incidentDate', e.target.value)}
              />
            </div>

            <div className="form-group">
              <label>Location: *</label>
              <input
                type="text"
                placeholder="Where did this happen?"
                value={form.location}
                onChange={(e) => handleFormChange('location', e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label>Witness Names (Optional):</label>
              <div className="witness-input">
                <input
                  type="text"
                  placeholder="Add witness name..."
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      handleAddWitness(e.currentTarget.value);
                      e.currentTarget.value = '';
                    }
                  }}
                />
                <button
                  className="btn btn-secondary"
                  onClick={(e) => {
                    const input = (e.target as HTMLElement).previousElementSibling as HTMLInputElement;
                    handleAddWitness(input.value);
                    input.value = '';
                  }}
                >
                  Add
                </button>
              </div>

              {form.witnesses.length > 0 && (
                <div className="witnesses-list">
                  {form.witnesses.map((witness, i) => (
                    <div key={i} className="witness-tag">
                      <span>{witness}</span>
                      <button
                        className="remove-btn"
                        onClick={() => handleRemoveWitness(i)}
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="form-group">
              <label>Additional Context:</label>
              <textarea
                placeholder="Any additional details that might be helpful..."
                value={form.context}
                onChange={(e) => handleFormChange('context', e.target.value)}
                maxLength={500}
                rows={4}
              />
              <small>{form.context.length}/500 characters</small>
            </div>
          </div>
        </div>
      )}

      {/* Step 4: Review */}
      {step === 'review' && (
        <div className="form-step">
          <h2>✅ Review Your Testimonial</h2>
          <p>Please review your information before submitting</p>

          <div className="review-section">
            <h3>Recording</h3>
            <p>Duration: {(form.recordingDuration / 1000).toFixed(1)} seconds</p>
            <audio controls style={{ width: '100%', marginTop: '10px' }}>
              <source src={form.recordingBlob ? URL.createObjectURL(form.recordingBlob) : ''} type="audio/wav" />
            </audio>

            <h3 style={{ marginTop: '20px' }}>Transcription</h3>
            <p className="transcription-text">{form.transcription}</p>

            <h3 style={{ marginTop: '20px' }}>Incident Information</h3>
            <p>
              <strong>Type:</strong> {VIOLATION_TYPES.find((t) => t.value === form.incidentType)?.label}
            </p>
            <p>
              <strong>Date:</strong> {new Date(form.incidentDate).toLocaleDateString()}
            </p>
            <p>
              <strong>Location:</strong> {form.location}
            </p>
            {form.witnesses.length > 0 && (
              <p>
                <strong>Witnesses:</strong> {form.witnesses.join(', ')}
              </p>
            )}
            {form.context && (
              <p>
                <strong>Context:</strong> {form.context}
              </p>
            )}

            <h3 style={{ marginTop: '20px' }}>Privacy Settings</h3>
            <p>Anonymous: {form.anonymous ? 'Yes' : 'No'}</p>
            <p>Share with Researchers: {form.shareWithResearchers ? 'Yes' : 'No'}</p>
            <p>Protect Witnesses: {form.protectWitnesses ? 'Yes' : 'No'}</p>
            <p>Location Precision: {form.locationPrecision}</p>
          </div>

          <div className="consent">
            <p>
              By submitting, you confirm that this information is accurate to the best of your knowledge
              and consent to its encrypted storage for human rights documentation.
            </p>
          </div>
        </div>
      )}

      {/* Navigation buttons */}
      <div className="form-actions">
        <button
          className="btn btn-secondary"
          onClick={onCancel || handlePreviousStep}
          disabled={step === 'recording' && !isSubmitting}
        >
          {step === 'recording' ? '✕ Cancel' : '← Back'}
        </button>

        {step !== 'review' && (
          <button
            className="btn btn-primary"
            onClick={handleNextStep}
            disabled={!canProceedToNextStep() || isTranscribing || isRecording}
          >
            Next →
          </button>
        )}

        {step === 'review' && (
          <button
            className="btn btn-primary btn-submit"
            onClick={handleSubmit}
            disabled={isSubmitting}
          >
            {isSubmitting ? '⏳ Submitting...' : '✓ Submit Testimonial'}
          </button>
        )}
      </div>
    </div>
  );
};
