import streamlit as st
import time
import pandas as pd
import altair as alt
import datetime
from types import SimpleNamespace

# --- Page Config ---
st.set_page_config(
    page_title="Zenith Wellness",
    page_icon="",
    layout="centered",  # This will be further controlled by our CSS
    initial_sidebar_state="expanded"
)

# --- App Data ---
# Encapsulating all default data in one place for easier management.
def get_default_events():
    """Returns a list of all available events."""
    return [
        {
            "id": "evt1",
            "title": "Wellness Week Yoga", "time": "Today, 6:00 PM",
            "loc": "Rec Center, Main Gym", "dist": "0.3 mi", "cost": "Free",
            "desc": "Join us for a relaxing evening yoga session. All levels welcome!",
            "details": "This session is part of Wellness Week and focuses on vinyasa flow. Mats are provided, but you can bring your own. Please arrive 10 minutes early."
        },
        {
            "id": "evt2",
            "title": "Mindful Meditation Drop-in", "time": "Tomorrow, 12:00 PM",
            "loc": "Student Union, Rm 302", "dist": "0.5 mi", "cost": "Free",
            "desc": "A 30-minute guided meditation to de-stress during your day.",
            "details": "No experience necessary. This is a guided audio meditation led by a campus wellness professional. Feel free to drop in anytime during the 12-1 PM hour."
        },
        {
            "id": "evt3",
            "title": "Nutrition & Brain Food", "time": "Fri, Nov 22, 4:00 PM",
            "loc": "Health Services Bldg.", "dist": "0.7 mi", "cost": "Free (w/ RSVP)",
            "desc": "Learn how to fuel your body and mind for finals week.",
            "details": "A nutritionist will discuss foods that boost memory and focus, and healthy snack ideas for late-night study sessions. Free samples provided!"
        },
        {
            "id": "evt4",
            "title": "Therapy Dogs @ The Library", "time": "Mon, Nov 25, 2:00 PM",
            "loc": "Main Library, 1st Floor", "dist": "0.2 mi", "cost": "Free",
            "desc": "Take a break from studying and pet some friendly dogs!",
            "details": "Certified therapy dogs will be available in the main lobby. Take 15 minutes to de-stress and cuddle with a furry friend. Hosted by 'Paws for a Cause'."
        },
        {
            "id": "evt5",
            "title": "Campus 5K Fun Run", "time": "Sat, Nov 30, 9:00 AM",
            "loc": "Main Quad", "dist": "0.1 mi", "cost": "$5 Entry",
            "desc": "Join the annual Turkey Trot 5K! All proceeds go to the campus food pantry.",
            "details": "Check-in starts at 8:00 AM. The first 100 runners get a free t-shirt. This is a fun run, so all speeds (walking or running) are welcome!"
        }
    ]

def get_default_resources():
    """Returns a list of all available resources."""
    return [
        {"id": "res1", "cat": "Mental Health", "title": "5 Ways to Beat Exam Stress", "read_time": "4 min read", "img": "https://placehold.co/600x400/EDE7F6/4A148C?text=Mental+Health&font=inter"},
        {"id": "res2", "cat": "Study", "title": "The Pomodoro Technique: Explained", "read_time": "3 min read", "img": "https://placehold.co/600x400/EDE7F6/4A148C?text=Study+Tips&font=inter"},
        {"id": "res3", "cat": "Campus", "title": "Contact Campus Counseling Services", "read_time": "1 min read", "img": "https://placehold.co/600x400/EDE7F6/4A148C?text=Campus&font=inter"},
        {"id": "res4", "cat": "Mental Health", "title": "Understanding Burnout vs. Stress", "read_time": "5 min read", "img": "https://placehold.co/600x400/EDE7F6/4A148C?text=Wellness&font=inter"},
        {"id": "res5", "cat": "Sleep", "title": "Why 8 Hours is Non-Negotiable", "read_time": "4 min read", "img": "https://placehold.co/600x400/EDE7F6/4A148C?text=Sleep&font=inter"},
        # fixed img URL here:
        {"id": "res6", "cat": "Study", "title": "Active Recall: How to Really Learn", "read_time": "6 min read", "img": "https://placehold.co/600x400/EDE7F6/4A148C?text=Academics&font=inter"},
    ]

# --- Initialize Session State ---
# This is the "brain" of the app, controlling all interactivity.
if 'page' not in st.session_state:
    st.session_state.page = "Today"
if 'user_goals' not in st.session_state:
    st.session_state.user_goals = ["Meditate 5 mins/day", "Sleep 8 hours"]

# --- Timer State ---
if 'timer_state' not in st.session_state:
    st.session_state.timer_state = SimpleNamespace(
        running=False,
        start_time=0,
        task_name="",
        duration_min=25,
        is_break=False,
        break_duration_min=5
    )

