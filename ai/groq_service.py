import os
import json
import groq
from datetime import datetime

class GroqService:
    """Service class for Groq API interaction."""
    
    def __init__(self):
        """Initialize the Groq client."""
        api_key = os.getenv("GROQ_API_KEY")
        self.client = groq.Client(api_key=api_key)
        self.model = "llama3-70b-8192"  # Default model
    
    def send_request(self, messages):
        """Send a request to the Groq API."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.5,
                max_tokens=1024,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error sending request to Groq API: {e}")
            return None
    
    def analyze_sms_content(self, sender, content):
        """Analyze SMS content to extract bill information."""
        messages = [
            {
                "role": "system",
                "content": """You are an AI assistant that extracts bill information from SMS messages.
                Extract the following details if present:
                - Bill type or name (e.g. electricity, water, credit card)
                - Amount due
                - Due date
                - Merchant or company name
                
                Return ONLY a JSON object with these fields:
                {
                    "title": "Bill name",
                    "amount": 123.45,
                    "dueDate": "YYYY-MM-DD",
                    "merchantName": "Company name",
                    "description": "Brief description of the bill",
                    "categoryId": null
                }
                
                If you can't extract all fields, use null for missing fields.
                If the SMS doesn't appear to be a bill notification, return {"isBill": false}.
                """
            },
            {
                "role": "user",
                "content": f"Sender: {sender}\nMessage: {content}"
            }
        ]
        
        response = self.send_request(messages)
        if response:
            try:
                bill_data = json.loads(response)
                
                # If it's not a bill, return None
                if "isBill" in bill_data and not bill_data["isBill"]:
                    return None
                
                # Determine category ID based on bill title or description
                if bill_data.get("categoryId") is None:
                    bill_data["categoryId"] = self._determine_category(bill_data)
                
                # Set additional fields
                bill_data["paid"] = False
                bill_data["recurring"] = True
                bill_data["detectedFromSms"] = True
                bill_data["autoPay"] = False
                
                return bill_data
            except json.JSONDecodeError:
                print("Failed to parse JSON response from Groq API")
                return None
        
        return None
    
    def _determine_category(self, bill_data):
        """Determine the category ID based on bill information."""
        title = bill_data.get("title", "").lower()
        merchant = bill_data.get("merchantName", "").lower()
        description = bill_data.get("description", "").lower()
        
        # Combined text for keyword matching
        text = f"{title} {merchant} {description}"
        
        # Category mapping
        category_keywords = {
            1: ["rent", "mortgage", "housing", "apartment", "home"],
            2: ["utility", "electric", "water", "gas", "power", "energy", "internet", "wifi", "broadband"],
            3: ["car", "auto", "vehicle", "transportation", "fuel", "gas", "petrol", "diesel", "parking"],
            4: ["grocery", "food", "supermarket", "market"],
            5: ["entertainment", "movie", "theater", "game", "subscription"],
            6: ["restaurant", "dining", "cafe", "food delivery"],
            7: ["health", "medical", "doctor", "hospital", "clinic", "pharmacy", "prescription"],
            8: ["insurance", "coverage", "policy", "protection", "premium"],
            9: ["subscription", "membership", "streaming", "netflix", "spotify", "amazon prime"],
            10: []  # Other (default)
        }
        
        # Check for keyword matches
        for category_id, keywords in category_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return category_id
        
        # Default to Other
        return 10
    
    def generate_bill_suggestions(self, user_data):
        """Generate bill management suggestions based on user data."""
        messages = [
            {
                "role": "system",
                "content": """You are an AI assistant that analyzes user spending data and generates
                actionable bill management suggestions. Generate 2-3 suggestions in JSON format:
                [
                    {
                        "type": "savings" or "reminder" or "optimization",
                        "title": "Short title",
                        "description": "Detailed suggestion",
                        "icon": "emoji icon for the suggestion",
                        "billId": ID of related bill or null,
                        "subscriptionId": ID of related subscription or null,
                        "potentialSavings": estimated savings amount or null
                    }
                ]
                """
            },
            {
                "role": "user",
                "content": json.dumps(user_data)
            }
        ]
        
        response = self.send_request(messages)
        if response:
            try:
                suggestions = json.loads(response)
                return suggestions
            except json.JSONDecodeError:
                print("Failed to parse JSON response from Groq API")
                return []
        
        return []
    
    def forecast_bills(self, historical_bills, months=3):
        """Generate a forecast of future bills based on historical data."""
        messages = [
            {
                "role": "system",
                "content": f"""You are an AI assistant that forecasts future bill payments based on historical data.
                Generate a forecast for the next {months} months, considering seasonality and trends.
                Return ONLY a JSON array of objects with these fields:
                [
                    {{
                        "month": "Month name",
                        "subscriptions": 123.45,
                        "utilities": 123.45,
                        "other": 123.45,
                        "total": 123.45
                    }}
                ]
                """
            },
            {
                "role": "user",
                "content": json.dumps(historical_bills)
            }
        ]
        
        response = self.send_request(messages)
        if response:
            try:
                forecast = json.loads(response)
                return forecast
            except json.JSONDecodeError:
                print("Failed to parse JSON response from Groq API")
                return []
        
        return []
