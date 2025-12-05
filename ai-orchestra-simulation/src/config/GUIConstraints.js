/**
 * GUIConstraints.js
 * 
 * Configuration constraints for GUI parameter ranges.
 * Defines min/max/step values for interactive controls.
 * 
 * Extracted from app.js for better configuration management.
 */

export const GUI_CONSTRAINTS = {
  POSITION_RANGE: { min: -100.0, max: 100.0, step: 0.1 },
  HEIGHT_RANGE: { min: 130.0, max: 185.0, step: 0.1 },
  DEPTH_RANGE: { min: -15.0, max: 20.0, step: 0.1 },
};
