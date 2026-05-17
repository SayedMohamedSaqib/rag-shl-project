from pydantic import BaseModel


class RetrievalIntent(BaseModel):

    role: str | None = None

    technical_skills: list[str] = []

    behavioral_traits: list[str] = []

    seniority: str | None = None

    cognitive_required: bool = False

    personality_required: bool = False

    assessment_preferences: list[str] = []

    constraints: list[str] = []


class Recommendation(BaseModel):

    name: str

    url: str

    test_type: str


class RetrievalResult(BaseModel):

    recommendations: list[Recommendation]

    reasoning: str