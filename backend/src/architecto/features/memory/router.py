from fastapi import APIRouter, Query

from architecto.features.memory.adapters import SqlDecisionStore
from architecto.features.memory.schemas import (
    DecisionOut,
    DecisionsList,
    ProjectOut,
    ProjectsList,
)

router = APIRouter(prefix="/memory", tags=["memory"])


@router.get("/projects", response_model=ProjectsList)
async def list_projects() -> ProjectsList:
    """Projets ayant des décisions enregistrées (les plus récents d'abord)."""
    projects = SqlDecisionStore().list_projects()
    return ProjectsList(
        projects=[
            ProjectOut(slug=p.slug, name=p.name, decision_count=p.decision_count)
            for p in projects
        ]
    )


@router.get("/decisions", response_model=DecisionsList)
async def list_decisions(project: str = Query(..., min_length=1)) -> DecisionsList:
    """Décisions d'architecture (ADR) d'un projet, les plus récentes d'abord."""
    decisions = SqlDecisionStore().list_by_project(project)
    return DecisionsList(
        decisions=[
            DecisionOut(
                id=d.id,
                title=d.title,
                status=d.status,
                context=d.context,
                decision=d.decision,
                consequences=d.consequences,
            )
            for d in decisions
        ]
    )
