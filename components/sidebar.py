import streamlit as st

def render_sidebar():
    """Renders the sidebar navigation and returns the selected page."""
    # Add logo/title to sidebar
    st.sidebar.title("BillTracker AI")
    st.sidebar.markdown("---")
    
    # Navigation
    st.sidebar.markdown("### Navigation")
    
    # Create navigation buttons with icons
    pages = {
        "Dashboard": "📊",
        "Bills": "💵",
        "Subscriptions": "🔄",
        "Analytics": "📈",
        "SMS Import": "📱",
        "Settings": "⚙️"
    }
    
    # Store current page selection in session state
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Dashboard"
    
    # Create sidebar navigation
    for page, icon in pages.items():
        if st.sidebar.button(f"{icon} {page}", 
                           key=f"nav_{page}", 
                           use_container_width=True,
                           type="primary" if st.session_state.current_page == page else "secondary"):
            st.session_state.current_page = page
    
    # Display a version number and other info
    st.sidebar.markdown("---")
    st.sidebar.caption("© 2023 BillTracker AI")
    st.sidebar.caption("Version 1.0.0")
    
    return st.session_state.current_page