# helper: stop timer cleanly (replaces ts.update which doesn't exist)
def stop_timer():
    ts = st.session_state.timer_state
    ts.running = False
    ts.is_break = False

# --- Modal & Sub-Page States ---
if 'breathing_active' not in st.session_state:
    st.session_state.breathing_active = False
if 'wind_down_active' not in st.session_state:
    st.session_state.wind_down_active = False
if 'selected_event_details' not in st.session_state:
    st.session_state.selected_event_details = None
if 'show_modal' not in st.session_state:
    st.session_state.show_modal = None  # e.g., "privacy", "help", "logout"

# --- Data States ---
if 'all_events' not in st.session_state:
    st.session_state.all_events = get_default_events()
if 'my_schedule' not in st.session_state:
    st.session_state.my_schedule = []  # Stores IDs of RSVP'd events
if 'all_resources' not in st.session_state:
    st.session_state.all_resources = get_default_resources()

# --- Custom CSS for HIFI Purple/White Theme ---
def load_css():
    """Injects custom CSS for the HIFI app theme."""
    st.markdown("""
    <style>
        /* --- Import Google Font --- */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        /* --- Base & App Layout --- */
        html, body, .stApp {
            background-color: #F8F7FF; /* Very light purple-white */
            font-family: 'Inter', sans-serif;
        }
        
        /* --- Create the "App Pane" Look --- */
        .stApp {
            max-width: 680px; /* Max width of the app content */
            margin: 0 auto;  /* Center the app */
            padding: 1rem 0.5rem;
            border-left: 1px solid #E0E0E0;
            border-right: 1px solid #E0E0E0;
            min-height: 100vh;
            background-color: #FFFFFF; /* Main app pane is white */
            box-shadow: 0 0 40px rgba(0,0,0,0.05);
        }

        /* --- Sidebar Navigation --- */
        [data-testid="stSidebar"] {
            background-color: #F8F7FF; /* Sidebar background matches page bg */
            border-right: 1px solid #E0E0E0;
            padding-top: 1.5rem;
        }
        [data-testid="stSidebar"] h1 {
            color: #4A148C; /* Deep Purple */
            font-weight: 700;
            font-size: 28px;
            padding: 0 10px;
        }
        [data-testid="stSidebar"] .stMarkdown {
            color: #6A11CB; /* Medium Purple */
            font-size: 14px;
            padding: 0 10px;
            margin-bottom: 1.5rem;
        }
        
        /* --- Sidebar Radio (Nav) --- */
        .stRadio [role="radio"] {
            border-radius: 10px;
            padding: 12px 18px;
            margin: 0.5rem;
            transition: all 0.3s ease;
            border: 1px solid transparent;
            font-weight: 500;
            color: #5E35B1; 
        }
        .stRadio [role="radio"]:hover {
            background-color: #F4F0FF; /* Light purple hover */
        }
        /* --- HIFI Selected Nav Item --- */
        .stRadio [data-baseweb="radio"] span[data-checked="true"] {
            background-color: #EDE7F6; /* Light purple selected */
            border: 1px solid #D1C4E9;
            color: #4A148C;
            font-weight: 700;
            border-left: 4px solid #6A11CB; /* Accent border */
            border-radius: 10px;
        }
        .stRadio [data-baseweb="radio"] span {
            font-size: 1.1rem;
        }

        /* --- Main Content --- */
        h1 {
            color: #4A148C;
            font-weight: 700;
        }
        h2 {
            color: #5E35B1;
            border-bottom: 2px solid #EDE7F6;
            padding-bottom: 5px;
        }
        h3 {
            color: #673AB7;
        }
        
        /* --- Custom Cards --- */
        .card {
            background-color: #FFFFFF;
            border-radius: 20px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(106, 17, 203, 0.08); /* Softer shadow */
            border: 1px solid #EDE7F6;
            margin-bottom: 20px;
        }
        .card-highlight {
            background-color: #FAF5FF; /* Lighter purple card */
            border: 1px solid #D1C4E9;
            padding: 25px;
            border-radius: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 12px rgba(106, 17, 203, 0.05);
        }
        
        /* --- Metric Cards (for Sleep) --- */
        .metric-card {
            background-color: #FFFFFF;
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            text-align: center;
            border: 1px solid #E0E0E0;
            height: 100%; /* Make cols same height */
        }
        /* ... (Metric card h3, p styles remain same) ... */
        
        /* --- Resource Card (New) --- */
        .resource-card {
            border: 1px solid #E0E0E0;
            border-radius: 15px;
            overflow: hidden;
            margin-bottom: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            transition: all 0.3s ease;
        }
        .resource-card:hover {
            box-shadow: 0 8px 24px rgba(106, 17, 203, 0.1);
            transform: translateY(-2px);
        }
        .resource-card img {
            width: 100%;
            height: 150px;
            object-fit: cover;
        }
        .resource-card-content {
            padding: 15px 20px;
        }
        .resource-card-content h3 {
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 5px;
        }
        .resource-card-content small {
            color: #6A11CB;
            font-weight: 500;
        }

        /* --- Buttons --- */
        .stButton > button {
            background-image: linear-gradient(135deg, #6A11CB 0%, #2575FC 100%);
            color: white;
            border: none;
            border-radius: 25px; /* Fully rounded */
            padding: 12px 25px;
            font-size: 1rem;
            font-weight: 600;
            box-shadow: 0 4px 15px rgba(106, 17, 203, 0.3);
            transition: all 0.3s ease;
            width: 100%; /* Make buttons full width */
        }
        /* ... (Button hover, active, secondary styles remain same) ... */
        
        /* --- Sliders --- */
        .stSlider [data-baseweb="slider"] {
            color: #7E57C2; /* Purple slider track */
        }
        
        /* --- Chat Messages --- */
        [data-testid="chat-message-container"] {
            background-color: #F4F0FF;
            border-radius: 15px;
            border: 1px solid #D1C4E9;
            box-shadow: 0 4px 12px rgba(106, 17, 203, 0.05);
        }
        
        /* --- Goal List --- */
        /* ... (Goal list styles remain same) ... */

        /* --- Breathing Animator (New) --- */
        .breathing-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 40px 20px;
            text-align: center;
        }
        .breathing-circle {
            width: 200px;
            height: 200px;
            background-color: #EDE7F6;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 5px solid #D1C4E9;
            animation: pulse 8s ease-in-out infinite;
        }
        .breathing-text {
            font-size: 1.5rem;
            font-weight: 600;
            color: #4A148C;
            animation: text-fade 8s ease-in-out infinite;
        }
        @keyframes pulse {
            0% { transform: scale(0.8); background-color: #D1C4E9; }
            50% { transform: scale(1.1); background-color: #EDE7F6; }
            100% { transform: scale(0.8); background-color: #D1C4E9; }
        }
        @keyframes text-fade {
            0% { content: "Inhale"; opacity: 1; }
            40% { opacity: 1; }
            50% { content: "Hold"; opacity: 1; }
            60% { opacity: 1; }
            61% { content: "Exhale"; opacity: 1; }
            90% { opacity: 1; }
            100% { content: "Inhale"; opacity: 1; }
        }
        /* A bit of a hack to change text with animation */
        .breathing-text::before {
            content: "Inhale";
            animation: text-change 8s ease-in-out infinite;
        }
        @keyframes text-change {
            0% { content: "Inhale"; }
            45% { content: "Inhale"; }
            50% { content: "Hold"; }
            60% { content: "Hold"; }
            65% { content: "Exhale"; }
            95% { content: "Exhale"; }
            100% { content: "Inhale"; }
        }
        
        /* --- Wind-down Checklist (New) --- */
        .wind-down-item {
            display: flex;
            align-items: center;
            font-size: 1.1rem;
            background-color: #F4F0FF;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
            border: 1px solid #D1C4E9;
        }
        .wind-down-item span {
            margin-left: 10px;
        }
        
        /* --- Dialog/Modal Styling (New) --- */
        [data-baseweb="dialog"] {
            border-radius: 20px;
            border: 2px solid #EDE7F6;
            box-shadow: 0 8px 32px rgba(106, 17, 203, 0.1);
        }
        
    </style>
    """, unsafe_allow_html=True)

