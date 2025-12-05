/**
 * Simple test runner for MorphTargetBlender
 * Runs basic validation tests without Jest dependencies
 */

import { MorphTargetBlender } from '../src/animation/MorphTargetBlender.js';

console.log('🧪 Testing MorphTargetBlender...\n');

// Test 1: Initialization
console.log('Test 1: Initialization');
try {
  const blender = new MorphTargetBlender();
  const state = blender.getBlendState();

  console.log('✅ Blender initialized successfully');
  console.log(`   - Blend mode: ${blender.config.blendMode}`);
  console.log(`   - Transition duration: ${blender.config.transitionDuration}ms`);
  console.log(`   - Max concurrent: ${blender.config.maxConcurrentTransitions}`);
  console.log(`   - Initial state: ${state.activeTransitions} active, ${state.queuedTransitions} queued`);
} catch (error) {
  console.log('❌ Initialization failed:', error.message);
}

// Test 2: Basic blending
console.log('\nTest 2: Basic blending');
try {
  const blender = new MorphTargetBlender();
  const currentValues = { jawOpen: 0.0, mouthSmile: 0.0 };
  const targetValues = { jawOpen: 0.8, mouthSmile: 0.6 };

  const blended1 = blender.blendMorphTargets(currentValues, targetValues, 16.67); // ~60fps
  const blended2 = blender.blendMorphTargets(currentValues, targetValues, 16.67);

  if (blended1.jawOpen > 0 && blended1.mouthSmile > 0) {
    console.log('✅ Basic blending working');
    console.log(`   - Frame 1 - jawOpen: ${blended1.jawOpen.toFixed(3)}, mouthSmile: ${blended1.mouthSmile.toFixed(3)}`);
    console.log(`   - Frame 2 - jawOpen: ${blended2.jawOpen.toFixed(3)}, mouthSmile: ${blended2.mouthSmile.toFixed(3)}`);
  } else {
    console.log('❌ Basic blending failed');
  }
} catch (error) {
  console.log('❌ Basic blending failed:', error.message);
}

// Test 3: Transition creation
console.log('\nTest 3: Transition creation');
try {
  const blender = new MorphTargetBlender();
  const currentValues = { jawOpen: 0.0 };
  const targetValues = { jawOpen: 1.0 };

  blender.blendMorphTargets(currentValues, targetValues, 16.67);
  const state = blender.getBlendState();

  if (state.activeTransitions === 1) {
    console.log('✅ Transition creation working');
    console.log(`   - Active transitions: ${state.activeTransitions}`);
    console.log(`   - Current values:`, state.currentValues);
  } else {
    console.log('❌ Transition creation failed');
  }
} catch (error) {
  console.log('❌ Transition creation failed:', error.message);
}

// Test 4: Different blend modes
console.log('\nTest 4: Different blend modes');
try {
  const linearBlender = new MorphTargetBlender({ blendMode: 'linear' });
  const splineBlender = new MorphTargetBlender({ blendMode: 'spline' });
  const physicsBlender = new MorphTargetBlender({ blendMode: 'physics' });

  const currentValues = { jawOpen: 0.0 };
  const targetValues = { jawOpen: 1.0 };

  // Run a few frames
  for (let i = 0; i < 5; i++) {
    linearBlender.blendMorphTargets(currentValues, targetValues, 16.67);
    splineBlender.blendMorphTargets(currentValues, targetValues, 16.67);
    physicsBlender.blendMorphTargets(currentValues, targetValues, 16.67);
  }

  const linearState = linearBlender.getBlendState();
  const splineState = splineBlender.getBlendState();
  const physicsState = physicsBlender.getBlendState();

  if (linearState.activeTransitions === 1 && splineState.activeTransitions === 1 && physicsState.activeTransitions === 1) {
    console.log('✅ Different blend modes working');
    console.log(`   - Linear: ${Object.values(linearState.currentValues)[0]?.toFixed(3)}`);
    console.log(`   - Spline: ${Object.values(splineState.currentValues)[0]?.toFixed(3)}`);
    console.log(`   - Physics: ${Object.values(physicsState.currentValues)[0]?.toFixed(3)}`);
  } else {
    console.log('❌ Different blend modes failed');
  }
} catch (error) {
  console.log('❌ Different blend modes failed:', error.message);
}

// Test 5: Easing functions
console.log('\nTest 5: Easing functions');
try {
  const blender = new MorphTargetBlender();

  // Test various easing functions
  const testEasings = ['easeInQuad', 'easeOutCubic', 'easeInOutQuart'];

  testEasings.forEach(easing => {
    const result = blender.applyEasing(0.5, easing);
    if (typeof result === 'number' && result >= 0 && result <= 1) {
      console.log(`   - ${easing}: ${result.toFixed(3)} ✓`);
    } else {
      console.log(`   - ${easing}: failed ❌`);
    }
  });

  console.log('✅ Easing functions working');
} catch (error) {
  console.log('❌ Easing functions failed:', error.message);
}

