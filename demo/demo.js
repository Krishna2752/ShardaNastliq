/*
 * JS port of koshur_sharada/transliterate.py's CONTROL FLOW for the
 * static web demo (Pyodide can't reliably run in this sandbox -- its
 * runtime needs binary asset fetches the CSP blocks).
 *
 * The codepoint TABLES are not hand-transcribed here: they're loaded
 * from data.json, generated straight from sharada.py/persoarabic.py by
 * generate_data.py. Only the parsing/rendering logic is duplicated, kept
 * as a line-for-line mirror of transliterate.py so the two don't drift
 * apart silently. If transliterate.py's logic changes, update this file
 * to match; if the mapping tables change, just re-run generate_data.py.
 *
 * Codepoints are indexed by Unicode CODE POINT, not UTF-16 code unit --
 * Sharada and some Perso-Arabic marks are outside the BMP (surrogate
 * pairs in JS strings), so plain string indexing/slicing would silently
 * split them. Array.from(str) iterates by code point and avoids that.
 */

let DATA = null;
let REV = null;

function invert(obj) {
  const out = {};
  for (const k in obj) out[obj[k]] = k;
  return out;
}

async function loadData() {
  const res = await fetch('data.json');
  DATA = await res.json();
  const shr = DATA.sharada, pa = DATA.persoarabic;
  REV = {
    shrConsonants: invert(shr.consonants),
    shrVowelSigns: invert(shr.vowelSigns),
    shrIndepVowels: invert(shr.independentVowels),
    paConsonants: invert(pa.consonants),
    paVowelDiacriticToPhoneme: pa.vowelDiacriticToPhoneme,
    paPhonemeToVowelDiacritic: invert(pa.vowelDiacriticToPhoneme),
  };
}

class Unit {
  constructor(consonant, vowel, nasalized = false, isWordBoundary = false) {
    this.consonant = consonant;
    this.vowel = vowel;
    this.nasalized = nasalized;
    this.isWordBoundary = isWordBoundary;
  }
}

// ---------------------------------------------------------------- Sharada

function sharadaToUnits(text) {
  const chars = Array.from(text);
  const units = [];
  let i = 0;
  const shr = DATA.sharada;
  while (i < chars.length) {
    const ch = chars[i];
    if (ch === ' ' || ch === '\n' || ch === '\t') {
      units.push(new Unit(null, '', false, true));
      i += 1;
      continue;
    }

    const twoChar = chars.slice(i, i + 2).join('');
    let consPhoneme = null;
    if (Object.prototype.hasOwnProperty.call(REV.shrConsonants, twoChar)) {
      consPhoneme = REV.shrConsonants[twoChar];
      i += 2;
    } else if (Object.prototype.hasOwnProperty.call(REV.shrConsonants, ch)) {
      consPhoneme = REV.shrConsonants[ch];
      i += 1;
    }

    if (consPhoneme !== null) {
      let vowelPhoneme = 'a';
      let nasal = false;

      if (i < chars.length && chars[i] === shr.virama) {
        vowelPhoneme = '';
        i += 1;
      } else if (i < chars.length && Object.prototype.hasOwnProperty.call(REV.shrVowelSigns, chars[i])) {
        const two = chars.slice(i, i + 2).join('');
        if (Object.prototype.hasOwnProperty.call(REV.shrVowelSigns, two)) {
          vowelPhoneme = REV.shrVowelSigns[two];
          i += 2;
        } else {
          vowelPhoneme = REV.shrVowelSigns[chars[i]];
          i += 1;
        }
      }

      if (i < chars.length && chars[i] === shr.anusvara) {
        nasal = true;
        i += 1;
      }

      units.push(new Unit(consPhoneme, vowelPhoneme, nasal, false));
      continue;
    }

    if (Object.prototype.hasOwnProperty.call(REV.shrIndepVowels, ch)) {
      const two = chars.slice(i, i + 2).join('');
      if (Object.prototype.hasOwnProperty.call(REV.shrIndepVowels, two)) {
        units.push(new Unit(null, REV.shrIndepVowels[two]));
        i += 2;
      } else {
        units.push(new Unit(null, REV.shrIndepVowels[ch]));
        i += 1;
      }
      continue;
    }

    units.push(new Unit(null, '', false, false));
    i += 1;
  }
  return units;
}

function unitsToSharada(units) {
  const shr = DATA.sharada;
  const out = [];
  for (const u of units) {
    if (u.isWordBoundary) {
      out.push(' ');
      continue;
    }
    if (u.consonant === null) {
      if (u.vowel) out.push(shr.independentVowels[u.vowel]);
      continue;
    }
    out.push(shr.consonants[u.consonant]);
    if (u.vowel === '') {
      out.push(shr.virama);
    } else if (u.vowel !== 'a') {
      out.push(shr.vowelSigns[u.vowel] ?? '');
    }
    if (u.nasalized) out.push(shr.anusvara);
  }
  return out.join('');
}

// ----------------------------------------------------------- Perso-Arabic

