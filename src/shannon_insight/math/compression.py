"""Compression-based complexity using Kolmogorov complexity approximation.

Reference: Li & Vitanyi, "An Introduction to Kolmogorov Complexity
and Its Applications", 2008.

The compression ratio approximates normalized Kolmogorov complexity:
    K(s) <= |C(s)| <= K(s) + O(1)
    Ratio = |C(s)| / |s|
"""

import zlib
from typing import Literal


class Compression:
    """Compression-based complexity metrics."""

    MIN_SIZE_THRESHOLD = 512  # bytes; below this, compression ratios are unreliable

    @staticmethod
    def compression_ratio(
        content: bytes,
        algorithm: Literal["zlib", "gzip", "bzip2"] = "zlib",
        level: int = 9,
    ) -> float:
        """Compute compression ratio as Kolmogorov complexity approximation.

        Args:
            content: Raw bytes to compress.
            algorithm: Compression algorithm (default: zlib level 9).
            level: Compression level (0-9, default: 9 for maximum).

        Returns:
            Compression ratio = compressed_size / original_size in [0, 1].

        Calibration:
            < 0.20: Highly repetitive (possible duplication)
            0.20-0.45: Normal source code
            0.45-0.65: Dense, complex
            > 0.65: Very dense or already compressed

        Edge Cases:
            - Empty or tiny files (< MIN_SIZE_THRESHOLD): Return 0.0
            - Compression inflation: Return 1.0
        """
        if not content or len(content) < Compression.MIN_SIZE_THRESHOLD:
            return 0.0

        original_size = len(content)

        if algorithm == "zlib":
            compressed = zlib.compress(content, level=level)
        elif algorithm == "gzip":
            import gzip as gzip_module

            compressed = gzip_module.compress(content, compresslevel=level)
        elif algorithm == "bzip2":
            import bz2

            compressed = bz2.compress(content, compresslevel=level)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")

        compressed_size = len(compressed)

        # Compression can sometimes inflate small or already-compressed data
        if compressed_size >= original_size:
            return 1.0

        return compressed_size / original_size