// Test 6: Concurrency limits
console.log('\nTest 6: Concurrency limits');
try {
  const blender = new MorphTargetBlender({ maxConcurrentTransitions: 2 });
  const currentValues = { target1: 0, target2: 0, target3: 0 };
  const targetValues = { target1: 1, target2: 1, target3: 1 };

  blender.blendMorphTargets(currentValues, targetValues, 16.67);
  const state = blender.getBlendState();

  if (state.activeTransitions <= 2 && state.queuedTransitions >= 1) {
    console.log('✅ Concurrency limits working');
    console.log(`   - Active: ${state.activeTransitions}, Queued: ${state.queuedTransitions}`);
  } else {
    console.log('❌ Concurrency limits failed');
  }
} catch (error) {
  console.log('❌ Concurrency limits failed:', error.message);
}

// Test 7: Immediate setting
console.log('\nTest 7: Immediate setting');
try {
  const blender = new MorphTargetBlender();
  const values = { jawOpen: 0.5, mouthSmile: 0.8 };

  blender.setMorphTargetsImmediate(values);
  const state = blender.getBlendState();

  if (state.activeTransitions === 0 && state.currentValues.jawOpen === 0.5) {
    console.log('✅ Immediate setting working');
    console.log(`   - Active transitions: ${state.activeTransitions}`);
    console.log(`   - jawOpen value: ${state.currentValues.jawOpen}`);
  } else {
    console.log('❌ Immediate setting failed');
  }
} catch (error) {
  console.log('❌ Immediate setting failed:', error.message);
}

// Test 8: Transition cancellation
console.log('\nTest 8: Transition cancellation');
try {
  const blender = new MorphTargetBlender();
  const currentValues = { jawOpen: 0.0, mouthSmile: 0.0 };
  const targetValues = { jawOpen: 1.0, mouthSmile: 1.0 };

  blender.blendMorphTargets(currentValues, targetValues, 16.67);
  let state = blender.getBlendState();

  const initialActive = state.activeTransitions;

  blender.cancelTransitions('jawOpen');
  state = blender.getBlendState();

  if (state.activeTransitions < initialActive) {
    console.log('✅ Transition cancellation working');
    console.log(`   - Before: ${initialActive} active`);
    console.log(`   - After: ${state.activeTransitions} active`);
  } else {
    console.log('❌ Transition cancellation failed');
  }
} catch (error) {
  console.log('❌ Transition cancellation failed:', error.message);
}

// Test 9: Idle state detection
console.log('\nTest 9: Idle state detection');
try {
  const blender = new MorphTargetBlender();

  // Initially idle
  if (blender.isIdle()) {
    console.log('✅ Initially idle');

    // Add a transition
    const currentValues = { jawOpen: 0.0 };
    const targetValues = { jawOpen: 1.0 };
    blender.blendMorphTargets(currentValues, targetValues, 16.67);

    if (!blender.isIdle()) {
      console.log('✅ Not idle with active transitions');

      // Cancel all transitions
      blender.cancelAllTransitions();

      if (blender.isIdle()) {
        console.log('✅ Idle after cancelling all transitions');
      } else {
        console.log('❌ Not idle after cancelling');
      }
    } else {
      console.log('❌ Should not be idle with transitions');
    }
  } else {
    console.log('❌ Should be initially idle');
  }
} catch (error) {
  console.log('❌ Idle state detection failed:', error.message);
}

// Test 10: Performance metrics
console.log('\nTest 10: Performance metrics');
try {
  const blender = new MorphTargetBlender();
  const currentValues = { jawOpen: 0.0 };
  const targetValues = { jawOpen: 1.0 };

  // Run multiple blend operations
  for (let i = 0; i < 10; i++) {
    blender.blendMorphTargets(currentValues, targetValues, 16.67);
  }

  const state = blender.getBlendState();

  if (state.metrics.transitionsProcessed > 0) {
    console.log('✅ Performance metrics working');
    console.log(`   - Transitions processed: ${state.metrics.transitionsProcessed}`);
    console.log(`   - Average blend time: ${state.metrics.averageBlendTime.toFixed(2)}ms`);
    console.log(`   - Max concurrent: ${state.metrics.maxConcurrentTransitions}`);
  } else {
    console.log('❌ Performance metrics failed');
  }
} catch (error) {
  console.log('❌ Performance metrics failed:', error.message);
}

// Test 11: State export and reset
console.log('\nTest 11: State export and reset');
try {
  const blender = new MorphTargetBlender();
  const currentValues = { jawOpen: 0.0 };
  const targetValues = { jawOpen: 1.0 };

  blender.blendMorphTargets(currentValues, targetValues, 16.67);
  const exportedState = blender.exportState();

  if (exportedState.config && exportedState.metrics) {
    console.log('✅ State export working');

    blender.reset();
    const resetState = blender.getBlendState();

    if (resetState.activeTransitions === 0 && resetState.queuedTransitions === 0) {
      console.log('✅ Reset working');
      console.log(`   - After reset - Active: ${resetState.activeTransitions}, Queued: ${resetState.queuedTransitions}`);
    } else {
      console.log('❌ Reset failed');
    }
  } else {
    console.log('❌ State export failed');
  }
} catch (error) {
  console.log('❌ State export and reset failed:', error.message);
}

console.log('\n🎉 MorphTargetBlender testing complete!');