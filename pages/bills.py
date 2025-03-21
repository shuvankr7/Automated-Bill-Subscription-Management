import streamlit as st
import pandas as pd
from datetime import datetime

from models.storage import MemStorage
from utils.date_utils import format_date, format_currency, get_due_date_status

def show():
    """Display the bills page."""
    # Initialize storage
    storage = MemStorage()
    
    # Get user ID (in a real app, this would come from authentication)
    user_id = 1
    
    # Get bills for the user
    bills = storage.get_bills(user_id)
    
    # Get categories
    categories = {category["id"]: category for category in storage.get_categories()}
    
    # Header
    st.markdown('<h1 class="main-header">Bills</h1>', unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2 = st.tabs(["All Bills", "Add New Bill"])
    
    with tab1:
        # Display bills
        if not bills:
            st.info("No bills found.")
        else:
            # Sort bills by due date
            bills.sort(key=lambda x: x["dueDate"])
            
            # Create a simple table for bills
            for bill in bills:
                status = get_due_date_status(bill["dueDate"])
                
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                # Bill title and merchant
                col1.markdown(f"<strong>{bill['title']}</strong><br><small>{bill['merchantName'] or 'N/A'}</small>", unsafe_allow_html=True)
                
                # Due date
                col2.write(format_date(bill["dueDate"]))
                
                # Amount
                col3.write(format_currency(bill["amount"]))
                
                # Status
                col4.markdown(
                    f'<span style="background-color: {status["color"]}20; color: {status["color"]}; '
                    f'padding: 3px 10px; border-radius: 12px; font-size: 0.7rem; font-weight: 500;">'
                    f'{status["label"]}</span>',
                    unsafe_allow_html=True
                )
                
                # Display bill details in an expander
                with st.expander("Details", expanded=False):
                    st.markdown(f"**Description:** {bill['description'] or 'No description'}")
                    st.markdown(f"**Category:** {categories[bill['categoryId']]['name']}")
                    st.markdown(f"**Recurring:** {'Yes' if bill['recurring'] else 'No'}")
                    st.markdown(f"**Paid:** {'Yes' if bill['paid'] else 'No'}")
                    st.markdown(f"**Auto-pay:** {'Yes' if bill['autoPay'] else 'No'}")
                
                st.markdown("<hr>", unsafe_allow_html=True)
    
    with tab2:
    # Simple approach to add a bill without using st.form
    st.subheader("Add New Bill")
    
    # Bill details
    title = st.text_input("Bill Title", key="bill_title")
    amount = st.number_input("Amount", min_value=0.01, value=0.01, step=0.01, key="bill_amount")
    due_date = st.date_input("Due Date", datetime.now().date(), key="bill_due_date")
    
    col1, col2 = st.columns(2)
    with col1:
        category_id = st.selectbox(
            "Category",
            options=[category["id"] for category in categories.values()],
            format_func=lambda x: categories[x]["name"],
            key="bill_category"
        )
    
    with col2:
        merchant = st.text_input("Merchant/Company", key="bill_merchant")
    
    col1, col2 = st.columns(2)
    with col1:
        recurring = st.checkbox("Recurring Bill", True, key="bill_recurring")
    
    with col2:
        auto_pay = st.checkbox("Auto-Pay Enabled", False, key="bill_autopay")
    
    description = st.text_area("Description", key="bill_description")
    
    # Submit button
    if st.button("Add Bill", key="add_bill_btn"):
        if not title:
            st.error("Please enter a bill title.")
        else:
            # Debug info
            st.write("Submitting bill data...")
            
            # Create bill object
            new_bill = {
                "title": title,
                "amount": float(amount),
                "dueDate": due_date.strftime("%Y-%m-%d"),
                "categoryId": category_id,
                "userId": user_id,
                "paid": False,
                "recurring": recurring,
                "description": description,
                "merchantName": merchant,
                "autoPay": auto_pay,
                "detectedFromSms": False
            }
            
            # Add to storage
            bill = storage.create_bill(new_bill)
            
            if bill:
                st.success(f"Added new bill: {title}")
            else:
                st.error("Failed to add bill.")
