#!/usr/bin/env python3
"""
Shannon Insight - Architecture Diagram Generator

Generates high-quality SVG/PNG diagrams of the system architecture.
Requires: pip install matplotlib networkx numpy

Usage:
    python generate_diagrams.py --all          # Generate all diagrams
    python generate_diagrams.py --layers       # Just the layer stack
    python generate_diagrams.py --pipeline     # Just the pipeline
    python generate_diagrams.py --tensor       # Just the tensor visualization
"""

import argparse
import math
from pathlib import Path
from typing import Optional

# Try to import visualization libraries
try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from matplotlib.patches import FancyBboxPatch, ConnectionPatch, Circle, Wedge
    import matplotlib.patheffects as path_effects
    import numpy as np
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("matplotlib not installed. Install with: pip install matplotlib numpy")


# ============ COLOR SCHEMES ============

COLORS = {
    'bg': '#0a0a0f',
    'bg_secondary': '#12121a',
    'text': '#ffffff',
    'text_muted': '#9ca3af',
    'border': '#2a2a3a',

    # Layer colors (from bottom to top)
    'layer_0': '#10b981',  # emerald
    'layer_1': '#14b8a6',  # teal
    'layer_2': '#06b6d4',  # cyan
    'layer_3': '#3b82f6',  # blue
    'layer_4': '#6366f1',  # indigo
    'layer_5': '#a855f7',  # purple
    'layer_6': '#f43f5e',  # rose

    # Relationship colors
    'import': '#6366f1',
    'cochange': '#10b981',
    'author': '#f59e0b',
    'semantic': '#a855f7',
    'clone': '#f43f5e',
    'combined': '#06b6d4',

    # Severity
    'critical': '#ef4444',
    'high': '#f59e0b',
    'medium': '#3b82f6',
    'low': '#6b7280',
}


# ============ LAYER STACK DIAGRAM ============

def generate_layer_stack(output_path: str = 'layer_stack.svg', dpi: int = 150):
    """Generate the 7-layer signal stack diagram."""

    layers = [
        {'id': 6, 'name': 'COMPOSITES', 'signals': 'risk_score, health_score, codebase_health', 'desc': 'Weighted fusion'},
        {'id': 5, 'name': 'CROSS-LAYER', 'signals': 'behavioral_coherence, hidden_coupling', 'desc': 'Multi-graph compare'},
        {'id': 4, 'name': 'TRAJECTORY', 'signals': 'pagerank_velocity, graph_velocity', 'desc': 'Time derivatives'},
        {'id': 3, 'name': 'GRAPH SIGNALS', 'signals': 'pagerank, modularity, fiedler', 'desc': 'Per-graph metrics'},
        {'id': 2, 'name': 'GRAPHS', 'signals': 'G_import, G_cochange, G_author', 'desc': '6 relationship types'},
        {'id': 1, 'name': 'INDEXED FACTS', 'signals': 'events, lifecycle, windows', 'desc': 'Temporal index'},
        {'id': 0, 'name': 'RAW EXTRACTION', 'signals': 'FileSyntax, GitCommit', 'desc': 'Parsing + Git'},
    ]

    fig, ax = plt.subplots(figsize=(14, 10), facecolor=COLORS['bg'])
    ax.set_facecolor(COLORS['bg'])
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Title
    ax.text(7, 9.5, 'The Seven-Layer Signal Stack',
            fontsize=24, fontweight='bold', color=COLORS['text'],
            ha='center', va='center')
    ax.text(7, 9.0, 'Data flows upward through transformation layers',
            fontsize=12, color=COLORS['text_muted'], ha='center', va='center')

    # Draw layers
    layer_height = 0.9
    start_y = 0.5

    for i, layer in enumerate(reversed(layers)):
        y = start_y + i * (layer_height + 0.2)
        color = COLORS[f'layer_{layer["id"]}']

        # Layer box with gradient effect
        rect = FancyBboxPatch(
            (1, y), 12, layer_height,
            boxstyle="round,pad=0.02,rounding_size=0.1",
            facecolor=color,
            edgecolor='white',
            linewidth=1,
            alpha=0.9
        )
        ax.add_patch(rect)

        # Layer ID badge
        badge = Circle((1.8, y + layer_height/2), 0.35,
                       facecolor='white', edgecolor='none', alpha=0.2)
        ax.add_patch(badge)
        ax.text(1.8, y + layer_height/2, f'L{layer["id"]}',
                fontsize=11, fontweight='bold', color='white',
                ha='center', va='center')

        # Layer name
        ax.text(3.0, y + layer_height/2 + 0.15, layer['name'],
                fontsize=14, fontweight='bold', color='white',
                ha='left', va='center')

        # Description
        ax.text(3.0, y + layer_height/2 - 0.15, layer['desc'],
                fontsize=9, color='white', alpha=0.8,
                ha='left', va='center')

        # Signals (right side)
        ax.text(12.8, y + layer_height/2, layer['signals'],
                fontsize=8, color='white', alpha=0.7,
                ha='right', va='center', family='monospace')

        # Arrow between layers
        if i < len(layers) - 1:
            ax.annotate('', xy=(7, y + layer_height + 0.15), xytext=(7, y + layer_height + 0.05),
                       arrowprops=dict(arrowstyle='->', color=COLORS['text_muted'], lw=1.5))

    # Bottom label
    ax.text(7, 0.2, 'Source Code + Git History  →  Insights',
            fontsize=10, color=COLORS['text_muted'], ha='center', va='center')

    # Save
    plt.tight_layout()
    plt.savefig(output_path, dpi=dpi, facecolor=COLORS['bg'], edgecolor='none',
                bbox_inches='tight', pad_inches=0.3)
    plt.close()
    print(f"Generated: {output_path}")