load_css()

# --- Helper Functions for Card UI ---
def card_start():
    """Starts a custom card div."""
    st.markdown("<div class='card'>", unsafe_allow_html=True)

def card_end():
    """Ends a custom card div."""
    st.markdown("</div>", unsafe_allow_html=True)

def card_highlight_start():
    """Starts a custom highlighted card div."""
    st.markdown("<div class='card-highlight'>", unsafe_allow_html=True)

def card_highlight_end():
    """Ends a custom highlighted card div."""
    st.markdown("</div>", unsafe_allow_html=True)

def set_page(page_name):
    """Helper function to set the page state."""
    st.session_state.page = page_name

# --- ================================== ---
# --- MODAL/SUB-PAGE RENDER FUNCTIONS ---
# --- ================================== ---

@st.dialog("Event Details")
def show_event_details_dialog():
    """
    Renders the Event Details modal (st.dialog).
    Uses st.session_state.selected_event_details.
    """
    event = st.session_state.selected_event_details
    if not event:
        st.error("Could not load event details.")
        st.button("Close")
        return

    st.markdown(f"### {event['title']}")
    st.markdown(f"**{event['time']}**")
    st.markdown(f"Location: {event['loc']} • Cost: {event['cost']} • Distance: {event['dist']}")
    st.markdown("---")
    st.markdown(f"**About this event:**\n\n{event['details']}")
    
    # Check if already RSVP'd
    already_rsvpd = event['id'] in st.session_state.my_schedule
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("RSVP", disabled=already_rsvpd, key=f"rsvp_modal_{event['id']}"):
            st.session_state.my_schedule.append(event['id'])
            st.toast("Added to your schedule!")
            st.session_state.selected_event_details = None # Close dialog
            st.rerun() # Re-run to update disabled state
    with col2:
        if st.button("Close", type="secondary"):
            st.session_state.selected_event_details = None
            st.rerun() # Re-run to close

