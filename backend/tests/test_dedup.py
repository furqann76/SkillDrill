import pytest

from quizbank.dedup import cosine_similarity, is_near_duplicate


def test_identical_vectors_have_similarity_one():
    v = [1.0, 2.0, 3.0]
    assert cosine_similarity(v, v) == pytest.approx(1.0)


def test_orthogonal_vectors_have_similarity_zero():
    assert cosine_similarity([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)


def test_opposite_vectors_have_similarity_negative_one():
    assert cosine_similarity([1.0, 0.0], [-1.0, 0.0]) == pytest.approx(-1.0)


def test_scale_invariance():
    """Cosine similarity should ignore magnitude, only direction matters."""
    a = [1.0, 2.0, 3.0]
    b = [2.0, 4.0, 6.0]  # same direction, different magnitude
    assert cosine_similarity(a, b) == pytest.approx(1.0)


def test_zero_vector_similarity_is_zero_not_nan():
    assert cosine_similarity([0.0, 0.0], [1.0, 1.0]) == 0.0


def test_no_existing_embeddings_is_never_a_duplicate():
    assert is_near_duplicate([1.0, 0.0], [], threshold=0.9) is False


def test_near_duplicate_detected_above_threshold():
    embedding = [1.0, 0.0]
    near_identical = [0.99, 0.05]  # cosine similarity ~0.999
    assert is_near_duplicate(embedding, [near_identical], threshold=0.9) is True


def test_distinct_question_not_flagged_as_duplicate():
    embedding = [1.0, 0.0]
    unrelated = [0.0, 1.0]
    assert is_near_duplicate(embedding, [unrelated], threshold=0.9) is False


def test_threshold_boundary_is_inclusive():
    v = [1.0, 0.0]
    assert is_near_duplicate(v, [v], threshold=1.0) is True


def test_flags_duplicate_against_any_one_of_several_existing():
    embedding = [1.0, 0.0]
    existing = [[0.0, 1.0], [0.0, -1.0], [0.999, 0.01]]  # third one is near-identical
    assert is_near_duplicate(embedding, existing, threshold=0.9) is True
