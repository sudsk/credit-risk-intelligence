"""
Chat Service
AI-powered chatbot for portfolio queries using Claude API.
"""

from typing import Dict, Any, List
import json
from .portfolio_service import get_portfolio_service
from .risk_engine import get_risk_engine

class ChatService:
    """Service for AI-powered chat interactions."""
    
    def __init__(self):
        self.portfolio_service = get_portfolio_service()
        self.risk_engine = get_risk_engine()
        self.conversation_history = []
    
    async def process_query(self, query: str, use_claude_api: bool = False) -> Dict[str, Any]:
        """
        Process natural language query about the portfolio.
        
        Args:
            query: User's natural language question
            use_claude_api: If True, use Claude API; if False, use rule-based responses
        
        Returns:
            Response with answer and relevant data
        """
        # Get portfolio context for the query
        context = await self._build_context()
        
        # For MVP demo without API key, use intelligent rule-based responses
        if not use_claude_api:
            response = await self._process_query_rule_based(query, context)
        else:
            response = await self._process_query_with_claude(query, context)
        
        # Store in conversation history
        self.conversation_history.append({
            "query": query,
            "response": response["answer"]
        })
        
        return response
    
    async def _build_context(self) -> Dict[str, Any]:
        """Build portfolio context for the AI."""
        portfolio_summary = await self.portfolio_service.get_portfolio_summary()
        critical_smes = await self.portfolio_service.get_critical_smes(limit=10)
        
        return {
            "portfolio": portfolio_summary,
            "critical_smes": critical_smes
        }
    
    async def _process_query_rule_based(self, query: str, context: Dict) -> Dict[str, Any]:
        """
        Process query using intelligent rule-based responses.
        Good for demo without requiring API keys.
        """
        query_lower = query.lower()
        
        # Portfolio overview queries
        if any(word in query_lower for word in ["overview", "summary", "total", "portfolio"]):
            portfolio = context["portfolio"]
            answer = f"""**Portfolio Overview:**

• **Total Exposure:** €{portfolio['total_exposure']:,.0f}
• **Total SMEs:** {portfolio['total_smes']}
• **Average Risk Score:** {portfolio['avg_risk_score']}

**Risk Distribution:**
• Critical: {portfolio['risk_distribution']['counts']['critical']} SMEs (€{portfolio['risk_distribution']['exposures']['critical']:,.0f})
• Medium: {portfolio['risk_distribution']['counts']['medium']} SMEs (€{portfolio['risk_distribution']['exposures']['medium']:,.0f})
• Stable: {portfolio['risk_distribution']['counts']['stable']} SMEs (€{portfolio['risk_distribution']['exposures']['stable']:,.0f})

**Key Concerns:** {portfolio['risk_distribution']['counts']['critical']} SMEs require immediate attention."""
            
            return {
                "answer": answer,
                "data": portfolio,
                "type": "portfolio_overview"
            }
        
        # Critical SMEs queries
        elif any(word in query_lower for word in ["critical", "high risk", "worst", "problem"]):
            critical = context["critical_smes"]
            
            answer = f"""**Critical SMEs Analysis:**

Found {len(critical)} SMEs in critical risk category (risk score ≥ 60):

"""
            for i, sme in enumerate(critical[:5], 1):
                answer += f"{i}. **{sme['name']}** (ID: {sme['id']})\n"
                answer += f"   • Risk Score: {sme['risk_score']} ({sme['risk_category']})\n"
                answer += f"   • Exposure: €{sme['exposure']:,.0f}\n"
                answer += f"   • Sector: {sme['sector']}\n"
                answer += f"   • Trend: {sme['trend']} ({sme['trend_value']:+.1f}%)\n\n"
            
            total_critical_exposure = sum(s['exposure'] for s in critical)
            answer += f"\n**Total Critical Exposure:** €{total_critical_exposure:,.0f}\n"
            answer += f"**Recommended Action:** Immediate review and risk mitigation required."
            
            return {
                "answer": answer,
                "data": critical,
                "type": "critical_smes"
            }
        
        # Sector queries
        elif any(word in query_lower for word in ["sector", "industry", "retail", "construction", "technology", "software"]):
            # Extract sector from query
            sector_map = {
                "retail": "Retail/Fashion",
                "fashion": "Retail/Fashion",
                "construction": "Construction",
                "technology": "Software/Technology",
                "software": "Software/Technology",
                "tech": "Software/Technology",
                "food": "Food/Hospitality",
                "hospitality": "Food/Hospitality",
                "manufacturing": "Manufacturing",
                "energy": "Energy/Utilities"
            }
            
            sector = None
            for key, value in sector_map.items():
                if key in query_lower:
                    sector = value
                    break
            
            if sector:
                sector_data = await self.portfolio_service.get_sector_breakdown(sector)
                
                answer = f"""**{sector} Sector Analysis:**

• **Total SMEs:** {sector_data['total_smes']}
• **Total Exposure:** €{sector_data['total_exposure']:,.0f}
• **Average Risk Score:** {sector_data['avg_risk_score']:.1f}

**Risk Distribution:**
• Critical: {sector_data['risk_distribution']['critical']} SMEs
• Medium: {sector_data['risk_distribution']['medium']} SMEs
• Stable: {sector_data['risk_distribution']['stable']} SMEs

**Assessment:** {"⚠️ High concentration of critical SMEs - sector under stress" if sector_data['risk_distribution']['critical'] > sector_data['total_smes'] * 0.3 else "✅ Sector showing healthy risk profile"}"""
                
                return {
                    "answer": answer,
                    "data": sector_data,
                    "type": "sector_analysis"
                }
            else:
                # Show all sectors
                portfolio = context["portfolio"]
                answer = "**Sector Distribution:**\n\n"
                
                for sector, data in portfolio['sector_distribution'].items():
                    answer += f"• **{sector}:** {data['count']} SMEs, €{data['exposure']:,.0f}\n"
                
                return {
                    "answer": answer,
                    "data": portfolio['sector_distribution'],
                    "type": "sector_overview"
                }
        
        # Trend queries
        elif any(word in query_lower for word in ["declining", "growing", "trend", "improving", "worsening"]):
            # Get SMEs by trend
            if "declining" in query_lower or "worsening" in query_lower or "down" in query_lower:
                smes_result = await self.portfolio_service.get_sme_list(trend="down", limit=10)
                smes = smes_result["smes"]
                
                answer = f"""**Declining SMEs (Negative Trend):**

Found {smes_result['total_count']} SMEs showing declining trends:

"""
                for i, sme in enumerate(smes[:5], 1):
                    answer += f"{i}. **{sme['name']}**\n"
                    answer += f"   • Risk Score: {sme['risk_score']}\n"
                    answer += f"   • Trend: {sme['trend_value']:+.1f}% (declining)\n"
                    answer += f"   • Exposure: €{sme['exposure']:,.0f}\n\n"
                
                answer += "**⚠️ Recommendation:** Monitor closely for further deterioration. Consider reducing exposure."
                
                return {
                    "answer": answer,
                    "data": smes,
                    "type": "declining_smes"
                }
            else:
                smes_result = await self.portfolio_service.get_sme_list(trend="up", limit=10)
                smes = smes_result["smes"]
                
                answer = f"""**Growing SMEs (Positive Trend):**

Found {smes_result['total_count']} SMEs showing growth:

"""
                for i, sme in enumerate(smes[:5], 1):
                    answer += f"{i}. **{sme['name']}**\n"
                    answer += f"   • Risk Score: {sme['risk_score']}\n"
                    answer += f"   • Trend: +{sme['trend_value']:.1f}% (growing)\n"
                    answer += f"   • Exposure: €{sme['exposure']:,.0f}\n\n"
                
                answer += "**✅ Opportunity:** Consider increasing exposure to these growing businesses."
                
                return {
                    "answer": answer,
                    "data": smes,
                    "type": "growing_smes"
                }
        
        # Exposure queries
        elif any(word in query_lower for word in ["exposure", "large", "biggest", "top"]):
            smes_result = await self.portfolio_service.get_sme_list(sort_by="exposure", sort_order="desc", limit=10)
            smes = smes_result["smes"]
            
            answer = f"""**Top 10 SMEs by Exposure:**

"""
            total_top_10 = 0
            for i, sme in enumerate(smes[:10], 1):
                total_top_10 += sme['exposure']
                answer += f"{i}. **{sme['name']}** - €{sme['exposure']:,.0f}\n"
                answer += f"   Risk: {sme['risk_score']} ({sme['risk_category']}) | Sector: {sme['sector']}\n\n"
            
            portfolio_total = context["portfolio"]["total_exposure"]
            concentration = (total_top_10 / portfolio_total * 100)
            
            answer += f"\n**Concentration Risk:** Top 10 represent {concentration:.1f}% of total exposure"
            
            return {
                "answer": answer,
                "data": smes,
                "type": "top_exposures"
            }
        
        # Search by name
        elif "show me" in query_lower or "find" in query_lower or "search" in query_lower:
            # Extract potential company name
            words = query.split()
            # Try to find capitalized words (likely company names)
            search_terms = [w for w in words if w[0].isupper() and len(w) > 2]
            
            if search_terms:
                search_query = " ".join(search_terms)
                smes = await self.portfolio_service.search_smes(search_query, limit=5)
                
                if smes:
                    answer = f"**Search Results for '{search_query}':**\n\n"
                    for sme in smes:
                        answer += f"• **{sme['name']}** (ID: {sme['id']})\n"
                        answer += f"  Risk Score: {sme['risk_score']} | Exposure: €{sme['exposure']:,.0f}\n\n"
                    
                    return {
                        "answer": answer,
                        "data": smes,
                        "type": "search_results"
                    }
            
            return {
                "answer": "I couldn't find any SMEs matching that search. Try searching by sector, risk category, or specific company attributes.",
                "data": None,
                "type": "no_results"
            }
        
        # Default helpful response
        else:
            answer = """I can help you with:

• **Portfolio overview** - "Give me a portfolio summary"
• **Critical SMEs** - "Show me critical risk SMEs"
• **Sector analysis** - "Analyze the retail sector"
• **Trends** - "Which SMEs are declining?"
• **Exposures** - "Show me top 10 exposures"
• **Search** - "Find TechStart Solutions"

What would you like to know?"""
            
            return {
                "answer": answer,
                "data": None,
                "type": "help"
            }
    
    async def _process_query_with_claude(self, query: str, context: Dict) -> Dict[str, Any]:
        """
        Process query using Claude API (for production with API key).
        """
        try:
            import anthropic
            
            client = anthropic.Anthropic()
            
            # Build system prompt with context
            system_prompt = f"""You are a credit risk analyst assistant for an SME portfolio monitoring platform.

Portfolio Context:
- Total SMEs: {context['portfolio']['total_smes']}
- Total Exposure: €{context['portfolio']['total_exposure']:,.0f}
- Critical SMEs: {context['portfolio']['risk_distribution']['counts']['critical']}

Provide concise, actionable insights about credit risk and portfolio health."""
            
            # Call Claude API
            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                system=system_prompt,
                messages=[{
                    "role": "user",
                    "content": f"Portfolio data: {json.dumps(context, default=str)}\n\nQuery: {query}"
                }]
            )
            
            answer = message.content[0].text
            
            return {
                "answer": answer,
                "data": context,
                "type": "claude_response"
            }
        
        except Exception as e:
            # Fallback to rule-based if API fails
            return await self._process_query_rule_based(query, context)
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []


# Singleton instance
_chat_service = None

def get_chat_service() -> ChatService:
    """Get singleton chat service instance."""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service