def show_breathing_exercise():
    """
    Renders the full-page breathing exercise modal.
    Replaces the content of the 'Today' page when active.
    """
    card_highlight_start()
    st.subheader("60-Second Breathing Reset")
    st.markdown(
        """
        <div class="breathing-container">
            <div class="breathing-circle">
                <span class="breathing-text"></span>
            </div>
            <p style="margin-top: 20px;">Follow the rhythm. Inhale as the circle grows, exhale as it shrinks.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.button("I'm Done", type="secondary", on_click=lambda: st.session_state.update(breathing_active=False))
    card_highlight_end()

def show_wind_down_routine():
    """
    Renders the full-page wind-down modal.
    Replaces the content of the 'Sleep' page when active.
    """
    card_highlight_start()
    st.subheader("Start Your Wind-Down")
    st.markdown("Try this 30-minute routine to prepare your mind for sleep.")
    
    st.markdown(
        """
        <div class="wind-down-item">
            <span>Put phone on charger (away from bed)</span>
        </div>
        <div class="wind-down-item">
            <span>Read a physical book for 15 mins</span>
        </div>
        <div class="wind-down-item">
            <span>Sip some non-caffeinated tea</span>
        </div>
        <div class="wind-down-item">
            <span>Do a 5-minute guided meditation</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    if st.button("Start 30-Min Timer"):
        st.toast("Wind-down timer started. See you in 30!")
    
    st.button("Close", type="secondary", on_click=lambda: st.session_state.update(wind_down_active=False))
    card_highlight_end()

def show_placeholder_modal(title, message):
    """
    Renders a generic placeholder modal for non-functional buttons.
    """
    st.markdown(f"### {title}")
    st.markdown(message)
    if st.button("Close", type="secondary"):
        st.session_state.show_modal = None
        st.rerun()

# --- ================================== ---
# --- MAIN PAGE RENDER FUNCTIONS ---
# --- ================================== ---

# --- 1. TODAY / HOME PAGE ---
def page_today():
    """Renders the 'Today' (Home) page or its sub-modals."""
    
    # Check if a sub-page (like breathing) is active
    if st.session_state.breathing_active:
        show_breathing_exercise()
        return  # Stop rendering the rest of the page

    # --- If no sub-page, render the main 'Today' page ---
    st.title("Good Afternoon, Alex!")
    st.markdown("How are you feeling right now?")

    # --- Check-In Card ---
    card_start()
    st.subheader("Daily Check-In")
    mood = st.slider("Your Mood (1 = Low, 5 = Great)", 1, 5, 3)
    stress = st.slider("Your Stress (1 = Low, 5 = High)", 1, 5, 2)
    tags = st.multiselect(
        "What's on your mind?",
        ["Exams", "Homework", "Social", "Sleep", "Relationships", "Future"],
        ["Exams"]
    )
    if st.button("Log Now", key="log_now"):
        st.toast(f"Logged: Mood {mood}/5, Stress {stress}/5")
    card_end()

    # --- Breathing Reset Card ---
    card_highlight_start()
    st.subheader("Try a Breathing Reset")
    st.markdown("Your stress levels seem to be trending up this morning.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start 60-Sec Reset", key="start_breathing"):
            st.session_state.breathing_active = True
            st.rerun()
    with col2:
        st.button("Maybe Later", type="secondary", key="later_breathing")
    card_highlight_end()

    # --- Insight Card ---
    card_start()
    st.subheader("Your AI Coach Insight")
    st.markdown("Your sleep dipped to ~6.5 hours before your stats exam. **Try a 10pm wind-down tonight** to stay ahead.")
    st.button("Chat with Coach", type="secondary", key="chat_coach_home", on_click=set_page, args=("AI Coach",))
    card_end()

    # --- Event Card ---
    card_start()
    st.subheader("Upcoming Event")
    st.markdown("### Wellness Week Yoga")
    st.markdown("Location: **Rec Center** • Cost: **Free** • Distance: **0.3 mi away**")
    st.markdown("Join us for a relaxing evening yoga session. All levels welcome!")
    st.button("View All Events", key="view_events_home", on_click=set_page, args=("Events",))
    card_end()

# --- 2. FOCUS / STUDY PAGE (UPGRADED) ---
def page_focus():
    """Renders the 'Focus Hub' page with a complete Pomodoro loop."""
    st.title("Focus Hub")
    ts = st.session_state.timer_state

    if ts.running:
        # --- TIMER IS RUNNING ---
        
        # Calculate remaining time
        elapsed = time.time() - ts.start_time
        current_duration_sec = (ts.duration_min if not ts.is_break else ts.break_duration_min) * 60
        remaining_seconds = current_duration_sec - elapsed
        
        if remaining_seconds <= 0:
            # --- TIMER FINISHED ---
            st.balloons()
            ts.running = False
            
            if ts.is_break:
                # Break finished
                st.header(f"Break's over!")
                st.markdown(f"Ready for another focus session?")
                if st.button("Start Next Focus"):
                    ts.is_break = False
                    ts.running = True
                    ts.start_time = time.time()
                    st.rerun()
            else:
                # Focus session finished
                st.header(f"Time's up!")
                st.markdown(f"You completed your focus session for **{ts.task_name}**.")
                if st.button(f"Start {ts.break_duration_min}-min Break"):
                    ts.is_break = True
                    ts.running = True
                    ts.start_time = time.time()
                    st.rerun()
            
            # fixed: use stop_timer instead of ts.update(...)
            st.button("Stop for Now", type="secondary", on_click=stop_timer)
        
        else:
            # --- TIMER IS ACTIVELY COUNTING DOWN ---
            card_highlight_start()
            timer_title = "Focusing on:" if not ts.is_break else "On a Break"
            task_display = f"**{ts.task_name}**" if not ts.is_break else "Time to relax!"
            
            st.markdown(f"{timer_title} {task_display}")
            
            mins, secs = divmod(int(remaining_seconds), 60)
            timer_display = f"{mins:02d}:{secs:02d}"
            
            # Display big timer
            st.markdown(f"<h1 style='text-align: center; color: #4A148C; font-size: 5rem; margin-bottom: 0;'>{timer_display}</h1>", unsafe_allow_html=True)
            
            # Progress bar
            percent_complete = elapsed / current_duration_sec
            st.progress(percent_complete, text=f"{int(percent_complete * 100)}% complete")
            card_highlight_end()

            if st.button("Stop Session", type="secondary"):
                ts.running = False
                ts.is_break = False
                st.rerun()
            
            # This is the "hack" to force Streamlit to re-run the script
            # to update the timer display.
            time.sleep(1)
            st.rerun()
            
    else:
        # --- TIMER IS NOT RUNNING (Settings Screen) ---
        st.markdown("Let's get in the zone. What are you working on?")
        card_start()
        
        task = st.text_input("Task:", "Read Chapter 3 (Stats 210)")
        
        col1, col2 = st.columns(2)
        with col1:
            duration = st.number_input("Focus time (minutes):", 5, 120, 25, 5)
        with col2:
            break_time = st.number_input("Break time (minutes):", 5, 30, 5, 5)

        if st.button("Start Focus Session"):
            # Set session state variables and rerun
            ts.running = True
            ts.start_time = time.time()
            ts.duration_min = duration
            ts.break_duration_min = break_time
            ts.task_name = task
            ts.is_break = False
            st.rerun()
        
        card_end()
        
        card_start()
        st.subheader("Why use a focus timer?")
        st.markdown("The Pomodoro Technique breaks work into focused intervals (usually 25 mins) separated by short breaks. It's proven to boost productivity and reduce burnout.")
        card_end()

# --- 3. SLEEP TRACKER PAGE (UPGRADED) ---
def page_sleep():
    """Renders the 'Sleep' page or its sub-modals."""
    
    # Check if a sub-page (like wind-down) is active
    if st.session_state.wind_down_active:
        show_wind_down_routine()
        return # Stop rendering the rest of the page

    # --- If no sub-page, render the main 'Sleep' page ---
    st.title("Sleep Tracker")
    st.markdown("Good sleep is the foundation of wellness.")

    # --- Metric Cards ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            "<div class='metric-card'><h3>Sleep Score</h3><p>82</p><small>Good</small></div>",
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            "<div class='metric-card'><h3>Duration</h3><p>7h 24m</p><small>Target: 8h</small></div>",
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            "<div class='metric-card'><h3>Consistency</h3><p>↑ 5%</p><small>vs. last week</small></div>",
            unsafe_allow_html=True
        )
    
    st.markdown("---") # Visual separator

    # --- Log Your Sleep Card ---
    card_start()
    st.subheader("Log Your Sleep")
    with st.expander("Tap to open log"):
        log_date = st.date_input("Night of:", datetime.date.today() - datetime.timedelta(days=1))
        
        col1, col2 = st.columns(2)
        with col1:
            bed_time = st.time_input("Went to bed:", datetime.time(23, 30))
        with col2:
            wake_time = st.time_input("Woke up:", datetime.time(7, 15))
        
        quality = st.slider("Sleep Quality (1 = Poor, 5 = Great)", 1, 5, 4)
        
        if st.button("Save Log", type="secondary"):
            st.toast("Sleep log saved!")
    card_end()

    # --- Sleep Trends Chart ---
    card_start()
    st.subheader("Your Sleep Trends")
    
    # Fake data for the chart
    data = {
        "Day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "Hours": [6.5, 7.0, 7.2, 6.8, 7.5, 8.1, 7.8],
        "Target": [8.0] * 7
    }
    df = pd.DataFrame(data)
    
    # Melt for Altair
    df_melted = df.melt('Day', var_name='Metric', value_name='Sleep Duration')
    
    # Base encodings (fixed layering logic – no get_layer)
    base = alt.Chart(df_melted).encode(
        x=alt.X('Day', sort=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]),
        y=alt.Y('Sleep Duration', title='Hours of Sleep', scale=alt.Scale(domain=[5, 9])),
        color=alt.Color('Metric',
                        scale=alt.Scale(domain=['Hours', 'Target'],
                                        range=['#6A11CB', '#D1C4E9']),
                        legend=alt.Legend(title="Legend"))
    ).properties(
        title="Sleep Duration vs. Target (Last 7 Days)"
    )
    
    hours_line = base.transform_filter(alt.datum.Metric == 'Hours').mark_line(point=True)
    target_line = base.transform_filter(alt.datum.Metric == 'Target').mark_line(
        point=True,
        strokeDash=[5, 5]
    )

    st.altair_chart((hours_line + target_line).interactive(), use_container_width=True)
    card_end()

    # --- Wind-down Card ---
    card_highlight_start()
    st.subheader("Wind-down Routine")
    st.markdown("Your average bedtime this week was **11:42 PM**. Students who wind-down 30 minutes before bed report better sleep quality.")
    if st.button("Start Wind-down Routine", type="secondary", key="wind_down"):
        st.session_state.wind_down_active = True
        st.rerun()
    card_highlight_end()

