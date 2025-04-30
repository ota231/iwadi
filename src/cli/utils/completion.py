from typing import List


def complete_sources(incomplete: str) -> List[str]:
    """Tab completion for source names."""
    available_sources = ["arxiv", "ieee", "springer", "acm"]
    return [s for s in available_sources if s.startswith(incomplete)]


def complete_projects(incomplete: str) -> List[str]:
    """Tab completion for project names."""
    # You would implement project name lookup here
    return ["quantum_ml", "nlp_research", "ai_ethics"]
