-- accidental_coupling.sql
-- Detects structural edges between conceptually unrelated files
--
-- Scope: FILE_PAIR
-- Severity: 0.50 (base)
--
-- Criteria:
--   G1 structural edge exists AND concept_overlap(A, B) < 0.2
--   concept_overlap = Jaccard similarity of concept sets
--
-- Since concept sets are not stored per-file in edges, we use
-- semantic_coherence and concept_entropy as proxies. Files with
-- a structural dependency but very different concept profiles
-- (low coherence, different concept counts) suggest accidental coupling.
--
-- When G6 (semantic distance) edges are available, use those directly.
--
-- The $snapshot_id parameter filters to a specific snapshot.

WITH structural AS (
    SELECT source, target
    FROM edges
    WHERE snapshot_id = $snapshot_id
      AND space = 'G1'
),
-- Check for G6 semantic similarity edges
semantic_edges AS (
    SELECT
        source,
        target,
        weight AS semantic_distance
    FROM edges
    WHERE snapshot_id = $snapshot_id
      AND space = 'G6'
)
SELECT
    s.source AS file_a,
    s.target AS file_b,
    fs_a.semantic_coherence AS coherence_a,
    fs_b.semantic_coherence AS coherence_b,
    fs_a.concept_count AS concepts_a,
    fs_b.concept_count AS concepts_b,
    fs_a.concept_entropy AS entropy_a,
    fs_b.concept_entropy AS entropy_b,
    se.semantic_distance,
    -- If we have semantic_distance: high distance = low overlap
    -- If not: use concept disparity as proxy
    CASE
        WHEN se.semantic_distance IS NOT NULL THEN se.semantic_distance
        ELSE ABS(COALESCE(fs_a.concept_entropy, 0) - COALESCE(fs_b.concept_entropy, 0))
             + ABS(COALESCE(fs_a.semantic_coherence, 0) - COALESCE(fs_b.semantic_coherence, 0))
    END AS concept_disparity
FROM structural s
JOIN file_signals fs_a ON s.source = fs_a.file_path AND fs_a.snapshot_id = $snapshot_id
JOIN file_signals fs_b ON s.target = fs_b.file_path AND fs_b.snapshot_id = $snapshot_id
LEFT JOIN semantic_edges se ON (
    (s.source = se.source AND s.target = se.target)
    OR (s.source = se.target AND s.target = se.source)
)
WHERE
    -- Filter for high concept disparity (proxy for concept_overlap < 0.2)
    (
        -- If G6 edges exist, use semantic distance > 0.8 (equiv to overlap < 0.2)
        (se.semantic_distance IS NOT NULL AND se.semantic_distance > 0.8)
        OR
        -- Otherwise use concept profile disparity as proxy
        (se.semantic_distance IS NULL AND (
            ABS(COALESCE(fs_a.concept_entropy, 0) - COALESCE(fs_b.concept_entropy, 0)) > 1.0
            OR (fs_a.semantic_coherence < 0.3 AND fs_b.semantic_coherence > 0.7)
            OR (fs_a.semantic_coherence > 0.7 AND fs_b.semantic_coherence < 0.3)
        ))
    )
    -- Exclude __init__.py
    AND s.source NOT LIKE '%__init__.py'
    AND s.target NOT LIKE '%__init__.py'
    -- Exclude infrastructure files (models, config, logging, etc.)
    AND s.source NOT LIKE '%models.py'
    AND s.target NOT LIKE '%models.py'
    AND s.source NOT LIKE '%config.py'
    AND s.target NOT LIKE '%config.py'
    AND s.source NOT LIKE '%logging%.py'
    AND s.target NOT LIKE '%logging%.py'
    AND s.source NOT LIKE '%_common.py'
    AND s.target NOT LIKE '%_common.py'
    AND s.source NOT LIKE '%utils.py'
    AND s.target NOT LIKE '%utils.py'
    AND s.source NOT LIKE '%helpers.py'
    AND s.target NOT LIKE '%helpers.py'
    AND s.source NOT LIKE '%constants.py'
    AND s.target NOT LIKE '%constants.py'
    AND s.source NOT LIKE '%types.py'
    AND s.target NOT LIKE '%types.py'
    AND s.source NOT LIKE '%schemas.py'
    AND s.target NOT LIKE '%schemas.py'
    AND s.source NOT LIKE '%exceptions.py'
    AND s.target NOT LIKE '%exceptions.py'
    -- Exclude base.py files (base classes are infrastructure)
    AND s.source NOT LIKE '%base.py'
    AND s.target NOT LIKE '%base.py'
    -- Exclude registry files (registries are meant to import many things)
    AND s.source NOT LIKE '%registry.py'
    AND s.target NOT LIKE '%registry.py'
    -- Exclude plugins (plugins are designed for registry import)
    AND s.source NOT LIKE '%plugins/%'
    AND s.target NOT LIKE '%plugins/%'
ORDER BY concept_disparity DESC
LIMIT 20