# --- 4. EVENTS HUB PAGE (UPGRADED) ---
def page_events():
    """Renders the 'Events' page, handles RSVP, and shows Details modal."""
    
    # This check is crucial: if a dialog is open, we show it.
    if st.session_state.selected_event_details:
        show_event_details_dialog()
        # Do not render the rest of the page while dialog is open
        return

    st.title("Campus Events")
    st.markdown("Find wellness activities happening near you.")

    # Event filters
    st.selectbox(
        "Filter by Category",
        ["All", "Wellness", "Academic", "Social", "Fitness"],
        label_visibility="collapsed"
    )

    # --- Featured Event ---
    featured_event = st.session_state.all_events[0]
    card_highlight_start()
    st.subheader("Featured Event")
    st.markdown(f"### {featured_event['title']}")
    st.markdown(f"**{featured_event['time']}** @ {featured_event['loc']}")
    
    col1, col2 = st.columns(2)
    with col1:
        # Check if already RSVP'd
        already_rsvpd = featured_event['id'] in st.session_state.my_schedule
        if st.button("RSVP Now", key="rsvp_featured", disabled=already_rsvpd):
            st.session_state.my_schedule.append(featured_event['id'])
            st.toast("Added to your schedule!")
            st.rerun()
    with col2:
        if st.button("Details", type="secondary", key="det_featured"):
            st.session_state.selected_event_details = featured_event
            st.rerun()
    card_highlight_end()

    st.subheader("All Events")
    # Display *other* events as cards
    for event in st.session_state.all_events[1:]:
        card_start()
        st.markdown(f"### {event['title']}")
        st.markdown(f"**{event['time']}**")
        st.markdown(f"Location: **{event['loc']}** • Cost: **{event['cost']}** • Distance: **{event['dist']}**")
        
        c1, c2, c3 = st.columns([1, 1, 1.5])
        with c1:
            already_rsvpd = event['id'] in st.session_state.my_schedule
            if st.button("RSVP", type="secondary", key=f"rsvp_{event['id']}", disabled=already_rsvpd):
                st.session_state.my_schedule.append(event['id'])
                st.toast("Added to your schedule!")
                st.rerun()
        with c2:
            if st.button("Details", type="secondary", key=f"det_{event['id']}"):
                st.session_state.selected_event_details = event
                st.rerun()
        card_end()

