/**
 * @file Phoneme to Viseme Mapping
 *
 * This module defines the mapping between phonemes (the basic units of sound)
 * and visemes (the visual representation of those sounds on the face).
 * This mapping is crucial for creating believable, automated lip-sync animations.
 */

const phonemeToVisemeMap = {
  // Consonants
  M: 'viseme_M', // Also B, P
  F: 'viseme_F', // Also V
  L: 'viseme_L',
  TH: 'viseme_TH',
  CH: 'viseme_CH', // Also SH, J

  // Vowels
  I: 'viseme_I',
  A: 'viseme_A',
  E: 'viseme_E',
  O: 'viseme_O',
  U: 'viseme_U',

  // Default fallback
  default: 'viseme_M', // A closed or neutral mouth shape
};

/**
 * Maps a given phoneme to its corresponding viseme parameter name.
 *
 * @param {string} phoneme - The phoneme to map (e.g., "M", "A", "TH").
 * @returns {string} The name of the viseme parameter (e.g., "viseme_M").
 */
export function getVisemeForPhoneme(phoneme) {
  const upperPhoneme = phoneme.toUpperCase();
  return phonemeToVisemeMap[upperPhoneme] || phonemeToVisemeMap.default;
}
