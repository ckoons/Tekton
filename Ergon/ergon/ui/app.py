"""
Ergon Streamlit UI Application

This is the main entry point for the Streamlit UI. It has been refactored into 
a modular structure with components in separate files for better maintainability.
"""

import streamlit as st
import sys
import os
import importlib.util

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure Streamlit page
st.set_page_config(
    page_title="Ergon Nexus",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "Ergon Nexus - Your AI-powered assistant with memory capabilities"
    }
)

# Hide Streamlit default header/footer and module names
hide_streamlit_style = """
<style>
/* Hide main menu and standard Streamlit elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
div[data-testid="stToolbar"] {visibility: hidden;}

/* Hide the module names that appear at the top of sidebar */
div[data-testid="stSidebarNav"] {display: none;}

/* Hide redundant elements */
.stDeployButton {display: none;}

/* Make sure the sidebar icon remains visible */
div[data-testid="stSidebar"] > div:first-child {
    background-color: transparent !important;
}

/* Main content needs less top padding without the header */
.main .block-container {
    padding-top: 1rem;
}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Import the main application module
from ergon.ui.main import main

# Run the application
if __name__ == "__main__":
    main()