# --- 5. NEW PAGE: MY SCHEDULE ---
def page_my_schedule():
    """Renders the user's personal schedule of RSVP'd events."""
    st.title("My Schedule")
    
    if not st.session_state.my_schedule:
        st.markdown("You haven't RSVP'd for any events yet.")
        st.markdown("Go to the **Events** page to find activities!")
        return

    st.markdown("Here are your upcoming events.")
    
    # Get full event details from the IDs in my_schedule
    event_details_map = {event['id']: event for event in st.session_state.all_events}
    
    for event_id in st.session_state.my_schedule:
        event = event_details_map.get(event_id)
        if event:
            card_start()
            st.markdown(f"### {event['title']}")
            st.markdown(f"**{event['time']}**")
            st.markdown(f"Location: **{event['loc']}**")
            
            col1, col2, col3 = st.columns([1.2, 1, 1])
            with col1:
                st.button("View Details", type="secondary", key=f"detail_sched_{event_id}", on_click=lambda e=event: st.session_state.update(selected_event_details=e))
            with col2:
                if st.button("Cancel RSVP", type="secondary", key=f"cancel_sched_{event_id}"):
                    st.session_state.my_schedule.remove(event_id)
                    st.toast(f"Removed '{event['title']}' from schedule.")
                    st.rerun()
            card_end()

