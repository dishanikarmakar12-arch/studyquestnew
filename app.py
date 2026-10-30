import streamlit as st
import time
from datetime import date, timedelta

st.set_page_config(page_title="Study Quest", page_icon="📚", layout="wide")

# Keep the student's progress while the app is open.
if "subjects" not in st.session_state:
    st.session_state.subjects = []
if "xp" not in st.session_state:
    st.session_state.xp = 0
if "sessions" not in st.session_state:
    st.session_state.sessions = []
if "streak" not in st.session_state:
    st.session_state.streak = 0
if "last_study_day" not in st.session_state:
    st.session_state.last_study_day = None

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #130d25, #101a31);
    color: #f5f2ff;
}
h1, h2, h3 { color: #f5f2ff; }
.quest-card {
    background: rgba(120, 95, 190, 0.18);
    border: 1px solid rgba(180, 150, 255, 0.28);
    border-radius: 18px;
    padding: 22px;
    margin: 10px 0;
}
.small-note { color: #b9addd; }
</style>
""", unsafe_allow_html=True)

def add_completed_session(subject, minutes):
    """Give XP, save the session, and update the study streak."""
    today = date.today()
    st.session_state.xp += minutes * 2

    st.session_state.sessions.append({
        "subject": subject,
        "minutes": minutes,
        "date": today.isoformat()
    })

    last_day = st.session_state.last_study_day
    if last_day is None:
        st.session_state.streak = 1
    else:
        previous_day = date.fromisoformat(last_day)
        if previous_day == today:
            pass  # Another session today does not add another streak day.
        elif previous_day == today - timedelta(days=1):
            st.session_state.streak += 1
        else:
            st.session_state.streak = 1

    st.session_state.last_study_day = today.isoformat()

st.title("📚 Study Quest")
st.caption("Study more. Level up.")

xp = st.session_state.xp
level = xp // 100 + 1
xp_in_level = xp % 100
level_names = ["Beginner", "Explorer", "Scholar", "Master", "Legend"]
level_name = level_names[min(level - 1, len(level_names) - 1)]

left, right = st.columns([2, 1])

with left:
    st.markdown('<div class="quest-card">', unsafe_allow_html=True)
    st.subheader(f"✨ Level {level}: {level_name}")
    st.write(f"{xp} total XP · {100 - xp_in_level} XP to the next level")
    st.progress(xp_in_level / 100)
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="quest-card">', unsafe_allow_html=True)
    st.subheader("🔥 Study streak")
    st.metric("Days in a row", st.session_state.streak)
    st.markdown('</div>', unsafe_allow_html=True)

# Study journey milestones
st.markdown('<div class="quest-card">', unsafe_allow_html=True)
st.subheader("🗺️ Keep climbing")

milestones = [
    ("Start", 0),
    ("Camp", 100),
    ("Forest", 250),
    ("Mountain", 500),
    ("Summit", 1000),
]

st.write("  ───  ".join(
    f"📍 **{name}** ({needed} XP)" if xp >= needed else f"○ {name} ({needed} XP)"
    for name, needed in milestones
))

next_milestone = next(
    ((name, needed) for name, needed in milestones if needed > xp),
    None
)
if next_milestone:
    name, needed = next_milestone
    st.caption(f"{name}: {needed - xp} XP to go")
else:
    st.caption("You reached the Summit!")
st.markdown('</div>', unsafe_allow_html=True)

# Add subjects
st.markdown('<div class="quest-card">', unsafe_allow_html=True)
st.subheader("📖 Your subjects")

with st.form("add_subject_form"):
    new_subject = st.text_input("Add a subject", placeholder="For example: Python")
    add_button = st.form_submit_button("Add subject")

    if add_button and new_subject.strip():
        if new_subject.strip() not in st.session_state.subjects:
            st.session_state.subjects.append(new_subject.strip())
            st.success(f"Added {new_subject.strip()}!")
        else:
            st.info("That subject is already on your list.")

if st.session_state.subjects:
    for subject in st.session_state.subjects:
        minutes = sum(
            session["minutes"]
            for session in st.session_state.sessions
            if session["subject"] == subject
        )
        st.write(f"📘 **{subject}** — {minutes} minutes studied")
else:
    st.info("Add a subject first to start a study session.")
st.markdown('</div>', unsafe_allow_html=True)

# Study timer
st.markdown('<div class="quest-card">', unsafe_allow_html=True)
st.subheader("⏱️ Focus quest")

if st.session_state.subjects:
    chosen_subject = st.selectbox("What are you studying?", st.session_state.subjects)
    duration_choice = st.selectbox("Session length", [("10 sec (test)", 10), ("15 min", 900), ("25 min", 1500), ("45 min", 2700)])
    duration_label, duration_seconds = duration_choice

    if st.button("Start studying", type="primary"):
        with st.spinner("Focus time! Your timer is running..."):
            time.sleep(duration_seconds)
        session_minutes = max(1, round(duration_seconds / 60))
        add_completed_session(chosen_subject, session_minutes)
        st.success(f"🎉 Quest complete! You earned {session_minutes * 2} XP.")
        st.rerun()
else:
    st.button("Start studying", disabled=True)
    st.caption("Add a subject first to start a study session.")

st.markdown('</div>', unsafe_allow_html=True)

# Badges
st.markdown('<div class="quest-card">', unsafe_allow_html=True)
st.subheader("🏅 Collect your badges")

badges = [
    ("First Session", len(st.session_state.sessions) >= 1),
    ("100 XP", st.session_state.xp >= 100),
    ("3-Day Streak", st.session_state.streak >= 3),
    ("Level 3", level >= 3),
]

badge_columns = st.columns(4)
for column, (badge_name, unlocked) in zip(badge_columns, badges):
    with column:
        if unlocked:
            st.success(f"🏆 {badge_name}\n\nUnlocked!")
        else:
            st.info(f"🔒 {badge_name}\n\nKeep studying to unlock")

st.markdown('</div>', unsafe_allow_html=True)

# Completed sessions list
st.markdown('<div class="quest-card">', unsafe_allow_html=True)
st.subheader("📝 Completed sessions")
if st.session_state.sessions:
    for session in reversed(st.session_state.sessions):
        st.write(
            f"• {session['subject']} — {session['minutes']} min — {session['date']}"
        )
else:
    st.caption("Your finished sessions will appear here.")
st.markdown('</div>', unsafe_allow_html=True)

# Reset progress
st.divider()
if st.button("Reset all progress"):
    st.session_state.clear()
    st.success("Progress reset. Refresh the page to start a new quest.")
    st.rerun()