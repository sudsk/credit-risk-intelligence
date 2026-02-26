"""
Portfolio Service
Aggregates portfolio data and provides SME list/detail views.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional
from .risk_engine import get_risk_engine

# Data paths
DATA_DIR = Path(__file__).parent.parent.parent / "mcp-servers" / "data"
SMES_CSV = DATA_DIR / "smes.csv"

class PortfolioService:
    """Service for portfolio-level operations and SME queries."""
    
    def __init__(self):
        self.smes_df = pd.read_csv(SMES_CSV)
        self.risk_engine = get_risk_engine()
    
    async def get_portfolio_summary(self) -> Dict[str, Any]:
        """
        Get portfolio overview metrics.
        
        Returns:
            Dict with total exposure, SME count, risk distribution, etc.
        """
        total_exposure = float(self.smes_df['exposure'].sum())
        total_smes = len(self.smes_df)
        avg_risk_score = float(self.smes_df['risk_score'].mean())
        
        # Risk distribution
        risk_dist = {
            "critical": int(len(self.smes_df[self.smes_df['risk_category'] == 'critical'])),
            "medium": int(len(self.smes_df[self.smes_df['risk_category'] == 'medium'])),
            "stable": int(len(self.smes_df[self.smes_df['risk_category'] == 'stable']))
        }
        
        # Calculate exposures by risk category
        critical_exposure = float(self.smes_df[self.smes_df['risk_category'] == 'critical']['exposure'].sum())
        medium_exposure = float(self.smes_df[self.smes_df['risk_category'] == 'medium']['exposure'].sum())
        stable_exposure = float(self.smes_df[self.smes_df['risk_category'] == 'stable']['exposure'].sum())
        
        # Sector distribution
        sector_dist = self.smes_df.groupby('sector').agg({
            'exposure': 'sum',
            'id': 'count'
        }).to_dict('index')
        
        # Geography distribution
        geo_dist = self.smes_df.groupby('geography').agg({
            'exposure': 'sum',
            'id': 'count'
        }).to_dict('index')
        
        # Trend analysis
        trend_dist = self.smes_df['trend'].value_counts().to_dict()
        
        return {
            "total_exposure": total_exposure,
            "total_smes": total_smes,
            "avg_risk_score": round(avg_risk_score, 1),
            "risk_distribution": {
                "counts": risk_dist,
                "exposures": {
                    "critical": critical_exposure,
                    "medium": medium_exposure,
                    "stable": stable_exposure
                },
                "percentages": {
                    "critical": round(critical_exposure / total_exposure * 100, 1),
                    "medium": round(medium_exposure / total_exposure * 100, 1),
                    "stable": round(stable_exposure / total_exposure * 100, 1)
                }
            },
            "sector_distribution": {
                k: {"exposure": float(v['exposure']), "count": int(v['id'])} 
                for k, v in sector_dist.items()
            },
            "geography_distribution": {
                k: {"exposure": float(v['exposure']), "count": int(v['id'])} 
                for k, v in geo_dist.items()
            },
            "trend_distribution": trend_dist
        }
    
    async def get_sme_list(
        self, 
        risk_category: Optional[str] = None,
        sector: Optional[str] = None,
        geography: Optional[str] = None,
        trend: Optional[str] = None,
        min_exposure: Optional[float] = None,
        max_exposure: Optional[float] = None,
        search: Optional[str] = None,
        sort_by: str = "risk_score",
        sort_order: str = "desc",
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get filtered and sorted list of SMEs.
        
        Args:
            risk_category: Filter by risk category (critical/medium/stable)
            sector: Filter by sector
            geography: Filter by geography
            trend: Filter by trend (up/down/stable)
            min_exposure: Minimum exposure amount
            max_exposure: Maximum exposure amount
            search: Search by name
            sort_by: Field to sort by
            sort_order: Sort order (asc/desc)
            limit: Max results to return
            offset: Pagination offset
        
        Returns:
            Dict with smes list and metadata
        """
        df = self.smes_df.copy()
        
        # Apply filters
        if risk_category:
            df = df[df['risk_category'] == risk_category]
        
        if sector:
            df = df[df['sector'] == sector]
        
        if geography:
            df = df[df['geography'] == geography]
        
        if trend:
            df = df[df['trend'] == trend]
        
        if min_exposure is not None:
            df = df[df['exposure'] >= min_exposure]
        
        if max_exposure is not None:
            df = df[df['exposure'] <= max_exposure]
        
        if search:
            df = df[df['name'].str.contains(search, case=False, na=False)]
        
        # Sort
        ascending = sort_order == "asc"
        df = df.sort_values(by=sort_by, ascending=ascending)
        
        # Count before pagination
        total_count = len(df)
        
        # Paginate
        df = df.iloc[offset:offset + limit]
        
        # Convert to list of dicts
        smes = []
        for _, row in df.iterrows():
            smes.append({
                "id": row['id'],
                "name": row['name'],
                "risk_score": int(row['risk_score']),
                "risk_category": row['risk_category'],
                "exposure": float(row['exposure']),
                "sector": row['sector'],
                "geography": row['geography'],
                "trend": row['trend'],
                "trend_value": float(row['trend_value']),
                "revenue": float(row['revenue']),
                "employee_count": int(row['employee_count']),
                "drawn_amount": float(row['drawn_amount']) if 'drawn_amount' in self.smes_df.columns else 0.0,
                "bank_rating": str(row['bank_rating']) if 'bank_rating' in self.smes_df.columns else '',
                "pd_original": float(row['pd_original']) if 'pd_original' in self.smes_df.columns else 0.0,
                "pd_adjusted": float(row['pd_adjusted']) if 'pd_adjusted' in self.smes_df.columns else 0.0,               
            })
        
        return {
            "smes": smes,
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total_count
        }
    
    async def get_sme_detail(self, sme_id: str) -> Dict[str, Any]:
        """
        Get detailed SME profile with comprehensive risk analysis.
        
        Args:
            sme_id: SME identifier
        
        Returns:
            Complete SME profile with risk breakdown
        """
        # Get base SME data
        sme_row = self.smes_df[self.smes_df['id'].astype(str).str.zfill(4) == str(sme_id).zfill(4)]

        if sme_row.empty:
            raise ValueError(f"SME {sme_id} not found")
        
        sme = sme_row.iloc[0]
        
        # Calculate comprehensive risk analysis
        risk_analysis = await self.risk_engine.calculate_risk_score(sme_id)
        
        # Add additional SME details
        risk_analysis["details"] = {
            "founded_year": int(sme['founded_year']),
            "employee_count": int(sme['employee_count']),
            "revenue": float(sme['revenue']),
            "ebitda": float(sme['ebitda']),
            "debt": float(sme['debt']),
            "cash_reserves": float(sme['cash_reserves']),
            "current_ratio": float(sme['current_ratio']),
            "debt_service_coverage": float(sme['debt_service_coverage'])
        }
        
        # Add trend information
        risk_analysis["trend"] = {
            "direction": sme['trend'],
            "value": float(sme['trend_value'])
        }
        
        return risk_analysis
    
    async def get_critical_smes(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get list of SMEs in critical risk category.
        
        Args:
            limit: Max results to return
        
        Returns:
            List of critical SMEs sorted by risk score (highest first)
        """
        result = await self.get_sme_list(
            risk_category="critical",
            sort_by="risk_score",
            sort_order="desc",
            limit=limit
        )
        return result["smes"]
    
    async def search_smes(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search SMEs by name.
        
        Args:
            query: Search query
            limit: Max results
        
        Returns:
            List of matching SMEs
        """
        result = await self.get_sme_list(
            search=query,
            limit=limit
        )
        return result["smes"]
    
    async def get_sector_breakdown(self, sector: str) -> Dict[str, Any]:
        """
        Get detailed breakdown for a specific sector.
        
        Args:
            sector: Sector name
        
        Returns:
            Sector statistics and SME list
        """
        sector_smes = self.smes_df[self.smes_df['sector'] == sector]
        
        return {
            "sector": sector,
            "total_smes": len(sector_smes),
            "total_exposure": float(sector_smes['exposure'].sum()),
            "avg_risk_score": float(sector_smes['risk_score'].mean()),
            "risk_distribution": {
                "critical": int(len(sector_smes[sector_smes['risk_category'] == 'critical'])),
                "medium": int(len(sector_smes[sector_smes['risk_category'] == 'medium'])),
                "stable": int(len(sector_smes[sector_smes['risk_category'] == 'stable']))
            }
        }

    async def get_breakdown_by_risk(self, risk_level: str) -> Dict[str, Any]:
        df = self.smes_df[self.smes_df['risk_category'] == risk_level]
        
        by_sector = df.groupby('sector').agg(
            smes=('id', 'count'),
            exposure=('exposure', 'sum')
        ).reset_index().to_dict('records')
        
        by_geo = df.groupby('geography').agg(
            smes=('id', 'count'),
            exposure=('exposure', 'sum')
        ).reset_index().to_dict('records')
        
        return {
            "risk_level": risk_level,
            "total": {
                "smes": len(df),
                "exposure": float(df['exposure'].sum()),
            },
            "by_sector": by_sector,
            "by_geography": by_geo,
        }

# Singleton instance
_portfolio_service = None

def get_portfolio_service() -> PortfolioService:
    """Get singleton portfolio service instance."""
    global _portfolio_service
    if _portfolio_service is None:
        _portfolio_service = PortfolioService()
    return _portfolio_service
