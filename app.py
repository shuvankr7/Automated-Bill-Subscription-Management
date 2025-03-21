import streamlit as st
import os
from dotenv import load_dotenv
from components.sidebar import render_sidebar
import pages.dashboard as dashboard
import pages.bills as bills
import pages.subscriptions as subscriptions
import pages.analytics as analytics
import pages.sms_import as sms_import
import pages.settings as settings

# Load environment variables
load_dotenv()

def local_css():
    """Apply custom CSS styling."""
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E88E5;
        margin-bottom: 1rem;
    }
    .card {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .card-title {
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 10px;
    }
    .metric-card {
        background-color: white;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        text-align: center;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1E88E5;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #757575;
    }
    .status-badge {
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.7rem;
        font-weight: 500;
    }
    .status-badge.overdue {
        background-color: #ffebee;
        color: #c62828;
    }
    .status-badge.due-soon {
        background-color: #fff8e1;
        color: #ff8f00;
    }
    .status-badge.upcoming {
        background-color: #e8f5e9;
        color: #2e7d32;
    }
    .small-icon {
        font-size: 1.2rem;
        margin-right: 5px;
    }
    .suggestion-card {
        border-left: 4px solid #1E88E5;
        padding-left: 10px;
    }
    .tab-content {
        padding: 20px 0;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    """Main entry point for the Streamlit application."""
    # Page configuration
    st.set_page_config(
        page_title=os.getenv("APP_TITLE", "BillTracker AI"),
        page_icon=os.getenv("APP_ICON", "💰"),
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply custom CSS
    local_css()
    
    # Render sidebar and get selected page
    selected_page = render_sidebar()
    
    # Display selected page
    if selected_page == "Dashboard":
        dashboard.show()
    elif selected_page == "Bills":
        bills.show()
    elif selected_page == "Subscriptions":
        subscriptions.show()
    elif selected_page == "Analytics":
        analytics.show()
    elif selected_page == "SMS Import":
        sms_import.show()
    elif selected_page == "Settings":
        settings.show()

if __name__ == "__main__":
    main()