# ============ PIPELINE DIAGRAM ============

def generate_pipeline(output_path: str = 'pipeline.svg', dpi: int = 150):
    """Generate the 6-stage pipeline diagram."""

    stages = [
        {'id': 0, 'name': 'EXTRACT', 'time': '1-5min', 'db': 'facts.db', 'parallel': True},
        {'id': 1, 'name': 'INDEX', 'time': '30s-2min', 'db': 'temporal.db', 'parallel': False},
        {'id': 2, 'name': 'GRAPH', 'time': '40s-2min', 'db': 'graph.db', 'parallel': True},
        {'id': 3, 'name': 'SIGNALS', 'time': '30s-90s', 'db': 'signals.db', 'parallel': True},
        {'id': 4, 'name': 'PATTERNS', 'time': '5-60s', 'db': 'findings.db', 'parallel': True},
        {'id': 5, 'name': 'SNAPSHOT', 'time': '5-10s', 'db': 'snapshots.db', 'parallel': False},
    ]

    colors = ['#10b981', '#14b8a6', '#06b6d4', '#3b82f6', '#6366f1', '#a855f7']

    fig, ax = plt.subplots(figsize=(16, 6), facecolor=COLORS['bg'])
    ax.set_facecolor(COLORS['bg'])
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 6)
    ax.axis('off')

    # Title
    ax.text(8, 5.5, 'Pipeline Execution',
            fontsize=24, fontweight='bold', color=COLORS['text'],
            ha='center', va='center')
    ax.text(8, 5.1, 'Six stages, each persisted to database',
            fontsize=12, color=COLORS['text_muted'], ha='center', va='center')

    # Connection line
    ax.plot([1.5, 14.5], [3, 3], color=COLORS['border'], linewidth=3, zorder=1)

    # Draw stages
    for i, stage in enumerate(stages):
        x = 1.5 + i * 2.4
        y = 3
        color = colors[i]

        # Stage circle
        circle = Circle((x, y), 0.6, facecolor=color, edgecolor='white', linewidth=2, zorder=2)
        ax.add_patch(circle)

        # Stage number
        ax.text(x, y, str(stage['id']), fontsize=18, fontweight='bold',
                color='white', ha='center', va='center', zorder=3)

        # Parallel indicator
        if stage['parallel']:
            ax.text(x, y - 0.35, '∥', fontsize=10, color='white',
                    ha='center', va='center', alpha=0.7, zorder=3)

        # Stage name
        ax.text(x, y + 1.1, stage['name'], fontsize=11, fontweight='bold',
                color=COLORS['text'], ha='center', va='center')

        # Time
        ax.text(x, y + 0.85, stage['time'], fontsize=8,
                color=COLORS['text_muted'], ha='center', va='center',
                family='monospace')

        # Database
        rect = FancyBboxPatch(
            (x - 0.5, y - 1.4), 1.0, 0.4,
            boxstyle="round,pad=0.02,rounding_size=0.05",
            facecolor=COLORS['bg_secondary'],
            edgecolor=COLORS['border'],
            linewidth=1
        )
        ax.add_patch(rect)
        ax.text(x, y - 1.2, stage['db'], fontsize=7,
                color=COLORS['text_muted'], ha='center', va='center',
                family='monospace')

    # Runtime estimates
    estimates = [
        ('Small (<100)', '~30s'),
        ('Medium (100-1K)', '~3min'),
        ('Large (1K-10K)', '~15min'),
    ]

    for i, (size, time) in enumerate(estimates):
        x = 4 + i * 4
        rect = FancyBboxPatch(
            (x - 1.2, 0.3), 2.4, 0.8,
            boxstyle="round,pad=0.02,rounding_size=0.05",
            facecolor=COLORS['bg_secondary'],
            edgecolor=COLORS['border'],
            linewidth=1
        )
        ax.add_patch(rect)
        ax.text(x, 0.8, size, fontsize=9, color=COLORS['text_muted'], ha='center', va='center')
        ax.text(x, 0.5, time, fontsize=11, fontweight='bold', color=COLORS['text'], ha='center', va='center')

    plt.tight_layout()
    plt.savefig(output_path, dpi=dpi, facecolor=COLORS['bg'], edgecolor='none',
                bbox_inches='tight', pad_inches=0.3)
    plt.close()
    print(f"Generated: {output_path}")


