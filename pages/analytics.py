import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

from models.storage import MemStorage
from utils.date_utils import format_currency

def show():
    storage = get_storage()

    
    # Get user ID (in a real app, this would come from authentication)
    user_id = 1
    
    # Get data
    bills = storage.get_bills(user_id)
    subscriptions = storage.get_subscriptions(user_id)
    
    # Header
    st.markdown('<h1 class="main-header">Analytics</h1>', unsafe_allow_html=True)
    
    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Date Range")
        range_option = st.radio(
            "Select range",
            ["Last 3 months", "Last 6 months", "Last year", "Custom"]
        )
    
    with col2:
        st.subheader(" ")  # Empty header for alignment
        
        if range_option == "Last 3 months":
            end_date = datetime.now().date()
            start_date = end_date.replace(month=end_date.month - 3) if end_date.month > 3 else end_date.replace(year=end_date.year - 1, month=end_date.month + 9)
        elif range_option == "Last 6 months":
            end_date = datetime.now().date()
            start_date = end_date.replace(month=end_date.month - 6) if end_date.month > 6 else end_date.replace(year=end_date.year - 1, month=end_date.month + 6)
        elif range_option == "Last year":
            end_date = datetime.now().date()
            start_date = end_date.replace(year=end_date.year - 1)
        else:  # Custom
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start date", datetime.now().date() - timedelta(days=90))
            with col2:
                end_date = st.date_input("End date", datetime.now().date())
    
    # Filtert data based on date range
    def is_in_date_range(date_str):
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        return start_date <= date_obj <= end_date
    
    filtered_bills = [bill for bill in bills if is_in_date_range(bill["dueDate"])]
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Spending Overview", "Category Breakdown", "Forecast"])
    
    with tab1:
        show_spending_overview(filtered_bills, subscriptions, start_date, end_date)
    
    with tab2:
        show_category_breakdown(filtered_bills, subscriptions)
    
    with tab3:
        show_forecast(user_id)

