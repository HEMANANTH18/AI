from typing import List, Dict, Any, Optional
from app.data.csv_loader import loader
from app.schemas.scheme import Scheme

class SchemeService:
    def __init__(self):
        self.loader = loader

    def get_all_schemes(self) -> List[Scheme]:
        return self.loader.get_all()

    def get_scheme_by_id(self, scheme_id: str) -> Optional[Scheme]:
        return self.loader.get_by_id(scheme_id)

    def search_schemes(
        self,
        query: Optional[str] = None,
        state: Optional[str] = None,
        category: Optional[str] = None,
        benefit_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Search and filter schemes by keywords, state, category, and benefit type."""
        schemes = self.loader.get_all()
        filtered = schemes

        if state and isinstance(state, str):
            st = state.strip().lower()
            filtered = [
                s for s in filtered
                if (s.state and st in s.state.lower()) or s.parsed_criteria.is_central or "all india" in (s.state or "").lower()
            ]

        if category and isinstance(category, str):
            cat = category.strip().lower()
            filtered = [
                s for s in filtered
                if any(cat in c.lower() for c in s.categories)
            ]

        if benefit_type and isinstance(benefit_type, str):
            bt = benefit_type.strip().lower()
            filtered = [
                s for s in filtered
                if bt in s.benefit_type.lower()
            ]

        if query and isinstance(query, str):
            q = query.strip().lower()
            filtered = [
                s for s in filtered
                if q in s.name.lower() or q in s.brief_description.lower() or any(q in t.lower() for t in s.tags)
            ]

        total = len(filtered)
        paginated = filtered[offset:offset + limit]

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "results": [
                {
                    "id": s.id,
                    "name": s.name,
                    "short_title": s.short_title,
                    "level": s.level,
                    "state": s.state or "All India",
                    "categories": s.categories,
                    "benefit_type": s.benefit_type,
                    "brief_description": s.brief_description,
                    "official_url": s.source_url,
                }
                for s in paginated
            ]
        }

    def get_metadata(self) -> Dict[str, Any]:
        """Returns categories, states, and counts for UI filtering and stats display."""
        schemes = self.loader.get_all()
        categories = set()
        states = set()
        benefit_types = set()

        for s in schemes:
            for c in s.categories:
                categories.add(c)
            if s.state and s.state != "All India":
                states.add(s.state)
            benefit_types.add(s.benefit_type)

        return {
            "total_schemes": len(schemes),
            "central_schemes_count": sum(1 for s in schemes if s.parsed_criteria.is_central),
            "state_schemes_count": sum(1 for s in schemes if not s.parsed_criteria.is_central),
            "categories": sorted(list(categories)),
            "states": sorted(list(states)),
            "benefit_types": sorted(list(benefit_types)),
        }

scheme_service = SchemeService()
