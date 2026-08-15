from pydantic import BaseModel


class ProjectOut(BaseModel):
    slug: str
    name: str
    decision_count: int


class DecisionOut(BaseModel):
    id: str
    title: str
    status: str
    context: str
    decision: str
    consequences: str


class ProjectsList(BaseModel):
    projects: list[ProjectOut]


class DecisionsList(BaseModel):
    decisions: list[DecisionOut]
