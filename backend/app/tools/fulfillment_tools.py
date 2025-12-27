"""Tools for Order Fulfillment Agent."""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from app.data.mock_data import MockDataStore
import random


class FulfillmentTools:
    """Tools for order fulfillment operations."""
    
    @staticmethod
    def receive_order(order_items: List[Dict[str, Any]], customer_id: str = None) -> Dict[str, Any]:
        """Receive and validate an incoming order."""
        order_id = f"ORD-{random.randint(10000, 99999)}"
        
        validated_items = []
        for item in order_items:
            validated_items.append({
                "sku": item.get("sku", f"SKU-{random.randint(100, 999)}"),
                "name": item.get("name", "Unknown Item"),
                "quantity": item.get("quantity", 1),
                "validated": True
            })
        
        return {
            "tool": "receive_order",
            "status": "success",
            "order_id": order_id,
            "customer_id": customer_id or "GUEST",
            "items": validated_items,
            "received_at": datetime.now().isoformat(),
            "validation": "passed"
        }
    
    @staticmethod
    def check_inventory(sku: str) -> Dict[str, Any]:
        """Check inventory levels across all warehouses."""
        inventory = MockDataStore.check_inventory(sku)
        
        total_quantity = sum(w["quantity"] for w in inventory.get("warehouses", []))
        
        return {
            "tool": "check_inventory",
            "status": "success",
            "sku": sku,
            "total_available": total_quantity,
            "warehouses": inventory.get("warehouses", []),
            "in_stock": total_quantity > 0
        }
    
    @staticmethod
    def allocate_inventory(
        sku: str, 
        quantity_needed: int,
        warehouses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Allocate inventory from warehouses."""
        allocations = []
        remaining = quantity_needed
        
        # Sort by quantity (allocate from largest stock first)
        sorted_warehouses = sorted(warehouses, key=lambda x: x.get("quantity", 0), reverse=True)
        
        for wh in sorted_warehouses:
            if remaining <= 0:
                break
            
            available = wh.get("quantity", 0)
            alloc_qty = min(remaining, available)
            
            if alloc_qty > 0:
                allocations.append({
                    "warehouse_id": wh.get("warehouse_id"),
                    "warehouse_name": wh.get("name"),
                    "quantity": alloc_qty,
                    "zone": wh.get("zone", "A1"),
                    "pick_sequence": len(allocations) + 1
                })
                remaining -= alloc_qty
        
        return {
            "tool": "allocate_inventory",
            "status": "success" if remaining == 0 else "partial",
            "sku": sku,
            "quantity_requested": quantity_needed,
            "quantity_allocated": quantity_needed - remaining,
            "quantity_backordered": remaining,
            "allocations": allocations
        }
    
    @staticmethod
    def generate_pick_list(allocations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate optimized pick list for warehouse workers."""
        pick_list_id = f"PL-{random.randint(10000, 99999)}"
        
        # Group by warehouse and sort by zone
        warehouse_picks = {}
        for alloc in allocations:
            wh_id = alloc.get("warehouse_id", "unknown")
            if wh_id not in warehouse_picks:
                warehouse_picks[wh_id] = {
                    "warehouse_name": alloc.get("warehouse_name", "Unknown"),
                    "items": []
                }
            warehouse_picks[wh_id]["items"].append({
                "sku": alloc.get("sku"),
                "quantity": alloc.get("quantity"),
                "zone": alloc.get("zone"),
                "bin_location": f"{alloc.get('zone', 'A1')}-{random.randint(1, 50):02d}"
            })
        
        # Sort items within each warehouse by zone
        for wh_id in warehouse_picks:
            warehouse_picks[wh_id]["items"].sort(key=lambda x: x["zone"])
        
        return {
            "tool": "generate_pick_list",
            "status": "success",
            "pick_list_id": pick_list_id,
            "warehouses": warehouse_picks,
            "total_items": len(allocations),
            "estimated_pick_time": f"{len(allocations) * 5} minutes"
        }
    
    @staticmethod
    def schedule_delivery(
        order_id: str,
        items: List[Dict[str, Any]],
        delivery_address: str = "Customer Address"
    ) -> Dict[str, Any]:
        """Schedule delivery for fulfilled order."""
        tracking_number = f"TRK-{random.randint(100000, 999999)}"
        
        # Calculate delivery date (1-2 business days)
        delivery_date = datetime.now() + timedelta(days=random.randint(1, 2))
        
        return {
            "tool": "schedule_delivery",
            "status": "success",
            "order_id": order_id,
            "tracking_number": tracking_number,
            "carrier": "Express Logistics",
            "delivery_date": delivery_date.strftime("%Y-%m-%d"),
            "delivery_window": "9:00 AM - 6:00 PM",
            "delivery_address": delivery_address,
            "items_count": len(items)
        }
    
    @staticmethod
    def update_order_status(order_id: str, status: str, details: str = "") -> Dict[str, Any]:
        """Update order status."""
        return {
            "tool": "update_order_status",
            "status": "success",
            "order_id": order_id,
            "new_status": status,
            "details": details,
            "updated_at": datetime.now().isoformat()
        }

