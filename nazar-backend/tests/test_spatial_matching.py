from app.pipeline.spatial_matching import match_parcels_to_structures, composite_score

SQUARE = [[0, 0], [0, 0.001], [0.001, 0.001], [0.001, 0], [0, 0]]
FAR_AWAY = [[1, 1], [1, 1.001], [1.001, 1.001], [1.001, 1], [1, 1]]


def test_identical_polygons_score_near_one():
    s, iou, centroid, edge, attr = composite_score(SQUARE, SQUARE, {}, {}, [])
    assert iou == 1.0
    assert s > 0.9


def test_far_apart_polygons_score_near_zero():
    s, iou, centroid, edge, attr = composite_score(SQUARE, FAR_AWAY, {}, {}, [])
    assert iou == 0.0
    assert s < 0.1


def test_greedy_matching_pairs_best_candidates():
    parcels = [{"id": "P1", "coords": SQUARE, "attrs": {}}]
    structures = [
        {"id": "S1", "coords": FAR_AWAY, "attrs": {}},
        {"id": "S2", "coords": SQUARE, "attrs": {}},
    ]
    results = match_parcels_to_structures(parcels, structures)
    assert len(results) == 1
    assert results[0].structure_id == "S2"
    assert results[0].matched is True


def test_no_structures_means_unmatched():
    parcels = [{"id": "P1", "coords": SQUARE, "attrs": {}}]
    results = match_parcels_to_structures(parcels, [])
    assert results[0].matched is False
    assert results[0].structure_id is None
