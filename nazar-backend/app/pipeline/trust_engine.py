"""
Module E (part 1): Bayesian Trust Engine.

Tracks a Beta(alpha, beta) reliability distribution per data source
(e.g. "drone_survey_2026", "revenue_dept_up", "cadastral_gis"). Every time a
human official ACCEPTs an anomaly flag sourced from X, X's alpha increments;
every REJECT increments beta. The running mean alpha/(alpha+beta) is the
source's current trust weight, used to break ties in the spatial matching /
classification stages (e.g. when two conflicting records disagree, prefer the
higher-trust source in the rationale).
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class SourceTrust:
    source_id: str
    alpha: float = 1.0  # prior: 1 accept, 1 reject => trust = 0.5
    beta: float = 1.0

    @property
    def trust_score(self) -> float:
        return self.alpha / (self.alpha + self.beta)

    def record_feedback(self, accepted: bool) -> None:
        if accepted:
            self.alpha += 1.0
        else:
            self.beta += 1.0


class TrustEngine:
    """In-memory registry of per-source trust; swap the dict for a DB table in postgis mode."""

    def __init__(self) -> None:
        self._sources: dict[str, SourceTrust] = {}

    def get(self, source_id: str) -> SourceTrust:
        return self._sources.setdefault(source_id, SourceTrust(source_id))

    def record_feedback(self, source_id: str, accepted: bool) -> float:
        source = self.get(source_id)
        source.record_feedback(accepted)
        return source.trust_score

    def all_scores(self) -> dict[str, float]:
        return {sid: s.trust_score for sid, s in self._sources.items()}


trust_engine = TrustEngine()
