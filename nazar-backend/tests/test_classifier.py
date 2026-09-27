from app.pipeline.spatial_matching import MatchResult
from app.pipeline.anomaly_classifier import classify, ClassificationInput
from app.schemas.anomaly import AnomalyClass

SQUARE_A = [[0, 0], [0, 0.001], [0.001, 0.001], [0.001, 0], [0, 0]]
# Same square shifted by ~2m (well inside the 1-3m drift band) at this latitude.
SQUARE_B_DRIFT = [[0, 0.00002], [0, 0.00102], [0.001, 0.00102], [0.001, 0.00002], [0, 0.00002]]


def _no_match() -> MatchResult:
    return MatchResult("P1", None, 0.0, 0.0, 0.0, 0.0, 0.0, False)


def _matched(score=0.9) -> MatchResult:
    return MatchResult("P1", "S1", score, score, score, score, score, True)


def test_ghost_structure_when_physical_but_no_record():
    result = classify(ClassificationInput(parcel_id="P1", match=_matched(), parcel_attrs={}))
    assert result.anomaly_class == AnomalyClass.GHOST_STRUCTURE


def test_phantom_record_when_record_but_no_physical_structure():
    result = classify(ClassificationInput(
        parcel_id="P1", match=_no_match(), parcel_attrs={"owner": "Ramesh"}
    ))
    assert result.anomaly_class == AnomalyClass.PHANTOM_RECORD


def test_boundary_drift_when_offset_within_band():
    result = classify(ClassificationInput(
        parcel_id="P1", match=_matched(), parcel_attrs={"owner": "Ramesh"},
        structure_attrs={"height_max": 4.0},
        parcel_coords=SQUARE_A, structure_coords=SQUARE_B_DRIFT,
    ))
    assert result.anomaly_class == AnomalyClass.BOUNDARY_DRIFT
    assert result.drift_margin_m is not None


def test_attribute_mismatch_when_geometry_matches_but_attrs_conflict():
    result = classify(ClassificationInput(
        parcel_id="P1", match=_matched(), parcel_attrs={"owner": "Ramesh"},
        structure_attrs={"height_max": 4.0},
        parcel_coords=SQUARE_A, structure_coords=SQUARE_A,  # identical -> no drift
        attribute_conflict_fields=["owner"],
    ))
    assert result.anomaly_class == AnomalyClass.ATTRIBUTE_MISMATCH


def test_duplicate_identity_wins_when_multiple_record_ids():
    result = classify(ClassificationInput(
        parcel_id="P1", match=_matched(), parcel_attrs={"owner": "Ramesh"},
        duplicate_record_ids=["REC-1", "REC-2"],
    ))
    assert result.anomaly_class == AnomalyClass.DUPLICATE_IDENTITY


def test_temporal_ghost_when_presence_flips_across_epochs():
    result = classify(ClassificationInput(
        parcel_id="P1", match=_matched(), parcel_attrs={"owner": "Ramesh"},
        epoch_presence={"2021": True, "2023": False, "2025": True, "2026": False},
    ))
    assert result.anomaly_class == AnomalyClass.TEMPORAL_GHOST


def test_verified_when_everything_aligns():
    result = classify(ClassificationInput(
        parcel_id="P1", match=_matched(), parcel_attrs={"owner": "Ramesh"},
        structure_attrs={"height_max": 4.0},
        parcel_coords=SQUARE_A, structure_coords=SQUARE_A,
    ))
    assert result.anomaly_class == AnomalyClass.VERIFIED
