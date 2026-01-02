#!/bin/bash
# Audio Integration Patches for AI Orchestra Production App
# This file contains the exact code changes needed

# =============================================================================
# PATCH 1: Update start() method in MorphTargetAnimationController.js
# Location: Lines 118-140 (approximately)
# =============================================================================

# FIND THIS:
cat << 'EOF'
  start() {
    console.log('[CHECKPOINT 2] Animation start() called');
    console.log('[CHECKPOINT 2] Audio object:', this.audio);
    console.log('[CHECKPOINT 2] Audio isPlaying:', this.audio?.isPlaying);

    if (this.audio) {
      if (!this.audio.isPlaying) {
        this.audio.play();
        console.log('[CHECKPOINT 2] Audio play() triggered');
        this.logger.log('SUCCESS', 'Audio playback started');
      } else {
        this.logger.log('INFO', 'Audio already playing');
      }
    } else {
      this.logger.log('WARNING', 'No audio object available');
    }

    this.clock.start();
    this.animationState.isPlaying = true;
    this.lastLoggedTime = 0;

    console.log('[CHECKPOINT 2] Animation state:', this.animationState);
    console.log('[CHECKPOINT 2] Clock started:', this.clock.running);

    this.logger.log('SUCCESS', 'Morph target animation started');
    return true;
  }
EOF

# REPLACE WITH THIS:
cat << 'EOF'
  start() {
    console.log('[CHECKPOINT 2] Animation start() called');
    console.log('[CHECKPOINT 2] HTML Audio element:', this.htmlAudioElement);
    console.log('[CHECKPOINT 2] THREE.Audio object:', this.audio);

    // Prefer HTML audio element for reliable playback and synchronization
    if (this.htmlAudioElement) {
      if (this.htmlAudioElement.paused) {
        this.htmlAudioElement.currentTime = 0;
        this.htmlAudioElement.play();
        console.log('[CHECKPOINT 2] HTML audio play() triggered');
        this.logger.log('SUCCESS', 'Audio playback started via HTML audio element');
      } else {
        console.log('[CHECKPOINT 2] HTML audio already playing');
        this.logger.log('INFO', 'Audio already playing');
      }
    } else if (this.audio) {
      // Fallback to THREE.Audio if HTML audio not available
      if (!this.audio.isPlaying) {
        this.audio.play();
        console.log('[CHECKPOINT 2] THREE.Audio play() triggered (fallback)');
        this.logger.log('SUCCESS', 'Audio playback started via THREE.Audio');
      } else {
        this.logger.log('INFO', 'Audio already playing');
      }
    } else {
      this.logger.log('WARNING', 'No audio object available');
    }

    this.clock.start();
    this.animationState.isPlaying = true;
    this.lastLoggedTime = 0;

    console.log('[CHECKPOINT 2] Animation state:', this.animationState);
    console.log('[CHECKPOINT 2] Clock started:', this.clock.running);

    this.logger.log('SUCCESS', 'Morph target animation started');
    return true;
  }
EOF

# =============================================================================
# PATCH 2: Update updateMouthAnimation() method to use HTML audio currentTime
# Location: Lines 169-195 (approximately)
# =============================================================================

# FIND THIS (first 15 lines of updateMouthAnimation):
cat << 'EOF'
  updateMouthAnimation(elapsedTime) {
    if (!this.speechData || Object.keys(this.mouthMorphTargets).length === 0) return;

    // CHECKPOINT 4: Audio-Animation Sync
    const audioTime = this.audio?.context?.currentTime || 0;
    if (!this._lastSyncLog || Date.now() - this._lastSyncLog > 1000) {
      console.log('[CHECKPOINT 4] Time sync - Clock:', elapsedTime.toFixed(2),
                  'Audio context time:', audioTime.toFixed(2));
      this._lastSyncLog = Date.now();
    }

    // Find current word (with caching for performance)
    const currentWordIndex = this.speechData.words.findIndex(
      (w) => elapsedTime >= w.start && elapsedTime <= w.end
    );
EOF

# REPLACE WITH THIS (use HTML audio element time):
cat << 'EOF'
  updateMouthAnimation(elapsedTime) {
    if (!this.speechData || Object.keys(this.mouthMorphTargets).length === 0) return;

    // Use HTML audio element's currentTime for accurate synchronization
    if (this.htmlAudioElement && !this.htmlAudioElement.paused) {
      elapsedTime = this.htmlAudioElement.currentTime;
    }

    // CHECKPOINT 4: Audio-Animation Sync
    const audioTime = this.htmlAudioElement?.currentTime || this.audio?.context?.currentTime || 0;
    if (!this._lastSyncLog || Date.now() - this._lastSyncLog > 1000) {
      console.log('[CHECKPOINT 4] Time sync - Elapsed:', elapsedTime.toFixed(2),
                  'Audio time:', audioTime.toFixed(2));
      this._lastSyncLog = Date.now();
    }

    // Find current word (with caching for performance)
    const currentWordIndex = this.speechData.words.findIndex(
      (w) => elapsedTime >= w.start && elapsedTime <= w.end
    );
EOF

# =============================================================================
# TESTING
# =============================================================================

echo "After applying these patches:"
echo ""
echo "1. Hard refresh browser: Ctrl+Shift+R (or Cmd+Shift+R on Mac)"
echo "2. Go to: http://localhost:8000"
echo "3. Click 'Start'"
echo "4. Toggle 'Enable Lip-Sync'"
echo ""
echo "Expected behavior:"
echo "✓ Audio plays through speakers"
echo "✓ Mouth moves with phonemes from speech.json"
echo "✓ Lip-sync timing is accurate"
echo "✓ Console shows CHECKPOINT 2 logs indicating HTML audio is being used"
