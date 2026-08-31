from datetime import datetime, timedelta, timezone

import pytest

from acrm_core.evolution.session_c import EvolutionObservation, ObservationKind
from acrm_core.session_c.observation import EvolutionObservation as CanonicalObservation
from acrm_core.session_c.observation import ObservationLog


def make_observation(number=1, *, offset_hours=0):
    return CanonicalObservation(
        observation_id=f"boundary-{number}",
        kind=ObservationKind.PRESSURE,
        description=f"pressure observation {number}",
        observed_at=datetime(2026, 8, 31, 12, number, tzinfo=timezone(timedelta(hours=offset_hours))),
        context={"signal": "pressure"},
    )


def test_evolution_import_uses_canonical_observation_type():
    item = make_observation()
    assert isinstance(item, EvolutionObservation)
    assert EvolutionObservation is CanonicalObservation


def test_observation_is_normalized_to_utc():
    item = make_observation(offset_hours=4)
    assert item.observed_at.tzinfo == timezone.utc
    assert item.observed_at_utc == item.observed_at


def test_duplicate_observation_ids_are_rejected():
    log = ObservationLog()
    log.record(make_observation(1))
    with pytest.raises(ValueError, match="duplicate observation_id"):
        log.record(make_observation(1))


def test_observation_has_no_judgment_fields():
    item = make_observation()
    assert not hasattr(item, "severity")
    assert not hasattr(item, "score")
    assert not hasattr(item, "topic")
    with pytest.raises(TypeError):
        item.context["score"] = 1.0
