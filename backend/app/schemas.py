from pydantic import BaseModel, field_validator


class MCQPayload(BaseModel):
    """Shape expected back from the LLM for a single MCQ. Raises on invalid shape."""

    question_text: str
    options: list[str]
    correct_index: int
    explanation: str
    difficulty: str

    @field_validator("question_text", "explanation")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("field must not be blank")
        return v.strip()

    @field_validator("options")
    @classmethod
    def exactly_four_distinct_options(cls, v: list[str]) -> list[str]:
        if len(v) != 4:
            raise ValueError("options must contain exactly 4 items")
        cleaned = [o.strip() for o in v]
        if any(not o for o in cleaned):
            raise ValueError("options must not contain blank entries")
        if len(set(cleaned)) != len(cleaned):
            raise ValueError("options must not contain duplicates")
        return cleaned

    @field_validator("correct_index")
    @classmethod
    def index_in_range(cls, v: int) -> int:
        if not (0 <= v <= 3):
            raise ValueError("correct_index must be between 0 and 3")
        return v

    @field_validator("difficulty")
    @classmethod
    def valid_difficulty(cls, v: str) -> str:
        v = v.strip().lower()
        if v not in ("basic", "mid"):
            raise ValueError("difficulty must be 'basic' or 'mid'")
        return v


class ScenarioPayload(BaseModel):
    """Shape expected back from the LLM for a single scenario question."""

    question_text: str
    model_answer: str
    rubric: list[str]
    difficulty: str

    @field_validator("question_text", "model_answer")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("field must not be blank")
        return v.strip()

    @field_validator("rubric")
    @classmethod
    def rubric_has_points(cls, v: list[str]) -> list[str]:
        cleaned = [r.strip() for r in v if r and r.strip()]
        if not (2 <= len(cleaned) <= 4):
            raise ValueError("rubric must contain between 2 and 4 non-empty key points")
        return cleaned

    @field_validator("difficulty")
    @classmethod
    def valid_difficulty(cls, v: str) -> str:
        v = v.strip().lower()
        if v not in ("basic", "mid"):
            raise ValueError("difficulty must be 'basic' or 'mid'")
        return v


class MCQBatch(BaseModel):
    questions: list[dict]


class ScenarioBatch(BaseModel):
    questions: list[dict]
