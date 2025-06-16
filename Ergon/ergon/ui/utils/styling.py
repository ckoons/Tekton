"""
UI styling utilities for Ergon
"""

import streamlit as st
import os

def load_css():
    """Load custom CSS for the UI"""
    st.markdown("""
    <style>
    /* Global styles */
    .stApp {
        max-width: 1300px;
        margin: 0 auto;
    }
    
    /* Global text color - make everything bright white by default */
    body, p, span, div, h1, h2, h3, h4, h5, h6, label, button, input, textarea, select {
        color: #FFFFFF !important;
    }
    
    /* All Streamlit text elements to be white */
    .stTextInput, .stTextArea, .stSelectbox, .stSlider, .stCheckbox, 
    .stRadio, .stNumber, .stText, .stMarkdown, .stTitle, .stHeader, 
    .stSubheader, .stSuccess, .stInfo, .stWarning, .stError, .stTabs,
    .stDataFrame, .stTable {
        color: #FFFFFF !important;
    }
    
    /* Larger, bolder form labels across the app */
    .stTextInput > label, .stTextArea > label, .stSelectbox > label, .stSlider > label {
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        color: #FFFFFF !important;  /* Bright white for maximum visibility */
    }
    
    /* Improved contrast for info boxes */
    .stAlert > div {
        color: #FFFFFF !important;
        font-weight: 500 !important;
    }
    
    /* Better visibility for Streamlit text and markdown */
    .css-183lzff {  /* General text */
        color: #FFFFFF !important;
    }
    
    /* Make text in widgets more visible */
    .stSelectbox label, .stSlider label, .stText, .stMarkdown, 
    .stMarkdown p, .stMarkdown span, .stMarkdown div {
        color: #FFFFFF !important;
    }
    
    /* Make help text more visible */
    .stMarkdown a, small, .stSelectbox div small, .stTextInput div small, 
    .stNumberInput div small, .stTextArea div small {
        color: #FFFFFF !important;  /* White text for everything */
        opacity: 1 !important;
    }
    
    /* Bright sidebar text */
    .css-1544g2n {  /* Sidebar */
        color: white !important;
    }
    
    /* All sidebar content should be bright white */
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown span,
    [data-testid="stSidebar"] .stMarkdown div,
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stSelectbox,
    [data-testid="stSidebar"] .stButton,
    [data-testid="stSidebar"] div {
        color: white !important;
    }
    
    /* Larger tab labels/buttons */
    .stTabs button[role="tab"] {
        font-size: 1.15rem !important;
        font-weight: 600 !important;
    }
    
    /* Make the tab text more visible */
    .stTabs button[role="tab"] p {
        color: #FFFFFF !important;
    }
    
    /* Highlight the active tab more clearly - with blue to match buttons */
    .stTabs button[role="tab"][aria-selected="true"] {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border-bottom-color: #2196F3 !important; /* Blue to match buttons */
        border-bottom-width: 3px !important;
    }
    
    /* Improve form field visibility */
    .stTextInput, .stNumberInput, .stTextArea, .stSelectbox, .stMultiselect {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 5px;
        padding: 5px;
        margin-bottom: 10px;
    }
    
    /* Better form field styling */
    .stTextInput > div[data-baseweb="input"] > div,
    .stTextArea > div[data-baseweb="textarea"] > div {
        border-width: 2px !important;
        color: #FFFFFF !important;
    }
    
    /* Input field text */
    input, textarea, .stTextInput input, .stTextArea textarea {
        color: #FFFFFF !important;
    }
    
    /* Focus styling for form fields */
    .stTextInput > div[data-baseweb="input"]:focus-within > div,
    .stTextArea > div[data-baseweb="textarea"]:focus-within > div {
        border-color: #ff4b4b !important;
        box-shadow: 0 0 0 1px #ff4b4b !important;
    }
    
    /* Style cards */
    div.agent-card {
        border: 1px solid rgba(49, 51, 63, 0.2);
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        background-color: rgba(255, 255, 255, 0.05);
        transition: transform 0.2s;
    }
    
    div.agent-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    }
    
    /* Highlight active field */
    .streamlit-expanderHeader:hover {
        background-color: rgba(255, 255, 255, 0.1) !important;
    }
    
    /* Make sure headers are especially visible */
    h1, h2, h3, .stTitle, .stHeader, .stSubheader {
        color: #FFFFFF !important;
        font-weight: bold !important;
    }
    
    /* Chat message styling */
    .chat-container {
        max-height: 600px;
        overflow-y: auto;
        border: 1px solid rgba(49, 51, 63, 0.2);
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 15px;
    }
    
    .user-message {
        background-color: rgba(70, 130, 180, 0.1);
        border-radius: 15px 15px 0 15px;
        padding: 10px 15px;
        margin: 5px 0;
        margin-left: 20%;
        max-width: 80%;
    }
    
    .agent-message {
        background-color: rgba(47, 79, 79, 0.1);
        border-radius: 15px 15px 15px 0;
        padding: 10px 15px;
        margin: 5px 0;
        margin-right: 20%;
        max-width: 80%;
    }
    
    /* Enhanced chat interface */
    [data-testid="stChatMessage"] {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border-radius: 8px !important;
        padding: 10px !important;
        margin-bottom: 10px !important;
        animation: fadeIn 0.3s ease-in-out !important;
    }
    
    [data-testid="stChatMessage"] [data-testid="stChatMessageContent"] {
        color: white !important;
    }
    
    /* Make user messages stand out */
    [data-testid="stChatMessage"][data-testid="user"] {
        background-color: rgba(33, 150, 243, 0.1) !important;
        margin-left: 25px !important;
    }
    
    /* Make assistant messages stand out */
    [data-testid="stChatMessage"]:not([data-testid="user"]) {
        background-color: rgba(33, 150, 243, 0.05) !important;
        margin-right: 25px !important;
    }
    
    /* Add animation for chat messages */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Chat input */
    [data-testid="stChatInput"] {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important;
        padding: 5px 15px !important;
        border: 2px solid rgba(33, 150, 243, 0.3) !important;
    }
    
    [data-testid="stChatInput"]:focus-within {
        border-color: rgba(33, 150, 243, 0.8) !important;
        box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.2) !important;
    }
    
    /* Improve button responsiveness */
    button[kind="primary"], button[kind="secondary"] {
        transition: all 0.2s ease !important;
    }
    
    /* Button hover effects to make them more responsive */
    button[kind="primary"]:hover {
        background-color: #F4511E !important; /* Darker orange on hover */
        transform: scale(1.03) !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2) !important;
    }
    
    button[kind="secondary"]:hover {
        background-color: #BF360C !important; /* Even darker orange on hover */
        transform: scale(1.03) !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2) !important;
    }
    
    /* Make buttons stand out more - using light red/orange color scheme */
    button[kind="primary"] {
        background-color: #FF7043 !important; /* Light red/orange */
        color: white !important;
        font-weight: 600 !important;
    }
    
    button[kind="secondary"] {
        background-color: #E64A19 !important; /* Darker orange */
        color: white !important;
        font-weight: 500 !important;
    }
    
    /* Style for Navigation expander - Light Orange */
    [data-testid="stSidebar"] [data-testid="stExpander"]:nth-of-type(1) > div:first-child {
        background-color: #FF9800 !important; /* Light Orange */
    }
    
    /* Navigation expander hover - Brighter Orange */
    [data-testid="stSidebar"] [data-testid="stExpander"]:nth-of-type(1) > div:first-child:hover {
        background-color: #FFA726 !important; /* Brighter Orange */
    }
    
    /* Style for all expander headers in the sidebar */
    [data-testid="stSidebar"] [data-testid="stExpander"] {
        margin-bottom: 0.5rem;
    }
    
    /* Base style for all expander headers */
    [data-testid="stSidebar"] [data-testid="stExpander"] > div:first-child {
        border-radius: 4px !important;
        transition: background-color 0.3s ease !important;
        padding: 0.5rem !important;
    }
    
    /* Make expander label text white and bold */
    [data-testid="stSidebar"] [data-testid="stExpander"] p {
        color: #FFFFFF !important;
        font-weight: bold !important;
        font-size: 1.1em !important;
    }
    
    /* Default style for buttons in sidebar */
    [data-testid="stSidebar"] button[kind="primary"] {
        background-color: #FF7043 !important; /* Light red/orange */
    }
    
    /* Button hover effects for sidebar */
    [data-testid="stSidebar"] button[kind="primary"]:hover {
        background-color: #F4511E !important; /* Darker orange on hover */
    }
    
    /* Style for Recent Activity expander in main content */
    [data-testid="stExpander"] {
        margin-bottom: 1rem;
    }
    
    /* Recent Activity expander - Green */
    div:not([data-testid="stSidebar"]) [data-testid="stExpander"] > div:first-child {
        background-color: #4CAF50 !important; /* Green */
        border-radius: 4px !important;
        transition: background-color 0.3s ease !important;
        padding: 0.5rem !important;
    }
    
    /* Recent Activity expander hover - Brighter Green */
    div:not([data-testid="stSidebar"]) [data-testid="stExpander"] > div:first-child:hover {
        background-color: #66BB6A !important; /* Brighter Green */
    }
    
    /* Make expander label text white and bold */
    div:not([data-testid="stSidebar"]) [data-testid="stExpander"] p {
        color: #FFFFFF !important;
        font-weight: bold !important;
        font-size: 1.1em !important;
    }
    
    /* Keep all buttons inside main content orange */
    div:not([data-testid="stSidebar"]) button[kind="primary"] {
        background-color: #FF7043 !important; /* Light red/orange */
        color: white !important;
        font-weight: 600 !important;
    }
    
    /* Orange button hover effects */
    div:not([data-testid="stSidebar"]) button[kind="primary"]:hover {
        background-color: #F4511E !important; /* Darker orange on hover */
        transform: scale(1.03) !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2) !important;
    }
    
    /* Activity section */
    .activity-header {
        font-weight: bold;
        padding: 5px 0;
        border-bottom: 1px solid rgba(49, 51, 63, 0.2);
    }
    
    .activity-item {
        padding: 8px 5px;
        border-bottom: 1px solid rgba(49, 51, 63, 0.1);
        font-size: 0.9rem;
    }
    
    .activity-item:hover {
        background-color: rgba(49, 51, 63, 0.05);
    }
    
    /* Footer */
    footer {
        margin-top: 50px;
        text-align: center;
        font-size: 0.8rem;
        color: rgba(49, 51, 63, 0.6);
    }
    </style>
    """, unsafe_allow_html=True)

