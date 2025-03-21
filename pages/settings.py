import streamlit as st
from datetime import datetime

from models.storage import MemStorage

def show():
    """Display the settings page."""
    # Initialize storage
    storage = MemStorage()
    
    # Get user ID (in a real app, this would come from authentication)
    user_id = 1
    
    # Get user data
    user = storage.get_user(user_id)
    
    # Header
    st.markdown('<h1 class="main-header">Settings</h1>', unsafe_allow_html=True)
    
    # Create tabs for different settings categories
    tab1, tab2, tab3 = st.tabs(["Profile", "Notifications", "Preferences"])
    
    with tab1:
        show_profile_settings(user)
    
    with tab2:
        show_notification_settings(user)
    
    with tab3:
        show_preferences_settings(user)

def show_profile_settings(user):
    """Display profile settings."""
    st.subheader("Profile Settings")
    
    # Display current profile information
    st.markdown("### Current Profile")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Name:** {user['name']}")
        st.markdown(f"**Email:** {user['email']}")
    
    with col2:
        st.markdown(f"**Username:** {user['username']}")
        st.markdown(f"**Joined:** {user['createdAt'].strftime('%b %d, %Y')}")
    
    st.markdown("---")
    
    # Form to update profile
    st.markdown("### Update Profile")
    
    with st.form("profile_form"):
        name = st.text_input("Full Name", user["name"])
        email = st.text_input("Email Address", user["email"])
        
        # Password fields
        st.markdown("### Change Password")
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        # Submit button
        submit = st.form_submit_button("Update Profile")
        
        if submit:
            # Validate inputs
            if not name or not email:
                st.error("Name and email are required.")
            elif "@" not in email:
                st.error("Please enter a valid email address.")
            elif new_password and new_password != confirm_password:
                st.error("New passwords do not match.")
            else:
                # Update profile (in a real app, password change would be handled securely)
                updates = {
                    "name": name,
                    "email": email
                }
                
                # Mock successful update
                st.success("Profile updated successfully!")

def show_notification_settings(user):
    """Display notification settings."""
    st.subheader("Notification Settings")
    
    notification_settings = user["settings"]["notifications"]
    
    with st.form("notification_form"):
        # Notification toggles
        email_notifications = st.toggle("Email Notifications", notification_settings["email"])
        push_notifications = st.toggle("Push Notifications", notification_settings["push"])
        sms_notifications = st.toggle("SMS Notifications", notification_settings["sms"])
        
        # Notification preferences
        st.markdown("### Notification Preferences")
        
        bill_due_days = st.slider(
            "Send bill payment reminders ____ days before due date",
            min_value=1,
            max_value=14,
            value=3
        )
        
        notify_options = st.multiselect(
            "Notify me about:",
            options=[
                "Upcoming bills",
                "Overdue payments",
                "Subscription renewals",
                "Savings opportunities",
                "New bill detection"
            ],
            default=[
                "Upcoming bills",
                "Overdue payments",
                "Subscription renewals"
            ]
        )
        
        # Submit button
        submit = st.form_submit_button("Save Notification Settings")
        
        if submit:
            # Mock successful update
            st.success("Notification settings updated successfully!")

def show_preferences_settings(user):
    """Display app preferences settings."""
    st.subheader("App Preferences")
    
    with st.form("preferences_form"):
        # Theme selection
        current_theme = user["settings"]["theme"]
        theme = st.selectbox(
            "App Theme",
            options=["light", "dark", "system"],
            index=["light", "dark", "system"].index(current_theme)
        )
        
        # Currency selection
        current_currency = user["settings"]["currency"]
        currency = st.selectbox(
            "Currency",
            options=["USD", "EUR", "GBP", "CAD", "AUD", "INR", "JPY"],
            index=["USD", "EUR", "GBP", "CAD", "AUD", "INR", "JPY"].index(current_currency) if current_currency in ["USD", "EUR", "GBP", "CAD", "AUD", "INR", "JPY"] else 0
        )
        
        # Dashboard preferences
        st.markdown("### Dashboard Preferences")
        
        default_view = st.radio(
            "Default Dashboard View",
            options=["Summary", "Upcoming Bills", "Spending Breakdown"],
            index=0
        )
        
        # Date format
        date_format = st.radio(
            "Date Format",
            options=["MM/DD/YYYY", "DD/MM/YYYY", "YYYY-MM-DD"],
            index=0
        )
        
        # Submit button
        submit = st.form_submit_button("Save Preferences")
        
        if submit:
            # Mock successful update
            st.success("Preferences updated successfully!")
