"""Drug Information & Compliance Agent - Search drug info, stock, and compliance details."""
from typing import Dict, Any, List, Optional, AsyncGenerator
from langgraph.graph import StateGraph, END
from app.agents.base_agent import BaseAgent, AgentState, get_llm_service
import json
import asyncio


# Drug catalog with detailed information
DRUG_CATALOG = {
    "CARD-001": {
        "name": "Cardiomax 100mg",
        "generic_name": "Amlodipine Besylate",
        "category": "Cardiovascular",
        "indication": "Hypertension, Angina Pectoris",
        "dosage": "5-10mg once daily",
        "price_per_unit": 250,
        "pack_size": 30,
        "manufacturer": "PharmaCare Global",
        "stock": 5000,
        "warehouse_location": "Cold Storage A-12",
        "expiry_date": "2027-06-30",
        "prescription_required": True,
        "controlled": False,
        "storage": "Store below 25°C, protect from light",
        "contraindications": "Hypersensitivity to dihydropyridines, severe aortic stenosis",
        "side_effects": "Edema, headache, dizziness, flushing",
        "drug_interactions": "CYP3A4 inhibitors may increase levels"
    },
    "CARD-002": {
        "name": "Cardiomax Plus 200mg",
        "generic_name": "Amlodipine/Valsartan",
        "category": "Cardiovascular",
        "indication": "Hypertension (combination therapy)",
        "dosage": "One tablet once daily",
        "price_per_unit": 500,
        "pack_size": 30,
        "manufacturer": "PharmaCare Global",
        "stock": 2500,
        "warehouse_location": "Cold Storage A-12",
        "expiry_date": "2027-08-15",
        "prescription_required": True,
        "controlled": False,
        "storage": "Store below 25°C",
        "contraindications": "Pregnancy, bilateral renal artery stenosis",
        "side_effects": "Dizziness, hypotension, hyperkalemia",
        "drug_interactions": "NSAIDs may reduce efficacy"
    },
    "LIPID-001": {
        "name": "Lipidol 20mg",
        "generic_name": "Atorvastatin Calcium",
        "category": "Cardiovascular",
        "indication": "Hyperlipidemia, Prevention of cardiovascular events",
        "dosage": "10-80mg once daily",
        "price_per_unit": 120,
        "pack_size": 30,
        "manufacturer": "PharmaCare Global",
        "stock": 8000,
        "warehouse_location": "Standard Storage B-05",
        "expiry_date": "2027-12-31",
        "prescription_required": True,
        "controlled": False,
        "storage": "Store below 30°C",
        "contraindications": "Active liver disease, pregnancy, breastfeeding",
        "side_effects": "Myalgia, elevated liver enzymes, GI upset",
        "drug_interactions": "CYP3A4 inhibitors, grapefruit juice"
    },
    "DIAB-001": {
        "name": "Diabetix 500mg",
        "generic_name": "Metformin Hydrochloride",
        "category": "Diabetes",
        "indication": "Type 2 Diabetes Mellitus",
        "dosage": "500-2000mg daily in divided doses",
        "price_per_unit": 140,
        "pack_size": 60,
        "manufacturer": "GlucoPharm Ltd",
        "stock": 12000,
        "warehouse_location": "Standard Storage B-08",
        "expiry_date": "2027-09-30",
        "prescription_required": True,
        "controlled": False,
        "storage": "Store below 25°C",
        "contraindications": "Renal impairment, metabolic acidosis, contrast dye procedures",
        "side_effects": "GI upset, lactic acidosis (rare), vitamin B12 deficiency",
        "drug_interactions": "Iodinated contrast, alcohol"
    },
    "DIAB-002": {
        "name": "Diabetix Premium 1000mg",
        "generic_name": "Metformin XR/Sitagliptin",
        "category": "Diabetes",
        "indication": "Type 2 Diabetes (combination therapy)",
        "dosage": "One tablet once daily with evening meal",
        "price_per_unit": 500,
        "pack_size": 30,
        "manufacturer": "GlucoPharm Ltd",
        "stock": 3000,
        "warehouse_location": "Standard Storage B-08",
        "expiry_date": "2027-07-15",
        "prescription_required": True,
        "controlled": False,
        "storage": "Store below 30°C",
        "contraindications": "Type 1 diabetes, DKA, severe renal impairment",
        "side_effects": "Hypoglycemia, nasopharyngitis, headache",
        "drug_interactions": "Other hypoglycemic agents"
    },
    "ONCO-001": {
        "name": "Oncotab 50mg",
        "generic_name": "Capecitabine",
        "category": "Oncology",
        "indication": "Colorectal cancer, Breast cancer",
        "dosage": "1250mg/m² twice daily for 14 days, 7 days rest",
        "price_per_unit": 900,
        "pack_size": 120,
        "manufacturer": "OncoMed Sciences",
        "stock": 800,
        "warehouse_location": "Restricted Storage R-01",
        "expiry_date": "2026-12-31",
        "prescription_required": True,
        "controlled": True,
        "storage": "Store below 30°C",
        "contraindications": "DPD deficiency, severe renal impairment, pregnancy",
        "side_effects": "Hand-foot syndrome, diarrhea, nausea, neutropenia",
        "drug_interactions": "Warfarin, phenytoin, allopurinol"
    },
    "ONCO-002": {
        "name": "Oncotab Premium 100mg",
        "generic_name": "Capecitabine/Bevacizumab combo",
        "category": "Oncology",
        "indication": "Metastatic colorectal cancer",
        "dosage": "As per oncologist protocol",
        "price_per_unit": 2000,
        "pack_size": 60,
        "manufacturer": "OncoMed Sciences",
        "stock": 300,
        "warehouse_location": "Restricted Storage R-01",
        "expiry_date": "2026-09-30",
        "prescription_required": True,
        "controlled": True,
        "storage": "2-8°C Cold chain required",
        "contraindications": "Uncontrolled hypertension, recent surgery, GI perforation history",
        "side_effects": "Hypertension, proteinuria, bleeding, delayed wound healing",
        "drug_interactions": "Anthracyclines, taxanes"
    },
    "ANTI-001": {
        "name": "Antibiox 500mg",
        "generic_name": "Amoxicillin/Clavulanate",
        "category": "Antibiotics",
        "indication": "Bacterial infections (respiratory, urinary, skin)",
        "dosage": "One tablet every 8 hours",
        "price_per_unit": 60,
        "pack_size": 21,
        "manufacturer": "BioAnti Pharma",
        "stock": 15000,
        "warehouse_location": "Standard Storage C-03",
        "expiry_date": "2026-11-30",
        "prescription_required": True,
        "controlled": False,
        "storage": "Store below 25°C",
        "contraindications": "Penicillin allergy, history of cholestatic jaundice",
        "side_effects": "Diarrhea, nausea, skin rash, hepatic dysfunction",
        "drug_interactions": "Methotrexate, warfarin"
    },
    "PAIN-001": {
        "name": "Painex 400mg",
        "generic_name": "Ibuprofen",
        "category": "Pain Management",
        "indication": "Pain, inflammation, fever",
        "dosage": "200-400mg every 4-6 hours as needed",
        "price_per_unit": 45,
        "pack_size": 50,
        "manufacturer": "PainRelief Inc",
        "stock": 20000,
        "warehouse_location": "Standard Storage C-10",
        "expiry_date": "2027-03-31",
        "prescription_required": False,
        "controlled": False,
        "storage": "Store below 30°C",
        "contraindications": "GI ulcers, severe renal impairment, third trimester pregnancy",
        "side_effects": "GI upset, dizziness, renal impairment with prolonged use",
        "drug_interactions": "Anticoagulants, lithium, ACE inhibitors"
    },
    "IMMU-001": {
        "name": "Immunoboost 250mg",
        "generic_name": "Adalimumab Biosimilar",
        "category": "Immunology",
        "indication": "Rheumatoid arthritis, Psoriasis, Crohn's disease",
        "dosage": "40mg every two weeks subcutaneously",
        "price_per_unit": 400,
        "pack_size": 2,
        "manufacturer": "BioImmune Labs",
        "stock": 500,
        "warehouse_location": "Cold Storage A-05",
        "expiry_date": "2026-08-31",
        "prescription_required": True,
        "controlled": True,
        "storage": "2-8°C Cold chain required, protect from light",
        "contraindications": "Active TB, severe infections, heart failure",
        "side_effects": "Injection site reactions, increased infection risk, malignancy risk",
        "drug_interactions": "Live vaccines, other biologics"
    }
}