function unitsToPersoarabic(units) {
  const pa = DATA.persoarabic;
  const out = [];
  for (const u of units) {
    if (u.isWordBoundary) {
      out.push(' ');
      continue;
    }

    if (u.consonant === null) {
      if (Object.prototype.hasOwnProperty.call(pa.longVowelSequences, u.vowel)) {
        out.push(pa.alef + pa.longVowelSequences[u.vowel]);
      } else if (Object.prototype.hasOwnProperty.call(REV.paPhonemeToVowelDiacritic, u.vowel)) {
        out.push(pa.alef + REV.paPhonemeToVowelDiacritic[u.vowel]);
      }
      if (u.nasalized) out.push(pa.nasalMark);
      continue;
    }

    let base = null;
    for (const [aspId, baseId] of Object.entries(pa.aspiratePairs)) {
      if (aspId === u.consonant) { base = baseId; break; }
    }
    if (base) {
      out.push(pa.consonants[base] + pa.aspirateMark);
    } else {
      out.push(pa.consonants[u.consonant] ?? '?');
    }

    if (u.vowel === '') {
      out.push(pa.sukun);
    } else if (u.vowel === 'a') {
      // inherent-ish; Perso-Arabic usually leaves short 'a' unmarked
    } else if (Object.prototype.hasOwnProperty.call(pa.longVowelSequences, u.vowel)) {
      out.push(pa.longVowelSequences[u.vowel]);
    } else if (Object.prototype.hasOwnProperty.call(REV.paPhonemeToVowelDiacritic, u.vowel)) {
      out.push(REV.paPhonemeToVowelDiacritic[u.vowel]);
    }

    if (u.nasalized) out.push(pa.nasalMark);
  }
  return out.join('');
}

function persoarabicToUnits(text) {
  const pa = DATA.persoarabic;
  const chars = Array.from(text);
  const units = [];
  let i = 0;
  while (i < chars.length) {
    const ch = chars[i];
    if (ch === ' ' || ch === '\n' || ch === '\t') {
      units.push(new Unit(null, '', false, true));
      i += 1;
      continue;
    }

    if (ch === pa.alef) {
      i += 1;
      let matched = false;
      for (const [phon, seq] of Object.entries(pa.longVowelSequences)) {
        const seqChars = Array.from(seq);
        if (chars.slice(i, i + seqChars.length).join('') === seq) {
          units.push(new Unit(null, phon));
          i += seqChars.length;
          matched = true;
          break;
        }
      }
      let vowel = null;
      if (!matched && i < chars.length && Object.prototype.hasOwnProperty.call(pa.vowelDiacriticToPhoneme, chars[i])) {
        vowel = pa.vowelDiacriticToPhoneme[chars[i]];
        i += 1;
      } else if (!matched) {
        vowel = 'a';
      }
      if (vowel !== null) {
        let nasal = false;
        if (i < chars.length && chars[i] === pa.nasalMark) {
          nasal = true;
          i += 1;
        }
        units.push(new Unit(null, vowel, nasal));
      } else if (matched) {
        if (i < chars.length && chars[i] === pa.nasalMark) {
          units[units.length - 1].nasalized = true;
          i += 1;
        }
      }
      continue;
    }

    if (Object.prototype.hasOwnProperty.call(REV.paConsonants, ch)) {
      let cons = REV.paConsonants[ch];
      i += 1;
      if (i < chars.length && chars[i] === pa.aspirateMark) {
        for (const [aspId, baseId] of Object.entries(pa.aspiratePairs)) {
          if (baseId === cons) { cons = aspId; break; }
        }
        i += 1;
      }
      let vowel = 'a';
      let matched = false;
      for (const [phon, seq] of Object.entries(pa.longVowelSequences)) {
        const seqChars = Array.from(seq);
        if (chars.slice(i, i + seqChars.length).join('') === seq) {
          vowel = phon;
          i += seqChars.length;
          matched = true;
          break;
        }
      }
      if (!matched && i < chars.length && chars[i] === pa.sukun) {
        vowel = '';
        i += 1;
      } else if (!matched && i < chars.length && Object.prototype.hasOwnProperty.call(pa.vowelDiacriticToPhoneme, chars[i])) {
        vowel = pa.vowelDiacriticToPhoneme[chars[i]];
        i += 1;
      }
      let nasal = false;
      if (i < chars.length && chars[i] === pa.nasalMark) {
        nasal = true;
        i += 1;
      }
      units.push(new Unit(cons, vowel, nasal));
      continue;
    }

    units.push(new Unit(null, '', false, false));
    i += 1;
  }
  return units;
}

// ---------------------------------------------------------------- Public

function sharadaToPersoarabic(text) {
  return unitsToPersoarabic(sharadaToUnits(text));
}

function persoarabicToSharada(text) {
  return unitsToSharada(persoarabicToUnits(text));
}

window.KoshurSharada = { loadData, sharadaToPersoarabic, persoarabicToSharada };