# ============ TENSOR DIAGRAM ============

def generate_tensor(output_path: str = 'tensor.svg', dpi: int = 150):
    """Generate the 4D tensor visualization."""

    relationships = [
        ('R1', 'IMPORT', '#6366f1'),
        ('R2', 'COCHANGE', '#10b981'),
        ('R3', 'AUTHOR', '#f59e0b'),
        ('R4', 'SEMANTIC', '#a855f7'),
        ('R5', 'CLONE', '#f43f5e'),
        ('R6', 'COMBINED', '#06b6d4'),
    ]

    fig, ax = plt.subplots(figsize=(14, 10), facecolor=COLORS['bg'])
    ax.set_facecolor(COLORS['bg'])
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Title
    ax.text(7, 9.5, 'The Tensor: T ∈ ℝ^(N×N×K×R)',
            fontsize=24, fontweight='bold', color=COLORS['text'],
            ha='center', va='center', family='monospace')
    ax.text(7, 9.0, 'Files × Files × Time Points × Relationship Types',
            fontsize=12, color=COLORS['text_muted'], ha='center', va='center')

    # Draw stacked matrices (pseudo-3D)
    base_x, base_y = 3, 2
    matrix_size = 3.5
    offset_x, offset_y = 0.4, 0.3

    for i, (rid, name, color) in enumerate(reversed(relationships)):
        x = base_x + i * offset_x
        y = base_y + i * offset_y

        # Matrix background
        rect = FancyBboxPatch(
            (x, y), matrix_size, matrix_size,
            boxstyle="round,pad=0.02,rounding_size=0.05",
            facecolor=color,
            edgecolor='white',
            linewidth=1,
            alpha=0.3 + 0.1 * (5 - i)
        )
        ax.add_patch(rect)

        # Grid cells
        cell_size = matrix_size / 6
        for row in range(6):
            for col in range(6):
                if np.random.random() > 0.6:
                    cell_rect = patches.Rectangle(
                        (x + col * cell_size + 0.05, y + row * cell_size + 0.05),
                        cell_size - 0.1, cell_size - 0.1,
                        facecolor=color,
                        alpha=0.3 + np.random.random() * 0.5
                    )
                    ax.add_patch(cell_rect)

    # Legend
    legend_x = 9.5
    ax.text(legend_x, 7.5, 'Relationship Types (R = 6)',
            fontsize=12, fontweight='bold', color=COLORS['text'],
            ha='left', va='center')

    for i, (rid, name, color) in enumerate(relationships):
        y = 7.0 - i * 0.6

        # Color box
        rect = FancyBboxPatch(
            (legend_x, y - 0.15), 0.4, 0.3,
            boxstyle="round,pad=0.01,rounding_size=0.05",
            facecolor=color,
            edgecolor='none'
        )
        ax.add_patch(rect)

        ax.text(legend_x + 0.2, y, rid, fontsize=9, fontweight='bold',
                color='white', ha='center', va='center')
        ax.text(legend_x + 0.6, y, name, fontsize=10, color=COLORS['text'],
                ha='left', va='center')

    # Formula
    ax.text(7, 0.8, 'T[i, j, t, r] = weight of relationship r from file i to file j at time t',
            fontsize=10, color=COLORS['text_muted'], ha='center', va='center',
            family='monospace',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=COLORS['bg_secondary'], edgecolor=COLORS['border']))

    plt.tight_layout()
    plt.savefig(output_path, dpi=dpi, facecolor=COLORS['bg'], edgecolor='none',
                bbox_inches='tight', pad_inches=0.3)
    plt.close()
    print(f"Generated: {output_path}")


