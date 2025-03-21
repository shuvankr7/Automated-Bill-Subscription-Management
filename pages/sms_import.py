import streamlit as st
import json
from datetime import datetime

from models.storage import MemStorage
from ai.groq_service import GroqService
from utils.date_utils import format_currency, format_date

def show():
    """Display the SMS import page."""
    # Initialize storage and AI service
    storage = MemStorage()
    groq_service = GroqService()
    
    # Get user ID (in a real app, this would come from authentication)
    user_id = 1
    
    # Header
    st.markdown('<h1 class="main-header">SMS Import</h1>', unsafe_allow_html=True)
    
    # Introduction
    st.markdown("""
    Import bills from SMS notifications. Our AI will analyze the message content and extract bill information automatically.
    
    This feature works best with payment reminder and bill notification messages from utilities, financial services, and subscription providers.
    """)
    
    # Create tabs
    tab1, tab2 = st.tabs(["Import SMS", "Import History"])
    
    with tab1:
        # Form for SMS input
        with st.form("sms_import_form"):
            st.subheader("Enter SMS Details")
            
            # SMS details
            sender = st.text_input("Sender (e.g., Company Name or Number)", "")
            content = st.text_area("SMS Content", "", height=150)
            
            # Submit button
            submit = st.form_submit_button("Analyze SMS")
            
            if submit:
                if not sender or not content:
                    st.error("Please enter both sender and SMS content.")
                else:
                    with st.spinner("Analyzing SMS content..."):
                        # Create SMS record
                        sms_data = {
                            "sender": sender,
                            "content": content,
                            "userId": user_id,
                            "receivedAt": datetime.now(),
                            "processed": False,
                            "billId": None
                        }
                        
                        sms = storage.create_sms_message(sms_data)
                        
                        # Analyze with AI
                        bill_data = groq_service.analyze_sms_content(sender, content)
                        
                        if bill_data:
                            # Add userId
                            bill_data["userId"] = user_id
                            
                            # Create bill
                            bill = storage.create_bill(bill_data)
                            
                            if bill:
                                # Update SMS record with bill ID
                                storage.update_sms_message(sms["id"], {
                                    "processed": True,
                                    "billId": bill["id"]
                                })
                                
                                # Show success message with detected information
                                st.success("Successfully detected bill information!")
                                
                                # Display detected bill information
                                st.markdown("### Detected Bill Information")
                                
                                # Get category name
                                category = storage.get_category(bill["categoryId"])
                                category_name = category["name"] if category else "Unknown"
                                
                                # Create a card with bill details
                                st.markdown(
                                    f"""
                                    <div style="background-color: #f0f7ff; padding: 20px; border-radius: 10px; margin-top: 20px;">
                                        <h3 style="margin-top: 0;">{bill["title"]}</h3>
                                        <p><strong>Amount:</strong> {format_currency(bill["amount"])}</p>
                                        <p><strong>Due Date:</strong> {format_date(bill["dueDate"])}</p>
                                        <p><strong>Merchant:</strong> {bill["merchantName"] or "N/A"}</p>
                                        <p><strong>Category:</strong> {category_name}</p>
                                        <p><strong>Description:</strong> {bill["description"] or "N/A"}</p>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                            else:
                                st.error("Failed to create bill record.")
                        else:
                            st.warning("Could not detect bill information from this SMS. The message may not be a bill notification.")
    
    with tab2:
        # Get SMS history
        sms_messages = storage.get_sms_messages(user_id)
        
        if not sms_messages:
            st.info("No SMS import history found.")
        else:
            # Sort by receivedAt (most recent first)
            sms_messages.sort(key=lambda x: x["receivedAt"], reverse=True)
            
            st.subheader("SMS Import History")
            
            # Display each SMS
            for sms in sms_messages:
                with st.expander(f"{sms['sender']} - {sms['receivedAt'].strftime('%b %d, %Y %H:%M')}"):
                    st.markdown(f"**Content:** {sms['content']}")
                    
                    if sms["processed"] and sms["billId"]:
                        bill = storage.get_bill(sms["billId"])
                        if bill:
                            st.markdown("**Detected Bill:**")
                            st.markdown(f"- Title: {bill['title']}")
                            st.markdown(f"- Amount: {format_currency(bill['amount'])}")
                            st.markdown(f"- Due Date: {format_date(bill['dueDate'])}")
                            
                            # Add button to view full bill
                            if st.button("View Full Bill Details", key=f"view_bill_{sms['id']}"):
                                st.session_state.selected_page = "Bills"
                                st.session_state.selected_bill = bill["id"]
                                st.rerun()
                    else:
                        st.markdown("**Status:** No bill information detected")
                        
                        # Add button to retry analysis
                        if st.button("Retry Analysis", key=f"retry_{sms['id']}"):
                            with st.spinner("Analyzing SMS content..."):
                                bill_data = groq_service.analyze_sms_content(sms["sender"], sms["content"])
                                
                                if bill_data:
                                    # Add userId
                                    bill_data["userId"] = user_id
                                    
                                    # Create bill
                                    bill = storage.create_bill(bill_data)
                                    
                                    if bill:
                                        # Update SMS record with bill ID
                                        storage.update_sms_message(sms["id"], {
                                            "processed": True,
                                            "billId": bill["id"]
                                        })
                                        
                                        st.success("Successfully detected bill information!")
                                        st.rerun()
                                    else:
                                        st.error("Failed to create bill record.")
                                else:
                                    st.warning("Still could not detect bill information from this SMS.")
