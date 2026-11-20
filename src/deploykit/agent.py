"""Reference customer-service agent: bilingual (Italian / English) triage that answers only from approved text
and hands off to a person whenever a rule says so.

This is the deterministic baseline every engagement starts from: it fixes the escalation policy and the
evaluation set before any language model is put in front of customers. A model-based agent replacing it
must pass the same test set, with the same must-escalate cases at 100%.
"""
from __future__ import annotations

import re
import unicodedata

# language markers (function words only; "a" and "i" are left out because both languages use them)
IT_WORDS = {"il", "la", "le", "lo", "gli", "di", "che", "non", "per", "un", "una", "mi", "ho", "sono", "come", "voglio",
            "della", "perche", "posso", "nella", "con", "del", "al", "e", "c", "vorrei", "mio", "mia", "devo", "da", "questa",
            "questo", "dove", "quando", "cosa", "si", "ci", "vi", "ma", "anche", "sul", "nel", "entro"}
EN_WORDS = {"the", "an", "my", "is", "to", "how", "can", "why", "do", "not", "have", "of", "in", "want", "me", "am",
            "and", "it", "this", "your", "you", "what", "where", "when", "please", "with", "for", "on", "are", "need",
            "will", "there", "here", "our", "we", "m", "s"}
# words ignored when matching intents (function words in both languages)
STOP = IT_WORDS | EN_WORDS | {"a", "i", "ciao", "hello", "hi", "buongiorno", "favore", "grazie", "thanks"}

PII = [  # personal financial data must not be processed in chat
    ("iban", re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9 ]{11,30}\b")),
    ("card number", re.compile(r"\b(?:\d[ -]?){13,19}\b")),
]

HANDOFF_TEXT = {
    "it": "La metto in contatto con un collega che puo aiutarla meglio. Non serve ripetere quanto ha scritto: gli passo la conversazione.",
    "en": "I am passing you to a colleague who can help with this. You will not need to repeat yourself: they will see this conversation.",
}
PII_TEXT = {
    "it": "Per sicurezza non tratto dati bancari o di carte in chat. La metto in contatto con un collega che la aiutera tramite un canale protetto.",
    "en": "For your security I do not handle bank or card details in chat. I am passing you to a colleague who will help through a secure channel.",
}


def normalise(text: str) -> str:
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    t = t.replace("'", " ")
    return re.sub(r"[^a-z0-9 ]+", " ", t)


def tokens(text: str) -> list[str]:
    return [w for w in normalise(text).split() if w]


def language(text: str) -> str:
    toks = tokens(text)
    it = sum(w in IT_WORDS for w in toks)
    en = sum(w in EN_WORDS for w in toks)
    return "en" if en > it else "it"


def _stem(w: str) -> str:
    return w[:5]  # crude stem: enough for bolletta/bollette, pagare/pagamento, payment/payments


def similarity(message: str, example: str) -> float:
    m = {_stem(w) for w in tokens(message) if w not in STOP}
    e = {_stem(w) for w in tokens(example) if w not in STOP}
    if not e or not m:
        return 0.0
    if normalise(example).strip() in normalise(message):
        return 1.0
    hit = len(m & e)
    if hit < min(2, len(e)):   # one shared word is not enough evidence unless the example is a single word
        return 0.0
    return hit / len(e)


def best(message: str, intents: dict) -> tuple[str | None, float]:
    top, score = None, 0.0
    for name, spec in intents.items():
        for ex in spec.get("examples_it", []) + spec.get("examples_en", []):
            s = similarity(message, ex)
            if s > score:
                top, score = name, s
    return top, round(score, 3)


def respond(message: str, kb: dict, threshold: float = 0.5, escalation_threshold: float = 0.5) -> dict:
    """Return {action: answer|handoff, intent, confidence, reason, language, text}. Rules, in order:
    1. personal financial data in the message -> handoff (secure channel)
    2. a safety keyword (complaint, hardship, vulnerability, bank-detail change) -> handoff
    3. an escalation intent matches -> handoff, even if an answer intent also matches
    4. an answer intent matches above the threshold -> approved answer in the customer's language
    5. otherwise -> handoff (low confidence). The agent never improvises an answer."""
    lang = language(message)
    for label, rx in PII:
        if rx.search(message.upper() if label == "iban" else message):
            return {"action": "handoff", "intent": "personal_data", "confidence": 1.0, "language": lang,
                    "reason": f"{label} detected: personal financial data is not processed in chat", "text": PII_TEXT[lang]}
    norm = " " + normalise(message) + " "
    for intent, words in kb.get("escalation_keywords", {}).items():
        if intent.startswith("_"):
            continue
        hit = next((w for w in words if (" " + w) in norm), None)
        if hit:
            return {"action": "handoff", "intent": intent, "confidence": 1.0, "language": lang,
                    "reason": kb["escalation_intents"][intent]["reason"] + f" (safety keyword: {hit})",
                    "text": HANDOFF_TEXT[lang]}
    esc, es = best(message, kb["escalation_intents"])
    if esc and es >= escalation_threshold:
        return {"action": "handoff", "intent": esc, "confidence": es, "language": lang,
                "reason": kb["escalation_intents"][esc]["reason"], "text": HANDOFF_TEXT[lang]}
    intent, s = best(message, kb["intents"])
    if intent and s >= threshold:
        return {"action": "answer", "intent": intent, "confidence": s, "language": lang, "reason": "",
                "text": kb["intents"][intent][f"answer_{lang}"]}
    return {"action": "handoff", "intent": intent if intent else "unknown", "confidence": s, "language": lang,
            "reason": "low confidence: no approved answer matches", "text": HANDOFF_TEXT[lang]}
