"""
Portfolio service - business logic
"""
from typing import List, Optional
from datetime import datetime
from app.models.sme import SME, PortfolioMetrics, BreakdownData, SectorBreakdown, GeographyBreakdown


class PortfolioService:
    """Portfolio management service"""
    
    def __init__(self):
        # Mock data storage (in-memory for demo)
        self._mock_smes = self._generate_mock_smes()
    
    def get_metrics(self) -> PortfolioMetrics:
        """Get portfolio metrics"""
        critical = len([s for s in self._mock_smes if s.risk_category == "critical"])
        medium = len([s for s in self._mock_smes if s.risk_category == "medium"])
        stable = len([s for s in self._mock_smes if s.risk_category == "stable"])
        
        return PortfolioMetrics(
            total_smes=1284,
            total_exposure="€328M",
            avg_risk_score=64,
            critical_count=23,
            medium_count=142,
            stable_count=1119,
            default_probability=2.8,
            portfolio_trend="up"
        )
    
    def get_all_smes(self) -> List[SME]:
        """Get all SMEs"""
        return self._mock_smes
    
    def get_sme_by_id(self, sme_id: str) -> Optional[SME]:
        """Get SME by ID"""
        return next((s for s in self._mock_smes if s.id == sme_id), None)
    
    def get_breakdown_data(self, risk_level: str) -> BreakdownData:
        """Get breakdown data for risk level"""
        breakdown_data = {
            "critical": {
                "title": "Critical Risk (80-100) - Detailed Breakdown",
                "total": {"smes": 23, "exposure": "€42M", "percent": "12.8%"},
                "sectors": [
                    SectorBreakdown(
                        icon="💻",
                        name="Software/Technology",
                        smes=8,
                        exposure="€18M",
                        percent="6.2%"
                    ),
                    SectorBreakdown(
                        icon="🛍️",
                        name="Retail/Fashion",
                        smes=6,
                        exposure="€12M",
                        percent="4.1%"
                    ),
                    SectorBreakdown(
                        icon="📢",
                        name="Marketing Services",
                        smes=4,
                        exposure="€7M",
                        percent="2.4%"
                    ),
                ],
                "geographies": [
                    GeographyBreakdown(
                        icon="🇬🇧",
                        name="UK",
                        smes=15,
                        exposure="€28M",
                        percent="9.6%"
                    ),
                    GeographyBreakdown(
                        icon="🇪🇺",
                        name="EU",
                        smes=5,
                        exposure="€9M",
                        percent="3.1%"
                    ),
                    GeographyBreakdown(
                        icon="🇺🇸",
                        name="NA",
                        smes=2,
                        exposure="€3M",
                        percent="1.0%"
                    ),
                ],
            },
            "medium": {
                "title": "Medium Risk (50-79) - Detailed Breakdown",
                "total": {"smes": 142, "exposure": "€98M", "percent": "29.9%"},
                "sectors": [
                    SectorBreakdown(
                        icon="💻",
                        name="Software/Technology",
                        smes=42,
                        exposure="€28M",
                        percent="9.6%"
                    ),
                ],
                "geographies": [
                    GeographyBreakdown(
                        icon="🇬🇧",
                        name="UK",
                        smes=95,
                        exposure="€66M",
                        percent="22.6%"
                    ),
                ],
            },
            "stable": {
                "title": "Low Risk (0-49) - Detailed Breakdown",
                "total": {"smes": 1119, "exposure": "€188M", "percent": "57.3%"},
                "sectors": [
                    SectorBreakdown(
                        icon="💻",
                        name="Software/Technology",
                        smes=197,
                        exposure="€36M",
                        percent="11.0%"
                    ),
                ],
                "geographies": [
                    GeographyBreakdown(
                        icon="🇬🇧",
                        name="UK",
                        smes=745,
                        exposure="€125M",
                        percent="38.1%"
                    ),
                ],
            },
        }
        
        return BreakdownData(**breakdown_data[risk_level])
    
    def _generate_mock_smes(self) -> List[SME]:
        """Generate mock SME data"""
        mock_smes = [
            SME(
                id="#0142",
                name="TechStart Solutions Ltd",
                risk_score=68,
                risk_category="critical",
                exposure="€250K",
                sector="Software/Technology",
                geography="UK",
                trend="up",
                trend_value=14
            ),
            SME(
                id="#0287",
                name="Urban Fashion Ltd",
                risk_score=62,
                risk_category="medium",
                exposure="€180K",
                sector="Retail/Fashion",
                geography="UK",
                trend="up",
                trend_value=8
            ),
            SME(
                id="#0531",
                name="Digital Marketing Hub",
                risk_score=58,
                risk_category="medium",
                exposure="€140K",
                sector="Marketing Services",
                geography="UK",
                trend="up",
                trend_value=12
            ),
            SME(
                id="#0445",
                name="GreenLeaf Products",
                risk_score=72,
                risk_category="critical",
                exposure="€320K",
                sector="Food/Hospitality",
                geography="UK",
                trend="stable",
                trend_value=2
            ),
            SME(
                id="#0672",
                name="Natural Wellness Ltd",
                risk_score=68,
                risk_category="critical",
                exposure="€210K",
                sector="Retail/Fashion",
                geography="EU",
                trend="up",
                trend_value=6
            ),
        ]
        
        # Add more stable SMEs to reach realistic count
        for i in range(5, 25):
            mock_smes.append(
                SME(
                    id=f"#{i:04d}",
                    name=f"Sample SME {i}",
                    risk_score=35,
                    risk_category="stable",
                    exposure="€100K",
                    sector="Other",
                    geography="UK",
                    trend="stable",
                    trend_value=0
                )
            )
        
        return mock_smes
