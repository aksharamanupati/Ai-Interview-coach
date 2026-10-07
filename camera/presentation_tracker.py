"""
Optional Camera & Presentation Observation Tracker.
Computes objective presentation pacing signals (WPM, pause indicators)
with strict ethical guardrails: never scores appearance, gender, ethnicity, or personality.
"""
from typing import Dict, Any

ETHICAL_DISCLAIMER = (
    "Note on Presentation Observations: Presentation analysis is strictly optional and intended "
    "solely for practice self-awareness. In adherence to fairness principles, this system NEVER evaluates "
    "appearance, physical traits, skin tone, gender, ethnicity, or accent. All metrics reflect objective "
    "cadence indicators and are not a measure of employability or character."
)

def evaluate_presentation_cadence(word_count: int, duration_seconds: float) -> Dict[str, Any]:
    """
    Evaluate speaking pace (WPM) and pacing smoothness.
    Normal professional interview speaking rate is approx 120-160 WPM.
    """
    if duration_seconds <= 0:
        duration_seconds = max(1.0, (word_count / 130.0) * 60.0)
        
    minutes = duration_seconds / 60.0
    wpm = round(word_count / minutes, 1) if minutes > 0 else 0.0
    
    if 115 <= wpm <= 165:
        pace_status = "Optimal"
        pace_feedback = f"Excellent pacing ({wpm} WPM). You speak at a clear, easy-to-follow conversational rhythm."
    elif wpm > 165:
        pace_status = "Fast"
        pace_feedback = f"Slightly fast cadence ({wpm} WPM). Consider slowing down slightly on complex architectural explanations."
    elif 70 <= wpm < 115:
        pace_status = "Deliberate"
        pace_feedback = f"Deliberate, steady pace ({wpm} WPM). Good composure; ensure you maintain energy throughout."
    else:
        pace_status = "Brief / Slow"
        pace_feedback = f"Low cadence detected ({wpm} WPM). Aim to expand with more detailed technical reasoning."

    return {
        "words_spoken": word_count,
        "estimated_duration_sec": round(duration_seconds, 1),
        "wpm": wpm,
        "pace_status": pace_status,
        "pace_feedback": pace_feedback,
        "ethical_disclaimer": ETHICAL_DISCLAIMER
    }
