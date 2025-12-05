/**
 * @file Defines the schema for facial expression parameters.
 *
 * This schema serves as the single source of truth for all controllable
 * facial expressions in the "Computational Elegance" engine. It defines
 * over 50 parameters, their default values, ranges, and descriptions,
 * mapping directly to the capabilities of the underlying 3D model's blendshapes.
 *
 * Each parameter has:
 * - `defaultValue`: The neutral state of the parameter.
 * - `min`: The minimum value (usually for an opposing expression).
 * - `max`: The maximum value for full expression intensity.
 * - `description`: A brief explanation of the parameter's effect.
 */

export const expressionSchema = {
  // -- Mouth Expressions --
  mouthOpen: { defaultValue: 0, min: 0, max: 1, description: 'Opens the mouth.' },
  mouthSmile: { defaultValue: 0, min: 0, max: 1, description: 'Creates a smile.' },
  mouthFrown: { defaultValue: 0, min: 0, max: 1, description: 'Creates a frown.' },
  mouthUpperUp: { defaultValue: 0, min: 0, max: 1, description: 'Raises the upper lip.' },
  mouthLowerDown: { defaultValue: 0, min: 0, max: 1, description: 'Lowers the lower lip.' },
  mouthPress: { defaultValue: 0, min: 0, max: 1, description: 'Presses lips together.' },
  mouthPucker: { defaultValue: 0, min: 0, max: 1, description: 'Puckers the lips.' },
  mouthStretchLeft: { defaultValue: 0, min: 0, max: 1, description: 'Stretches the left corner of the mouth.' },
  mouthStretchRight: { defaultValue: 0, min: 0, max: 1, description: 'Stretches the right corner of the mouth.' },
  mouthDimpleLeft: { defaultValue: 0, min: 0, max: 1, description: 'Creates a dimple on the left.' },
  mouthDimpleRight: { defaultValue: 0, min: 0, max: 1, description: 'Creates a dimple on the right.' },
  mouthFunnel: { defaultValue: 0, min: 0, max: 1, description: 'Funnels the lips (e.g., for "oo" sound).' },
  mouthRollUpper: { defaultValue: 0, min: 0, max: 1, description: 'Rolls the upper lip inward.' },
  mouthRollLower: { defaultValue: 0, min: 0, max: 1, description: 'Rolls the lower lip inward.' },
  mouthShrugUpper: { defaultValue: 0, min: 0, max: 1, description: 'Shrugs the upper lip.' },
  mouthShrugLower: { defaultValue: 0, min: 0, max: 1, description: 'Shrugs the lower lip.' },
  mouthClose: { defaultValue: 0, min: 0, max: 1, description: 'Closes the mouth.' },

  // -- Eye Expressions --
  eyesBlink: { defaultValue: 0, min: 0, max: 1, description: 'Closes both eyelids.' },
  eyesBlinkLeft: { defaultValue: 0, min: 0, max: 1, description: 'Closes the left eyelid.' },
  eyesBlinkRight: { defaultValue: 0, min: 0, max: 1, description: 'Closes the right eyelid.' },
  eyesLookUp: { defaultValue: 0, min: 0, max: 1, description: 'Directs gaze upwards.' },
  eyesLookDown: { defaultValue: 0, min: 0, max: 1, description: 'Directs gaze downwards.' },
  eyesLookLeft: { defaultValue: 0, min: 0, max: 1, description: 'Directs gaze to the left.' },
  eyesLookRight: { defaultValue: 0, min: 0, max: 1, description: 'Directs gaze to the right.' },
  eyesWideLeft: { defaultValue: 0, min: 0, max: 1, description: 'Widens the left eye.' },
  eyesWideRight: { defaultValue: 0, min: 0, max: 1, description: 'Widens the right eye.' },
  eyesSquintLeft: { defaultValue: 0, min: 0, max: 1, description: 'Squints the left eye.' },
  eyesSquintRight: { defaultValue: 0, min: 0, max: 1, description: 'Squints the right eye.' },

  // -- Eyebrow Expressions --
  browDownLeft: { defaultValue: 0, min: 0, max: 1, description: 'Lowers the left eyebrow.' },
  browDownRight: { defaultValue: 0, min: 0, max: 1, description: 'Lowers the right eyebrow.' },
  browInnerUp: { defaultValue: 0, min: 0, max: 1, description: 'Raises the inner part of the brows.' },
  browOuterUpLeft: { defaultValue: 0, min: 0, max: 1, description: 'Raises the outer part of the left brow.' },
  browOuterUpRight: { defaultValue: 0, min: 0, max: 1, description: 'Raises the outer part of the right brow.' },

  // -- Jaw and Cheek Expressions --
  jawOpen: { defaultValue: 0, min: 0, max: 1, description: 'Opens the jaw.' },
  jawForward: { defaultValue: 0, min: 0, max: 1, description: 'Moves the jaw forward.' },
  jawLeft: { defaultValue: 0, min: 0, max: 1, description: 'Moves the jaw to the left.' },
  jawRight: { defaultValue: 0, min: 0, max: 1, description: 'Moves the jaw to the right.' },
  cheekPuff: { defaultValue: 0, min: 0, max: 1, description: 'Puffs out the cheeks.' },
  cheekSquintLeft: { defaultValue: 0, min: 0, max: 1, description: 'Raises the left cheek (squint).' },
  cheekSquintRight: { defaultValue: 0, min: 0, max: 1, description: 'Raises the right cheek (squint).' },

  // -- Nose and Snarl --
  noseSneerLeft: { defaultValue: 0, min: 0, max: 1, description: 'Raises the left side of the nose.' },
  noseSneerRight: { defaultValue: 0, min: 0, max: 1, description: 'Raises the right side of the nose.' },

  // -- Phoneme Shapes (Visemes) --
  viseme_I: { defaultValue: 0, min: 0, max: 1, description: 'Shape for "I" as in "ice".' },
  viseme_A: { defaultValue: 0, min: 0, max: 1, description: 'Shape for "A" as in "apple".' },
  viseme_E: { defaultValue: 0, min: 0, max: 1, description: 'Shape for "E" as in "eat".' },
  viseme_O: { defaultValue: 0, min: 0, max: 1, description: 'Shape for "O" as in "open".' },
  viseme_U: { defaultValue: 0, min:0, max: 1, description: 'Shape for "U" as in "blue".' },
  viseme_F: { defaultValue: 0, min: 0, max: 1, description: 'Shape for "F" or "V".' },
  viseme_M: { defaultValue: 0, min: 0, max: 1, description: 'Shape for "M", "B", or "P".' },
  viseme_L: { defaultValue: 0, min: 0, max: 1, description: 'Shape for "L".' },
  viseme_CH: { defaultValue: 0, min: 0, max: 1, description: 'Shape for "CH", "SH", or "J".' },
  viseme_TH: { defaultValue: 0, min: 0, max: 1, description: 'Shape for "TH".' },
};

/**
 * Validates a given set of expression parameters against the schema.
 *
 * @param {object} parameters - An object where keys are parameter names and values are their settings.
 * @returns {boolean} - True if all parameters are valid, otherwise throws an error.
 */
export function validateParameters(parameters) {
  for (const key in parameters) {
    if (!expressionSchema.hasOwnProperty(key)) {
      throw new Error(`Validation Error: Parameter "${key}" is not defined in the schema.`);
    }
    const value = parameters[key];
    const schemaEntry = expressionSchema[key];
    if (typeof value !== 'number' || value < schemaEntry.min || value > schemaEntry.max) {
      throw new Error(
        `Validation Error: Parameter "${key}" has value ${value}, which is outside the allowed range [${schemaEntry.min}, ${schemaEntry.max}].`
      );
    }
  }
  return true;
}

/**
 * Returns the default state for all expression parameters.
 *
 * @returns {object} - An object containing all parameters set to their default values.
 */
export function getDefaultParameters() {
  const defaults = {};
  for (const key in expressionSchema) {
    defaults[key] = expressionSchema[key].defaultValue;
  }
  return defaults;
}
