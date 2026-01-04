"""Mock data store for demo purposes."""
from typing import Dict, List, Any
from datetime import datetime, timedelta
import random


class MockDataStore:
    """Centralized mock data for all use cases."""
    
    # Vehicle Inventory
    VEHICLES = [
        {"id": "V001", "brand": "Toyota", "model": "Camry", "year": 2024, "price": 35000, "color": "Silver", "status": "available"},
        {"id": "V002", "brand": "Honda", "model": "Accord", "year": 2024, "price": 38000, "color": "White", "status": "available"},
        {"id": "V003", "brand": "BMW", "model": "3 Series", "year": 2024, "price": 55000, "color": "Black", "status": "available"},
        {"id": "V004", "brand": "Mercedes", "model": "C-Class", "year": 2024, "price": 58000, "color": "Blue", "status": "reserved"},
        {"id": "V005", "brand": "Lexus", "model": "ES", "year": 2024, "price": 48000, "color": "Pearl White", "status": "available"},
    ]
    
    # Service History
    SERVICE_HISTORY = {
        "CUS001": [
            {"date": "2024-01-15", "service": "Oil Change", "cost": 150, "vehicle": "Toyota Camry"},
            {"date": "2024-03-20", "service": "Brake Inspection", "cost": 80, "vehicle": "Toyota Camry"},
        ],
        "CUS002": [
            {"date": "2024-02-10", "service": "Tire Rotation", "cost": 60, "vehicle": "Honda Accord"},
        ]
    }
    
    # Parts Inventory
    PARTS = [
        {"id": "P001", "name": "Brake Pads (Front)", "price": 120, "stock": 45, "compatible": ["Toyota", "Honda", "Lexus"]},
        {"id": "P002", "name": "Brake Pads (Rear)", "price": 100, "stock": 38, "compatible": ["Toyota", "Honda", "Lexus"]},
        {"id": "P003", "name": "Brake Fluid", "price": 25, "stock": 100, "compatible": ["all"]},
        {"id": "P004", "name": "Brake Rotors", "price": 180, "stock": 20, "compatible": ["Toyota", "Honda"]},
        {"id": "P005", "name": "Brake Sensors", "price": 65, "stock": 30, "compatible": ["BMW", "Mercedes"]},
        {"id": "P006", "name": "Oil Filter", "price": 15, "stock": 200, "compatible": ["all"]},
        {"id": "P007", "name": "Air Filter", "price": 35, "stock": 80, "compatible": ["all"]},
        {"id": "P008", "name": "Timing Belt", "price": 250, "stock": 15, "compatible": ["Toyota", "Honda"]},
    ]
    
    # Warehouse Inventory
    WAREHOUSES = {
        "WH-HK-CENTRAL": {
            "name": "Hong Kong Central Warehouse",
            "location": "Central, HK",
            "inventory": {
                "SKU001": {"name": "Organic Oat Milk 1L", "quantity": 500, "zone": "A1"},
                "SKU002": {"name": "Korean Rosé Tteokbokki", "quantity": 200, "zone": "B3"},
                "SKU003": {"name": "Premium Green Tea", "quantity": 1000, "zone": "A2"},
                "SKU004": {"name": "Imported Italian Pasta", "quantity": 300, "zone": "C1"},
            }
        },
        "WH-HK-KOWLOON": {
            "name": "Kowloon Warehouse",
            "location": "Kowloon, HK",
            "inventory": {
                "SKU001": {"name": "Organic Oat Milk 1L", "quantity": 300, "zone": "A1"},
                "SKU005": {"name": "Plant-Based Burger Patties", "quantity": 150, "zone": "F1"},
                "SKU006": {"name": "Japanese Sake 720ml", "quantity": 80, "zone": "B2"},
            }
        }
    }
    
    # Customer Profiles
    CUSTOMERS = {
        "CUS001": {
            "name": "John Wong",
            "email": "john.wong@email.com",
            "phone": "+852 9123 4567",
            "purchase_history": ["beverages", "dairy"],
            "preferences": ["organic", "imported"],
            "loyalty_tier": "Gold"
        },
        "CUS002": {
            "name": "Sarah Lee",
            "email": "sarah.lee@email.com",
            "phone": "+852 9234 5678",
            "purchase_history": ["frozen", "snacks", "beverages"],
            "preferences": ["korean", "japanese"],
            "loyalty_tier": "Platinum"
        },
        "CUS003": {
            "name": "Michael Chen",
            "email": "michael.chen@email.com",
            "phone": "+852 9345 6789",
            "purchase_history": ["automotive", "electronics"],
            "preferences": ["premium", "warranty"],
            "loyalty_tier": "Silver"
        }
    }
    
    # Warranty Records
    WARRANTY_RECORDS = {
        "SN-12345678": {
            "product": "Smart Air Purifier",
            "purchase_date": "2024-06-15",
            "warranty_end": "2026-06-15",
            "claims": []
        },
        "SN-87654321": {
            "product": "Robot Vacuum",
            "purchase_date": "2023-12-01",
            "warranty_end": "2025-12-01",
            "claims": [{"date": "2024-03-15", "reason": "Motor failure", "status": "approved"}]
        },
        "SN-11111111": {
            "product": "Electric Kettle",
            "purchase_date": "2022-01-10",
            "warranty_end": "2024-01-10",
            "claims": []
        }
    }
    
    # Compliance Documents (simulated)
    COMPLIANCE_SOPS = {
        "SOP-001": {
            "title": "Pharmaceutical Storage Guidelines",
            "version": "2.1",
            "last_updated": "2024-01-15",
            "sections": [
                "Temperature Control: 2-8°C for cold chain items",
                "Humidity Control: Max 60% RH",
                "Documentation: Batch tracking required"
            ]
        },
        "SOP-002": {
            "title": "Import Documentation Requirements",
            "version": "1.5",
            "last_updated": "2024-02-20",
            "sections": [
                "Certificate of Origin required",
                "GMP certification for all suppliers",
                "Customs declaration within 48 hours"
            ]
        }
    }
    
    # Social Trends Data (simulated)
    SOCIAL_TRENDS = [
        {"trend": "Korean Rosé Tteokbokki", "platform": "Instagram", "mentions": 15420, "growth": "+340%", "sentiment": "positive"},
        {"trend": "Oat Milk Coffee", "platform": "Instagram", "mentions": 8900, "growth": "+120%", "sentiment": "positive"},
        {"trend": "Plant-Based Meat", "platform": "Facebook", "mentions": 5600, "growth": "+85%", "sentiment": "mixed"},
        {"trend": "Japanese Whisky", "platform": "Instagram", "mentions": 4200, "growth": "+65%", "sentiment": "positive"},
        {"trend": "Matcha Desserts", "platform": "TikTok", "mentions": 12000, "growth": "+200%", "sentiment": "positive"},
    ]
    
    # Supplier Directory
    SUPPLIERS = {
        "korean": [
            {"name": "Seoul Food Co.", "products": ["Tteokbokki", "Kimchi", "Gochujang"], "contact": "info@seoulfood.kr"},
            {"name": "K-Snacks Ltd", "products": ["Korean Snacks", "Rice Cakes"], "contact": "sales@ksnacks.kr"},
        ],
        "japanese": [
            {"name": "Tokyo Imports", "products": ["Sake", "Matcha", "Miso"], "contact": "order@tokyoimports.jp"},
            {"name": "Osaka Foods", "products": ["Ramen", "Curry", "Snacks"], "contact": "hello@osakafoods.jp"},
        ],
        "organic": [
            {"name": "Green Valley Organics", "products": ["Oat Milk", "Almond Milk"], "contact": "sales@greenvalley.com"},
        ]
    }
    
    # Customer Service Call Recordings (simulated transcripts)
    CALL_RECORDINGS = [
        {
            "id": "CALL-001",
            "customer_id": "CUS001",
            "date": "2024-01-15",
            "duration": "4:32",
            "agent": "Agent Sarah",
            "topic": "Product Return",
            "transcript": [
                {"speaker": "Agent", "text": "Thank you for calling. My name is Sarah. How can I help you today?", "timestamp": "0:00"},
                {"speaker": "Customer", "text": "Hi, I received a damaged product yesterday and I want to return it. This is really frustrating.", "timestamp": "0:08"},
                {"speaker": "Agent", "text": "I'm so sorry to hear that. I completely understand your frustration. Let me help you with that right away.", "timestamp": "0:18"},
                {"speaker": "Customer", "text": "The package was completely crushed and the item inside is broken.", "timestamp": "0:28"},
                {"speaker": "Agent", "text": "That's unacceptable. I'll process a full refund and arrange a replacement to be sent today at no extra cost.", "timestamp": "0:36"},
                {"speaker": "Customer", "text": "Oh, that's great! Thank you so much for being so helpful.", "timestamp": "0:48"},
                {"speaker": "Agent", "text": "You're welcome. Is there anything else I can help you with?", "timestamp": "0:55"},
                {"speaker": "Customer", "text": "No, that's all. You've been wonderful. Thank you!", "timestamp": "1:02"}
            ],
            "sentiment_score": 0.72,
            "sentiment_journey": ["negative", "negative", "neutral", "negative", "positive", "positive", "positive", "positive"],
            "resolution": "resolved",
            "csat_score": 5
        },
        {
            "id": "CALL-002",
            "customer_id": "CUS002",
            "date": "2024-01-16",
            "duration": "6:15",
            "agent": "Agent Michael",
            "topic": "Billing Dispute",
            "transcript": [
                {"speaker": "Agent", "text": "Hello, thank you for calling. This is Michael. How may I assist you?", "timestamp": "0:00"},
                {"speaker": "Customer", "text": "I've been charged twice for my last order! This is the third time this has happened!", "timestamp": "0:10"},
                {"speaker": "Agent", "text": "I apologize for this inconvenience. Let me look into your account right away.", "timestamp": "0:22"},
                {"speaker": "Customer", "text": "I'm really fed up with this. I've been a loyal customer for 5 years!", "timestamp": "0:35"},
                {"speaker": "Agent", "text": "I completely understand, and I value your loyalty. I can see the duplicate charge. Let me process a refund immediately.", "timestamp": "0:48"},
                {"speaker": "Customer", "text": "How long will the refund take? I need that money back.", "timestamp": "1:05"},
                {"speaker": "Agent", "text": "The refund will be processed within 24 hours. I'm also adding a $20 credit to your account for the inconvenience.", "timestamp": "1:15"},
                {"speaker": "Customer", "text": "Well, I appreciate that. But please make sure this doesn't happen again.", "timestamp": "1:30"},
                {"speaker": "Agent", "text": "Absolutely. I've flagged your account and will personally follow up. You have my direct extension.", "timestamp": "1:42"}
            ],
            "sentiment_score": 0.35,
            "sentiment_journey": ["neutral", "very_negative", "neutral", "very_negative", "neutral", "negative", "positive", "neutral", "positive"],
            "resolution": "resolved",
            "csat_score": 3
        },
        {
            "id": "CALL-003",
            "customer_id": "CUS003",
            "date": "2024-01-17",
            "duration": "3:45",
            "agent": "Agent Lisa",
            "topic": "Product Inquiry",
            "transcript": [
                {"speaker": "Agent", "text": "Good morning! Thank you for calling. I'm Lisa. How can I make your day better?", "timestamp": "0:00"},
                {"speaker": "Customer", "text": "Hi Lisa! I'm interested in the new Korean snack collection. Can you tell me more about it?", "timestamp": "0:12"},
                {"speaker": "Agent", "text": "Absolutely! We have an exciting new range of authentic Korean snacks. Are you a fan of spicy or sweet flavors?", "timestamp": "0:24"},
                {"speaker": "Customer", "text": "I love spicy! What do you recommend?", "timestamp": "0:38"},
                {"speaker": "Agent", "text": "The Honey Butter Chips and Spicy Tteokbokki Snacks are our bestsellers. They're flying off the shelves!", "timestamp": "0:48"},
                {"speaker": "Customer", "text": "That sounds amazing! I'll order both. You've been super helpful!", "timestamp": "1:02"},
                {"speaker": "Agent", "text": "Thank you! I'll add a sample pack of our new Matcha cookies as a gift. Enjoy!", "timestamp": "1:12"}
            ],
            "sentiment_score": 0.92,
            "sentiment_journey": ["positive", "positive", "positive", "positive", "positive", "very_positive", "very_positive"],
            "resolution": "sale_completed",
            "csat_score": 5
        },
        {
            "id": "CALL-004",
            "customer_id": "CUS004",
            "date": "2024-01-18",
            "duration": "8:20",
            "agent": "Agent David",
            "topic": "Service Cancellation",
            "transcript": [
                {"speaker": "Agent", "text": "Thank you for calling. This is David. How can I help you today?", "timestamp": "0:00"},
                {"speaker": "Customer", "text": "I want to cancel my subscription. I'm done with this service.", "timestamp": "0:10"},
                {"speaker": "Agent", "text": "I'm sorry to hear that. May I ask what prompted this decision?", "timestamp": "0:20"},
                {"speaker": "Customer", "text": "The prices keep going up and the quality has dropped. I found a better alternative.", "timestamp": "0:32"},
                {"speaker": "Agent", "text": "I appreciate your honest feedback. We've actually just launched improved products. Would you consider staying if I offered you 30% off for 6 months?", "timestamp": "0:48"},
                {"speaker": "Customer", "text": "That's a significant discount... but I'm not sure.", "timestamp": "1:05"},
                {"speaker": "Agent", "text": "I understand. How about I also include free premium delivery? That's a $60 annual value.", "timestamp": "1:18"},
                {"speaker": "Customer", "text": "Okay, that does sound like a good deal. I'll give it another try.", "timestamp": "1:35"},
                {"speaker": "Agent", "text": "Wonderful! I'll apply the discount immediately. Welcome back!", "timestamp": "1:48"}
            ],
            "sentiment_score": 0.48,
            "sentiment_journey": ["neutral", "negative", "neutral", "negative", "neutral", "neutral", "neutral", "positive", "positive"],
            "resolution": "retention_successful",
            "csat_score": 4
        }
    ]
    
    # Customer Behavior Data for Segmentation
    CUSTOMER_BEHAVIOR = [
        {
            "customer_id": "CUS-A001",
            "name": "Alice Chan",
            "registration_date": "2022-03-15",
            "total_orders": 45,
            "total_spend": 12500,
            "avg_order_value": 277.78,
            "order_frequency_days": 8,
            "last_order_date": "2024-01-10",
            "categories_purchased": ["beverages", "organic", "imported", "snacks"],
            "favorite_brands": ["Green Valley", "Tokyo Imports"],
            "preferred_channel": "mobile_app",
            "email_open_rate": 0.65,
            "promo_sensitivity": "low",
            "returns_count": 1,
            "review_count": 12,
            "avg_rating_given": 4.5,
            "segment": "VIP",
            "predicted_ltv": 25000
        },
        {
            "customer_id": "CUS-A002",
            "name": "Bob Liu",
            "registration_date": "2023-06-20",
            "total_orders": 8,
            "total_spend": 890,
            "avg_order_value": 111.25,
            "order_frequency_days": 28,
            "last_order_date": "2024-01-05",
            "categories_purchased": ["beverages", "snacks"],
            "favorite_brands": ["K-Snacks"],
            "preferred_channel": "website",
            "email_open_rate": 0.25,
            "promo_sensitivity": "high",
            "returns_count": 0,
            "review_count": 2,
            "avg_rating_given": 4.0,
            "segment": "Regular",
            "predicted_ltv": 2500
        },
        {
            "customer_id": "CUS-A003",
            "name": "Carol Wong",
            "registration_date": "2021-11-01",
            "total_orders": 120,
            "total_spend": 45000,
            "avg_order_value": 375.00,
            "order_frequency_days": 5,
            "last_order_date": "2024-01-15",
            "categories_purchased": ["beverages", "organic", "imported", "frozen", "premium", "snacks"],
            "favorite_brands": ["Green Valley", "Tokyo Imports", "Seoul Food"],
            "preferred_channel": "mobile_app",
            "email_open_rate": 0.85,
            "promo_sensitivity": "low",
            "returns_count": 2,
            "review_count": 35,
            "avg_rating_given": 4.8,
            "segment": "Champion",
            "predicted_ltv": 85000
        },
        {
            "customer_id": "CUS-A004",
            "name": "David Ng",
            "registration_date": "2023-01-15",
            "total_orders": 3,
            "total_spend": 250,
            "avg_order_value": 83.33,
            "order_frequency_days": 90,
            "last_order_date": "2023-10-20",
            "categories_purchased": ["snacks"],
            "favorite_brands": [],
            "preferred_channel": "website",
            "email_open_rate": 0.10,
            "promo_sensitivity": "high",
            "returns_count": 1,
            "review_count": 0,
            "avg_rating_given": 0,
            "segment": "At Risk",
            "predicted_ltv": 500
        },
        {
            "customer_id": "CUS-A005",
            "name": "Emily Lam",
            "registration_date": "2023-09-01",
            "total_orders": 15,
            "total_spend": 3200,
            "avg_order_value": 213.33,
            "order_frequency_days": 12,
            "last_order_date": "2024-01-12",
            "categories_purchased": ["organic", "beverages", "imported"],
            "favorite_brands": ["Green Valley"],
            "preferred_channel": "mobile_app",
            "email_open_rate": 0.55,
            "promo_sensitivity": "medium",
            "returns_count": 0,
            "review_count": 5,
            "avg_rating_given": 4.2,
            "segment": "Growing",
            "predicted_ltv": 12000
        },
        {
            "customer_id": "CUS-A006",
            "name": "Frank Ho",
            "registration_date": "2022-07-10",
            "total_orders": 25,
            "total_spend": 4800,
            "avg_order_value": 192.00,
            "order_frequency_days": 18,
            "last_order_date": "2023-12-01",
            "categories_purchased": ["frozen", "beverages", "snacks"],
            "favorite_brands": ["Osaka Foods"],
            "preferred_channel": "website",
            "email_open_rate": 0.35,
            "promo_sensitivity": "medium",
            "returns_count": 3,
            "review_count": 8,
            "avg_rating_given": 3.5,
            "segment": "Declining",
            "predicted_ltv": 6000
        }
    ]
    
    # Segment Definitions
    CUSTOMER_SEGMENTS = {
        "Champion": {
            "description": "Best customers who buy frequently and spend the most",
            "criteria": "High frequency, high spend, high engagement",
            "recommended_actions": ["VIP perks", "Early access to new products", "Exclusive events"],
            "color": "#10B981"
        },
        "VIP": {
            "description": "Loyal customers with high lifetime value",
            "criteria": "High spend, good frequency, brand loyal",
            "recommended_actions": ["Loyalty rewards", "Personalized recommendations", "Premium support"],
            "color": "#6366F1"
        },
        "Growing": {
            "description": "Recent customers showing promise",
            "criteria": "Increasing order frequency, good engagement",
            "recommended_actions": ["Nurture campaigns", "Cross-sell opportunities", "Referral programs"],
            "color": "#3B82F6"
        },
        "Regular": {
            "description": "Average customers with steady behavior",
            "criteria": "Moderate frequency and spend",
            "recommended_actions": ["Engagement campaigns", "Bundle offers", "Category expansion"],
            "color": "#8B5CF6"
        },
        "At Risk": {
            "description": "Previously active but declining engagement",
            "criteria": "Decreasing frequency, long since last order",
            "recommended_actions": ["Win-back campaigns", "Special offers", "Feedback surveys"],
            "color": "#F59E0B"
        },
        "Declining": {
            "description": "Customers showing signs of churn",
            "criteria": "Reduced spend, low engagement",
            "recommended_actions": ["Retention offers", "Personal outreach", "Exit surveys"],
            "color": "#EF4444"
        }
    }
    
    @classmethod
    def get_vehicle_by_id(cls, vehicle_id: str) -> Dict[str, Any]:
        """Get vehicle by ID."""
        for v in cls.VEHICLES:
            if v["id"] == vehicle_id:
                return v
        return {}
    
    @classmethod
    def get_available_vehicles(cls, brand: str = None) -> List[Dict[str, Any]]:
        """Get available vehicles, optionally filtered by brand."""
        vehicles = [v for v in cls.VEHICLES if v["status"] == "available"]
        if brand:
            vehicles = [v for v in vehicles if v["brand"].lower() == brand.lower()]
        return vehicles
    
    @classmethod
    def get_parts_for_service(cls, service_type: str) -> List[Dict[str, Any]]:
        """Get related parts for a service type."""
        if "brake" in service_type.lower():
            return [p for p in cls.PARTS if "brake" in p["name"].lower()]
        return cls.PARTS[:3]
    
    @classmethod
    def check_warranty(cls, serial_number: str) -> Dict[str, Any]:
        """Check warranty status for a serial number."""
        record = cls.WARRANTY_RECORDS.get(serial_number)
        if not record:
            return {"valid": False, "message": "Serial number not found"}
        
        warranty_end = datetime.strptime(record["warranty_end"], "%Y-%m-%d")
        is_valid = warranty_end > datetime.now()
        
        return {
            "valid": is_valid,
            "product": record["product"],
            "purchase_date": record["purchase_date"],
            "warranty_end": record["warranty_end"],
            "previous_claims": len(record["claims"])
        }
    
    @classmethod
    def get_trending_items(cls, limit: int = 5) -> List[Dict[str, Any]]:
        """Get trending items from social data."""
        return sorted(cls.SOCIAL_TRENDS, key=lambda x: x["mentions"], reverse=True)[:limit]
    
    @classmethod
    def find_suppliers(cls, category: str) -> List[Dict[str, Any]]:
        """Find suppliers by category."""
        return cls.SUPPLIERS.get(category.lower(), [])
    
    @classmethod
    def check_inventory(cls, sku: str) -> Dict[str, Any]:
        """Check inventory across all warehouses."""
        result = {"sku": sku, "warehouses": []}
        for wh_id, wh_data in cls.WAREHOUSES.items():
            if sku in wh_data["inventory"]:
                item = wh_data["inventory"][sku]
                result["warehouses"].append({
                    "warehouse_id": wh_id,
                    "name": wh_data["name"],
                    "quantity": item["quantity"],
                    "zone": item["zone"]
                })
        return result
    
    @classmethod
    def get_cross_sell_recommendations(cls, current_purchases: List[str], customer_id: str = None) -> List[Dict[str, Any]]:
        """Get cross-sell recommendations based on purchase history."""
        recommendations = []
        
        if "beverages" in current_purchases and "dairy" not in current_purchases:
            recommendations.append({
                "category": "dairy",
                "items": ["Organic Oat Milk", "Almond Milk Creamer"],
                "reason": "Customers who buy beverages often add dairy alternatives"
            })
        
        if "frozen" not in current_purchases:
            recommendations.append({
                "category": "frozen",
                "items": ["Plant-Based Burger Patties", "Frozen Dumplings"],
                "reason": "Popular frozen items with high margin"
            })
        
        return recommendations
    
    @classmethod
    def get_call_recordings(cls, call_id: str = None) -> List[Dict[str, Any]]:
        """Get call recordings, optionally filtered by ID."""
        if call_id:
            for call in cls.CALL_RECORDINGS:
                if call["id"] == call_id:
                    return [call]
            return []
        return cls.CALL_RECORDINGS
    
    @classmethod
    def get_customer_behavior(cls, customer_id: str = None, segment: str = None) -> List[Dict[str, Any]]:
        """Get customer behavior data, optionally filtered."""
        customers = cls.CUSTOMER_BEHAVIOR
        if customer_id:
            customers = [c for c in customers if c["customer_id"] == customer_id]
        if segment:
            customers = [c for c in customers if c["segment"].lower() == segment.lower()]
        return customers
    
    @classmethod
    def get_segment_info(cls, segment_name: str = None) -> Dict[str, Any]:
        """Get segment definitions."""
        if segment_name:
            return cls.CUSTOMER_SEGMENTS.get(segment_name, {})
        return cls.CUSTOMER_SEGMENTS
    
    @classmethod
    def get_all_sample_data(cls) -> Dict[str, Any]:
        """Get all sample data for display."""
        return {
            "vehicles": cls.VEHICLES,
            "warehouses": cls.WAREHOUSES,
            "customers": cls.CUSTOMERS,
            "warranty_records": cls.WARRANTY_RECORDS,
            "compliance_sops": cls.COMPLIANCE_SOPS,
            "social_trends": cls.SOCIAL_TRENDS,
            "suppliers": cls.SUPPLIERS,
            "parts": cls.PARTS,
            "call_recordings": cls.CALL_RECORDINGS,
            "customer_behavior": cls.CUSTOMER_BEHAVIOR,
            "customer_segments": cls.CUSTOMER_SEGMENTS
        }