def show_spending_overview(bills, subscriptions, start_date, end_date):
    """Show spending overview tab."""
    st.subheader("Monthly Spending Overview")
    
    # Prepare data for monthly overview
    months = []
    current_date = start_date
    while current_date <= end_date:
        months.append(current_date.strftime("%Y-%m"))
        # Increment month
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
    
    # Function to get month key from date string
    def get_month_key(date_str):
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%Y-%m")
    
    # Prepare data for chart
    monthly_data = {month: {"bills": 0, "subscriptions": 0} for month in months}
    
    # Add bills
    for bill in bills:
        month_key = get_month_key(bill["dueDate"])
        if month_key in monthly_data:
            monthly_data[month_key]["bills"] += bill["amount"]
    
    # Add subscriptions (simplified approach)
    active_subs = [sub for sub in subscriptions if sub["active"]]
    for month in months:
        for sub in active_subs:
            monthly_amount = sub["amount"]
            if sub["frequency"] == "yearly":
                monthly_amount = sub["amount"] / 12
            elif sub["frequency"] == "quarterly":
                monthly_amount = sub["amount"] / 3
            elif sub["frequency"] == "weekly":
                monthly_amount = sub["amount"] * 4.33  # Average weeks per month
            
            monthly_data[month]["subscriptions"] += monthly_amount
    
    # Convert to DataFrame for charting
    chart_data = []
    for month, values in monthly_data.items():
        month_date = datetime.strptime(month, "%Y-%m")
        month_name = month_date.strftime("%b %Y")
        
        chart_data.append({
            "month": month_name,
            "bills": values["bills"],
            "subscriptions": values["subscriptions"],
            "total": values["bills"] + values["subscriptions"]
        })
    
    df = pd.DataFrame(chart_data)
    
    # Create stacked bar chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df["month"],
        y=df["bills"],
        name="Bills",
        marker_color="#1E88E5"
    ))
    
    fig.add_trace(go.Bar(
        x=df["month"],
        y=df["subscriptions"],
        name="Subscriptions",
        marker_color="#8E24AA"
    ))
    
    # Add total line
    fig.add_trace(go.Scatter(
        x=df["month"],
        y=df["total"],
        mode="lines+markers",
        name="Total",
        line=dict(color="#FB8C00", width=3),
        marker=dict(size=8)
    ))
    
    # Update layout
    fig.update_layout(
        barmode="stack",
        height=400,
        hovermode="x unified",
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
    
    # Display statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_spending = df["total"].sum()
        st.metric("Total Spending", format_currency(total_spending))
    
    with col2:
        avg_monthly = total_spending / len(df) if len(df) > 0 else 0
        st.metric("Average Monthly", format_currency(avg_monthly))
    
    with col3:
        highest_month = df.loc[df["total"].idxmax()]["month"] if not df.empty else "N/A"
        highest_amount = df["total"].max() if not df.empty else 0
        st.metric("Highest Month", f"{highest_month} ({format_currency(highest_amount)})")

def show_category_breakdown(bills, subscriptions):
    """Show category breakdown tab."""
    st.subheader("Spending by Category")
    
    # Initialize storage to get categories
    storage = get_storage()

    categories = {cat["id"]: cat for cat in storage.get_categories()}
    
    # Prepare category data
    category_totals = {}
    
    # Add bills
    for bill in bills:
        cat_id = bill["categoryId"]
        if cat_id not in category_totals:
            category_totals[cat_id] = 0
        category_totals[cat_id] += bill["amount"]
    
    # Add subscriptions (with monthly normalization)
    for sub in subscriptions:
        if not sub["active"]:
            continue
        
        cat_id = sub["categoryId"]
        if cat_id not in category_totals:
            category_totals[cat_id] = 0
        
        monthly_amount = sub["amount"]
        if sub["frequency"] == "yearly":
            monthly_amount = sub["amount"] / 12
        elif sub["frequency"] == "quarterly":
            monthly_amount = sub["amount"] / 3
        elif sub["frequency"] == "weekly":
            monthly_amount = sub["amount"] * 4.33  # Average weeks per month
        
        category_totals[cat_id] += monthly_amount
    
    # Create DataFrame for pie chart
    if category_totals:
        chart_data = []
        for cat_id, amount in category_totals.items():
            if cat_id in categories:
                chart_data.append({
                    "name": categories[cat_id]["name"],
                    "value": amount,
                    "color": categories[cat_id]["color"]
                })
        
        df = pd.DataFrame(chart_data)
        
        # Calculate total and percentages
        total = df["value"].sum()
        df["percentage"] = (df["value"] / total * 100).round(1)
        
        # Sort by value (descending)
        df = df.sort_values("value", ascending=False)
        
        # Create pie chart
        fig = px.pie(
            df,
            values="value",
            names="name",
            color_discrete_sequence=df["color"].tolist(),
            hole=0.4
        )
        
        # Update layout
        fig.update_layout(
            height=400,
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
        
        # Display pie chart
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Category Breakdown")
            
            # Display each category with amount and percentage
            for _, row in df.iterrows():
                st.markdown(
                    f'<div style="display: flex; justify-content: space-between; margin-bottom: 10px;">'
                    f'<span><span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background-color: {row["color"]}; margin-right: 5px;"></span> {row["name"]}</span>'
                    f'<span><strong>{format_currency(row["value"])}</strong> ({row["percentage"]}%)</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            
            st.markdown(f"<strong>Total:</strong> {format_currency(total)}", unsafe_allow_html=True)
    else:
        st.info("No spending data available for the selected period.")

def show_forecast(user_id):
    """Show forecast tab."""
    st.subheader("Bill Forecast")
    
    # Initialize storage
    storage = get_storage()

    
    # Get forecast data
    forecast_data = storage.get_forecast_data(user_id, 3)
    
    if forecast_data:
        # Create DataFrame for the chart
        df = pd.DataFrame(forecast_data)
        
        # Create stacked bar chart
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
        
        # Add total line
        fig.add_trace(go.Scatter(
            x=df["month"],
            y=df["total"],
            mode="lines+markers",
            name="Total",
            line=dict(color="#1E88E5", width=3),
            marker=dict(size=8)
        ))
        
        # Update layout
        fig.update_layout(
            barmode="stack",
            height=400,
            hovermode="x unified",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            xaxis_title=None,
            yaxis_title="Projected Amount ($)",
            template="plotly_white"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display forecast details in a table
        st.markdown("### Forecast Details")
        
        # Create a styled table
        table_html = '<table style="width:100%; border-collapse: collapse;">'
        
        # Header row
        table_html += '''
        <tr style="border-bottom: 1px solid #ddd;">
            <th style="text-align: left; padding: 8px;">Month</th>
            <th style="text-align: right; padding: 8px;">Subscriptions</th>
            <th style="text-align: right; padding: 8px;">Utilities</th>
            <th style="text-align: right; padding: 8px;">Other</th>
            <th style="text-align: right; padding: 8px; font-weight: bold;">Total</th>
        </tr>
        '''
        
        # Data rows
        for _, row in df.iterrows():
            table_html += f'''
            <tr style="border-bottom: 1px solid #ddd;">
                <td style="text-align: left; padding: 8px;">{row["month"]}</td>
                <td style="text-align: right; padding: 8px;">{format_currency(row["subscriptions"])}</td>
                <td style="text-align: right; padding: 8px;">{format_currency(row["utilities"])}</td>
                <td style="text-align: right; padding: 8px;">{format_currency(row["other"])}</td>
                <td style="text-align: right; padding: 8px; font-weight: bold;">{format_currency(row["total"])}</td>
            </tr>
            '''
        
        # Close table
        table_html += '</table>'
        
        st.markdown(table_html, unsafe_allow_html=True)
        
        # Add insights
        st.markdown("### Insights")
        
        # Calculate some basic insights
        avg_total = df["total"].mean()
        max_month = df.loc[df["total"].idxmax()]
        min_month = df.loc[df["total"].idxmin()]
        month_diff = (df["total"].max() - df["total"].min()) / df["total"].min() * 100 if df["total"].min() > 0 else 0
        
        st.markdown(f"- Average monthly expenses: **{format_currency(avg_total)}**")
        st.markdown(f"- Highest spending month: **{max_month['month']}** with **{format_currency(max_month['total'])}**")
        st.markdown(f"- Lowest spending month: **{min_month['month']}** with **{format_currency(min_month['total'])}**")
        st.markdown(f"- Month-to-month variation: **{month_diff:.1f}%**")
        
        if df["subscriptions"].mean() > df["utilities"].mean():
            st.markdown("- **Subscription costs** make up the largest portion of your monthly expenses")
        else:
            st.markdown("- **Utility bills** make up the largest portion of your monthly expenses")
    else:
        st.info("No forecast data available.")