def display_logo():
    """Display the Ergon logo in sidebar"""
    # Get the absolute path to the images directory
    image_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "images/icon.jpeg")
    
    # Get sidebar width for centering
    sidebar_style = """
    <style>
    /* Center and resize logo to fit sidebar width */
    [data-testid="stSidebar"] .stImage img {
        display: block;
        margin: 0 auto;
        width: 100% !important;
        max-width: 220px;
    }
    
    /* Larger centered title */
    [data-testid="stSidebar"] h1 {
        text-align: center !important;
        font-size: 2.5rem !important;
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }
    
    /* Centered subtitle with larger font */
    [data-testid="stSidebar"] h4 {
        text-align: center !important;
        font-size: 1.2rem !important;
        margin-top: 0 !important;
    }
    </style>
    """
    st.markdown(sidebar_style, unsafe_allow_html=True)
    
    if os.path.exists(image_path):
        st.image(image_path, use_container_width=True)
    else:
        st.warning("Logo image not found. Please check the path.")
    
    st.markdown("<h1>Ergon</h1>", unsafe_allow_html=True)
    st.markdown("<h4>The Intelligent Agent Builder</h4>", unsafe_allow_html=True)
    
def display_logo_centered():
    """Display the Ergon logo centered in main content - removed per design requirement"""
    # We no longer show the logo on main pages, only in sidebar
    st.markdown("<h1 style='text-align: center;'>Ergon</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center;'>The Intelligent Agent Builder</h4>", unsafe_allow_html=True)