# ============ CROSS-LAYER DIAGRAM ============

def generate_cross_layer(output_path: str = 'cross_layer.svg', dpi: int = 150):
    """Generate the cross-layer comparison diagram."""

    fig, ax = plt.subplots(figsize=(12, 8), facecolor=COLORS['bg'])
    ax.set_facecolor(COLORS['bg'])
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis('off')

    # Title
    ax.text(6, 7.5, 'Cross-Layer Analysis: The Key Innovation',
            fontsize=20, fontweight='bold', color=COLORS['text'],
            ha='center', va='center')
    ax.text(6, 7.0, 'Comparing multiple relationship graphs via mutual information',
            fontsize=11, color=COLORS['text_muted'], ha='center', va='center')

    # Left graph (Structure)
    circle1 = Circle((3, 4), 1.5, facecolor=COLORS['import'],
                     edgecolor='white', linewidth=2, alpha=0.3)
    ax.add_patch(circle1)
    ax.text(3, 4, 'G_import', fontsize=14, fontweight='bold',
            color='white', ha='center', va='center')
    ax.text(3, 2.2, 'STRUCTURE', fontsize=10, color=COLORS['import'],
            ha='center', va='center', fontweight='bold')
    ax.text(3, 1.8, '(what code declares)', fontsize=8, color=COLORS['text_muted'],
            ha='center', va='center')

    # Right graph (Behavior)
    circle2 = Circle((9, 4), 1.5, facecolor=COLORS['cochange'],
                     edgecolor='white', linewidth=2, alpha=0.3)
    ax.add_patch(circle2)
    ax.text(9, 4, 'G_cochange', fontsize=14, fontweight='bold',
            color='white', ha='center', va='center')
    ax.text(9, 2.2, 'BEHAVIOR', fontsize=10, color=COLORS['cochange'],
            ha='center', va='center', fontweight='bold')
    ax.text(9, 1.8, '(what developers do)', fontsize=8, color=COLORS['text_muted'],
            ha='center', va='center')

    # Mutual information arrow
    ax.annotate('', xy=(7.3, 4), xytext=(4.7, 4),
               arrowprops=dict(arrowstyle='<->', color='white', lw=2))
    ax.text(6, 4.5, 'I(X; Y)', fontsize=14, fontweight='bold',
            color='white', ha='center', va='center', family='monospace')
    ax.text(6, 3.5, 'behavioral_coherence', fontsize=9,
            color=COLORS['text_muted'], ha='center', va='center',
            family='monospace')

    # Insight box
    rect = FancyBboxPatch(
        (1.5, 0.5), 9, 1,
        boxstyle="round,pad=0.02,rounding_size=0.1",
        facecolor=COLORS['bg_secondary'],
        edgecolor=COLORS['border'],
        linewidth=1
    )
    ax.add_patch(rect)
    ax.text(6, 1, '💡 When these graphs diverge, that\'s where the bugs hide',
            fontsize=11, color=COLORS['text'], ha='center', va='center')

    plt.tight_layout()
    plt.savefig(output_path, dpi=dpi, facecolor=COLORS['bg'], edgecolor='none',
                bbox_inches='tight', pad_inches=0.3)
    plt.close()
    print(f"Generated: {output_path}")


