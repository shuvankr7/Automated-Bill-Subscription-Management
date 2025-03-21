import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta

from models.storage import MemStorage
from utils.date_utils import format_currency, get_due_date_status, format_date

def show():
    """Display the dashboard page."""
    # Initialize storage
    storage = MemStorage()
    
    # Get user ID (in a real app, this would come from authentication)
    user_id = 1
    
    # Get dashboard stats
    stats = storage.get_stats(user_id)
    
    # Get upcoming bills
    upcoming_bills = storage.get_upcoming_bills(user_id, 7)
    
    # Get active suggestions
    suggestions = storage.get_active_suggestions(user_id)
    
    # Header
    st.markdown('<h1 class="main-header">Dashboard</h1>', unsafe_allow_html=True)
    
    # Top metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        display_summary_card(
            "This Month", 
            format_currency(stats.get("totalBillsThisMonth", 0)), 
            "💵", 
            "#1E88E5"
        )
    
    with col2:
        display_summary_card(
            "Upcoming Bills", 
            str(stats.get("totalUpcoming", 0)), 
            "📅", 
            "#43A047"
        )
    
    with col3:
        display_summary_card(
            "Subscriptions", 
            format_currency(stats.get("monthlySubscriptionCost", 0)), 
            "🔄", 
            "#8E24AA"
        )
    
    with col4:
        display_summary_card(
            "Potential Savings", 
            format_currency(stats.get("potentialSavings", 0)), 
            "💰", 
            "#FB8C00"
        )
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Upcoming bills card
        display_upcoming_bills(upcoming_bills)
        
        # Spending categories visualization
        if stats.get("categories"):
            display_spending_categories(stats["categories"])
    
    with col2:
        # Suggestions card
        display_suggestions(suggestions)
        
        # Forecast visualization
        st.markdown('<div class="card"><h3 class="card-title">🔮 Bill Forecast</h3>', unsafe_allow_html=True)
        
        # Get forecast data
        forecast_data = storage.get_forecast_data(user_id, 3)
        
        # Create a DataFrame for plotting
        df = pd.DataFrame(forecast_data)
        
        # Plot stacked bar chart
        fig = go.Figure()
        
        # Add traces for each expense category
        fig.add_trace(go.Bar(
            x=df["month"],
            y=df["subscriptions"],
            name="Subscriptions",
            marker_color="#8E24AA"
        ))
        fig.add_trace(go.Bar(
            x=df["month"],
            y=df["utilities"],
            name="Utilities",
            marker_color="#43A047"
        ))
        fig.add_trace(go.Bar(
            x=df["month"],
            y=df["other"],
            name="Other",
            marker_color="#FB8C00"
        ))
        
        # Update layout
        fig.update_layout(
            barmode="stack",
            height=300,
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            xaxis_title=None,
            yaxis_title="Amount ($)",
            template="plotly_white"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display totals
        for month in forecast_data:
            st.markdown(
                f'<div style="display: flex; justify-content: space-between; margin-bottom: 5px;">'
                f'<span>{month["month"]}</span>'
                f'<span><strong>{format_currency(month["total"])}</strong></span>'
                f'</div>',
                unsafe_allow_html=True
            )
        
        st.markdown('</div>', unsafe_allow_html=True)

def display_summary_card(title, value, icon, color):
    """Display a summary card with title, value, and icon."""
    st.markdown(
        f"""
        <div class="metric-card">
            <div style="font-size: 2rem; color: {color};">{icon}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-label">{title}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def display_upcoming_bills(bills):
    """Display upcoming bills section."""
    st.markdown('<div class="card"><h3 class="card-title">📅 Upcoming Bills</h3>', unsafe_allow_html=True)
    
    if not bills:
        st.markdown("<p>No upcoming bills for the next 7 days.</p>", unsafe_allow_html=True)
    else:
        # Create columns for the table header
        cols = st.columns([3, 2, 2, 2])
        cols[0].markdown("<strong>Bill</strong>", unsafe_allow_html=True)
        cols[1].markdown("<strong>Due Date</strong>", unsafe_allow_html=True)
        cols[2].markdown("<strong>Amount</strong>", unsafe_allow_html=True)
        cols[3].markdown("<strong>Status</strong>", unsafe_allow_html=True)
        
        st.markdown("<hr style='margin: 5px 0; opacity: 0.3;'>", unsafe_allow_html=True)
        
        # Display each bill row
        for bill in bills:
            # Get status for the bill
            status = get_due_date_status(bill["dueDate"])
            
            cols = st.columns([3, 2, 2, 2])
            cols[0].markdown(f"<strong>{bill['title']}</strong><br><small>{bill['merchantName'] or 'N/A'}</small>", unsafe_allow_html=True)
            cols[1].markdown(format_date(bill["dueDate"]), unsafe_allow_html=True)
            cols[2].markdown(format_currency(bill["amount"]), unsafe_allow_html=True)
            cols[3].markdown(
                f'<span class="status-badge {status["label"].lower().replace(" ", "-")}" '
                f'style="background-color: {status["color"]}20; color: {status["color"]};">'
                f'{status["label"]}</span>',
                unsafe_allow_html=True
            )
            
            st.markdown("<hr style='margin: 5px 0; opacity: 0.2;'>", unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_spending_categories(categories):
    """Display spending categories visualization."""
    st.markdown('<div class="card"><h3 class="card-title">📊 Spending by Category</h3>', unsafe_allow_html=True)
    
    # Create DataFrame for pie chart
    df = pd.DataFrame(categories)
    
    # Create pie chart
    fig = px.pie(
        df,
        values="amount",
        names="name",
        color_discrete_sequence=df["color"].tolist(),
        hole=0.4
    )
    
    # Update layout
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        template="plotly_white"
    )
    
    # Update traces
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display top categories
    top_categories = sorted(categories, key=lambda x: x["amount"], reverse=True)[:3]
    
    for cat in top_categories:
        st.markdown(
            f'<div style="display: flex; justify-content: space-between; margin-bottom: 5px;">'
            f'<span><span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background-color: {cat["color"]}; margin-right: 5px;"></span> {cat["name"]}</span>'
            f'<span><strong>{format_currency(cat["amount"])}</strong> ({cat["percentage"]:.1f}%)</span>'
            f'</div>',
            unsafe_allow_html=True
        )
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_suggestions(suggestions):
    """Display suggestions section."""
    st.markdown('<div class="card"><h3 class="card-title">💡 Smart Suggestions</h3>', unsafe_allow_html=True)
    
    if not suggestions:
        st.markdown("<p>No active suggestions at this time.</p>", unsafe_allow_html=True)
    else:
        for suggestion in suggestions:
            icon = suggestion.get("icon", "💡")
            
            st.markdown(
                f'<div class="suggestion-card" style="margin-bottom: 15px; padding: 10px; background-color: #f5f5f5; border-radius: 8px;">'
                f'<div style="display: flex; align-items: center; margin-bottom: 5px;">'
                f'<span style="font-size: 1.5rem; margin-right: 10px;">{icon}</span>'
                f'<span style="font-weight: 600;">{suggestion["title"]}</span>'
                f'</div>'
                f'<p style="margin: 5px 0 10px 0;">{suggestion["description"]}</p>',
                unsafe_allow_html=True
            )
            
            if suggestion.get("potentialSavings"):
                st.markdown(
                    f'<div style="display: flex; justify-content: space-between; margin-top: 5px;">'
                    f'<span style="font-size: 0.9rem;">Potential savings:</span>'
                    f'<span style="font-weight: 600; color: #43A047;">{format_currency(suggestion["potentialSavings"])}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
