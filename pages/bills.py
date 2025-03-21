import streamlit as st
import pandas as pd
from datetime import datetime

from models.storage import MemStorage
from utils.date_utils import format_date, format_currency, get_due_date_status
# Clear form fields if previously submitted
if 'form_submitted' in st.session_state and st.session_state.form_submitted:
    st.session_state.form_submitted = False
    # Reset form fields as needed
def show():
    """Display the bills page."""
    # Initialize storage
   storage = get_storage()

    
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
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Filter by payment status
            status_filter = st.selectbox(
                "Status",
                ["All", "Paid", "Unpaid", "Overdue", "Due Soon"]
            )
        
        with col2:
            # Filter by category
            category_options = ["All"] + [cat["name"] for cat in categories.values()]
            category_filter = st.selectbox("Category", category_options)
        
        with col3:
            # Filter by date range
            date_range = st.selectbox(
                "Date Range",
                ["All", "This Month", "Next 7 Days", "Next 30 Days", "Past Due"]
            )
        
        # Apply filters
        filtered_bills = bills.copy()
        
        # Status filter
        if status_filter == "Paid":
            filtered_bills = [bill for bill in filtered_bills if bill["paid"]]
        elif status_filter == "Unpaid":
            filtered_bills = [bill for bill in filtered_bills if not bill["paid"]]
        elif status_filter == "Overdue":
            filtered_bills = [bill for bill in filtered_bills 
                             if not bill["paid"] and datetime.strptime(bill["dueDate"], "%Y-%m-%d").date() < datetime.now().date()]
        elif status_filter == "Due Soon":
            today = datetime.now().date()
            filtered_bills = [bill for bill in filtered_bills 
                             if not bill["paid"] and 
                             today <= datetime.strptime(bill["dueDate"], "%Y-%m-%d").date() <= today.replace(day=today.day + 7)]
        
        # Category filter
        if category_filter != "All":
            category_id = next((cat_id for cat_id, cat in categories.items() if cat["name"] == category_filter), None)
            if category_id:
                filtered_bills = [bill for bill in filtered_bills if bill["categoryId"] == category_id]
        
        # Date range filter
        today = datetime.now().date()
        if date_range == "This Month":
            current_month = today.month
            current_year = today.year
            filtered_bills = [bill for bill in filtered_bills 
                             if datetime.strptime(bill["dueDate"], "%Y-%m-%d").date().month == current_month
                             and datetime.strptime(bill["dueDate"], "%Y-%m-%d").date().year == current_year]
        elif date_range == "Next 7 Days":
            end_date = today.replace(day=today.day + 7)
            filtered_bills = [bill for bill in filtered_bills 
                             if today <= datetime.strptime(bill["dueDate"], "%Y-%m-%d").date() <= end_date]
        elif date_range == "Next 30 Days":
            end_date = today.replace(day=today.day + 30)
            filtered_bills = [bill for bill in filtered_bills 
                             if today <= datetime.strptime(bill["dueDate"], "%Y-%m-%d").date() <= end_date]
        elif date_range == "Past Due":
            filtered_bills = [bill for bill in filtered_bills 
                             if not bill["paid"] and datetime.strptime(bill["dueDate"], "%Y-%m-%d").date() < today]
        
        # Sort bills by due date
        filtered_bills.sort(key=lambda x: x["dueDate"])
        
        # Display bills
        if not filtered_bills:
            st.info("No bills match your filter criteria.")
        else:
            # Create a DataFrame for display
            bills_data = []
            for bill in filtered_bills:
                status = get_due_date_status(bill["dueDate"])
                
                bills_data.append({
                    "ID": bill["id"],
                    "Title": bill["title"],
                    "Amount": f"${bill['amount']:.2f}",
                    "Due Date": format_date(bill["dueDate"]),
                    "Category": categories[bill["categoryId"]]["name"],
                    "Status": status["label"],
                    "Paid": "Yes" if bill["paid"] else "No",
                    "Recurring": "Yes" if bill["recurring"] else "No",
                    "Merchant": bill["merchantName"] or "N/A",
                    "_status_color": status["color"],
                    "_paid": bill["paid"],
                    "_bill": bill
                })
            
            df = pd.DataFrame(bills_data)
            
            # Create an interactive table
            for i, row in df.iterrows():
                col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])
                
                # Bill title and merchant
                col1.markdown(f"<strong>{row['Title']}</strong><br><small>{row['Merchant']}</small>", unsafe_allow_html=True)
                
                # Due date
                col2.write(row["Due Date"])
                
                # Amount
                col3.write(row["Amount"])
                
                # Status
                col4.markdown(
                    f'<span class="status-badge {row["Status"].lower().replace(" ", "-")}" '
                    f'style="background-color: {row["_status_color"]}20; color: {row["_status_color"]};">'
                    f'{row["Status"]}</span>',
                    unsafe_allow_html=True
                )
                
                # Actions
                if not row["_paid"]:
                    if col5.button("Mark Paid", key=f"pay_bill_{row['ID']}"):
                        # Update bill
                        storage.update_bill(row['ID'], {"paid": True})
                        st.success(f"Marked {row['Title']} as paid.")
                        st.rerun()
                else:
                    col5.write("✓ Paid")
                
                # Add expander with details
                with st.expander("Details", expanded=False):
                    bill = row["_bill"]
                    
                    # Bill details
                    st.markdown(f"**Description:** {bill['description'] or 'No description'}")
                    st.markdown(f"**Category:** {categories[bill['categoryId']]['name']}")
                    st.markdown(f"**Recurring:** {'Yes' if bill['recurring'] else 'No'}")
                    st.markdown(f"**Auto-pay:** {'Yes' if bill['autoPay'] else 'No'}")
                    st.markdown(f"**Detected from SMS:** {'Yes' if bill['detectedFromSms'] else 'No'}")
                    
                    # Edit/Delete buttons
                    col1, col2 = st.columns(2)
                    if col1.button("Edit", key=f"edit_bill_{row['ID']}"):
                        st.session_state.bill_to_edit = bill
                        st.rerun()
                    
                    if col2.button("Delete", key=f"delete_bill_{row['ID']}"):
                        if storage.delete_bill(row['ID']):
                            st.success(f"Deleted {row['Title']}.")
                            st.rerun()
                        else:
                            st.error("Failed to delete bill.")
                
                st.markdown("<hr style='margin: 5px 0; opacity: 0.2;'>", unsafe_allow_html=True)
    
    with tab2:
        # Form for adding a new bill
        with st.form("add_bill_form"):
            st.subheader("Add New Bill")
            
            # Bill details
            title = st.text_input("Bill Title", "")
            amount = st.number_input("Amount", min_value=0.01, value=0.01, step=0.01)
            due_date = st.date_input("Due Date", datetime.now().date())
            
            col1, col2 = st.columns(2)
            with col1:
                category_id = st.selectbox(
                    "Category",
                    options=[category["id"] for category in categories.values()],
                    format_func=lambda x: categories[x]["name"]
                )
            
            with col2:
                merchant = st.text_input("Merchant/Company", "")
            
            col1, col2 = st.columns(2)
            with col1:
                recurring = st.checkbox("Recurring Bill", True)
            
            with col2:
                auto_pay = st.checkbox("Auto-Pay Enabled", False)
            
            description = st.text_area("Description", "")
            
            # Submit button
            submit = st.form_submit_button("Add Bill")
            
            if submit:
                st.write("Form submitted!")
                if not title:
                    st.error("Please enter a bill title.")
                else:
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
                    st.write("Form data:", {
             "title": title,
    "amount": amount,
    "dueDate": due_date.strftime("%Y-%m-%d"),
    "categoryId": category_id,
    "userId": user_id,
    "paid": False,
    "recurring": recurring,
    "description": description,
    "merchantName": merchant,
    "autoPay": auto_pay,
    "detectedFromSms": False
})
                    bill = storage.create_bill(new_bill)
                    st.write("Created bill:", bill)
                    if bill:
                        st.success(f"Added new bill: {title}")
                        st.session_state.form_submitted = True
                    else:
                        st.error("Failed to add bill.")
