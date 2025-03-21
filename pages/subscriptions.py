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
        # Filters
        col1, col2 = st.columns(2)
        
        with col1:
            # Filter by status
            status_filter = st.selectbox(
                "Status",
                ["All", "Active", "Inactive"]
            )
        
        with col2:
            # Filter by category
            category_options = ["All"] + [cat["name"] for cat in categories.values()]
            category_filter = st.selectbox("Category", category_options)
        
        # Apply filters
        filtered_subs = subscriptions.copy()
        
        # Status filter
        if status_filter == "Active":
            filtered_subs = [sub for sub in filtered_subs if sub["active"]]
        elif status_filter == "Inactive":
            filtered_subs = [sub for sub in filtered_subs if not sub["active"]]
        
        # Category filter
        if category_filter != "All":
            category_id = next((cat_id for cat_id, cat in categories.items() if cat["name"] == category_filter), None)
            if category_id:
                filtered_subs = [sub for sub in filtered_subs if sub["categoryId"] == category_id]
        
        # Sort subscriptions by next renewal date
        filtered_subs.sort(key=lambda x: x["renewalDate"])
        
        # Calculate total monthly cost
        monthly_cost = 0
        for sub in filtered_subs:
            if sub["active"]:
                amount = sub["amount"]
                if sub["frequency"] == "yearly":
                    amount = amount / 12
                elif sub["frequency"] == "quarterly":
                    amount = amount / 3
                elif sub["frequency"] == "weekly":
                    amount = amount * 4.33  # Average weeks per month
                elif sub["frequency"] == "biweekly":
                    amount = amount * 2.17  # Average bi-weeks per month
                
                monthly_cost += amount
        
        # Display monthly cost
        st.markdown(
            f'<div style="background-color: #f0f7ff; padding: 15px; border-radius: 10px; margin-bottom: 20px;">'
            f'<h3 style="margin: 0; color: #1565C0;">Monthly Subscription Cost: {format_currency(monthly_cost)}</h3>'
            f'</div>',
            unsafe_allow_html=True
        )
        
        # Display subscriptions
        if not filtered_subs:
            st.info("No subscriptions match your filter criteria.")
        else:
            # Create a DataFrame for display
            subs_data = []
            for sub in filtered_subs:
                frequency = format_frequency(sub["frequency"])
                
                subs_data.append({
                    "ID": sub["id"],
                    "Title": sub["title"],
                    "Amount": sub["amount"],
                    "Frequency": frequency,
                    "Next Renewal": format_date(sub["renewalDate"]),
                    "Category": categories[sub["categoryId"]]["name"],
                    "Status": "Active" if sub["active"] else "Inactive",
                    "Merchant": sub["merchantName"] or "N/A",
                    "_active": sub["active"],
                    "_sub": sub
                })
            
            df = pd.DataFrame(subs_data)
            
            # Create an interactive table
            for i, row in df.iterrows():
                col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])
                
                # Subscription title and merchant
                col1.markdown(f"<strong>{row['Title']}</strong><br><small>{row['Merchant']}</small>", unsafe_allow_html=True)
                
                # Amount and frequency
                col2.markdown(f"{format_currency(row['Amount'])}<br><small>{row['Frequency']}</small>", unsafe_allow_html=True)
                
                # Next renewal
                col3.write(row["Next Renewal"])
                
                # Status
                status_color = "#4CAF50" if row["_active"] else "#9E9E9E"
                col4.markdown(
                    f'<span style="background-color: {status_color}20; color: {status_color}; '
                    f'padding: 3px 10px; border-radius: 12px; font-size: 0.7rem; font-weight: 500;">'
                    f'{row["Status"]}</span>',
                    unsafe_allow_html=True
                )
                
                # Actions
                if row["_active"]:
                    if col5.button("Deactivate", key=f"deactivate_sub_{row['ID']}"):
                        # Update subscription
                        storage.update_subscription(row['ID'], {"active": False})
                        st.success(f"Deactivated {row['Title']}.")
                        st.rerun()
                else:
                    if col5.button("Activate", key=f"activate_sub_{row['ID']}"):
                        # Update subscription
                        storage.update_subscription(row['ID'], {"active": True})
                        st.success(f"Activated {row['Title']}.")
                        st.rerun()
                
                # Add expander with details
                with st.expander("Details", expanded=False):
                    sub = row["_sub"]
                    
                    # Subscription details
                    st.markdown(f"**Description:** {sub['description'] or 'No description'}")
                    st.markdown(f"**Category:** {categories[sub['categoryId']]['name']}")
                    st.markdown(f"**Auto-renewal:** {'Yes' if sub['autoPay'] else 'No'}")
                    
                    if sub['lastUsed']:
                        last_used = datetime.strftime(sub['lastUsed'], "%b %d, %Y") if isinstance(sub['lastUsed'], datetime) else sub['lastUsed']
                        st.markdown(f"**Last used:** {last_used}")
                    
                    # Edit/Delete buttons
                    col1, col2 = st.columns(2)
                    if col1.button("Edit", key=f"edit_sub_{row['ID']}"):
                        st.session_state.sub_to_edit = sub
                        st.rerun()
                    
                    if col2.button("Delete", key=f"delete_sub_{row['ID']}"):
                        if storage.delete_subscription(row['ID']):
                            st.success(f"Deleted {row['Title']}.")
                            st.rerun()
                        else:
                            st.error("Failed to delete subscription.")
                
                st.markdown("<hr style='margin: 5px 0; opacity: 0.2;'>", unsafe_allow_html=True)
    
    with tab2:
        # Form for adding a new subscription
        with st.form("add_subscription_form"):
            st.subheader("Add New Subscription")
            
            # Subscription details
            title = st.text_input("Subscription Name", "")
            amount = st.number_input("Amount", min_value=0.01, value=9.99, step=0.01)
            
            col1, col2 = st.columns(2)
            with col1:
                frequency = st.selectbox(
                    "Billing Frequency",
                    options=["monthly", "yearly", "quarterly", "weekly", "biweekly"]
                )
            
            with col2:
                renewal_date = st.date_input("Next Renewal Date", datetime.now().date())
            
            col1, col2 = st.columns(2)
            with col1:
                category_id = st.selectbox(
                    "Category",
                    options=[category["id"] for category in categories.values()],
                    format_func=lambda x: categories[x]["name"]
                )
            
            with col2:
                merchant = st.text_input("Service Provider", "")
            
            col1, col2 = st.columns(2)
            with col1:
                active = st.checkbox("Active", True)
            
            with col2:
                auto_pay = st.checkbox("Auto-Renewal Enabled", True)
            
            description = st.text_area("Description", "")
            
            # Submit button
            submit = st.form_submit_button("Add Subscription")
            
            if submit:
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
                    
                    # Add to storage
                    sub = storage.create_subscription(new_sub)
                    
                    if sub:
                        st.success(f"Added new subscription: {title}")
                        st.rerun()
                    else:
                        st.error("Failed to add subscription.")
