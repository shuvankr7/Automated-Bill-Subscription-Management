import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Set page config
st.set_page_config(
    page_title="BillTracker AI",
    page_icon="💰",
    layout="wide"
)

# Initialize session state for storage
if 'bills' not in st.session_state:
    st.session_state.bills = []
    # Sample bills for demonstration
    st.session_state.bills = [
        {
            "id": 1,
            "title": "Rent",
            "amount": 1200.00,
            "due_date": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
            "category": "Housing",
            "paid": False,
            "recurring": True,
            "description": "Monthly apartment rent",
            "merchant": "ABC Properties"
        },
        {
            "id": 2,
            "title": "Electricity Bill",
            "amount": 87.50,
            "due_date": (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d"),
            "category": "Utilities",
            "paid": False,
            "recurring": True,
            "description": "Monthly electricity utility bill",
            "merchant": "Power Company"
        }
    ]

if 'subscriptions' not in st.session_state:
    st.session_state.subscriptions = []
    # Sample subscriptions for demonstration
    st.session_state.subscriptions = [
        {
            "id": 1,
            "title": "Netflix",
            "amount": 15.99,
            "renewal_date": (datetime.now() + timedelta(days=12)).strftime("%Y-%m-%d"),
            "frequency": "monthly",
            "category": "Entertainment",
            "active": True,
            "description": "Standard HD streaming plan",
            "merchant": "Netflix"
        },
        {
            "id": 2,
            "title": "Spotify",
            "amount": 9.99,
            "renewal_date": (datetime.now() + timedelta(days=20)).strftime("%Y-%m-%d"),
            "frequency": "monthly",
            "category": "Entertainment",
            "active": True,
            "description": "Premium music subscription",
            "merchant": "Spotify"
        }
    ]

if 'bill_counter' not in st.session_state:
    st.session_state.bill_counter = 2

if 'sub_counter' not in st.session_state:
    st.session_state.sub_counter = 2

if 'page' not in st.session_state:
    st.session_state.page = "Dashboard"

# CSS styling
st.markdown("""
<style>
    .main-header {font-size: 2.5rem; color: #1E88E5; margin-bottom: 1rem;}
    .card {background-color: #f9f9f9; border-radius: 10px; padding: 20px; 
           box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); margin-bottom: 20px;}
    .metric-card {background-color: white; border-radius: 8px; padding: 15px; 
                 box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05); text-align: center;}
    .metric-value {font-size: 1.8rem; font-weight: 700; color: #1E88E5;}
    .metric-label {font-size: 0.9rem; color: #757575;}
    .overdue {color: #c62828; background-color: #ffebee; padding: 3px 10px; 
              border-radius: 12px; font-size: 0.8rem;}
    .due-soon {color: #ff8f00; background-color: #fff8e1; padding: 3px 10px; 
               border-radius: 12px; font-size: 0.8rem;}
    .upcoming {color: #2e7d32; background-color: #e8f5e9; padding: 3px 10px; 
               border-radius: 12px; font-size: 0.8rem;}
</style>
""", unsafe_allow_html=True)

# Helper functions
def format_currency(amount):
    return f"${amount:,.2f}"

def format_date(date_str):
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    return date_obj.strftime("%b %d, %Y")

def get_bill_status(due_date):
    today = datetime.now().date()
    due = datetime.strptime(due_date, "%Y-%m-%d").date()
    
    if due < today:
        return "overdue", "Overdue"
    elif (due - today).days <= 3:
        return "due-soon", "Due Soon"
    else:
        return "upcoming", "Upcoming"

# Sidebar for navigation
with st.sidebar:
    st.title("BillTracker AI")
    st.markdown("---")
    
    # Navigation
    st.markdown("### Navigation")
    
    if st.button("📊 Dashboard", use_container_width=True, 
                type="primary" if st.session_state.page == "Dashboard" else "secondary"):
        st.session_state.page = "Dashboard"
        
    if st.button("💵 Bills", use_container_width=True,
                type="primary" if st.session_state.page == "Bills" else "secondary"):
        st.session_state.page = "Bills"
        
    if st.button("🔄 Subscriptions", use_container_width=True,
                type="primary" if st.session_state.page == "Subscriptions" else "secondary"):
        st.session_state.page = "Subscriptions"
    
    st.markdown("---")
    st.caption("© 2023 BillTracker AI")
    st.caption("Version 1.0.0")

# Main content based on selected page
if st.session_state.page == "Dashboard":
    st.markdown('<h1 class="main-header">Dashboard</h1>', unsafe_allow_html=True)
    
    # Calculate metrics
    total_bills = sum(bill["amount"] for bill in st.session_state.bills)
    upcoming_bills = sum(1 for bill in st.session_state.bills 
                        if not bill["paid"] and get_bill_status(bill["due_date"])[0] != "overdue")
    monthly_subs = sum(sub["amount"] for sub in st.session_state.subscriptions if sub["active"])
    
    # Top metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-value">{format_currency(total_bills)}</div>
            <div class="metric-label">Total Bills</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-value">{upcoming_bills}</div>
            <div class="metric-label">Upcoming Bills</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-value">{format_currency(monthly_subs)}</div>
            <div class="metric-label">Monthly Subscriptions</div>
        </div>
        ''', unsafe_allow_html=True)
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Upcoming bills
        st.markdown('<div class="card"><h3>📅 Upcoming Bills</h3>', unsafe_allow_html=True)
        
        if not st.session_state.bills:
            st.info("No bills found.")
        else:
            # Filter and sort upcoming bills
            upcoming = [bill for bill in st.session_state.bills 
                       if not bill["paid"] and datetime.strptime(bill["due_date"], "%Y-%m-%d").date() >= datetime.now().date()]
            upcoming.sort(key=lambda x: x["due_date"])
            
            if not upcoming:
                st.info("No upcoming bills.")
            else:
                for bill in upcoming[:5]:  # Show only top 5
                    status_class, status_text = get_bill_status(bill["due_date"])
                    
                    cols = st.columns([3, 2, 2, 1])
                    cols[0].markdown(f"<strong>{bill['title']}</strong><br><small>{bill['merchant']}</small>", unsafe_allow_html=True)
                    cols[1].write(format_date(bill["due_date"]))
                    cols[2].write(format_currency(bill["amount"]))
                    cols[3].markdown(f'<span class="{status_class}">{status_text}</span>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Subscriptions summary
        st.markdown('<div class="card"><h3>🔄 Active Subscriptions</h3>', unsafe_allow_html=True)
        
        if not st.session_state.subscriptions:
            st.info("No subscriptions found.")
        else:
            active_subs = [sub for sub in st.session_state.subscriptions if sub["active"]]
            if not active_subs:
                st.info("No active subscriptions.")
            else:
                for sub in active_subs[:3]:  # Show only top 3
                    st.markdown(f"""
                    <div style="margin-bottom: 10px; padding-bottom: 10px; border-bottom: 1px solid #eee;">
                        <strong>{sub['title']}</strong> - {format_currency(sub['amount'])}/month<br>
                        <small>Next renewal: {format_date(sub['renewal_date'])}</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                if len(active_subs) > 3:
                    st.write(f"+ {len(active_subs) - 3} more subscriptions")
        
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "Bills":
    st.markdown('<h1 class="main-header">Bills</h1>', unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2 = st.tabs(["All Bills", "Add New Bill"])
    
    with tab1:
        if not st.session_state.bills:
            st.info("No bills found.")
        else:
            # Sort bills by due date
            sorted_bills = sorted(st.session_state.bills, key=lambda x: x["due_date"])
            
            for bill in sorted_bills:
                status_class, status_text = get_bill_status(bill["due_date"])
                
                col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1])
                
                col1.markdown(f"<strong>{bill['title']}</strong><br><small>{bill['merchant']}</small>", unsafe_allow_html=True)
                col2.write(format_date(bill["due_date"]))
                col3.write(format_currency(bill["amount"]))
                col4.markdown(f'<span class="{status_class}">{status_text}</span>', unsafe_allow_html=True)
                
                if not bill["paid"]:
                    if col5.button("Mark Paid", key=f"pay_{bill['id']}"):
                        for b in st.session_state.bills:
                            if b["id"] == bill["id"]:
                                b["paid"] = True
                                st.success(f"Marked {bill['title']} as paid!")
                                st.rerun()
                else:
                    col5.write("✓ Paid")
                
                with st.expander("Details", expanded=False):
                    st.markdown(f"**Description:** {bill['description']}")
                    st.markdown(f"**Category:** {bill['category']}")
                    st.markdown(f"**Recurring:** {'Yes' if bill['recurring'] else 'No'}")
                    
                    # Edit/Delete buttons
                    col1, col2 = st.columns(2)
                    if col2.button("Delete", key=f"del_{bill['id']}"):
                        st.session_state.bills = [b for b in st.session_state.bills if b["id"] != bill["id"]]
                        st.success(f"Deleted {bill['title']}!")
                        st.rerun()
                
                st.markdown("<hr>", unsafe_allow_html=True)
    
    with tab2:
        # Form for adding a new bill
        st.subheader("Add New Bill")
        
        # Bill details
        title = st.text_input("Bill Title", key="new_bill_title")
        amount = st.number_input("Amount", min_value=0.01, value=0.01, step=0.01, key="new_bill_amount")
        due_date = st.date_input("Due Date", datetime.now().date(), key="new_bill_date")
        
        col1, col2 = st.columns(2)
        with col1:
            category = st.selectbox(
                "Category",
                ["Housing", "Utilities", "Transportation", "Entertainment", "Insurance", "Other"],
                key="new_bill_category"
            )
        
        with col2:
            merchant = st.text_input("Merchant/Company", key="new_bill_merchant")
        
        col1, col2 = st.columns(2)
        with col1:
            recurring = st.checkbox("Recurring Bill", True, key="new_bill_recurring")
        
        with col2:
            auto_pay = st.checkbox("Auto-Pay Enabled", False, key="new_bill_autopay")
        
        description = st.text_area("Description", key="new_bill_desc")
        
        # Submit button
        if st.button("Add Bill", key="add_bill_btn"):
            if not title:
                st.error("Please enter a bill title.")
            else:
                # Increment counter and create bill
                st.session_state.bill_counter += 1
                new_bill = {
                    "id": st.session_state.bill_counter,
                    "title": title,
                    "amount": float(amount),
                    "due_date": due_date.strftime("%Y-%m-%d"),
                    "category": category,
                    "paid": False,
                    "recurring": recurring,
                    "description": description,
                    "merchant": merchant,
                    "auto_pay": auto_pay
                }
                
                # Add to session state
                st.session_state.bills.append(new_bill)
                st.success(f"Added new bill: {title}")
                
                # Clear form fields
                st.session_state["new_bill_title"] = ""
                st.session_state["new_bill_amount"] = 0.01
                st.session_state["new_bill_merchant"] = ""
                st.session_state["new_bill_desc"] = ""
                
                # No rerun needed here - let the success message show

elif st.session_state.page == "Subscriptions":
    st.markdown('<h1 class="main-header">Subscriptions</h1>', unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2 = st.tabs(["All Subscriptions", "Add New Subscription"])
    
    with tab1:
        if not st.session_state.subscriptions:
            st.info("No subscriptions found.")
        else:
            # Sort subscriptions by renewal date
            sorted_subs = sorted(st.session_state.subscriptions, key=lambda x: x["renewal_date"])
            
            # Calculate monthly cost
            monthly_cost = sum(
                sub["amount"] if sub["frequency"] == "monthly" else
                sub["amount"] / 12 if sub["frequency"] == "yearly" else
                sub["amount"] / 3 if sub["frequency"] == "quarterly" else
                sub["amount"] * 4.33 if sub["frequency"] == "weekly" else 0
                for sub in st.session_state.subscriptions if sub["active"]
            )
            
            # Display total monthly cost
            st.markdown(
                f'<div style="background-color: #f0f7ff; padding: 15px; border-radius: 10px; margin-bottom: 20px;">'
                f'<h3 style="margin: 0; color: #1565C0;">Monthly Subscription Cost: {format_currency(monthly_cost)}</h3>'
                f'</div>',
                unsafe_allow_html=True
            )
            
            for sub in sorted_subs:
                col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1])
                
                frequency_display = {
                    "monthly": "Monthly",
                    "yearly": "Yearly",
                    "quarterly": "Quarterly",
                    "weekly": "Weekly",
                    "biweekly": "Bi-weekly"
                }.get(sub["frequency"], sub["frequency"].capitalize())
                
                col1.markdown(f"<strong>{sub['title']}</strong><br><small>{sub['merchant']}</small>", unsafe_allow_html=True)
                col2.markdown(f"{format_currency(sub['amount'])}<br><small>{frequency_display}</small>", unsafe_allow_html=True)
                col3.write(format_date(sub["renewal_date"]))
                
                status_color = "#4CAF50" if sub["active"] else "#9E9E9E"
                status_text = "Active" if sub["active"] else "Inactive"
                col4.markdown(
                    f'<span style="background-color: {status_color}20; color: {status_color}; '
                    f'padding: 3px 10px; border-radius: 12px; font-size: 0.8rem;">'
                    f'{status_text}</span>',
                    unsafe_allow_html=True
                )
                
                if sub["active"]:
                    if col5.button("Deactivate", key=f"deact_{sub['id']}"):
                        for s in st.session_state.subscriptions:
                            if s["id"] == sub["id"]:
                                s["active"] = False
                                st.success(f"Deactivated {sub['title']}!")
                                st.rerun()
                else:
                    if col5.button("Activate", key=f"act_{sub['id']}"):
                        for s in st.session_state.subscriptions:
                            if s["id"] == sub["id"]:
                                s["active"] = True
                                st.success(f"Activated {sub['title']}!")
                                st.rerun()
                
                with st.expander("Details", expanded=False):
                    st.markdown(f"**Description:** {sub['description']}")
                    st.markdown(f"**Category:** {sub['category']}")
                    
                    # Edit/Delete buttons
                    col1, col2 = st.columns(2)
                    if col2.button("Delete", key=f"del_sub_{sub['id']}"):
                        st.session_state.subscriptions = [s for s in st.session_state.subscriptions if s["id"] != sub["id"]]
                        st.success(f"Deleted {sub['title']}!")
                        st.rerun()
                
                st.markdown("<hr>", unsafe_allow_html=True)
    
    with tab2:
        # Form for adding a new subscription
        st.subheader("Add New Subscription")
        
        # Subscription details
        title = st.text_input("Subscription Name", key="new_sub_title")
        amount = st.number_input("Amount", min_value=0.01, value=9.99, step=0.01, key="new_sub_amount")
        
        col1, col2 = st.columns(2)
        with col1:
            frequency = st.selectbox(
                "Billing Frequency",
                ["monthly", "yearly", "quarterly", "weekly", "biweekly"],
                key="new_sub_freq"
            )
        
        with col2:
            renewal_date = st.date_input("Next Renewal Date", datetime.now().date(), key="new_sub_date")
        
        col1, col2 = st.columns(2)
        with col1:
            category = st.selectbox(
                "Category",
                ["Entertainment", "Utilities", "Digital Services", "Health", "Other"],
                key="new_sub_category"
            )
        
        with col2:
            merchant = st.text_input("Service Provider", key="new_sub_merchant")
        
        col1, col2 = st.columns(2)
        with col1:
            active = st.checkbox("Active", True, key="new_sub_active")
        
        with col2:
            auto_renewal = st.checkbox("Auto-Renewal Enabled", True, key="new_sub_auto")
        
        description = st.text_area("Description", key="new_sub_desc")
        
        # Submit button
        if st.button("Add Subscription", key="add_sub_btn"):
            if not title:
                st.error("Please enter a subscription name.")
            else:
                # Increment counter and create subscription
                st.session_state.sub_counter += 1
                new_sub = {
                    "id": st.session_state.sub_counter,
                    "title": title,
                    "amount": float(amount),
                    "frequency": frequency,
                    "renewal_date": renewal_date.strftime("%Y-%m-%d"),
                    "category": category,
                    "active": active,
                    "description": description,
                    "merchant": merchant,
                    "auto_renewal": auto_renewal
                }
                
                # Add to session state
                st.session_state.subscriptions.append(new_sub)
                st.success(f"Added new subscription: {title}")
                
                # Clear form fields
                st.session_state["new_sub_title"] = ""
                st.session_state["new_sub_amount"] = 9.99
                st.session_state["new_sub_merchant"] = ""
                st.session_state["new_sub_desc"] = ""
                
                # No rerun needed here - let the success message show

# Debug information (only visible during development)
# Uncomment this section for debugging
# with st.expander("Debug Information"):
#     st.write("Bills:", st.session_state.bills)
#     st.write("Subscriptions:", st.session_state.subscriptions)
#     st.write("Current Page:", st.session_state.page)




# import streamlit as st
# import os
# from dotenv import load_dotenv
# from components.sidebar import render_sidebar
# import pages.dashboard as dashboard
# import pages.bills as bills
# import pages.subscriptions as subscriptions
# import pages.analytics as analytics
# import pages.sms_import as sms_import
# import pages.settings as settings

# # Load environment variables
# load_dotenv()

# def local_css():
#     """Apply custom CSS styling."""
#     st.markdown("""
#     <style>
#     .main-header {
#         font-size: 2.5rem;
#         font-weight: 700;
#         color: #1E88E5;
#         margin-bottom: 1rem;
#     }
#     .card {
#         background-color: #f9f9f9;
#         border-radius: 10px;
#         padding: 20px;
#         box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
#         margin-bottom: 20px;
#     }
#     .card-title {
#         font-size: 1.2rem;
#         font-weight: 600;
#         margin-bottom: 10px;
#     }
#     .metric-card {
#         background-color: white;
#         border-radius: 8px;
#         padding: 15px;
#         box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
#         text-align: center;
#     }
#     .metric-value {
#         font-size: 1.8rem;
#         font-weight: 700;
#         color: #1E88E5;
#     }
#     .metric-label {
#         font-size: 0.9rem;
#         color: #757575;
#     }
#     .status-badge {
#         padding: 3px 10px;
#         border-radius: 12px;
#         font-size: 0.7rem;
#         font-weight: 500;
#     }
#     .status-badge.overdue {
#         background-color: #ffebee;
#         color: #c62828;
#     }
#     .status-badge.due-soon {
#         background-color: #fff8e1;
#         color: #ff8f00;
#     }
#     .status-badge.upcoming {
#         background-color: #e8f5e9;
#         color: #2e7d32;
#     }
#     .small-icon {
#         font-size: 1.2rem;
#         margin-right: 5px;
#     }
#     .suggestion-card {
#         border-left: 4px solid #1E88E5;
#         padding-left: 10px;
#     }
#     .tab-content {
#         padding: 20px 0;
#     }
#     </style>
#     """, unsafe_allow_html=True)

# def main():
#     """Main entry point for the Streamlit application."""
#     # Page configuration
#     st.set_page_config(
#         page_title=os.getenv("APP_TITLE", "BillTracker AI"),
#         page_icon=os.getenv("APP_ICON", "💰"),
#         layout="wide",
#         initial_sidebar_state="expanded"
#     )
    
#     # Apply custom CSS
#     local_css()
    
#     # Render sidebar and get selected page
#     selected_page = render_sidebar()
    
#     # Display selected page
#     if selected_page == "Dashboard":
#         dashboard.show()
#     elif selected_page == "Bills":
#         bills.show()
#     elif selected_page == "Subscriptions":
#         subscriptions.show()
#     elif selected_page == "Analytics":
#         analytics.show()
#     elif selected_page == "SMS Import":
#         sms_import.show()
#     elif selected_page == "Settings":
#         settings.show()

# if __name__ == "__main__":
#     main()
