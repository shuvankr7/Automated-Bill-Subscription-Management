import datetime
import uuid
from datetime import timedelta
import pandas as pd
def get_storage():
    """Get or create the storage instance in session state"""
    if 'storage' not in st.session_state:
        st.session_state.storage = MemStorage()
    return st.session_state.storage
class MemStorage:
    """In-memory storage for bills, subscriptions, and other data."""
    
    def __init__(self):
        """Initialize the storage with empty collections."""
        self.users = {}
        self.bills = {}
        self.subscriptions = {}
        self.categories = {}
        self.reminders = {}
        self.sms_messages = {}
        self.suggestions = {}
        
        # Initialize default categories
        self.initialize_default_categories()
        
        # Add default user
        self.users[1] = {
            "id": 1,
            "username": "demo",
            "email": "demo@example.com",
            "name": "Demo User",
            "createdAt": datetime.datetime.now(),
            "settings": {
                "notifications": {
                    "email": True,
                    "push": False,
                    "sms": False
                },
                "theme": "light",
                "currency": "USD"
            }
        }
        
        # Initialize demo data
        self.initialize_demo_data()
    
    def initialize_default_categories(self):
        """Initialize default bill categories."""
        categories = [
            {"id": 1, "name": "Housing", "type": "expense", "icon": "🏠", "color": "#3498db"},
            {"id": 2, "name": "Utilities", "type": "expense", "icon": "💡", "color": "#2ecc71"},
            {"id": 3, "name": "Transportation", "type": "expense", "icon": "🚗", "color": "#e74c3c"},
            {"id": 4, "name": "Groceries", "type": "expense", "icon": "🛒", "color": "#f39c12"},
            {"id": 5, "name": "Entertainment", "type": "expense", "icon": "🎬", "color": "#9b59b6"},
            {"id": 6, "name": "Dining", "type": "expense", "icon": "🍽️", "color": "#e67e22"},
            {"id": 7, "name": "Healthcare", "type": "expense", "icon": "🏥", "color": "#1abc9c"},
            {"id": 8, "name": "Insurance", "type": "expense", "icon": "🛡️", "color": "#34495e"},
            {"id": 9, "name": "Subscriptions", "type": "expense", "icon": "📱", "color": "#8e44ad"},
            {"id": 10, "name": "Other", "type": "expense", "icon": "📌", "color": "#95a5a6"}
        ]
        
        for category in categories:
            self.categories[category["id"]] = category
    
    def initialize_demo_data(self):
        """Initialize demo data for the application."""
        # Demo bills
        bills = [
            {
                "id": 1,
                "title": "Rent",
                "amount": 1200.00,
                "dueDate": (datetime.datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
                "categoryId": 1,
                "userId": 1,
                "paid": False,
                "recurring": True,
                "description": "Monthly apartment rent",
                "createdAt": datetime.datetime.now() - timedelta(days=25),
                "merchantName": "ABC Properties",
                "autoPay": False,
                "detectedFromSms": False
            },
            {
                "id": 2,
                "title": "Electricity Bill",
                "amount": 87.50,
                "dueDate": (datetime.datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d"),
                "categoryId": 2,
                "userId": 1,
                "paid": False,
                "recurring": True,
                "description": "Monthly electricity utility bill",
                "createdAt": datetime.datetime.now() - timedelta(days=5),
                "merchantName": "Power Company",
                "autoPay": True,
                "detectedFromSms": True
            },
            {
                "id": 3,
                "title": "Car Insurance",
                "amount": 150.00,
                "dueDate": (datetime.datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
                "categoryId": 8,
                "userId": 1,
                "paid": False,
                "recurring": True,
                "description": "Quarterly car insurance premium",
                "createdAt": datetime.datetime.now() - timedelta(days=20),
                "merchantName": "SafeDrive Insurance",
                "autoPay": False,
                "detectedFromSms": False
            }
        ]
        
        for bill in bills:
            self.bills[bill["id"]] = bill
        
        # Demo subscriptions
        subscriptions = [
            {
                "id": 1,
                "title": "Netflix",
                "amount": 15.99,
                "renewalDate": (datetime.datetime.now() + timedelta(days=12)).strftime("%Y-%m-%d"),
                "frequency": "monthly",
                "categoryId": 9,
                "userId": 1,
                "active": True,
                "description": "Standard HD streaming plan",
                "createdAt": datetime.datetime.now() - timedelta(days=60),
                "merchantName": "Netflix",
                "autoPay": True,
                "lastUsed": datetime.datetime.now() - timedelta(days=2)
            },
            {
                "id": 2,
                "title": "Spotify",
                "amount": 9.99,
                "renewalDate": (datetime.datetime.now() + timedelta(days=20)).strftime("%Y-%m-%d"),
                "frequency": "monthly",
                "categoryId": 9,
                "userId": 1,
                "active": True,
                "description": "Premium music subscription",
                "createdAt": datetime.datetime.now() - timedelta(days=90),
                "merchantName": "Spotify",
                "autoPay": True,
                "lastUsed": datetime.datetime.now() - timedelta(days=1)
            },
            {
                "id": 3,
                "title": "Gym Membership",
                "amount": 50.00,
                "renewalDate": (datetime.datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
                "frequency": "monthly",
                "categoryId": 5,
                "userId": 1,
                "active": True,
                "description": "Monthly gym membership",
                "createdAt": datetime.datetime.now() - timedelta(days=120),
                "merchantName": "FitLife Gym",
                "autoPay": False,
                "lastUsed": datetime.datetime.now() - timedelta(days=30)
            }
        ]
        
        for subscription in subscriptions:
            self.subscriptions[subscription["id"]] = subscription
        
        # Demo suggestions
        suggestions = [
            {
                "id": 1,
                "type": "savings",
                "title": "Cancel unused subscription",
                "description": "You haven't used your gym membership in the last 30 days. Consider cancelling to save $50/month.",
                "userId": 1,
                "createdAt": datetime.datetime.now() - timedelta(days=1),
                "dismissed": False,
                "icon": "💡",
                "subscriptionId": 3,
                "billId": None,
                "potentialSavings": 50.00
            },
            {
                "id": 2,
                "type": "reminder",
                "title": "Overdue bill",
                "description": "Your car insurance payment is overdue by 2 days.",
                "userId": 1,
                "createdAt": datetime.datetime.now(),
                "dismissed": False,
                "icon": "⚠️",
                "subscriptionId": None,
                "billId": 3,
                "potentialSavings": None
            }
        ]
        
        for suggestion in suggestions:
            self.suggestions[suggestion["id"]] = suggestion
        
        # Demo reminders
        reminders = [
            {
                "id": 1,
                "message": "Your rent payment is due in 5 days",
                "userId": 1,
                "billId": 1,
                "subscriptionId": None,
                "reminderDate": datetime.datetime.now() + timedelta(days=2),
                "createdAt": datetime.datetime.now() - timedelta(days=3),
                "sent": False,
                "dismissed": False,
                "priority": "high"
            }
        ]
        
        for reminder in reminders:
            self.reminders[reminder["id"]] = reminder
    
    def get_user(self, user_id):
        """Get a user by ID."""
        return self.users.get(user_id)
    
    def get_bills(self, user_id):
        """Get all bills for a user."""
        return [bill for bill in self.bills.values() if bill["userId"] == user_id]
    
    def get_bill(self, bill_id):
        """Get a bill by ID."""
        return self.bills.get(bill_id)
    
    def get_upcoming_bills(self, user_id, days=7):
        """Get upcoming bills for a user within the specified days."""
        today = datetime.datetime.now().date()
        target_date = today + timedelta(days=days)
        
        upcoming = []
        for bill in self.get_bills(user_id):
            due_date = datetime.datetime.strptime(bill["dueDate"], "%Y-%m-%d").date()
            if today <= due_date <= target_date and not bill["paid"]:
                upcoming.append(bill)
        
        return sorted(upcoming, key=lambda x: x["dueDate"])
    
    def create_bill(self, bill_data):
        """Create a new bill."""
        bill_id = max(self.bills.keys() or [0]) + 1
        bill_data["id"] = bill_id
        bill_data["createdAt"] = datetime.datetime.now()
        
        self.bills[bill_id] = bill_data
        return bill_data
    
    def update_bill(self, bill_id, updates):
        """Update a bill."""
        bill = self.get_bill(bill_id)
        if bill:
            bill.update(updates)
            return bill
        return None
    
    def delete_bill(self, bill_id):
        """Delete a bill."""
        if bill_id in self.bills:
            del self.bills[bill_id]
            return True
        return False
    
    def get_subscriptions(self, user_id):
        """Get all subscriptions for a user."""
        return [sub for sub in self.subscriptions.values() if sub["userId"] == user_id]
    
    def get_subscription(self, sub_id):
        """Get a subscription by ID."""
        return self.subscriptions.get(sub_id)
    
    def get_active_subscriptions(self, user_id):
        """Get active subscriptions for a user."""
        return [sub for sub in self.get_subscriptions(user_id) if sub["active"]]
    
    def create_subscription(self, sub_data):
        """Create a new subscription."""
        sub_id = max(self.subscriptions.keys() or [0]) + 1
        sub_data["id"] = sub_id
        sub_data["createdAt"] = datetime.datetime.now()
        
        self.subscriptions[sub_id] = sub_data
        return sub_data
    
    def update_subscription(self, sub_id, updates):
        """Update a subscription."""
        subscription = self.get_subscription(sub_id)
        if subscription:
            subscription.update(updates)
            return subscription
        return None
    
    def delete_subscription(self, sub_id):
        """Delete a subscription."""
        if sub_id in self.subscriptions:
            del self.subscriptions[sub_id]
            return True
        return False
    
    def get_categories(self):
        """Get all categories."""
        return list(self.categories.values())
    
    def get_category(self, category_id):
        """Get a category by ID."""
        return self.categories.get(category_id)
    
    def get_reminders(self, user_id):
        """Get all reminders for a user."""
        return [reminder for reminder in self.reminders.values() if reminder["userId"] == user_id]
    
    def get_pending_reminders(self, user_id):
        """Get pending reminders for a user."""
        now = datetime.datetime.now()
        return [reminder for reminder in self.get_reminders(user_id) 
                if reminder["reminderDate"] <= now and not reminder["sent"] and not reminder["dismissed"]]
    
    def get_sms_messages(self, user_id):
        """Get all SMS messages for a user."""
        return [sms for sms in self.sms_messages.values() if sms["userId"] == user_id]
    
    def create_sms_message(self, sms_data):
        """Create a new SMS message."""
        sms_id = max(self.sms_messages.keys() or [0]) + 1
        sms_data["id"] = sms_id
        sms_data["createdAt"] = datetime.datetime.now()
        
        self.sms_messages[sms_id] = sms_data
        return sms_data
    
    def update_sms_message(self, sms_id, updates):
        """Update an SMS message."""
        sms = self.sms_messages.get(sms_id)
        if sms:
            sms.update(updates)
            return sms
        return None
    
    def get_suggestions(self, user_id):
        """Get all suggestions for a user."""
        return [suggestion for suggestion in self.suggestions.values() if suggestion["userId"] == user_id]
    
    def get_active_suggestions(self, user_id):
        """Get active suggestions for a user."""
        return [suggestion for suggestion in self.get_suggestions(user_id) if not suggestion["dismissed"]]
    
    def create_suggestion(self, suggestion_data):
        """Create a new suggestion."""
        suggestion_id = max(self.suggestions.keys() or [0]) + 1
        suggestion_data["id"] = suggestion_id
        suggestion_data["createdAt"] = datetime.datetime.now()
        
        self.suggestions[suggestion_id] = suggestion_data
        return suggestion_data
    
    def update_suggestion(self, suggestion_id, updates):
        """Update a suggestion."""
        suggestion = self.suggestions.get(suggestion_id)
        if suggestion:
            suggestion.update(updates)
            return suggestion
        return None
    
    def delete_suggestion(self, suggestion_id):
        """Delete a suggestion."""
        if suggestion_id in self.suggestions:
            del self.suggestions[suggestion_id]
            return True
        return False
    
    def get_stats(self, user_id):
        """Get dashboard stats for a user."""
        total_bills_this_month = 0
        total_upcoming = 0
        total_active_subscriptions = 0
        monthly_subscription_cost = 0
        potential_savings = 0
        suggestion_count = 0
        
        # Calculate bills for current month
        now = datetime.datetime.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
        
        for bill in self.get_bills(user_id):
            bill_date = datetime.datetime.strptime(bill["dueDate"], "%Y-%m-%d")
            if month_start <= bill_date <= month_end:
                total_bills_this_month += bill["amount"]
        
        # Calculate upcoming bills
        total_upcoming = len(self.get_upcoming_bills(user_id, 7))
        
        # Calculate subscription stats
        active_subscriptions = self.get_active_subscriptions(user_id)
        total_active_subscriptions = len(active_subscriptions)
        
        for sub in active_subscriptions:
            monthly_amount = sub["amount"]
            if sub["frequency"] == "yearly":
                monthly_amount = sub["amount"] / 12
            elif sub["frequency"] == "quarterly":
                monthly_amount = sub["amount"] / 3
            elif sub["frequency"] == "weekly":
                monthly_amount = sub["amount"] * 4.33  # Average weeks per month
            
            monthly_subscription_cost += monthly_amount
        
        # Calculate suggestion stats
        active_suggestions = self.get_active_suggestions(user_id)
        suggestion_count = len(active_suggestions)
        
        for suggestion in active_suggestions:
            if suggestion["potentialSavings"]:
                potential_savings += suggestion["potentialSavings"]
        
        # Calculate category breakdown
        categories = {}
        for bill in self.get_bills(user_id):
            bill_date = datetime.datetime.strptime(bill["dueDate"], "%Y-%m-%d")
            if month_start <= bill_date <= month_end:
                cat_id = bill["categoryId"]
                if cat_id not in categories:
                    category = self.get_category(cat_id)
                    categories[cat_id] = {
                        "id": cat_id,
                        "name": category["name"],
                        "amount": 0,
                        "color": category["color"]
                    }
                categories[cat_id]["amount"] += bill["amount"]
        
        for sub in active_subscriptions:
            cat_id = sub["categoryId"]
            if cat_id not in categories:
                category = self.get_category(cat_id)
                categories[cat_id] = {
                    "id": cat_id,
                    "name": category["name"],
                    "amount": 0,
                    "color": category["color"]
                }
            
            monthly_amount = sub["amount"]
            if sub["frequency"] == "yearly":
                monthly_amount = sub["amount"] / 12
            elif sub["frequency"] == "quarterly":
                monthly_amount = sub["amount"] / 3
            elif sub["frequency"] == "weekly":
                monthly_amount = sub["amount"] * 4.33
            
            categories[cat_id]["amount"] += monthly_amount
        
        # Calculate percentages
        total_spending = sum(cat["amount"] for cat in categories.values())
        category_stats = []
        
        for cat in categories.values():
            percentage = 0
            if total_spending > 0:
                percentage = (cat["amount"] / total_spending) * 100
            
            category_stats.append({
                "id": cat["id"],
                "name": cat["name"],
                "amount": cat["amount"],
                "percentage": percentage,
                "color": cat["color"]
            })
        
        # Sort by amount (highest first)
        category_stats.sort(key=lambda x: x["amount"], reverse=True)
        
        return {
            "totalBillsThisMonth": total_bills_this_month,
            "totalUpcoming": total_upcoming,
            "totalActiveSubscriptions": total_active_subscriptions,
            "monthlySubscriptionCost": monthly_subscription_cost,
            "potentialSavings": potential_savings,
            "suggestionCount": suggestion_count,
            "categories": category_stats
        }
    
    def get_forecast_data(self, user_id, months=3):
        """Get forecasted bill data for the next several months."""
        # This is a simple forecast based on current bills and subscriptions
        forecast = []
        
        # Start from current month
        now = datetime.datetime.now()
        month_start = now.replace(day=1)
        
        for i in range(months):
            forecast_month = month_start + timedelta(days=30 * i)
            month_name = forecast_month.strftime("%B")
            
            utilities = 0
            subscriptions = 0
            other = 0
            
            # Calculate recurring bills
            for bill in self.get_bills(user_id):
                if not bill["recurring"]:
                    continue
                
                if bill["categoryId"] == 2:  # Utilities
                    utilities += bill["amount"]
                elif bill["categoryId"] == 9:  # Subscriptions
                    subscriptions += bill["amount"]
                else:
                    other += bill["amount"]
            
            # Add active subscriptions
            for sub in self.get_active_subscriptions(user_id):
                monthly_amount = sub["amount"]
                if sub["frequency"] == "yearly":
                    monthly_amount = sub["amount"] / 12
                elif sub["frequency"] == "quarterly":
                    monthly_amount = sub["amount"] / 3
                elif sub["frequency"] == "weekly":
                    monthly_amount = sub["amount"] * 4.33
                
                if sub["categoryId"] == 2:  # Utilities
                    utilities += monthly_amount
                elif sub["categoryId"] == 9:  # Subscriptions
                    subscriptions += monthly_amount
                else:
                    other += monthly_amount
            
            # Apply simple growth/seasonality to utilities
            # Summer months (May-August) typically have higher utility bills
            if forecast_month.month in [5, 6, 7, 8]:
                utilities *= 1.1
            # Winter months (December-February) also typically have higher bills
            elif forecast_month.month in [12, 1, 2]:
                utilities *= 1.08
            
            # Small growth factor for subscriptions (price increases)
            subscriptions *= (1 + (0.01 * i))
            
            total = utilities + subscriptions + other
            
            forecast.append({
                "month": month_name,
                "utilities": round(utilities, 2),
                "subscriptions": round(subscriptions, 2),
                "other": round(other, 2),
                "total": round(total, 2)
            })
        
        return forecast