# ============ FINDER MATRIX ============

def generate_finder_matrix(output_path: str = 'finder_matrix.svg', dpi: int = 150):
    """Generate the finder pattern matrix."""

    finders = {
        'FILE': ['GOD_FILE', 'ORPHAN_CODE', 'PHANTOM_DEP', 'CIRCULAR_DEP',
                 'HIGH_RISK_HUB', 'WEAK_LINK', 'UNSTABLE_FILE', 'BUS_FACTOR',
                 'HOLLOW_CODE', 'CHRONIC'],
        'PAIR': ['HIDDEN_COUPLING', 'CONWAY_VIOLATION', 'ACCIDENTAL_COUPLING',
                 'LAYER_VIOLATION', 'COPY_PASTE_CLONE'],
        'MODULE': ['ZONE_OF_PAIN', 'ZONE_OF_USELESSNESS', 'BOUNDARY_MISMATCH',
                   'KNOWLEDGE_SILO', 'UNSTABLE_INTERFACE', 'RIGID_CORE'],
        'CODEBASE': ['FLAT_ARCHITECTURE'],
    }

    scope_colors = {
        'FILE': '#06b6d4',
        'PAIR': '#3b82f6',
        'MODULE': '#6366f1',
        'CODEBASE': '#a855f7',
    }

    fig, ax = plt.subplots(figsize=(14, 10), facecolor=COLORS['bg'])
    ax.set_facecolor(COLORS['bg'])
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Title
    ax.text(7, 9.5, '22 Pattern Finders',
            fontsize=24, fontweight='bold', color=COLORS['text'],
            ha='center', va='center')
    ax.text(7, 9.0, 'Organized by detection scope',
            fontsize=12, color=COLORS['text_muted'], ha='center', va='center')

    y = 8.2
    for scope, patterns in finders.items():
        color = scope_colors[scope]

        # Scope header
        rect = FancyBboxPatch(
            (0.5, y - 0.3), 2, 0.5,
            boxstyle="round,pad=0.02,rounding_size=0.05",
            facecolor=color,
            edgecolor='none',
            alpha=0.3
        )
        ax.add_patch(rect)
        ax.text(1.5, y - 0.05, scope, fontsize=11, fontweight='bold',
                color=color, ha='center', va='center')

        # Pattern chips
        x = 3
        row_y = y - 0.05
        for pattern in patterns:
            if x + len(pattern) * 0.08 > 13.5:  # Wrap to next line
                x = 3
                row_y -= 0.5

            width = max(1.5, len(pattern) * 0.08 + 0.3)
            rect = FancyBboxPatch(
                (x, row_y - 0.2), width, 0.4,
                boxstyle="round,pad=0.02,rounding_size=0.05",
                facecolor=COLORS['bg_secondary'],
                edgecolor=COLORS['border'],
                linewidth=1
            )
            ax.add_patch(rect)
            ax.text(x + width/2, row_y, pattern, fontsize=7,
                    color=COLORS['text'], ha='center', va='center',
                    family='monospace')
            x += width + 0.2

        y = row_y - 0.8

    plt.tight_layout()
    plt.savefig(output_path, dpi=dpi, facecolor=COLORS['bg'], edgecolor='none',
                bbox_inches='tight', pad_inches=0.3)
    plt.close()
    print(f"Generated: {output_path}")


