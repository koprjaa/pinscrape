import numpy as np

from pinscrape.utils import current_epoch_ms, ensure_dir, image_hash


def _gradient_image(reverse: bool = False) -> np.ndarray:
    row = np.linspace(0, 255, 16, dtype=np.uint8)
    if reverse:
        row = row[::-1]
    return np.tile(row, (16, 1))


def test_image_hash_is_deterministic():
    image = _gradient_image()
    assert image_hash(image) == image_hash(image.copy())


def test_image_hash_differs_for_different_images():
    increasing = _gradient_image(reverse=False)
    decreasing = _gradient_image(reverse=True)
    assert image_hash(increasing) != image_hash(decreasing)


def test_ensure_dir_creates_nested_directory(tmp_path):
    target = tmp_path / "a" / "b" / "c"
    result = ensure_dir(str(target))
    assert result == target
    assert target.is_dir()


def test_current_epoch_ms_is_increasing_int():
    first = current_epoch_ms()
    second = current_epoch_ms()
    assert isinstance(first, int)
    assert second >= first
