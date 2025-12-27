"""Tools for Warranty Claims Agent."""
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.data.mock_data import MockDataStore
import random


class WarrantyTools:
    """Tools for warranty claim processing."""
    
    @staticmethod
    def receive_claim(
        serial_number: str,
        customer_name: str,
        issue_description: str,
        receipt_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Receive and log a new warranty claim."""
        claim_id = f"CLM-{random.randint(10000, 99999)}"
        
        return {
            "tool": "receive_claim",
            "status": "success",
            "claim_id": claim_id,
            "serial_number": serial_number,
            "customer_name": customer_name,
            "issue_description": issue_description,
            "receipt_provided": receipt_data is not None,
            "received_at": datetime.now().isoformat()
        }
    
    @staticmethod
    def extract_receipt_data(receipt_text: str) -> Dict[str, Any]:
        """Extract data from receipt text/OCR."""
        # Simulate OCR extraction
        extracted = {
            "store_name": "Electronics Mart",
            "purchase_date": "2024-06-15",
            "product_name": "Smart Air Purifier",
            "price": "$299.99",
            "payment_method": "Credit Card",
            "transaction_id": f"TXN-{random.randint(100000, 999999)}"
        }
        
        return {
            "tool": "extract_receipt_data",
            "status": "success",
            "extracted_data": extracted,
            "confidence": 0.95,
            "fields_found": len(extracted)
        }
    
    @staticmethod
    def verify_warranty(serial_number: str) -> Dict[str, Any]:
        """Verify warranty status for a product."""
        warranty_info = MockDataStore.check_warranty(serial_number)
        
        return {
            "tool": "verify_warranty",
            "status": "success",
            "serial_number": serial_number,
            "warranty_valid": warranty_info.get("valid", False),
            "product": warranty_info.get("product", "Unknown"),
            "purchase_date": warranty_info.get("purchase_date"),
            "warranty_end": warranty_info.get("warranty_end"),
            "previous_claims": warranty_info.get("previous_claims", 0),
            "coverage_type": "Full replacement" if warranty_info.get("valid") else "None"
        }
    
    @staticmethod
    def check_fraud_indicators(
        serial_number: str,
        claim_history: int,
        purchase_date: str,
        claim_date: str = None
    ) -> Dict[str, Any]:
        """Check for fraud indicators in the claim."""
        fraud_flags = []
        risk_score = 0
        
        # Check for multiple claims
        if claim_history > 0:
            fraud_flags.append({
                "indicator": "Previous claims exist",
                "severity": "medium",
                "details": f"{claim_history} previous claim(s) on this serial number"
            })
            risk_score += 30
        
        if claim_history > 2:
            fraud_flags.append({
                "indicator": "Excessive claims",
                "severity": "high",
                "details": "More than 2 claims on same product"
            })
            risk_score += 40
        
        # Check if claim is very soon after purchase
        if purchase_date:
            try:
                purchase = datetime.strptime(purchase_date, "%Y-%m-%d")
                days_since_purchase = (datetime.now() - purchase).days
                if days_since_purchase < 7:
                    fraud_flags.append({
                        "indicator": "Claim too soon after purchase",
                        "severity": "medium",
                        "details": f"Claimed within {days_since_purchase} days of purchase"
                    })
                    risk_score += 20
            except:
                pass
        
        # Determine risk level
        if risk_score >= 70:
            risk_level = "high"
        elif risk_score >= 30:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "tool": "check_fraud_indicators",
            "status": "success",
            "serial_number": serial_number,
            "fraud_flags": fraud_flags,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "recommendation": "manual_review" if risk_level == "high" else "proceed"
        }
    
    @staticmethod
    def make_decision(
        claim_id: str,
        warranty_valid: bool,
        fraud_risk: str,
        issue_description: str
    ) -> Dict[str, Any]:
        """Make final decision on warranty claim."""
        
        if not warranty_valid:
            decision = "rejected"
            reason = "Product is not under warranty"
            action = "Inform customer of out-of-warranty options"
        elif fraud_risk == "high":
            decision = "review_required"
            reason = "High fraud risk indicators detected"
            action = "Escalate to fraud investigation team"
        elif fraud_risk == "medium":
            decision = "approved_with_review"
            reason = "Claim approved pending documentation verification"
            action = "Request additional documentation from customer"
        else:
            decision = "approved"
            reason = "Valid warranty claim"
            action = "Process replacement/repair"
        
        return {
            "tool": "make_decision",
            "status": "success",
            "claim_id": claim_id,
            "decision": decision,
            "reason": reason,
            "action": action,
            "decided_at": datetime.now().isoformat(),
            "reference_number": f"REF-{random.randint(100000, 999999)}"
        }
    
    @staticmethod
    def process_approval(
        claim_id: str,
        decision: str,
        customer_email: str = None
    ) -> Dict[str, Any]:
        """Process approved claim and initiate fulfillment."""
        if decision not in ["approved", "approved_with_review"]:
            return {
                "tool": "process_approval",
                "status": "skipped",
                "reason": "Claim not approved"
            }
        
        return {
            "tool": "process_approval",
            "status": "success",
            "claim_id": claim_id,
            "fulfillment_type": "replacement",
            "shipping_label_generated": True,
            "estimated_delivery": "3-5 business days",
            "customer_notified": customer_email is not None,
            "next_steps": [
                "Customer receives prepaid return label",
                "Customer ships defective product",
                "Replacement shipped upon receipt"
            ]
        }