# Compliance information
COMPLIANCE_INFO = {
    "controlled_substances": {
        "description": "Controlled drugs require special handling and documentation",
        "requirements": [
            "Dual signature for dispensing",
            "Separate locked storage",
            "Daily inventory reconciliation",
            "Register maintained for 5 years",
            "Reporting to Department of Health monthly"
        ],
        "affected_products": ["ONCO-001", "ONCO-002", "IMMU-001"]
    },
    "cold_chain": {
        "description": "Cold chain products require temperature-controlled logistics",
        "requirements": [
            "Maintain 2-8°C throughout transport",
            "Temperature monitoring devices required",
            "Maximum 2 hours out of cold storage",
            "Thermal packaging for delivery",
            "Temperature excursion reporting"
        ],
        "affected_products": ["CARD-001", "CARD-002", "ONCO-002", "IMMU-001"]
    },
    "prescription_only": {
        "description": "Prescription-only medicines (POM) dispensing rules",
        "requirements": [
            "Valid prescription from registered medical practitioner",
            "Original prescription retained",
            "Patient identity verification",
            "Pharmacist counseling required",
            "Record keeping for 2 years"
        ],
        "affected_products": ["All except PAIN-001"]
    },
    "import_regulations": {
        "description": "Import license and documentation requirements",
        "requirements": [
            "Valid Import License from DH",
            "Certificate of Pharmaceutical Product (CPP)",
            "Certificate of Analysis for each batch",
            "Good Manufacturing Practice (GMP) certificate",
            "Customs declaration within 48 hours"
        ]
    },
    "storage_requirements": {
        "description": "General storage compliance requirements",
        "requirements": [
            "Temperature and humidity monitoring",
            "First-Expiry-First-Out (FEFO) principle",
            "Separate storage for different categories",
            "Pest control measures",
            "Regular inventory audits"
        ]
    }
}


