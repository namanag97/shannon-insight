"""Tests for compression-based complexity metrics."""

import os
import zlib
import pytest
from shannon_insight.math.compression import Compression


class TestCompressionRatio:
    """Tests for Compression.compression_ratio."""

    def test_empty_content(self):
        assert Compression.compression_ratio(b"") == 0.0

    def test_below_threshold(self):
        # Content below MIN_SIZE_THRESHOLD (512) should return 0.0
        assert Compression.compression_ratio(b"a" * 100) == 0.0
        assert Compression.compression_ratio(b"a" * 511) == 0.0

    def test_at_threshold(self):
        # Content at threshold should be processed
        content = b"a" * 512
        ratio = Compression.compression_ratio(content)
        # Highly repetitive content compresses well
        assert ratio < 0.1

    def test_repetitive_content_low_ratio(self):
        # Repeated pattern should compress well (low ratio)
        content = b"abc" * 1000  # 3000 bytes, highly repetitive
        ratio = Compression.compression_ratio(content)
        assert ratio < 0.1

    def test_real_source_code_normal_ratio(self):
        # Simulated source code should be in normal range
        code = b"""
def validate_email(email):
    if not email:
        return False
    parts = email.split('@')
    if len(parts) != 2:
        return False
    domain = parts[1]
    if '.' not in domain:
        return False
    return True

def validate_phone(phone):
    digits = ''.join(c for c in phone if c.isdigit())
    if len(digits) < 10:
        return False
    return True

def process_user(name, email, phone):
    result = {}
    result['name'] = name.strip()
    result['email_valid'] = validate_email(email)
    result['phone_valid'] = validate_phone(phone)
    return result
""" * 3  # Make it large enough
        ratio = Compression.compression_ratio(code)
        assert 0.05 < ratio < 0.6

    def test_random_content_high_ratio(self):
        # Random content should not compress well (high ratio)
        content = os.urandom(2000)
        ratio = Compression.compression_ratio(content)
        assert ratio > 0.5

    def test_ratio_in_valid_range(self):
        # Ratio should always be in [0, 1]
        for size in [512, 1000, 5000]:
            content = os.urandom(size)
            ratio = Compression.compression_ratio(content)
            assert 0.0 <= ratio <= 1.0

    def test_gzip_algorithm(self):
        content = b"hello world " * 200
        ratio = Compression.compression_ratio(content, algorithm="gzip")
        assert 0.0 < ratio < 0.3

    def test_bzip2_algorithm(self):
        content = b"hello world " * 200
        ratio = Compression.compression_ratio(content, algorithm="bzip2")
        assert 0.0 < ratio < 0.3

    def test_unknown_algorithm_raises(self):
        with pytest.raises(ValueError, match="Unknown algorithm"):
            Compression.compression_ratio(b"x" * 1000, algorithm="unknown")
