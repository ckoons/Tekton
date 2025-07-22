"""
Authentication pages for Ergon UI
"""

import sys
import os

# Add Tekton root to sys.path before other imports
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../'))
if tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)

import streamlit as st
import hashlib
from shared.env import TektonEnviron
from ..utils.session import debug, navigate_to

def login_page():
    """Display the login page"""
    st.title("Welcome to Ergon")
    st.markdown("### Login")
    
    # Simple login form
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if check_credentials(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                navigate_to("Home")
                st.experimental_rerun()
            else:
                st.error("Invalid username or password")
    
    # Link to registration
    st.markdown("---")
    st.markdown("Don't have an account? [Register](#)")
    if st.button("Create Account"):
        navigate_to("Register")
        st.experimental_rerun()
    
    # Option for demo mode
    st.markdown("---")
    if st.button("Continue without login"):
        if TektonEnviron.get("ERGON_AUTHENTICATION", "true").lower() == "false":
            st.session_state.authenticated = True
            st.session_state.username = "Guest"
            navigate_to("Home")
            st.experimental_rerun()
        else:
            st.error("Authentication is required. Please contact your administrator.")

def register_page():
    """Display the registration page"""
    st.title("Create an Account")
    
    with st.form("register_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submit = st.form_submit_button("Register")
        
        if submit:
            if password != confirm_password:
                st.error("Passwords do not match")
            elif username and password:
                # Simple stub for user registration
                st.success(f"Account created for {username}. You can now login.")
                # Navigate to login after 2 seconds
                navigate_to("Login")
                st.experimental_rerun()
            else:
                st.error("Please fill in all fields")
    
    # Back to login link
    if st.button("Back to Login"):
        navigate_to("Login")
        st.experimental_rerun()

def check_credentials(username, password):
    """Check if the credentials are valid"""
    # Demo authentication - in production, use a secure database
    if TektonEnviron.get("ERGON_AUTHENTICATION", "true").lower() == "false":
        return True
        
    # Simple credential check (replace with secure authentication in production)
    if username == "admin" and password == "password":
        return True
    return False