# ============ FULL SYSTEM OVERVIEW ============

def generate_full_overview(output_path: str = 'full_overview.svg', dpi: int = 150):
    """Generate a complete system overview diagram."""

    fig, ax = plt.subplots(figsize=(20, 14), facecolor=COLORS['bg'])
    ax.set_facecolor(COLORS['bg'])
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 14)
    ax.axis('off')

    # Main title
    ax.text(10, 13.5, 'Shannon Insight: Complete System Architecture',
            fontsize=28, fontweight='bold', color=COLORS['text'],
            ha='center', va='center')

    # The fundamental insight box
    insight_rect = FancyBboxPatch(
        (0.5, 11.5), 19, 1.5,
        boxstyle="round,pad=0.02,rounding_size=0.1",
        facecolor='#6366f1',
        edgecolor='white',
        linewidth=2,
        alpha=0.2
    )
    ax.add_patch(insight_rect)
    ax.text(10, 12.5, 'Core Insight: Code Health = Alignment(Structure, Behavior)',
            fontsize=16, fontweight='bold', color='white', ha='center', va='center')
    ax.text(10, 12.0, 'When imports match co-changes → Healthy | When they diverge → Problems',
            fontsize=11, color=COLORS['text_muted'], ha='center', va='center')

    # Left section: Inputs
    ax.text(2.5, 10.8, 'INPUTS', fontsize=14, fontweight='bold',
            color=COLORS['text_muted'], ha='center', va='center')

    input_rect = FancyBboxPatch(
        (0.5, 8.5), 4, 2,
        boxstyle="round,pad=0.02,rounding_size=0.1",
        facecolor=COLORS['bg_secondary'],
        edgecolor=COLORS['border'],
        linewidth=1
    )
    ax.add_patch(input_rect)
    ax.text(2.5, 10.0, '📁 Source Files', fontsize=11, color=COLORS['text'], ha='center', va='center')
    ax.text(2.5, 9.5, '*.py, *.ts, *.go, *.java...', fontsize=8,
            color=COLORS['text_muted'], ha='center', va='center', family='monospace')
    ax.text(2.5, 9.0, '📜 Git History', fontsize=11, color=COLORS['text'], ha='center', va='center')
    ax.text(2.5, 8.5, 'commits, diffs, blames', fontsize=8,
            color=COLORS['text_muted'], ha='center', va='center', family='monospace')

    # Arrow from inputs to pipeline
    ax.annotate('', xy=(5.3, 9.5), xytext=(4.7, 9.5),
               arrowprops=dict(arrowstyle='->', color=COLORS['text_muted'], lw=2))

    # Center section: Pipeline
    ax.text(10, 10.8, 'PIPELINE (6 Stages)', fontsize=14, fontweight='bold',
            color=COLORS['text_muted'], ha='center', va='center')

    stages = ['EXTRACT', 'INDEX', 'GRAPH', 'SIGNALS', 'PATTERNS', 'SNAPSHOT']
    stage_colors = ['#10b981', '#14b8a6', '#06b6d4', '#3b82f6', '#6366f1', '#a855f7']

    for i, (stage, color) in enumerate(zip(stages, stage_colors)):
        x = 5.5 + i * 1.8
        circle = Circle((x, 9.5), 0.5, facecolor=color, edgecolor='white', linewidth=1)
        ax.add_patch(circle)
        ax.text(x, 9.5, str(i), fontsize=12, fontweight='bold', color='white', ha='center', va='center')
        ax.text(x, 8.7, stage, fontsize=6, color=COLORS['text_muted'], ha='center', va='center', rotation=45)

        if i < len(stages) - 1:
            ax.plot([x + 0.5, x + 1.3], [9.5, 9.5], color=COLORS['border'], lw=2)

    # Arrow from pipeline to outputs
    ax.annotate('', xy=(16.3, 9.5), xytext=(15.7, 9.5),
               arrowprops=dict(arrowstyle='->', color=COLORS['text_muted'], lw=2))

    # Right section: Outputs
    ax.text(17.5, 10.8, 'OUTPUTS', fontsize=14, fontweight='bold',
            color=COLORS['text_muted'], ha='center', va='center')

    output_rect = FancyBboxPatch(
        (15.5, 8.5), 4, 2,
        boxstyle="round,pad=0.02,rounding_size=0.1",
        facecolor=COLORS['bg_secondary'],
        edgecolor='#10b981',
        linewidth=2
    )
    ax.add_patch(output_rect)
    ax.text(17.5, 10.0, '📊 Health Score', fontsize=11, color='#10b981',
            ha='center', va='center', fontweight='bold')
    ax.text(17.5, 9.5, '7.2 / 10', fontsize=16, color=COLORS['text'],
            ha='center', va='center', fontweight='bold')
    ax.text(17.5, 9.0, '🔍 22 Patterns', fontsize=10, color=COLORS['text'], ha='center', va='center')
    ax.text(17.5, 8.6, '79 Signals', fontsize=8, color=COLORS['text_muted'], ha='center', va='center')

    # Bottom section: The Tensor
    tensor_rect = FancyBboxPatch(
        (0.5, 0.5), 6, 7.5,
        boxstyle="round,pad=0.02,rounding_size=0.1",
        facecolor=COLORS['bg_secondary'],
        edgecolor=COLORS['border'],
        linewidth=1
    )
    ax.add_patch(tensor_rect)
    ax.text(3.5, 7.7, 'THE TENSOR', fontsize=12, fontweight='bold', color=COLORS['text'], ha='center', va='center')
    ax.text(3.5, 7.3, 'T ∈ ℝ^(N×N×K×R)', fontsize=10, color=COLORS['text_muted'],
            ha='center', va='center', family='monospace')

    # Mini tensor visualization
    rel_colors = ['#6366f1', '#10b981', '#f59e0b', '#a855f7', '#f43f5e', '#06b6d4']
    rel_names = ['IMPORT', 'COCHANGE', 'AUTHOR', 'SEMANTIC', 'CLONE', 'COMBINED']

    for i, (color, name) in enumerate(zip(rel_colors, rel_names)):
        y = 6.5 - i * 0.8
        rect = patches.Rectangle((1, y - 0.15), 0.3, 0.3, facecolor=color)
        ax.add_patch(rect)
        ax.text(1.5, y, f'R{i+1}: {name}', fontsize=8, color=COLORS['text'],
                ha='left', va='center')

    # Bottom center: Signal Layers
    layers_rect = FancyBboxPatch(
        (7, 0.5), 6, 7.5,
        boxstyle="round,pad=0.02,rounding_size=0.1",
        facecolor=COLORS['bg_secondary'],
        edgecolor=COLORS['border'],
        linewidth=1
    )
    ax.add_patch(layers_rect)
    ax.text(10, 7.7, 'SIGNAL LAYERS', fontsize=12, fontweight='bold', color=COLORS['text'], ha='center', va='center')

    layer_info = [
        ('L6', 'COMPOSITES', '#f43f5e'),
        ('L5', 'CROSS-LAYER', '#a855f7'),
        ('L4', 'TRAJECTORY', '#6366f1'),
        ('L3', 'GRAPH SIGNALS', '#3b82f6'),
        ('L2', 'GRAPHS', '#06b6d4'),
        ('L1', 'INDEXED FACTS', '#14b8a6'),
        ('L0', 'RAW EXTRACTION', '#10b981'),
    ]

    for i, (lid, name, color) in enumerate(layer_info):
        y = 7.0 - i * 0.9
        mini_rect = FancyBboxPatch(
            (7.3, y - 0.25), 5.4, 0.5,
            boxstyle="round,pad=0.02,rounding_size=0.05",
            facecolor=color,
            edgecolor='none',
            alpha=0.7
        )
        ax.add_patch(mini_rect)
        ax.text(7.7, y, lid, fontsize=8, fontweight='bold', color='white', ha='left', va='center')
        ax.text(8.3, y, name, fontsize=8, color='white', ha='left', va='center')

    # Bottom right: Finders
    finders_rect = FancyBboxPatch(
        (13.5, 0.5), 6, 7.5,
        boxstyle="round,pad=0.02,rounding_size=0.1",
        facecolor=COLORS['bg_secondary'],
        edgecolor=COLORS['border'],
        linewidth=1
    )
    ax.add_patch(finders_rect)
    ax.text(16.5, 7.7, 'PATTERN FINDERS', fontsize=12, fontweight='bold', color=COLORS['text'], ha='center', va='center')

    finder_groups = [
        ('CODEBASE', 1, '#a855f7'),
        ('MODULE', 6, '#6366f1'),
        ('PAIR', 5, '#3b82f6'),
        ('FILE', 10, '#06b6d4'),
    ]

    for i, (scope, count, color) in enumerate(finder_groups):
        y = 7.0 - i * 1.5
        ax.text(14, y, f'{scope}:', fontsize=10, fontweight='bold', color=color, ha='left', va='center')
        ax.text(14, y - 0.5, f'{count} patterns', fontsize=9, color=COLORS['text_muted'], ha='left', va='center')

    # Key examples
    examples = ['HIDDEN_COUPLING', 'HIGH_RISK_HUB', 'ZONE_OF_PAIN']
    ax.text(17, 6.5, 'Key patterns:', fontsize=8, color=COLORS['text_muted'], ha='left', va='center')
    for i, ex in enumerate(examples):
        ax.text(17, 6.0 - i * 0.4, f'• {ex}', fontsize=7, color=COLORS['text'],
                ha='left', va='center', family='monospace')

    plt.tight_layout()
    plt.savefig(output_path, dpi=dpi, facecolor=COLORS['bg'], edgecolor='none',
                bbox_inches='tight', pad_inches=0.3)
    plt.close()
    print(f"Generated: {output_path}")


