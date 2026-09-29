import numpy as np

from stage0.pipeline import best_train_threshold, cluster_entropy, normalize_answer


def test_normalize_answer():
    assert normalize_answer(" The Eiffel Tower. ") == "eiffel tower"


def test_cluster_entropy():
    assert np.isclose(cluster_entropy([0, 0, 1, 1]), np.log(2))
    assert cluster_entropy([0, 0, 0]) == 0.0


def test_training_threshold_is_nondegenerate():
    values = np.asarray([0.0, 0.0, 0.63, 0.63, 1.09, 1.09])
    threshold = best_train_threshold(values)
    labels = values >= threshold
    assert labels.any() and (~labels).any()