class DrugInfoAgent(BaseAgent):
    """Drug Information & Compliance Agent for searching drug info, stock, and compliance details."""
    
    def __init__(self):
        super().__init__(
            name="Drug Information & Compliance",
            description="AI assistant for pharmaceutical salesmen to search drug information, stock levels, and compliance requirements"
        )
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for drug information interactions."""
        return """You are a knowledgeable pharmaceutical information assistant helping sales representatives find drug information, check stock levels, and understand compliance requirements.

## Your Capabilities
1. **Drug Information**: Provide detailed drug info including generic name, indications, dosage, side effects, and interactions
2. **Stock Inquiry**: Check current inventory levels and warehouse locations
3. **Compliance Guidance**: Explain regulatory requirements for controlled substances, cold chain, and prescription drugs
4. **Product Comparison**: Compare similar products in the same therapeutic category
5. **Clinical Information**: Provide contraindications, drug interactions, and clinical guidance

## Response Guidelines
- Be accurate and professional - this is medical/pharmaceutical information
- Always mention if a drug is controlled or requires cold chain
- Include relevant warnings and contraindications
- Format prices in HKD
- Use clear formatting for drug information
- Recommend consulting product insert for complete information

## Drug Categories Available
- **Cardiovascular**: Cardiomax, Cardiomax Plus, Lipidol
- **Diabetes**: Diabetix, Diabetix Premium
- **Oncology**: Oncotab, Oncotab Premium (Controlled)
- **Antibiotics**: Antibiox
- **Pain Management**: Painex
- **Immunology**: Immunoboost (Controlled, Cold Chain)

## Example Interactions

**Drug Information Query:**
User: "Tell me about Cardiomax"
Response: "💊 **Cardiomax 100mg** (Amlodipine Besylate)

**Category:** Cardiovascular
**Indication:** Hypertension, Angina Pectoris
**Dosage:** 5-10mg once daily

**Stock Status:** ✅ 5,000 units available
**Location:** Cold Storage A-12
**Price:** HKD 250/pack (30 tablets)

**Key Points:**
- Prescription required
- Store below 25°C, protect from light
- ⚠️ Contraindicated in severe aortic stenosis

**Common Side Effects:** Edema, headache, dizziness

Need more details on drug interactions or comparison with similar products?"

**Compliance Query:**
User: "What are the requirements for controlled substances?"
Response: "🔒 **Controlled Substances Compliance Requirements**

Controlled drugs in our catalog: Oncotab 50mg, Oncotab Premium 100mg, Immunoboost 250mg

