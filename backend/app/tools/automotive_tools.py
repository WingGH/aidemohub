"""Tools for Automotive Sales Agent."""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from app.data.mock_data import MockDataStore
import random


class AutomotiveTools:
    """Tools for automotive sales operations."""
    
    @staticmethod
    def search_vehicles(
        max_price: Optional[float] = None,
        brand: Optional[str] = None,
        body_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Search for vehicles matching criteria."""
        vehicles = MockDataStore.get_available_vehicles(brand)
        
        if max_price:
            vehicles = [v for v in vehicles if v["price"] <= max_price]
        
        return {
            "tool": "search_vehicles",
            "status": "success",
            "count": len(vehicles),
            "vehicles": vehicles,
            "filters_applied": {
                "max_price": max_price,
                "brand": brand,
                "body_type": body_type
            }
        }
    
    @staticmethod
    def get_vehicle_details(vehicle_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific vehicle."""
        vehicle = MockDataStore.get_vehicle_by_id(vehicle_id)
        
        if not vehicle:
            return {
                "tool": "get_vehicle_details",
                "status": "not_found",
                "message": f"Vehicle {vehicle_id} not found"
            }
        
        # Add additional details
        vehicle_details = {
            **vehicle,
            "features": ["Leather seats", "Navigation", "Backup camera", "Bluetooth"],
            "mpg": {"city": 28, "highway": 38},
            "warranty": "5 years / 60,000 miles",
            "financing_available": True
        }
        
        return {
            "tool": "get_vehicle_details",
            "status": "success",
            "vehicle": vehicle_details
        }
    
    @staticmethod
    def check_availability(vehicle_id: str) -> Dict[str, Any]:
        """Check if a vehicle is available for test drive."""
        vehicle = MockDataStore.get_vehicle_by_id(vehicle_id)
        
        if not vehicle:
            return {
                "tool": "check_availability",
                "status": "not_found",
                "available": False
            }
        
        return {
            "tool": "check_availability",
            "status": "success",
            "vehicle_id": vehicle_id,
            "available": vehicle.get("status") == "available",
            "location": "Main Showroom",
            "next_available_slot": "Today, 2:00 PM"
        }
    
    @staticmethod
    def schedule_test_drive(
        vehicle_id: str,
        customer_name: str,
        preferred_date: str = None,
        preferred_time: str = None
    ) -> Dict[str, Any]:
        """Schedule a test drive for a vehicle."""
        vehicle = MockDataStore.get_vehicle_by_id(vehicle_id)
        
        if not vehicle:
            return {
                "tool": "schedule_test_drive",
                "status": "error",
                "message": "Vehicle not found"
            }
        
        # Generate confirmation
        confirmation_id = f"TD-{random.randint(10000, 99999)}"
        scheduled_time = preferred_time or "2:00 PM"
        scheduled_date = preferred_date or (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        return {
            "tool": "schedule_test_drive",
            "status": "success",
            "confirmation_id": confirmation_id,
            "vehicle": f"{vehicle['year']} {vehicle['brand']} {vehicle['model']}",
            "customer": customer_name,
            "scheduled_date": scheduled_date,
            "scheduled_time": scheduled_time,
            "location": "Main Showroom, 123 Auto Drive",
            "notes": "Please bring valid driver's license"
        }
    
    @staticmethod
    def calculate_financing(
        vehicle_price: float,
        down_payment: float = 0,
        term_months: int = 60,
        interest_rate: float = 5.9
    ) -> Dict[str, Any]:
        """Calculate financing options for a vehicle."""
        loan_amount = vehicle_price - down_payment
        monthly_rate = interest_rate / 100 / 12
        
        if monthly_rate > 0:
            monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**term_months) / ((1 + monthly_rate)**term_months - 1)
        else:
            monthly_payment = loan_amount / term_months
        
        total_payment = monthly_payment * term_months
        total_interest = total_payment - loan_amount
        
        return {
            "tool": "calculate_financing",
            "status": "success",
            "vehicle_price": vehicle_price,
            "down_payment": down_payment,
            "loan_amount": loan_amount,
            "term_months": term_months,
            "interest_rate": interest_rate,
            "monthly_payment": round(monthly_payment, 2),
            "total_payment": round(total_payment, 2),
            "total_interest": round(total_interest, 2)
        }
    
    @staticmethod
    def book_service_appointment(
        vehicle_info: str,
        service_type: str,
        preferred_date: str = None
    ) -> Dict[str, Any]:
        """Book a service appointment."""
        confirmation_id = f"SVC-{random.randint(10000, 99999)}"
        scheduled_date = preferred_date or (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
        
        # Estimate based on service type
        estimates = {
            "oil change": {"duration": "1 hour", "cost": "$49.99"},
            "brake": {"duration": "2-3 hours", "cost": "$199-$399"},
            "tire": {"duration": "1 hour", "cost": "$89.99"},
            "general": {"duration": "1-2 hours", "cost": "TBD after inspection"}
        }
        
        service_key = "general"
        for key in estimates:
            if key in service_type.lower():
                service_key = key
                break
        
        return {
            "tool": "book_service_appointment",
            "status": "success",
            "confirmation_id": confirmation_id,
            "vehicle": vehicle_info,
            "service_type": service_type,
            "scheduled_date": scheduled_date,
            "scheduled_time": "9:00 AM",
            "estimated_duration": estimates[service_key]["duration"],
            "estimated_cost": estimates[service_key]["cost"],
            "location": "Service Center, 456 Auto Drive"
        }

