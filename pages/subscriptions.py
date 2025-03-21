import streamlit as st
import pandas as pd
from datetime import datetime

from models.storage import MemStorage
from utils.date_utils import format_date, format_currency, format_frequency

def show():
    """Display the subscriptions page."""
    # Initialize storage
    storage = MemStorage()
    
    # Get user ID (in a real app, this would come from authentication)
    user_id = 1
    
    # Get subscriptions for the user
    subscriptions = storage.get_subscriptions(user_id)
    
    # Get categories
    categories = {category["id"]: category for category in storage.get_categories()}
    
    # Header
    st.markdown('<h1 class="main-header">Subscriptions</h1>', unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2 = st.tabs(["All Subscriptions", "Add New Subscription"])
    
    with tab1:
        # Display subscriptions
        if not subscriptions:
            st.info("No subscriptions found.")
        else:
            # Sort subscriptions by renewal date
            subscriptions.sort(key=lambda x: x["renewalDate"])
            
            for sub in subscriptions:
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                # Subscription title and merchant
                col1.markdown(f"<strong>{sub['title']}</strong><br><small>{sub['merchantName'] or 'N/A'}</small>", unsafe_allow_html=True)
                
                # Amount and frequency
                frequency = format_frequency(sub["frequency"])
                col2.markdown(f"{format_currency(sub['amount'])}<br><small>{frequency}</small>", unsafe_allow_html=True)
                
                # Renewal date
                col3.write(format_date(sub["renewalDate"]))
                
                # Status
                status_color = "#4CAF50" if sub["active"] else "#9E9E9E"
                status_text = "Active" if sub["active"] else "Inactive"
                col4.markdown(
                    f'<span style="background-color: {status_color}20; color: {status_color}; '
                    f'padding: 3px 10px; border-radius: 12px; font-size: 0.7rem; font-weight: 500;">'
                    f'{status_text}</span>',
                    unsafe_allow_html=True
                )
                
                # Display subscription details in an expander
                with st.expander("Details", expanded=False):
                    st.markdown(f"**Description:** {sub['description'] or 'No description'}")
                    st.markdown(f"**Category:** {categories[sub['categoryId']]['name']}")
                    st.markdown(f"**Auto-renewal:** {'Yes' if sub['autoPay'] else 'No'}")
                    
                    if sub['lastUsed']:
                        last_used = datetime.strftime(sub['lastUsed'], "%b %d, %Y") if isinstance(sub['lastUsed'], datetime) else sub['lastUsed']
                        st.markdown(f"**Last used:** {last_used}")
                
                st.markdown("<hr>", unsafe_allow_html=True)
    
    with tab2:
        # Form for adding a new subscription
        st.subheader("Add New Subscription")
        
        # Subscription details
        title = st.text_input("Subscription Name", key="sub_title")
        amount = st.number_input("Amount", min_value=0.01, value=9.99, step=0.01, key="sub_amount")
        
        col1, col2 = st.columns(2)
        with col1:
            frequency = st.selectbox(
                "Billing Frequency",
                options=["monthly", "yearly", "quarterly", "weekly", "biweekly"],
                key="sub_frequency"
            )
        
        with col2:
            renewal_date = st.date_input("Next Renewal Date", datetime.now().date(), key="sub_renewal_date")
        
        col1, col2 = st.columns(2)
        with col1:
            category_id = st.selectbox(
                "Category",
                options=[category["id"] for category in categories.values()],
                format_func=lambda x: categories[x]["name"],
                key="sub_category"
            )
        
        with col2:
            merchant = st.text_input("Service Provider", key="sub_merchant")
        
        col1, col2 = st.columns(2)
        with col1:
            active = st.checkbox("Active", True, key="sub_active")
        
        with col2:
            auto_pay = st.checkbox("Auto-Renewal Enabled", True, key="sub_autopay")
        
        description = st.text_area("Description", key="sub_description")
        
        # Submit button
        if st.button("Add Subscription", key="add_sub_btn"):
            if not title:
                st.error("Please enter a subscription name.")
            else:
                # Create subscription object
                new_sub = {
                    "title": title,
                    "amount": float(amount),
                    "frequency": frequency,
                    "renewalDate": renewal_date.strftime("%Y-%m-%d"),
                    "categoryId": category_id,
                    "userId": user_id,
                    "active": active,
                    "description": description,
                    "merchantName": merchant,
                    "autoPay": auto_pay,
                    "lastUsed": datetime.now()
                }
                
                # Debug output
                st.write("Creating subscription with data:", new_sub)
                
                # Add to storage
                sub = storage.create_subscription(new_sub)
                
                # Debug output
                st.write("Created subscription:", sub)
                
                if sub:
                    st.success(f"Added new subscription: {title}")
                    # Don't use rerun, just show the success message
                else:
                    st.error("Failed to add subscription.")
