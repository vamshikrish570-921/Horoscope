import streamlit as st
from PIL import Image
import cv2
import numpy as np
from datetime import date
import os

# anthropic and deepface are optional — imported lazily inside functions
# so the app deploys cleanly without them in requirements.txt

# ─────────────────────────────────────────────
#  PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="✨ Celestial Oracle",
    page_icon="🔮",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
#  GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700;900&family=Crimson+Pro:ital,wght@0,300;0,400;1,300;1,400&display=swap');

:root {
    --gold:   #C9A84C;
    --gold2:  #E8C97A;
    --deep:   #06030F;
    --navy:   #0B0825;
    --indigo: #160F3B;
    --violet: #2A1A6E;
    --glow:   #7B5EF8;
    --rose:   #E066A0;
    --teal:   #38D9C0;
    --text:   #EDE8FF;
    --muted:  #9B93CC;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--deep) !important;
    color: var(--text) !important;
    font-family: 'Crimson Pro', Georgia, serif !important;
}
[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 80% 50% at 50% -20%, #2A1A6E55 0%, transparent 70%),
        radial-gradient(ellipse 60% 40% at 80% 80%, #160F3B88 0%, transparent 60%),
        var(--deep) !important;
}
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background-image:
        radial-gradient(1px 1px at 10% 15%, white 0%, transparent 100%),
        radial-gradient(1px 1px at 30% 40%, #ccc 0%, transparent 100%),
        radial-gradient(1.5px 1.5px at 55% 10%, white 0%, transparent 100%),
        radial-gradient(1px 1px at 75% 60%, #aaa 0%, transparent 100%),
        radial-gradient(1px 1px at 90% 25%, white 0%, transparent 100%),
        radial-gradient(1px 1px at 20% 80%, #bbb 0%, transparent 100%),
        radial-gradient(1.5px 1.5px at 65% 85%, white 0%, transparent 100%),
        radial-gradient(1px 1px at 45% 55%, #ddd 0%, transparent 100%),
        radial-gradient(1px 1px at 85% 45%, white 0%, transparent 100%),
        radial-gradient(1px 1px at 5% 50%, #ccc 0%, transparent 100%);
    opacity: 0.6;
}

#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

.block-container {
    padding: 2rem 2rem 4rem !important;
    max-width: 820px !important;
    position: relative; z-index: 1;
}

/* Hero */
.celestial-hero { text-align: center; padding: 2.5rem 0 1rem; }
.celestial-hero h1 {
    font-family: 'Cinzel Decorative', serif !important;
    font-size: clamp(2rem, 6vw, 3.2rem) !important;
    font-weight: 900 !important;
    background: linear-gradient(135deg, var(--gold2) 0%, var(--gold) 40%, var(--rose) 70%, var(--glow) 100%);
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    letter-spacing: .12em; text-shadow: none; margin: 0; line-height: 1.2;
}
.celestial-hero .tagline {
    font-size: 1.05rem; color: var(--muted); font-style: italic;
    margin-top: .6rem; letter-spacing: .08em;
}
.celestial-hero .divider {
    margin: 1.2rem auto .2rem; width: 160px; height: 1px;
    background: linear-gradient(90deg, transparent, var(--gold), var(--rose), var(--gold), transparent);
}

/* Cards */
.oracle-card {
    background: linear-gradient(145deg, #11082A, #1A0F3C);
    border: 1px solid #3A2A7055; border-radius: 20px;
    padding: 2rem 2.2rem; margin: 1.4rem 0;
    box-shadow: 0 0 40px #7B5EF810, inset 0 1px 0 #ffffff08;
}
.section-label {
    font-family: 'Cinzel Decorative', serif !important;
    font-size: .72rem !important; letter-spacing: .22em !important;
    color: var(--gold) !important; text-transform: uppercase !important;
    margin-bottom: .6rem !important;
}

/* Inputs */
.stTextInput > div > div > input,
.stDateInput > div > div > input,
.stSelectbox > div > div {
    background: #0F0730 !important; border: 1px solid #3D2D7A !important;
    border-radius: 10px !important; color: var(--text) !important;
    font-family: 'Crimson Pro', serif !important; font-size: 1.05rem !important;
}
.stTextInput > div > div > input:focus,
.stDateInput > div > div > input:focus {
    border-color: var(--glow) !important;
    box-shadow: 0 0 0 2px #7B5EF830 !important;
}
.stTextInput label, .stDateInput label, .stSelectbox label, .stFileUploader label {
    font-family: 'Cinzel Decorative', serif !important;
    font-size: .7rem !important; letter-spacing: .18em !important;
    color: var(--gold) !important; text-transform: uppercase !important;
}
.stCamera, [data-testid="stFileUploadDropzone"] {
    background: #0A0525 !important; border: 1.5px dashed #3D2D7A !important;
    border-radius: 14px !important;
}

/* Buttons */
.stButton > button {
    width: 100% !important;
    background: linear-gradient(135deg, #3B1FA8, #7B5EF8, #5A3BC8) !important;
    color: white !important; border: none !important; border-radius: 50px !important;
    font-family: 'Cinzel Decorative', serif !important; font-size: .85rem !important;
    letter-spacing: .15em !important; padding: .85rem 2rem !important;
    cursor: pointer !important; transition: all .3s ease !important;
    box-shadow: 0 4px 20px #7B5EF845 !important; text-transform: uppercase !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px #7B5EF870 !important;
    background: linear-gradient(135deg, #4D2CC0, #9070FF, #6A4BD8) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* Progress */
.stProgress > div > div { background: linear-gradient(90deg, var(--glow), var(--rose)) !important; }

/* Result card */
.result-card {
    background: linear-gradient(145deg, #110B30, #1E1248);
    border-left: 3px solid var(--gold); border-radius: 0 16px 16px 0;
    padding: 1.8rem 2rem; margin: 1rem 0;
    box-shadow: 0 0 50px #7B5EF818;
}
.result-card h2 {
    font-family: 'Cinzel Decorative', serif !important; font-size: 1.6rem !important;
    background: linear-gradient(90deg, var(--gold2), var(--rose));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.result-card .zodiac-sign {
    font-size: 3.5rem; text-align: center; filter: drop-shadow(0 0 12px #C9A84C88);
}

/* Pills */
.stat-row { display: flex; flex-wrap: wrap; gap: .7rem; margin: 1rem 0; }
.stat-pill {
    background: #1C1048; border: 1px solid #3D2A7A; border-radius: 50px;
    padding: .35rem .9rem; color: var(--gold2);
    font-family: 'Cinzel Decorative', serif; font-size: .68rem; letter-spacing: .1em;
}

/* Emotion box */
.emotion-box {
    background: linear-gradient(135deg, #0D0830, #1A0F42);
    border: 1px solid #4A3A8A; border-radius: 14px;
    padding: 1.2rem 1.5rem; margin-top: 1rem; text-align: center;
}
.emotion-box .emotion-emoji { font-size: 3rem; }
.emotion-box .emotion-label {
    font-family: 'Cinzel Decorative', serif; font-size: .75rem;
    letter-spacing: .2em; color: var(--teal); text-transform: uppercase;
}

/* ── FIXED: Reading section rows render as proper HTML blocks ── */
.reading-intro {
    font-size: 1.08rem; line-height: 1.9; color: #DDD5F8;
    font-style: italic; margin-bottom: 1rem;
    border-bottom: 1px solid #2A1A5A; padding-bottom: .8rem;
}
.reading-section {
    border-left: 2px solid #3D2A7A;
    padding: .6rem 0 .6rem 1rem;
    margin: .8rem 0;
}
.reading-section .rs-title {
    font-family: 'Cinzel Decorative', serif;
    font-size: .72rem; letter-spacing: .18em;
    color: var(--gold); text-transform: uppercase; margin-bottom: .3rem;
}
.reading-section .rs-body {
    font-size: 1.05rem; line-height: 1.8; color: #DDD5F8;
}

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--deep); }
::-webkit-scrollbar-thumb { background: var(--violet); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────
ZODIAC_GLYPHS = {
    "Aries":"♈","Taurus":"♉","Gemini":"♊","Cancer":"♋",
    "Leo":"♌","Virgo":"♍","Libra":"♎","Scorpio":"♏",
    "Sagittarius":"♐","Capricorn":"♑","Aquarius":"♒","Pisces":"♓",
}
ZODIAC_ELEMENTS = {
    "Aries":"🔥 Fire","Leo":"🔥 Fire","Sagittarius":"🔥 Fire",
    "Taurus":"🌿 Earth","Virgo":"🌿 Earth","Capricorn":"🌿 Earth",
    "Gemini":"💨 Air","Libra":"💨 Air","Aquarius":"💨 Air",
    "Cancer":"💧 Water","Scorpio":"💧 Water","Pisces":"💧 Water",
}
LUCKY_NUMBERS = {
    "Aries":[1,9,17],"Taurus":[2,6,24],"Gemini":[3,12,21],
    "Cancer":[4,13,22],"Leo":[5,19,28],"Virgo":[6,15,24],
    "Libra":[7,16,25],"Scorpio":[8,18,27],"Sagittarius":[9,17,26],
    "Capricorn":[10,20,29],"Aquarius":[11,22,31],"Pisces":[12,21,30],
}
RULING_PLANETS = {
    "Aries":"♂ Mars","Taurus":"♀ Venus","Gemini":"☿ Mercury",
    "Cancer":"☽ Moon","Leo":"☀ Sun","Virgo":"☿ Mercury",
    "Libra":"♀ Venus","Scorpio":"♇ Pluto","Sagittarius":"♃ Jupiter",
    "Capricorn":"♄ Saturn","Aquarius":"♅ Uranus","Pisces":"♆ Neptune",
}
EMOTION_COSMIC_MAP = {
    "happy":   ("🌟","Your aura radiates solar brilliance today."),
    "sad":     ("🌊","The tides of Neptune draw you inward for reflection."),
    "angry":   ("🔥","Mars ignites your spirit — channel it wisely."),
    "fear":    ("🌒","Saturn's shadow tests your courage. Trust yourself."),
    "surprise":("⚡","Uranus brings sudden revelations your way!"),
    "disgust": ("🌿","Your soul seeks purity and higher vibrations."),
    "neutral": ("🔮","You hold the cosmic balance between the stars."),
}
LUCKY_COLORS = {
    "🔥 Fire":  ["Crimson","Gold","Saffron"],
    "🌿 Earth": ["Emerald","Amber","Sage"],
    "💨 Air":   ["Lavender","Sky Blue","Silver"],
    "💧 Water": ["Teal","Midnight Blue","Pearl"],
}
EMOTION_LAYER = {
    "happy":   "Your joyful aura amplifies every positive cosmic signal around you today. Ride this wave.",
    "sad":     "The cosmos honours your depth of feeling. Grief and growth share the same soil — something new is quietly germinating.",
    "angry":   "Mars sees your fire and raises it. Redirect this fierce energy toward a goal rather than a grievance — the results will astonish you.",
    "fear":    "Saturn tests only those strong enough to pass. The very thing you fear is the threshold to your next level of power.",
    "surprise":"Uranus loves catching you off-guard — surprise is the universe's way of reminding you that the story is still being written.",
    "disgust": "Your soul is performing a purge — clearing space for something far more aligned with who you are becoming.",
    "neutral": "Your centred aura gives you the rare gift of objective perception today. You can see clearly what others, clouded by emotion, cannot.",
}

# ── Full static readings — all 12 signs, all 4 sections ──
READINGS = {
    "Aries":{"intro":"The Ram charges forward under the blazing gaze of Mars. Your cosmic energy is at its peak — raw, unstoppable, primed for conquest.",
             "love":"Venus lights a spark between you and someone whose fire matches yours. If already in love, plan a bold adventure together — routine is your enemy right now.",
             "career":"A project you have been pushing uphill is about to gain traction. Mars rewards the persistent. Speak up in meetings — your words carry unusual authority today.",
             "health":"Your body craves movement and challenge. Channel pent-up energy into vigorous exercise. Avoid caffeine after noon — your nervous system is already running hot.",
             "cosmic":"The universe rewards the brave this week. Write the email. Make the call. Begin the thing you have been postponing since the last new moon."},
    "Taurus":{"intro":"Venus wraps you in a velvet embrace as the Bull stands firmly on fertile ground. Abundance is not coming — it is already here, waiting to be noticed.",
              "love":"Slow, steady devotion is your love language and someone nearby speaks it fluently. Singles: a chance meeting in a familiar place carries unexpected depth.",
              "career":"Your eye for quality and patience set you apart. A financial opportunity deserves careful review — the numbers are better than they first appear.",
              "health":"Your throat and neck hold tension you have been ignoring. Gentle stretching, warm herbal teas, and time in nature will restore your earthly equilibrium.",
              "cosmic":"Plant a seed today — literal or symbolic. Whatever you nurture with consistency now will bloom magnificently by the next full moon."},
    "Gemini":{"intro":"Mercury dances a quicksilver waltz through your chart, doubling your wit and tripling your curiosity. The Twins are in rare form — ideas flow like starlight.",
              "love":"Conversation is your greatest seduction. Share something you have never told anyone — vulnerability creates the intimacy your quick mind sometimes sidesteps.",
              "career":"A writing, speaking, or teaching opportunity materialises this week. Your ability to explain complex ideas simply is a superpower others are just now noticing.",
              "health":"Your lungs and hands need attention. Deep breathing exercises and breaks from screens will clear the mental fog that follows mental overload.",
              "cosmic":"Choose one idea from the ten spinning in your mind and give it a full week of focused attention. Depth is this season's gift from the cosmos."},
    "Cancer":{"intro":"The Moon whispers tenderly to your soul, illuminating the hidden chambers of your heart. Your intuition is sharper than any sword this week.",
              "love":"Home is where your love story is written most beautifully. Invite someone into your sanctuary — cooking together, sharing old memories — magic lives in the ordinary.",
              "career":"Your emotional intelligence is a professional asset. A colleague needs to feel understood before they can be convinced. Lead with empathy, then logic.",
              "health":"Your stomach mirrors your emotional state. Soothing foods, adequate rest, and an honest conversation you have been avoiding will ease the physical tension you carry.",
              "cosmic":"Your greatest power this week is the ability to create safety — for others and yourself. What would you do if you truly felt secure? Begin that."},
    "Leo":{"intro":"The Sun blazes in your honour, illuminating every room you enter. The Lion's mane is golden and the stage is set — this is your moment.",
           "love":"Generosity is your most magnetic quality right now. Grand gestures, heartfelt compliments, and undivided attention will make someone fall deeper under your spell.",
           "career":"Leadership opportunities are orbiting closer. Step forward — no one else in the room has your combination of vision and charisma. Your confidence is contagious.",
           "health":"Your heart — the organ Leo rules — needs joyful exercise. Dance, play a sport, or do anything that makes you laugh until your chest hurts in the best possible way.",
           "cosmic":"The cosmos asks you to shine not to outshine others, but to give them permission to shine too. Your light is a lantern, not a spotlight. Share it generously."},
    "Virgo":{"intro":"Mercury sharpens your already precise mind to a diamond point. The Maiden surveys her domain and sees exactly what needs mending — and exactly how to do it.",
             "love":"Acts of service are your love letter to the world. Someone has noticed every small thing you do for them. This week they find the words to tell you so.",
             "career":"The details you obsess over are the difference between good work and great work. A complex problem that has stumped others will yield to your methodical approach.",
             "health":"Your digestive system is your barometer for stress. Mindful eating, fewer processed foods, and a ten-minute evening walk will recalibrate your nervous system beautifully.",
             "cosmic":"Perfection is the enemy of completion. The project that is 85% ready is ready enough. Release it into the world and let it grow in the light."},
    "Libra":{"intro":"Venus harmonises your inner scales as the Scales-bearer stands at the crossroads of beauty and truth. Balance is not your limitation — it is your superpower.",
             "love":"You are irresistible when you stop trying to be irresistible. An authentic, slightly imperfect version of yourself draws more love than the polished performance ever could.",
             "career":"Negotiations, contracts, and partnerships all favour you this week. Your ability to see all sides of an argument makes you the most valuable person in any room.",
             "health":"Your kidneys and lower back hold the stress of indecision. Make the choice you have been agonising over — your body will thank you with immediate relief.",
             "cosmic":"The universe is asking you to choose — not between good and bad, but between two goods. Trust your first instinct. It has been whispering the answer for weeks."},
    "Scorpio":{"intro":"Pluto stirs the depths like a cosmic hand reaching into the ocean floor. The Scorpion's transformation is not coming — it is already happening beneath the surface.",
               "love":"Intensity is your natural frequency but intimacy requires trust before it can hold your full power. Let someone see your softness this week — it is your rarest gift.",
               "career":"Research, investigation, and uncovering hidden information are your gifts right now. Something that others have overlooked is the key that unlocks a major opportunity.",
               "health":"Hydration, rest, and releasing grudges are your medicine this week. Yes — emotional release has direct physical consequences for Scorpio.",
               "cosmic":"What are you holding onto that no longer serves you? A belief, a resentment, an old version of yourself? Release it consciously and feel the extraordinary lightness that follows."},
    "Sagittarius":{"intro":"Jupiter expands every horizon your eyes can reach. The Archer pulls back the bowstring of destiny — the arrow is ready and the target is calling your name.",
                   "love":"Your adventurous spirit is magnetic to someone who has been living too cautiously. Invite them into your world — a spontaneous plan works better than a perfect one.",
                   "career":"International matters, education, publishing, or philosophy all shine brightly in your chart this week. Think bigger than your current scope — then think bigger still.",
                   "health":"Your hips and thighs carry the weight of your wanderlust. Stretching, yoga, or a long walk somewhere new will free both body and mind from accumulated restlessness.",
                   "cosmic":"The universe is a library with no overdue fees. Learn something entirely outside your field this week — the unexpected connection it creates will be your next great adventure."},
    "Capricorn":{"intro":"Saturn stands as your steadfast guardian, rewarding every hour of disciplined effort you have invested. The Sea-Goat is climbing and the summit is no longer hidden in cloud.",
                 "love":"Commitment and reliability are romantic to the right person — and that person is paying attention. Let your guard down by just 10%: that is all the vulnerability required.",
                 "career":"Long-term investments and legacy work demand your focus. A senior figure offers guidance that is more valuable than it initially appears. Listen carefully.",
                 "health":"Your bones and joints are ruled by Capricorn. Calcium-rich foods, weight-bearing exercise, and adequate sleep are your body's love language right now.",
                 "cosmic":"The mountain you are climbing exists inside you as much as outside. The inner critic that says you are not there yet has served its purpose. Thank it and climb on."},
    "Aquarius":{"intro":"Uranus sparks revolution in the electric pathways of your brilliant mind. The Water-Bearer pours cosmic knowledge freely — humanity needs your peculiar genius right now.",
                "love":"Friendship is the foundation of your deepest love story. Someone in your circle sees you in a way no one else does. Pay attention to who makes you feel truly understood.",
                "career":"Technology, innovation, and humanitarian causes align with your energy this week. The unconventional solution you have been dismissed for proposing is about to be proved right.",
                "health":"Your circulatory system needs movement and oxygenation. Group exercise or community walks combine the social fuel your soul needs with the physical movement your body craves.",
                "cosmic":"You are ahead of your time — always have been. Find your people and build the future together. The loneliness of being first is the price of vision."},
    "Pisces":{"intro":"Neptune dissolves the boundary between you and the infinite as the Fish swim through the deep cosmic waters. Your dream life this week is a message — decode it.",
              "love":"Your empathy is a superpower and a vulnerability in equal measure. This week love asks you to receive as graciously as you give. Let someone take care of you.",
              "career":"Creative, healing, and spiritual work carry an unusual potency right now. The project that seems too imaginative, too unconventional — that is exactly the one to pursue.",
              "health":"Your immune system and feet are Pisces' domain. Rest before you think you need it. Soaking your feet in warm water with sea salt sounds simple because simple things work.",
              "cosmic":"The boundary between imagination and reality is thinner for you than for any other sign. Whatever you can dream clearly enough, consistently enough, is already on its way to you."},
}


# ─────────────────────────────────────────────
#  CORE FUNCTIONS
# ─────────────────────────────────────────────
def get_zodiac_sign(dob: date) -> str:
    m, d = dob.month, dob.day
    if (m==3 and d>=21) or (m==4 and d<=19):   return "Aries"
    if (m==4 and d>=20) or (m==5 and d<=20):   return "Taurus"
    if (m==5 and d>=21) or (m==6 and d<=20):   return "Gemini"
    if (m==6 and d>=21) or (m==7 and d<=22):   return "Cancer"
    if (m==7 and d>=23) or (m==8 and d<=22):   return "Leo"
    if (m==8 and d>=23) or (m==9 and d<=22):   return "Virgo"
    if (m==9 and d>=23) or (m==10 and d<=22):  return "Libra"
    if (m==10 and d>=23) or (m==11 and d<=21): return "Scorpio"
    if (m==11 and d>=22) or (m==12 and d<=21): return "Sagittarius"
    if (m==12 and d>=22) or (m==1 and d<=19):  return "Capricorn"
    if (m==1 and d>=20) or (m==2 and d<=18):   return "Aquarius"
    return "Pisces"


def fast_face_scan(pil_image: Image.Image) -> dict:
    """
    FIX 1: No heavy model loading on the main thread.
    Uses built-in OpenCV Haar cascade (instant, no download) for face detection.
    Brightness heuristic gives instant emotion. DeepFace tried only as a bonus.
    """
    img_rgb  = np.array(pil_image.convert("RGB"))
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)

    # Instant brightness-based mood heuristic
    brightness = float(np.mean(img_gray))
    contrast   = float(np.std(img_gray))
    if brightness > 160:
        q_emotion = "happy"
    elif brightness < 80:
        q_emotion = "sad"
    elif contrast > 70:
        q_emotion = "surprise"
    else:
        q_emotion = "neutral"

    # Fast Haar face detection — no download, ships with OpenCV
    cascade   = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces     = cascade.detectMultiScale(img_gray, scaleFactor=1.1, minNeighbors=5)
    face_found = len(faces) > 0

    # Try DeepFace only if face found (and only if installed)
    if face_found:
        try:
            from deepface import DeepFace
            img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
            res = DeepFace.analyze(
                img_bgr, actions=["emotion","age","gender"],
                enforce_detection=False, silent=True,
                detector_backend="opencv",
            )
            if isinstance(res, list):
                res = res[0]
            return {
                "emotion":    res.get("dominant_emotion", q_emotion).lower(),
                "age":        int(res.get("age", 0)) or None,
                "gender":     res.get("dominant_gender", res.get("gender", None)),
                "face_found": True,
                "deepface":   True,
            }
        except Exception:
            pass

    return {"emotion": q_emotion, "age": None, "gender": None,
            "face_found": face_found, "deepface": False}


def build_static_reading_html(name: str, sign: str, emotion: str) -> str:
    """
    FIX 2: Returns properly structured HTML with <div> sections — not \\n plain text.
    This guarantees Love / Career / Health / Cosmic Message all appear as
    distinct labelled blocks in the browser.
    """
    data    = READINGS.get(sign, READINGS["Aries"])
    em_note = EMOTION_LAYER.get(emotion, EMOTION_LAYER["neutral"])

    sections = [
        ("❤️ Love &amp; Relationships", data["love"]),
        ("💼 Career &amp; Purpose",     data["career"]),
        ("🌿 Health &amp; Vitality",    data["health"]),
        ("✨ Cosmic Message",           data["cosmic"]),
    ]
    html = (f'<p class="reading-intro">{data["intro"]}<br><br>'
            f'<em style="color:#9B93CC;">{em_note}</em></p>')
    for title, body in sections:
        html += (f'<div class="reading-section">'
                 f'<div class="rs-title">{title}</div>'
                 f'<div class="rs-body">{body}</div>'
                 f'</div>')
    return html


def generate_reading(name: str, sign: str, emotion: str, element: str, age: int) -> tuple:
    """Returns (html_string, used_ai_bool). AI if ANTHROPIC_API_KEY is set."""
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if api_key:
        try:
            import anthropic
            prompt = (
                f"You are a mystical cosmic oracle. Write a vivid personalised horoscope for "
                f"{name}, a {sign} ({element}), whose current emotional aura is '{emotion}'. "
                f"{'Age approximately ' + str(age) + '.' if age else ''} "
                f"Structure your response with exactly four labelled sections:\n"
                f"LOVE, CAREER, HEALTH, COSMIC MESSAGE\n"
                f"Each section: 2-3 poetic sentences. "
                f"Begin with one atmospheric opening sentence before the first section."
            )
            client  = anthropic.Anthropic(api_key=api_key)
            message = client.messages.create(
                model="claude-sonnet-4-20250514", max_tokens=500,
                messages=[{"role":"user","content":prompt}],
            )
            raw   = message.content[0].text
            lines = [l.strip() for l in raw.strip().splitlines() if l.strip()]
            intro = lines[0] if lines else ""
            smap  = {"LOVE":"","CAREER":"","HEALTH":"","COSMIC MESSAGE":""}
            cur   = None
            for line in lines[1:]:
                key = next((k for k in smap if line.upper().startswith(k)), None)
                if key:
                    cur  = key
                    rest = line[len(key):].lstrip(":— ").strip()
                    if rest: smap[cur] = rest
                elif cur:
                    smap[cur] += (" " if smap[cur] else "") + line

            icons = {"LOVE":"❤️ Love &amp; Relationships",
                     "CAREER":"💼 Career &amp; Purpose",
                     "HEALTH":"🌿 Health &amp; Vitality",
                     "COSMIC MESSAGE":"✨ Cosmic Message"}
            html  = f'<p class="reading-intro">{intro}</p>'
            for k, label in icons.items():
                body = smap.get(k, "")
                if body:
                    html += (f'<div class="reading-section">'
                             f'<div class="rs-title">{label}</div>'
                             f'<div class="rs-body">{body}</div>'
                             f'</div>')
            if html.count("reading-section") >= 2:
                return html, True
        except Exception:
            pass
    return build_static_reading_html(name, sign, emotion), False


# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
DEFAULTS = {
    "step": 1, "face_data": None, "horoscope_html": None, "horoscope_ai": False,
    "_name": "", "_dob": date(1995, 1, 1), "_gender": "Prefer not to say", "_sign": "Aries",
    "face_image": None,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─────────────────────────────────────────────
#  HERO
# ─────────────────────────────────────────────
st.markdown("""
<div class="celestial-hero">
  <h1>✦ Celestial Oracle ✦</h1>
  <div class="divider"></div>
  <p class="tagline">Where the stars meet your soul — personalised cosmic readings await.</p>
</div>
""", unsafe_allow_html=True)

# Step indicator
steps = ["Your Identity", "Face Scan", "Cosmic Reading"]
cols  = st.columns(3)
for i, (col, label) in enumerate(zip(cols, steps), 1):
    active = i == st.session_state.step
    done   = i < st.session_state.step
    icon   = "✓" if done else str(i)
    color  = "#C9A84C" if active else ("#38D9C0" if done else "#3D2A7A")
    col.markdown(
        f"<div style='text-align:center;font-family:\"Cinzel Decorative\",serif;"
        f"font-size:.65rem;letter-spacing:.12em;color:{color};padding:.5rem;'>"
        f"{icon} · {label.upper()}</div>",
        unsafe_allow_html=True,
    )
st.progress((st.session_state.step - 1) / (len(steps) - 1))
st.markdown("<br>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  STEP 1 — IDENTITY
# ─────────────────────────────────────────────
if st.session_state.step == 1:
    st.markdown('<div class="oracle-card">', unsafe_allow_html=True)
    st.markdown('<p class="section-label">✦ Your Celestial Identity</p>', unsafe_allow_html=True)

    name   = st.text_input("Full Name", value=st.session_state._name,
                            placeholder="e.g. Arjun Sharma")
    dob    = st.date_input("Date of Birth",
                            min_value=date(1920,1,1), max_value=date.today(),
                            value=st.session_state._dob)
    gender = st.selectbox("Gender (optional)",
                           ["Prefer not to say","Female","Male","Non-binary","Other"],
                           index=["Prefer not to say","Female","Male","Non-binary","Other"]
                                 .index(st.session_state._gender))

    if name and dob:
        sign    = get_zodiac_sign(dob)
        element = ZODIAC_ELEMENTS[sign]
        glyph   = ZODIAC_GLYPHS[sign]
        age     = (date.today() - dob).days // 365
        st.markdown(f"""
        <div style="margin-top:1.4rem;text-align:center;">
            <div style="font-size:4rem;filter:drop-shadow(0 0 14px #C9A84C88);">{glyph}</div>
            <div style="font-family:'Cinzel Decorative',serif;font-size:.8rem;
                        letter-spacing:.2em;color:#C9A84C;margin-top:.4rem;">YOUR SIGN IS</div>
            <div style="font-family:'Cinzel Decorative',serif;font-size:1.6rem;
                        color:#E8C97A;margin-top:.2rem;">{sign}</div>
            <div style="color:#9B93CC;margin-top:.3rem;font-style:italic;">
                {element} · {RULING_PLANETS[sign]} · Age {age}</div>
        </div>
        <div class="stat-row" style="justify-content:center;margin-top:1rem;">
            <div class="stat-pill">Lucky: {', '.join(map(str, LUCKY_NUMBERS[sign]))}</div>
            <div class="stat-pill">{element}</div>
            <div class="stat-pill">{RULING_PLANETS[sign]}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    if st.button("✦ Continue to Face Scan"):
        if not name:
            st.error("Please enter your name to continue.")
        else:
            st.session_state._name   = name
            st.session_state._dob    = dob
            st.session_state._gender = gender
            st.session_state._sign   = get_zodiac_sign(dob)
            st.session_state.step    = 2
            st.rerun()


# ─────────────────────────────────────────────
#  STEP 2 — FACE SCAN
# ─────────────────────────────────────────────
elif st.session_state.step == 2:
    st.markdown('<div class="oracle-card">', unsafe_allow_html=True)
    st.markdown('<p class="section-label">✦ Aura &amp; Emotion Scan</p>', unsafe_allow_html=True)
    st.markdown("""<p style="color:#9B93CC;font-style:italic;margin-bottom:1rem;">
        The stars read not only your birth chart but also your current emotional vibration.
        Capture or upload your photo so the oracle can sense your aura.
    </p>""", unsafe_allow_html=True)

    method  = st.radio("Scan method:", ["📷 Camera", "🖼 Upload Photo"], horizontal=True)
    img_pil = None

    if method == "📷 Camera":
        cam = st.camera_input("Look gently into the oracle…")
        if cam:
            img_pil = Image.open(cam)
    else:
        up = st.file_uploader("Upload your photo", type=["jpg","jpeg","png","webp"])
        if up:
            img_pil = Image.open(up)

    if img_pil:
        thumb = img_pil.copy()
        thumb.thumbnail((300, 300))
        # FIX 3: use_container_width replaces deprecated use_column_width
        st.image(thumb, caption="📸 Aura captured", width=300)
        st.markdown("</div>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("← Back"):
                st.session_state.step = 1
                st.rerun()
        with c2:
            if st.button("✦ Reveal My Destiny"):
                # FIX 4: spinner wraps only the fast scan (no model loading delay)
                with st.spinner("🔮 Reading your aura…"):
                    fd = fast_face_scan(img_pil)
                st.session_state.face_data = fd

                # Generate full reading here so step 3 is instant
                with st.spinner("✨ Consulting the star charts…"):
                    name    = st.session_state._name
                    sign    = st.session_state._sign
                    element = ZODIAC_ELEMENTS[sign]
                    dob     = st.session_state._dob
                    age     = (date.today() - dob).days // 365
                    html, used_ai = generate_reading(name, sign, fd["emotion"], element, age)
                    st.session_state.horoscope_html = html
                    st.session_state.horoscope_ai   = used_ai

                st.session_state.face_image = img_pil
                st.session_state.step       = 3
                st.rerun()
    else:
        st.markdown("</div>", unsafe_allow_html=True)
        if st.button("← Back"):
            st.session_state.step = 1
            st.rerun()


# ─────────────────────────────────────────────
#  STEP 3 — READING
# ─────────────────────────────────────────────
elif st.session_state.step == 3:
    name    = st.session_state._name or "Seeker"
    sign    = st.session_state._sign or "Aries"
    dob     = st.session_state._dob  or date(1995,1,1)
    fd      = st.session_state.face_data or {}
    emotion = fd.get("emotion","neutral")
    f_age   = fd.get("age")
    f_gen   = fd.get("gender")
    element = ZODIAC_ELEMENTS[sign]
    glyph   = ZODIAC_GLYPHS[sign]
    age     = (date.today() - dob).days // 365
    colors  = LUCKY_COLORS.get(element, ["Gold","Silver","White"])

    em_emoji, em_msg = EMOTION_COSMIC_MAP.get(emotion, EMOTION_COSMIC_MAP["neutral"])

    # ── Zodiac Banner ──
    st.markdown(f"""
    <div class="result-card">
        <div class="zodiac-sign">{glyph}</div>
        <h2 style="text-align:center;">{name} · {sign}</h2>
        <div style="text-align:center;color:#9B93CC;margin-bottom:1rem;">
            {element} · {RULING_PLANETS[sign]} · {dob.strftime('%B %d, %Y')}
        </div>
        <div class="stat-row" style="justify-content:center;">
            <div class="stat-pill">🔢 {', '.join(map(str,LUCKY_NUMBERS[sign]))}</div>
            <div class="stat-pill">🎨 {', '.join(colors)}</div>
            <div class="stat-pill">{RULING_PLANETS[sign]}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Aura Box ──
    aura = (f'<div class="emotion-box">'
            f'<div class="emotion-emoji">{em_emoji}</div>'
            f'<div class="emotion-label">Current Aura · {emotion.capitalize()}</div>'
            f'<p style="color:#C8C0E8;margin-top:.6rem;font-style:italic;">{em_msg}</p>')
    if f_age:
        aura += f'<p style="color:#9B93CC;font-size:.9rem;">Estimated age: {f_age}'
        aura += f' · {f_gen}</p>' if f_gen else '</p>'
    if fd.get("face_found") and not fd.get("deepface"):
        aura += '<p style="color:#6B6090;font-size:.78rem;margin-top:.3rem;">Face detected · Aura read by light analysis (DeepFace optional for deeper scan).</p>'
    elif not fd.get("face_found"):
        aura += '<p style="color:#6B6090;font-size:.78rem;margin-top:.3rem;">No face detected clearly — aura read via cosmic intuition.</p>'
    aura += '</div>'
    st.markdown(aura, unsafe_allow_html=True)

    # ── FIX 2 applied: reading_html is always structured HTML with visible sections ──
    reading_html = st.session_state.horoscope_html
    if not reading_html:
        with st.spinner("✨ Consulting the star charts…"):
            reading_html, used_ai = generate_reading(name, sign, emotion, element, age)
            st.session_state.horoscope_html = reading_html
            st.session_state.horoscope_ai   = used_ai

    badge = (
        ' <span style="color:#38D9C0;font-size:.65rem;letter-spacing:.1em;">· ✦ AI POWERED</span>'
        if st.session_state.horoscope_ai else
        ' <span style="color:#6B6090;font-size:.65rem;letter-spacing:.1em;">· CLASSIC READING</span>'
    )
    st.markdown(f"""
    <div class="oracle-card" style="margin-top:1.2rem;">
        <p class="section-label">✦ Your Cosmic Reading for Today{badge}</p>
        {reading_html}
    </div>
    """, unsafe_allow_html=True)

    # ── Celestial Gifts ──
    day = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"][date.today().weekday()]
    st.markdown(f"""
    <div class="oracle-card">
        <p class="section-label">✦ Today's Celestial Gifts</p>
        <div class="stat-row">
            <div class="stat-pill">🔢 Lucky: {', '.join(map(str,LUCKY_NUMBERS[sign]))}</div>
            <div class="stat-pill">🎨 {', '.join(colors)}</div>
            <div class="stat-pill">⭐ {element}</div>
            <div class="stat-pill">🪐 {RULING_PLANETS[sign]}</div>
        </div>
        <p style="color:#9B93CC;font-size:.88rem;margin-top:.8rem;font-style:italic;">
            ✦ Best hours: 6–9 AM &amp; 6–9 PM &nbsp;·&nbsp; Power day: {day}
        </p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔄 Refresh Reading"):
            st.session_state.horoscope_html = None
            st.rerun()
    with c2:
        # FIX 5: reset uses DEFAULTS dict — no key mismatch
        if st.button("✦ Start Over"):
            for k, v in DEFAULTS.items():
                st.session_state[k] = v
            st.rerun()

    st.markdown("""
    <div style="text-align:center;padding:2rem 0 1rem;color:#4A3A6A;font-size:.8rem;
                font-family:'Cinzel Decorative',serif;letter-spacing:.15em;">
        ✦ &nbsp; CELESTIAL ORACLE &nbsp; ✦ &nbsp; FOR ENTERTAINMENT PURPOSES &nbsp; ✦
    </div>
    """, unsafe_allow_html=True)