"""
Mock data generator for MCP servers
"""
import json
import random
from typing import List, Dict, Any
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()


class MockDataGenerator:
    """Generate realistic mock data for SME portfolio"""
    
    def __init__(self):
        self.smes = self._generate_smes()
    
    def _generate_smes(self) -> List[Dict[str, Any]]:
        """Generate mock SME data"""
        smes = [
            # Critical SMEs
            {
                "id": "0142",
                "name": "TechStart Solutions Ltd",
                "risk_score": 68,
                "risk_category": "critical",
                "exposure": "€250K",
                "sector": "Software/Technology",
                "geography": "UK",
                "employee_count": 45,
                "employee_trend": "down",
                "revenue": "€2.4M",
                "ebitda": "€420K",
            },
            {
                "id": "0287",
                "name": "Urban Fashion Ltd",
                "risk_score": 62,
                "risk_category": "medium",
                "exposure": "€180K",
                "sector": "Retail/Fashion",
                "geography": "UK",
                "employee_count": 32,
                "employee_trend": "stable",
                "revenue": "€1.8M",
                "ebitda": "€280K",
            },
            {
                "id": "0531",
                "name": "Digital Marketing Hub",
                "risk_score": 58,
                "risk_category": "medium",
                "exposure": "€140K",
                "sector": "Marketing Services",
                "geography": "UK",
                "employee_count": 28,
                "employee_trend": "down",
                "revenue": "€1.2M",
                "ebitda": "€180K",
            },
            {
                "id": "0445",
                "name": "GreenLeaf Products",
                "risk_score": 72,
                "risk_category": "critical",
                "exposure": "€320K",
                "sector": "Food/Hospitality",
                "geography": "UK",
                "employee_count": 52,
                "employee_trend": "stable",
                "revenue": "€3.2M",
                "ebitda": "€580K",
            },
            {
                "id": "0672",
                "name": "Natural Wellness Ltd",
                "risk_score": 68,
                "risk_category": "critical",
                "exposure": "€210K",
                "sector": "Retail/Fashion",
                "geography": "EU",
                "employee_count": 38,
                "employee_trend": "stable",
                "revenue": "€2.1M",
                "ebitda": "€350K",
            },
        ]
        
        # Add more stable SMEs
        for i in range(6, 50):
            smes.append({
                "id": f"{i:04d}",
                "name": fake.company(),
                "risk_score": random.randint(25, 45),
                "risk_category": "stable",
                "exposure": f"€{random.randint(50, 200)}K",
                "sector": random.choice([
                    "Software/Technology",
                    "Retail/Fashion",
                    "Manufacturing",
                    "Construction",
                    "Marketing Services"
                ]),
                "geography": random.choice(["UK", "EU", "NA"]),
                "employee_count": random.randint(15, 100),
                "employee_trend": random.choice(["up", "stable", "down"]),
                "revenue": f"€{random.randint(500, 5000)}K",
                "ebitda": f"€{random.randint(50, 800)}K",
            })
        
        return smes
    
    def get_sme_by_id(self, sme_id: str) -> Dict[str, Any]:
        """Get SME by ID"""
        sme_id = sme_id.replace("#", "")
        return next((s for s in self.smes if s["id"] == sme_id), None)
    
    def get_all_smes(self) -> List[Dict[str, Any]]:
        """Get all SMEs"""
        return self.smes


# Global instance
mock_data = MockDataGenerator()