# ============ MAIN ============

def main():
    parser = argparse.ArgumentParser(description='Generate Shannon Insight architecture diagrams')
    parser.add_argument('--all', action='store_true', help='Generate all diagrams')
    parser.add_argument('--layers', action='store_true', help='Generate layer stack diagram')
    parser.add_argument('--pipeline', action='store_true', help='Generate pipeline diagram')
    parser.add_argument('--tensor', action='store_true', help='Generate tensor diagram')
    parser.add_argument('--cross-layer', action='store_true', help='Generate cross-layer diagram')
    parser.add_argument('--finders', action='store_true', help='Generate finder matrix diagram')
    parser.add_argument('--overview', action='store_true', help='Generate full overview diagram')
    parser.add_argument('--output-dir', type=str, default='.', help='Output directory')
    parser.add_argument('--format', type=str, default='png', choices=['png', 'svg', 'pdf'], help='Output format')
    parser.add_argument('--dpi', type=int, default=200, help='DPI for raster formats')

    args = parser.parse_args()

    if not HAS_MATPLOTLIB:
        print("Error: matplotlib is required. Install with: pip install matplotlib numpy")
        return 1

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # If no specific diagram requested, generate all
    if not any([args.layers, args.pipeline, args.tensor, args.cross_layer, args.finders, args.overview]):
        args.all = True

    if args.all or args.layers:
        generate_layer_stack(str(output_dir / f'layer_stack.{args.format}'), args.dpi)

    if args.all or args.pipeline:
        generate_pipeline(str(output_dir / f'pipeline.{args.format}'), args.dpi)

    if args.all or args.tensor:
        generate_tensor(str(output_dir / f'tensor.{args.format}'), args.dpi)

    if args.all or args.cross_layer:
        generate_cross_layer(str(output_dir / f'cross_layer.{args.format}'), args.dpi)

    if args.all or args.finders:
        generate_finder_matrix(str(output_dir / f'finder_matrix.{args.format}'), args.dpi)

    if args.all or args.overview:
        generate_full_overview(str(output_dir / f'full_overview.{args.format}'), args.dpi)

    print(f"\nAll diagrams generated in: {output_dir.absolute()}")
    return 0


if __name__ == '__main__':
    exit(main())