# --- 6. NEW PAGE: RESOURCES ---
def page_resources():
    """Renders the 'Resources' page with filterable articles."""
    st.title("Resources")
    st.markdown("Explore articles and tools for your wellness.")
    
    categories = ["All"] + sorted(list(set(res["cat"] for res in st.session_state.all_resources)))
    selected_cat = st.selectbox(
        "Filter by Category",
        categories,
        label_visibility="collapsed"
    )
    
    # Filter resources
    if selected_cat == "All":
        filtered_resources = st.session_state.all_resources
    else:
        filtered_resources = [res for res in st.session_state.all_resources if res["cat"] == selected_cat]

    if not filtered_resources:
        st.warning(f"No resources found in '{selected_cat}'.")
        return

    # Display resources
    for res in filtered_resources:
        st.markdown(
            f"""
            <div class="resource-card">
                <img src="{res['img']}" alt="{res['title']}">
                <div class="resource-card-content">
                    <small>{res['cat'].upper()}</small>
                    <h3>{res['title']}</h3>
                    <small>{res['read_time']}</small>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("Read More", key=f"read_{res['id']}", type="secondary"):
            st.toast(f"Opening '{res['title']}'...")
            
# --- 7. AI COACH / MESSAGES PAGE ---
def page_coach():
    """Renders the 'AI Coach' chat interface."""
    st.title("Your AI Wellness Coach")
    st.markdown("Here are personalized insights and tips just for you.")

    # --- Insight Card ---
    card_highlight_start()
    st.subheader("This week's insight:")
    st.markdown("""
    "Hey Alex! I noticed your **stress logs were highest** on the two days just before your Stats exam. 
    
    Your **sleep duration also dipped** to ~6.5 hours those nights. 
    
    For your next exam, let's try starting a 10-minute wind-down routine 30 minutes before your target 11 PM bedtime."
    """)
    card_highlight_end()

    # --- Chat Interface ---
    st.subheader("Chat with your Coach")

    # Display a "fake" chat history
    with st.chat_message("assistant", avatar="A"):
        st.write("Hi Alex, how can I help you today? Are you looking for study tips, stress management, or something else?")

    with st.chat_message("user", avatar="U"):
        st.write("I'm feeling overwhelmed about finals.")

    with st.chat_message("assistant", avatar="A"):
        st.write("That's completely understandable. It's a high-stress time. Let's break it down.")
        st.write("1. **Prioritize:** What are your top 3 most urgent tasks?")
        st.write("2. **Time-block:** Have you tried the 'Focus Hub' Pomodoro timer? It can help make large tasks feel more manageable.")
        st.write("3. **Rest:** Don't forget to protect your sleep. It's when you consolidate memories!")

    with st.chat_message("user", avatar="U"):
        st.write("Okay, I'll try the timer. I just feel like I don't have enough time.")
        
    with st.chat_message("assistant", avatar="A"):
        st.write("It's a common feeling. But 25 minutes of *true* focus is often more effective than 2 hours of distracted studying. You've got this!")


    # User input
    if prompt := st.chat_input("Reply to your coach..."):
        st.chat_message("user", avatar="U").write(prompt)
        
        # Fake bot reply
        with st.spinner("Coach is typing..."):
            time.sleep(1.5)
        st.chat_message("assistant", avatar="A").write(
            "That's a great next step. Remember to take your 5-minute breaks! Let me know how that first session goes."
        )

# --- 8. PROFILE / SETTINGS PAGE (UPGRADED) ---
def page_profile():
    """Renders the 'Profile & Settings' page."""
    
    # --- Check for placeholder modals ---
    if st.session_state.show_modal:
        @st.dialog(st.session_state.show_modal)
        def _show_modal():
            if st.session_state.show_modal == "Privacy Policy":
                show_placeholder_modal("Privacy Policy", "Your data is anonymized and used only for campus wellness research. We never sell your data.")
            elif st.session_state.show_modal == "Help & Support":
                show_placeholder_modal("Help & Support", "Please contact zenith-support@campus.edu for any issues.")
            elif st.session_state.show_modal == "Logout":
                show_placeholder_modal("Logout", "Are you sure you want to log out?")
        _show_modal()
        
    st.title("Profile & Settings")

    # --- User Info Card ---
    card_start()
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image(
            "https://placehold.co/100x100/6A11CB/FFFFFF?text=A&font=inter",
            width=100,
        )
    with col2:
        st.subheader("Alex Johnson")
        st.markdown("B.S. Computer Science")
        st.markdown("Joined: Nov 2024")
    card_end()
    
    # --- Your Stats Card ---
    card_start()
    st.subheader("Your Stats (Last 7 Days)")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Avg. Mood", "3.8 / 5", "Up 0.2")
    with col2:
        st.metric("Avg. Stress", "2.5 / 5", "Down 0.5")
    with col3:
        st.metric("Focus Hours", "12.5", "Up 3.0")
    card_end()

    # --- Your Goals Card ---
    card_start()
    st.subheader("Your Wellness Goals")
    
    # Display existing goals
    for i, goal in enumerate(st.session_state.user_goals):
        col1, col2 = st.columns([0.9, 0.1])
        with col1:
            st.markdown(f"<span style='margin-left: 5px;'>{goal}</span>", unsafe_allow_html=True)
        with col2:
            if st.button("Remove", key=f"del_{i}", help="Remove goal"):
                st.session_state.user_goals.pop(i)
                st.rerun()
    
    # Add new goal
    st.markdown("---")
    new_goal = st.text_input("Add a new goal:")
    if st.button("Add Goal", type="secondary"):
        if new_goal and new_goal not in st.session_state.user_goals:
            st.session_state.user_goals.append(new_goal)
            st.rerun()
    card_end()

    # --- Settings Card ---
    card_start()
    st.subheader("App Settings")
    st.toggle("Enable Push Notifications", value=True)
    st.toggle("Sync with Calendar", value=True)
    st.toggle("Personalize AI Coach", value=True)
    
    st.subheader("Data & Privacy")
    st.toggle("Share Anonymized Data for Research", value=True)
    if st.button("View Privacy Policy", type="secondary", key="privacy"):
        st.session_state.show_modal = "Privacy Policy"
        st.rerun()
    card_end()
    
    # --- Actions ---
    card_start()
    if st.button("Help & Support", key="help"):
        st.session_state.show_modal = "Help & Support"
        st.rerun()
    if st.button("Logout", type="secondary", key="logout"):
        st.session_state.show_modal = "Logout"
        st.rerun()
    card_end()


# --- ================================== ---
# --- MAIN APP ROUTER ---
# --- ================================== ---

st.sidebar.title("Zenith")
st.sidebar.markdown("Modern Campus Wellness")

# Define navigation options
nav_options = [
    "Today", 
    "Focus", 
    "Sleep", 
    "Events", 
    "My Schedule", 
    "Resources", 
    "AI Coach", 
    "Profile"
]

page = st.sidebar.radio(
    "Navigation",
    nav_options,
    label_visibility="hidden",
    key="page" # Use session state key
)

# Page Routing
if page == "Today":
    page_today()
elif page == "Focus":
    page_focus()
elif page == "Sleep":
    page_sleep()
elif page == "Events":
    page_events()
elif page == "My Schedule":
    page_my_schedule()
elif page == "Resources":
    page_resources()
elif page == "AI Coach":
    page_coach()
elif page == "Profile":
    page_profile()

# --- Final cleanup check for modals ---
# This ensures modals can be opened from *any* page (e.g., details from schedule)
if st.session_state.selected_event_details and page not in ["Events", "My Schedule"]:
    show_event_details_dialog()

if st.session_state.show_modal and page != "Profile":
    @st.dialog(st.session_state.show_modal)
    def _show_modal_global():
        if st.session_state.show_modal == "Privacy Policy":
            show_placeholder_modal("Privacy Policy", "Your data is anonymized and used only for campus wellness research. We never sell your data.")
        elif st.session_state.show_modal == "Help & Support":
            show_placeholder_modal("Help & Support", "Please contact zenith-support@campus.edu for any issues.")
        elif st.session_state.show_modal == "Logout":
            show_placeholder_modal("Logout", "Are you sure you want to log out?")
    _show_modal_global()
