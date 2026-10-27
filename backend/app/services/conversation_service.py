import uuid
from datetime import datetime, timezone
from typing import Dict, Optional
from app.schemas.profile import CitizenProfile, ConversationSession, ConversationTurn

class ConversationService:
    def __init__(self):
        self._sessions: Dict[str, ConversationSession] = {}

    def get_or_create_session(self, session_id: Optional[str] = None, language: str = "en") -> ConversationSession:
        now = datetime.now(timezone.utc).isoformat()
        if not session_id or session_id not in self._sessions:
            new_id = session_id or str(uuid.uuid4())
            session = ConversationSession(
                session_id=new_id,
                profile=CitizenProfile(),
                history=[],
                language=language,
                created_at=now,
                updated_at=now,
            )
            self._sessions[new_id] = session
            return session
        
        session = self._sessions[session_id]
        if language and language != session.language:
            session.language = language
            session.updated_at = now
        return session

    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        return self._sessions.get(session_id)

    def record_turn(self, session_id: str, user_message: str, agent_message: str) -> ConversationSession:
        session = self.get_or_create_session(session_id)
        now = datetime.now(timezone.utc).isoformat()
        turn = ConversationTurn(
            turn_id=str(uuid.uuid4())[:8],
            user_message=user_message,
            agent_message=agent_message,
            timestamp=now
        )
        session.history.append(turn)
        session.updated_at = now
        return session

    def update_profile(self, session_id: str, profile: CitizenProfile) -> ConversationSession:
        session = self.get_or_create_session(session_id)
        session.profile = profile
        session.updated_at = datetime.now(timezone.utc).isoformat()
        return session

    def reset_session(self, session_id: str) -> ConversationSession:
        now = datetime.now(timezone.utc).isoformat()
        new_session = ConversationSession(
            session_id=session_id,
            profile=CitizenProfile(),
            history=[],
            language="en",
            created_at=now,
            updated_at=now,
        )
        self._sessions[session_id] = new_session
        return new_session

conversation_service = ConversationService()
