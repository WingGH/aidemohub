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

