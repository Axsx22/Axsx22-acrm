"""Session C: controlled self-evolution orchestration.

Observation is neutral; evolution is gated. Session C never executes or mutates
active runtime code.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from math import isfinite
from types import MappingProxyType
from typing import Callable, Iterable, Mapping

class ObservationKind(str, Enum):
    PRESSURE="pressure"; AMBIGUITY="ambiguity"; MISSING_CAPABILITY="missing_capability"; EVOLUTION_SIGNAL="evolution_signal"; FAILURE="failure"

@dataclass(frozen=True, slots=True)
class EvolutionObservation:
    observation_id: str; kind: ObservationKind|str; description: str; observed_at: datetime; context: Mapping[str,object]=field(default_factory=dict); source: str="session_c"
    def __post_init__(self):
        if not isinstance(self.observation_id,str) or not self.observation_id.strip(): raise ValueError("observation_id must be non-empty")
        if isinstance(self.kind,str):
            try: object.__setattr__(self,"kind",ObservationKind(self.kind))
            except ValueError as exc: raise ValueError("kind must be a supported ObservationKind") from exc
        if not isinstance(self.description,str) or not self.description.strip(): raise ValueError("description must be non-empty")
        if not isinstance(self.observed_at,datetime) or self.observed_at.tzinfo is None or self.observed_at.utcoffset() is None: raise ValueError("observed_at must be timezone-aware")
        if not isinstance(self.context,Mapping): raise TypeError("context must be a mapping")
        if not isinstance(self.source,str) or not self.source.strip(): raise ValueError("source must be non-empty")
        object.__setattr__(self,"context",MappingProxyType(dict(self.context)))
    @property
    def observed_at_utc(self): return self.observed_at.astimezone(timezone.utc)

class ObservationLog:
    def __init__(self): self._items=[]
    def record(self,observation):
        if not isinstance(observation,EvolutionObservation): raise TypeError("observation must be an EvolutionObservation")
        self._items.append(observation)
    def snapshot(self): return tuple(self._items)

@dataclass(frozen=True, slots=True)
class EvolutionTolerance:
    generation_after:int=3; successful_tests_before_review:int=2; switch_score:float=.70
    def __post_init__(self):
        if not isinstance(self.generation_after,int) or isinstance(self.generation_after,bool) or self.generation_after<1: raise ValueError("generation_after must be >= 1")
        if not isinstance(self.successful_tests_before_review,int) or isinstance(self.successful_tests_before_review,bool) or self.successful_tests_before_review<1: raise ValueError("successful_tests_before_review must be >= 1")
        if not isinstance(self.switch_score,(int,float)) or isinstance(self.switch_score,bool) or not isfinite(float(self.switch_score)) or not 0<=self.switch_score<=1: raise ValueError("switch_score must be finite and between 0.0 and 1.0")

@dataclass(frozen=True, slots=True)
class EvolutionCandidate:
    candidate_id:str; source:str; based_on:tuple[str,...]; successful_test_runs:int=0; test_attempts:int=0; ready_for_review:bool=False
    def __post_init__(self):
        if not self.candidate_id.strip() or not self.source.strip(): raise ValueError("candidate_id and source must be non-empty")
        if not isinstance(self.based_on,tuple): raise TypeError("based_on must be a tuple")
        if self.successful_test_runs<0 or self.test_attempts<0 or self.successful_test_runs>self.test_attempts: raise ValueError("invalid test counters")

@dataclass(frozen=True, slots=True)
class EvolutionContext:
    topic:str; state:Mapping[str,object]=field(default_factory=dict)
    def __post_init__(self):
        if not self.topic.strip(): raise ValueError("topic must be non-empty")
        object.__setattr__(self,"state",MappingProxyType(dict(self.state)))

@dataclass(frozen=True, slots=True)
class SpecialistVote:
    specialist_id:str; vote:float; reliability:float; relevance:float
    def __post_init__(self):
        if not self.specialist_id.strip(): raise ValueError("specialist_id must be non-empty")
        for v in (self.vote,self.reliability,self.relevance):
            if not isinstance(v,(int,float)) or isinstance(v,bool) or not isfinite(float(v)) or not 0<=v<=1: raise ValueError("vote values must be finite and between 0.0 and 1.0")
    @property
    def weight(self): return float(self.reliability)*float(self.relevance)

@dataclass(frozen=True, slots=True)
class EvolutionDecision:
    status:str; candidate:EvolutionCandidate|None; weighted_score:float|None; votes_used:int; reason:str

class EvolutionSessionC:
    def __init__(self,*,tolerance=None,generator,tester,vote_provider): self.tolerance=tolerance or EvolutionTolerance(); self._generator=generator; self._tester=tester; self._vote_provider=vote_provider; self._observation_log=ObservationLog(); self._candidate=None; self._review_complete=False
    @property
    def observations(self): return self._observation_log.snapshot()
    @property
    def candidate(self): return self._candidate
    @property
    def review_complete(self): return self._review_complete
    def record(self,observation):
        if self._review_complete: raise RuntimeError("review cycle is complete")
        self._observation_log.record(observation)
    def generation_ready(self): return len(self.observations)>=self.tolerance.generation_after
    def generate_candidate(self):
        if self._candidate is not None: return self._candidate
        if not self.generation_ready(): return None
        self._candidate=self._generator(self.observations)
        if not isinstance(self._candidate,EvolutionCandidate): raise TypeError("generator must return an EvolutionCandidate")
        return self._candidate
    def review(self,context):
        if self._candidate is None: return EvolutionDecision("WAIT_GENERATION",None,None,0,"generation tolerance has not produced a candidate")
        if self._review_complete: return EvolutionDecision("REVIEW_COMPLETE",self._candidate,None,0,"review has already completed")
        c=self._candidate; passed=bool(self._tester(c)); attempts=c.test_attempts+1; successful=c.successful_test_runs+int(passed); ready=successful>=self.tolerance.successful_tests_before_review
        self._candidate=EvolutionCandidate(c.candidate_id,c.source,c.based_on,successful,attempts,ready)
        if not passed: return EvolutionDecision("REJECT_TEST",self._candidate,None,0,"candidate failed independent test")
        if not ready: return EvolutionDecision("TESTING_PROGRESS",self._candidate,None,0,"successful test gate not yet reached")
        votes=tuple(self._vote_provider(self._candidate,context)); total=sum(v.weight for v in votes)
        if total<=0: self._review_complete=True; return EvolutionDecision("REJECT_VOTE",self._candidate,None,len(votes),"no positive specialist weight")
        score=sum(v.vote*v.weight for v in votes)/total; self._review_complete=True
        return EvolutionDecision("SWITCH_RECOMMENDED" if score>=self.tolerance.switch_score else "RETAIN_CURRENT",self._candidate,score,len(votes),"weighted topic-aware review completed")