**Handling Requirements:**
1. ✍️ Dual signature for dispensing
2. 🔐 Separate locked storage
3. 📊 Daily inventory reconciliation
4. 📋 Register maintained for 5 years
5. 📤 Monthly reporting to Department of Health

**For Sales Representatives:**
- Ensure hospital has valid controlled drug license
- Verify authorized person for ordering
- Document chain of custody
- Confirm secure storage facilities available"

Always provide accurate pharmaceutical information and remind users to refer to official product documentation."""

    def _build_graph(self) -> StateGraph:
        """Build the conversation workflow graph."""
        
        async def analyze_intent(state: AgentState) -> AgentState:
            """Analyze the user's intent from their message."""
            messages = state["messages"]
            last_message = messages[-1]["content"] if messages else ""
            
            intent = self._detect_intent(last_message)
            state["context"]["intent"] = intent
            state["current_step"] = "process"
            return state
        
        async def process_request(state: AgentState) -> AgentState:
            """Process the request and generate response."""
            messages = state["messages"]
            context = state["context"]
            intent = context.get("intent", "general")
            
            enriched_context = self._enrich_context(messages[-1]["content"] if messages else "", intent)
            context.update(enriched_context)
            
            system_prompt = self.get_system_prompt()
            if enriched_context:
                context_info = f"\n\n## Relevant Data Found:\n{json.dumps(enriched_context, indent=2, ensure_ascii=False)}"
                system_prompt += context_info
            
            response = await self.llm_service.chat(messages, system_prompt)
            
            state["result"] = response
            state["current_step"] = "complete"
            return state
        
        graph = StateGraph(AgentState)
        graph.add_node("analyze", analyze_intent)
        graph.add_node("process", process_request)
        graph.set_entry_point("analyze")
        graph.add_edge("analyze", "process")
        graph.add_edge("process", END)
        
        return graph
    
    def _detect_intent(self, message: str) -> str:
        """Detect user intent from message."""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["stock", "inventory", "available", "quantity", "how many"]):
            return "stock_inquiry"
        elif any(word in message_lower for word in ["compliance", "controlled", "regulation", "requirement", "cold chain", "storage", "import", "license"]):
            return "compliance"
        elif any(word in message_lower for word in ["compare", "versus", "vs", "difference", "alternative", "similar"]):
            return "comparison"
        elif any(word in message_lower for word in ["interaction", "contraindication", "side effect", "warning", "adverse"]):
            return "clinical_info"
        elif any(word in message_lower for word in ["price", "cost", "pricing"]):
            return "pricing"
        elif any(word in message_lower for word in ["list", "catalog", "all drugs", "categories"]):
            return "catalog"
        else:
            return "drug_info"
    
    def _enrich_context(self, message: str, intent: str) -> Dict[str, Any]:
        """Enrich context with relevant data based on intent."""
        context = {}
        message_lower = message.lower()
        
        # Find mentioned drugs
        drugs_found = []
        for drug_id, drug_data in DRUG_CATALOG.items():
            name_lower = drug_data["name"].lower()
            generic_lower = drug_data["generic_name"].lower()
            if name_lower in message_lower or any(word in message_lower for word in name_lower.split() if len(word) > 4):
                drugs_found.append({drug_id: drug_data})
            elif generic_lower in message_lower or any(word in message_lower for word in generic_lower.split() if len(word) > 4):
                drugs_found.append({drug_id: drug_data})
        
        if drugs_found:
            context["drugs_found"] = drugs_found
        
        # Find by category
        categories = ["cardiovascular", "diabetes", "oncology", "antibiotics", "pain", "immunology"]
        for cat in categories:
            if cat in message_lower:
                cat_drugs = {k: v for k, v in DRUG_CATALOG.items() if v["category"].lower() == cat or cat in v["category"].lower()}
                if cat_drugs:
                    context["category_drugs"] = cat_drugs
                break
        
        # Add compliance info
        if intent == "compliance":
            compliance_topics = []
            if "controlled" in message_lower:
                compliance_topics.append("controlled_substances")
            if "cold" in message_lower or "chain" in message_lower or "temperature" in message_lower:
                compliance_topics.append("cold_chain")
            if "prescription" in message_lower:
                compliance_topics.append("prescription_only")
            if "import" in message_lower:
                compliance_topics.append("import_regulations")
            if "storage" in message_lower:
                compliance_topics.append("storage_requirements")
            
            if compliance_topics:
                context["compliance_info"] = {k: COMPLIANCE_INFO[k] for k in compliance_topics}
            else:
                context["compliance_info"] = COMPLIANCE_INFO
        
        # Add catalog for listing intent
        if intent == "catalog":
            context["full_catalog"] = DRUG_CATALOG
        
        return context
    
    async def run_with_streaming(
        self, 
        user_input: str, 
        context: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Run the agent with streaming workflow updates."""
        
        yield {
            "type": "workflow_step",
            "step": {"step": "receive", "label": "Receiving Query", "status": "active"},
            "all_steps": [
                {"step": "receive", "label": "Receiving Query", "status": "active"},
                {"step": "search", "label": "Searching Drug Database", "status": "pending"},
                {"step": "compliance", "label": "Checking Compliance", "status": "pending"},
                {"step": "respond", "label": "Generating Response", "status": "pending"},
            ]
        }
        await asyncio.sleep(0.3)
        
        yield {
            "type": "workflow_step",
            "step": {"step": "search", "label": "Searching Drug Database", "status": "active"},
            "all_steps": [
                {"step": "receive", "label": "Receiving Query", "status": "completed"},
                {"step": "search", "label": "Searching Drug Database", "status": "active"},
                {"step": "compliance", "label": "Checking Compliance", "status": "pending"},
                {"step": "respond", "label": "Generating Response", "status": "pending"},
            ]
        }
        
        intent = self._detect_intent(user_input)
        await asyncio.sleep(0.4)
        
        yield {
            "type": "workflow_step",
            "step": {"step": "compliance", "label": "Checking Compliance", "status": "active"},
            "all_steps": [
                {"step": "receive", "label": "Receiving Query", "status": "completed"},
                {"step": "search", "label": "Searching Drug Database", "status": "completed"},
                {"step": "compliance", "label": "Checking Compliance", "status": "active"},
                {"step": "respond", "label": "Generating Response", "status": "pending"},
            ]
        }
        
        enriched_context = self._enrich_context(user_input, intent)
        await asyncio.sleep(0.5)
        
        yield {
            "type": "workflow_step",
            "step": {"step": "respond", "label": "Generating Response", "status": "active"},
            "all_steps": [
                {"step": "receive", "label": "Receiving Query", "status": "completed"},
                {"step": "search", "label": "Searching Drug Database", "status": "completed"},
                {"step": "compliance", "label": "Checking Compliance", "status": "completed"},
                {"step": "respond", "label": "Generating Response", "status": "active"},
            ]
        }
        
        messages = self._build_messages_with_history(user_input, conversation_history)
        
        system_prompt = self.get_system_prompt()
        if enriched_context:
            context_info = f"\n\n## Relevant Data Found:\n{json.dumps(enriched_context, indent=2, ensure_ascii=False)}"
            system_prompt += context_info
        
        response = await self.llm_service.chat(messages, system_prompt)
        
        yield {
            "type": "workflow_step",
            "step": {"step": "respond", "label": "Generating Response", "status": "completed"},
            "all_steps": [
                {"step": "receive", "label": "Receiving Query", "status": "completed"},
                {"step": "search", "label": "Searching Drug Database", "status": "completed"},
                {"step": "compliance", "label": "Checking Compliance", "status": "completed"},
                {"step": "respond", "label": "Generating Response", "status": "completed"},
            ]
        }
        
        yield {
            "type": "response",
            "content": response
        }
    
    def get_drug(self, drug_id: str) -> Optional[Dict[str, Any]]:
        """Get drug by ID."""
        return DRUG_CATALOG.get(drug_id.upper())
    
    def search_drugs(self, query: str) -> List[Dict[str, Any]]:
        """Search drugs by name or category."""
        query_lower = query.lower()
        results = []
        for drug_id, drug_data in DRUG_CATALOG.items():
            if (query_lower in drug_data["name"].lower() or 
                query_lower in drug_data["generic_name"].lower() or
                query_lower in drug_data["category"].lower()):
                results.append({drug_id: drug_data})
        return results
    
    def get_compliance_info(self, topic: str) -> Optional[Dict[str, Any]]:
        """Get compliance information for a topic."""
        return COMPLIANCE_INFO.get(topic.lower())
