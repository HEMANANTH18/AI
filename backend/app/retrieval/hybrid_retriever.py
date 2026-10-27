import re
from typing import List, Dict, Tuple, Optional
from app.core.logging_config import logger
from app.schemas.profile import CitizenProfile
from app.schemas.scheme import Scheme
from app.data.csv_loader import loader
from app.retrieval.vector_store import vector_store

class HybridRetriever:
    def __init__(self):
        self.loader = loader
        self.vector_store = vector_store

    def retrieve(self, profile: CitizenProfile, top_k: int = 40) -> List[Tuple[Scheme, float]]:
        """
        Retrieves candidate schemes via semantic search with fallback to lexical-attribute matching.
        Returns list of (Scheme, similarity_score).
        """
        # Formulate rich query representation from citizen profile and query text
        query_elements = []
        if profile.query_text:
            query_elements.append(profile.query_text)
        if profile.occupation:
            query_elements.append(f"occupation {profile.occupation}")
        if profile.state:
            query_elements.append(f"state {profile.state}")
        if profile.gender:
            query_elements.append(f"gender {profile.gender}")
        if profile.social_category:
            query_elements.append(f"category {profile.social_category}")
        if profile.disability:
            query_elements.append("disability physically handicapped")
        if profile.marital_status == "widow":
            query_elements.append("widow pension welfare")

        query_str = " ".join(query_elements).strip()
        if not query_str:
            query_str = "welfare financial assistance subsidy grant pension education agriculture"

        candidates: List[Tuple[Scheme, float]] = []

        # 1. Try ChromaDB semantic retrieval
        if self.vector_store.count() > 0:
            try:
                pairs = self.vector_store.query(query_str, n_results=top_k * 2)
                for sid, sim in pairs:
                    scheme = self.loader.get_by_id(sid)
                    if scheme:
                        candidates.append((scheme, sim))
            except Exception as e:
                logger.error(f"Semantic search encountered error: {e}. Falling back to lexical retrieval.")
                candidates = []

        # 2. Fallback: Lexical & Attribute candidate retrieval if vector store returned empty
        if not candidates:
            logger.info("Using lexical attribute retriever fallback.")
            candidates = self._lexical_retrieval_fallback(profile, query_str, top_k=top_k)

        # 3. Apply geographic pre-filter: ensure user state or Central schemes match
        filtered_candidates: List[Tuple[Scheme, float]] = []
        user_state_clean = profile.state.strip().lower() if profile.state else None

        for scheme, sim in candidates:
            if user_state_clean:
                scheme_state = scheme.state.strip().lower() if scheme.state else ""
                is_central = scheme.parsed_criteria.is_central or scheme.level.lower() == "central" or "all india" in scheme_state
                # Match if Central or state substring matches
                if not is_central and user_state_clean not in scheme_state and scheme_state not in user_state_clean:
                    # Penalize but don't drop completely unless strictly mismatched
                    sim = sim * 0.4
            filtered_candidates.append((scheme, sim))

        # Sort by similarity score descending
        filtered_candidates.sort(key=lambda x: x[1], reverse=True)
        return filtered_candidates[:top_k]

    def _lexical_retrieval_fallback(self, profile: CitizenProfile, query: str, top_k: int = 40) -> List[Tuple[Scheme, float]]:
        """Fast keyword/attribute scoring fallback when vector store is uninitialized."""
        tokens = [t for t in re.findall(r'\b[a-zA-Z0-9]{3,}\b', query.lower()) if t not in ("the", "and", "for", "with", "from", "year", "old")]
        all_schemes = self.loader.get_all()
        scored: List[Tuple[Scheme, float]] = []

        user_occ = profile.occupation.lower() if profile.occupation else None
        user_st = profile.state.strip().lower() if profile.state else None

        for s in all_schemes:
            text = s.searchable_text.lower()
            matches = sum(1 for t in tokens if t in text)
            score = matches / max(1, len(tokens))

            # Bonus for occupation match
            if user_occ and user_occ in text:
                score += 0.25

            # Bonus for state match
            if user_st:
                if (s.state and user_st in s.state.lower()) or s.parsed_criteria.is_central:
                    score += 0.20

            scored.append((s, min(1.0, score)))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

hybrid_retriever = HybridRetriever()
