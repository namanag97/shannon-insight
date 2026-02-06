"""G5 author distance space for Phase 3.

Computes weighted Jaccard distance between author distributions of files.
This enables detection of Conway's law violations (files that change together
but are maintained by different teams).

Distance formula:
    d(A,B) = 1 - Σ_a min(w_a(A), w_a(B)) / Σ_a max(w_a(A), w_a(B))

Where w_a(F) = commits by author a on file F / total commits on file F.

Only returns pairs with distance < 1.0 (files sharing at least one author).
This keeps the representation sparse.
"""

from collections import defaultdict

from ..temporal.models import GitHistory
from .models import AuthorDistance


def compute_author_distances(
    git_history: GitHistory,
    analyzed_files: set[str],
) -> list[AuthorDistance]:
    """Compute weighted Jaccard distance between author distributions.

    Only computes for file pairs that share at least one author (sparse).
    Skips entirely if there are fewer than 2 distinct authors (solo project).

    Args:
        git_history: Git history containing commits with authors and files
        analyzed_files: Set of file paths to consider

    Returns:
        List of AuthorDistance entries for pairs with shared authors
    """
    if not git_history.commits:
        return []

    # Step 1: Build per-file author commit counts
    # file_author_counts[file][author] = number of commits by author on file
    file_author_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    all_authors: set[str] = set()

    for commit in git_history.commits:
        all_authors.add(commit.author)
        for file_path in commit.files:
            if file_path in analyzed_files:
                file_author_counts[file_path][commit.author] += 1

    # Skip solo projects (fewer than 2 distinct authors)
    if len(all_authors) < 2:
        return []

    # Step 2: Convert counts to normalized weights (distributions)
    # author_weights[file][author] = commits_by_author / total_commits_on_file
    author_weights: dict[str, dict[str, float]] = {}
    for file_path, counts in file_author_counts.items():
        total = sum(counts.values())
        if total > 0:
            author_weights[file_path] = {author: count / total for author, count in counts.items()}

    # Step 3: Build author -> files index for sparse computation
    author_files: dict[str, set[str]] = defaultdict(set)
    for file_path, weights in author_weights.items():
        for author in weights:
            author_files[author].add(file_path)

    # Step 4: Compute distances for pairs sharing at least one author
    computed_pairs: set[tuple[str, str]] = set()
    distances: list[AuthorDistance] = []

    for _author, files in author_files.items():
        files_list = sorted(files)  # Sort for determinism
        for i, file_a in enumerate(files_list):
            for file_b in files_list[i + 1 :]:
                pair_key = (file_a, file_b)
                if pair_key in computed_pairs:
                    continue
                computed_pairs.add(pair_key)

                # Compute weighted Jaccard distance
                weights_a = author_weights.get(file_a, {})
                weights_b = author_weights.get(file_b, {})

                all_authors_in_pair = set(weights_a.keys()) | set(weights_b.keys())
                if not all_authors_in_pair:
                    continue

                sum_min = 0.0
                sum_max = 0.0
                for a in all_authors_in_pair:
                    w_a = weights_a.get(a, 0.0)
                    w_b = weights_b.get(a, 0.0)
                    sum_min += min(w_a, w_b)
                    sum_max += max(w_a, w_b)

                if sum_max == 0:
                    distance = 1.0
                else:
                    distance = 1.0 - (sum_min / sum_max)

                # Only include pairs with distance < 1.0 (shared authors)
                if distance < 1.0:
                    distances.append(
                        AuthorDistance(
                            file_a=file_a,
                            file_b=file_b,
                            distance=distance,
                        )
                    )

    return distances


def distinct_author_count(git_history: GitHistory) -> int:
    """Count distinct authors in git history.

    Args:
        git_history: Git history

    Returns:
        Number of distinct authors
    """
    return len({c.author for c in git_history.commits})
