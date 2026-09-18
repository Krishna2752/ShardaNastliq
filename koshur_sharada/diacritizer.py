"""
Optional wrapper around HNM Research's Koshur Diacritizer (Malik, Nissar &
Iqbal, arXiv:2606.15883), a ByT5-small model that restores diacritics on
under-diacritized Perso-Arabic Kashmiri text:
https://huggingface.co/Omarrran/koshur-diacritizer-byt5-small

This engine assumes fully-diacritized input (see transliterate.py's
docstring); this module is the "run a diacritizer first" step the README
recommends instead of reimplementing diacritic recovery here.

transformers/torch are only imported inside _load(), so importing this
module -- or the rest of the package -- never requires them. Install with:
    pip install transformers torch
"""

_REPO_ID = "Omarrran/koshur-diacritizer-byt5-small"
_MAX_INPUT_BYTES = 256  # model's documented max input length

_tokenizer = None
_model = None


def _load():
    global _tokenizer, _model
    if _model is not None:
        return
    try:
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    except ImportError as exc:
        raise ImportError(
            "restore_diacritics() requires the optional 'transformers' and "
            "'torch' packages (not needed for the rest of koshur_sharada). "
            "Install with: pip install transformers torch"
        ) from exc
    _tokenizer = AutoTokenizer.from_pretrained(_REPO_ID)
    _model = AutoModelForSeq2SeqLM.from_pretrained(_REPO_ID)


def restore_diacritics(text: str) -> str:
    """
    Run under-diacritized Perso-Arabic Kashmiri text through Koshur
    Diacritizer and return the fully-diacritized result. Loads and caches
    the model from Hugging Face on first call (requires network access
    the first time; cached locally by `transformers` after that).

    The model reports a mean accuracy of 77.5% against native-speaker
    judgment (per the paper) -- treat its output as a best-effort
    restoration to feed into persoarabic_to_sharada(), not as certainly
    correct, especially for text longer than a short sentence.
    """
    if len(text.encode("utf-8")) > _MAX_INPUT_BYTES:
        raise ValueError(
            f"Input is longer than the model's documented max of "
            f"{_MAX_INPUT_BYTES} bytes; split it into shorter sentences first."
        )
    _load()
    inputs = _tokenizer(text, return_tensors="pt")
    out = _model.generate(**inputs, max_new_tokens=256)
    return _tokenizer.decode(out[0], skip_special_tokens=True)
