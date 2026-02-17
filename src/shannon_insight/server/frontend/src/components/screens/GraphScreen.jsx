/**
 * Graph Screen - Dependency graph visualization using Cytoscape.js
 *
 * Design principles (from Cambridge Intelligence research):
 * - Purpose-driven: Show dependency structure and community clusters
 * - Progressive disclosure: Detail on demand via click-to-select
 * - Color with meaning: Communities get distinct colors, risk gets red accents
 * - Avoid hairballs: Filtering, community thresholds, layout options
 * - Accessible: Keyboard nav, sufficient contrast, clear legends
 */

import { useEffect, useRef, useState, useCallback, useMemo } from "preact/hooks";
import useStore from "../../state/store.js";
import cytoscape from "cytoscape";
import dagre from "cytoscape-dagre";

// Register layouts
cytoscape.use(dagre);

// Colorblind-safe palette (based on ColorBrewer qualitative)
const COMMUNITY_COLORS = [
  "#2563eb", // blue
  "#dc2626", // red
  "#16a34a", // green
  "#ca8a04", // amber
  "#9333ea", // purple
  "#0891b2", // cyan
  "#ea580c", // orange
  "#4f46e5", // indigo
  "#be185d", // pink
  "#059669", // emerald
  "#7c3aed", // violet
  "#0d9488", // teal
  "#d97706", // yellow
  "#6366f1", // blue-violet
  "#db2777", // fuchsia
  "#65a30d", // lime
];
const OTHER_COLOR = "#4b5563";
const RISK_BORDER_COLOR = "#f59e0b";
const MAX_LEGEND_ITEMS = 12;
const DEFAULT_MIN_COMMUNITY_SIZE = 2;

export function GraphScreen() {
  const data = useStore((s) => s.data);
  const containerRef = useRef(null);
  const cyRef = useRef(null);

  // State
  const [filter, setFilter] = useState("all");
  const [layout, setLayout] = useState("dagre");
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({ nodes: 0, edges: 0 });
  const [selectedNode, setSelectedNode] = useState(null);
  const [minCommunitySize, setMinCommunitySize] = useState(DEFAULT_MIN_COMMUNITY_SIZE);
  const [highlightedCommunity, setHighlightedCommunity] = useState(null);
  const [showLabels, setShowLabels] = useState(true);

  // Compute community statistics
  const communityStats = useMemo(() => {
    if (!data?.files) return { communities: [], totalCount: 0, sizeMap: {} };

    const nodeCommunity = data.node_community || {};
    const sizeMap = {};

    // Build from node_community mapping or file signals
    if (Object.keys(nodeCommunity).length > 0) {
      for (const cid of Object.values(nodeCommunity)) {
        sizeMap[cid] = (sizeMap[cid] || 0) + 1;
      }
    } else {
      // Fallback: get from file signals
      for (const f of Object.values(data.files)) {
        const cid = f.signals?.community ?? 0;
        sizeMap[cid] = (sizeMap[cid] || 0) + 1;
      }
    }

    const sorted = Object.entries(sizeMap)
      .map(([id, size]) => ({ id: parseInt(id), size }))
      .sort((a, b) => b.size - a.size);

    return { communities: sorted, totalCount: sorted.length, sizeMap };
  }, [data]);

  // Filter communities by size threshold
  const { visibleCommunities, otherCommunityIds, otherFileCount } = useMemo(() => {
    const visible = [];
    const otherIds = new Set();
    let otherFiles = 0;

    for (const c of communityStats.communities) {
      if (c.size >= minCommunitySize) {
        visible.push(c);
      } else {
        otherIds.add(c.id);
        otherFiles += c.size;
      }
    }

    return { visibleCommunities: visible, otherCommunityIds: otherIds, otherFileCount: otherFiles };
  }, [communityStats, minCommunitySize]);

  // Color mapping
  const getNodeColor = useCallback((communityId) => {
    if (otherCommunityIds.has(communityId)) return OTHER_COLOR;
    const idx = visibleCommunities.findIndex((c) => c.id === communityId);
    return idx >= 0 ? COMMUNITY_COLORS[idx % COMMUNITY_COLORS.length] : OTHER_COLOR;
  }, [visibleCommunities, otherCommunityIds]);

  // Build and render graph
  const initGraph = useCallback(() => {
    if (!data?.files || !containerRef.current) return;

    if (cyRef.current) {
      cyRef.current.destroy();
      cyRef.current = null;
    }

    setLoading(true);
    setSelectedNode(null);

    const { nodes, edges } = buildGraphElements(data, filter, otherCommunityIds, getNodeColor);
    setStats({ nodes: nodes.length, edges: edges.length });

    if (nodes.length === 0) {
      setLoading(false);
      return;
    }

    requestAnimationFrame(() => {
      if (!containerRef.current) return;

      const layoutConfig = layout === "dagre"
        ? { name: "dagre", rankDir: "TB", nodeSep: 60, rankSep: 80, animate: false }
        : { name: "cose", animate: false, nodeRepulsion: 8000, idealEdgeLength: 100, gravity: 0.25 };

      const cy = cytoscape({
        container: containerRef.current,
        elements: [...nodes, ...edges],
        layout: layoutConfig,
        style: getCytoscapeStyles(showLabels),
        minZoom: 0.02,
        maxZoom: 4,
        wheelSensitivity: 0.2,
        boxSelectionEnabled: false,
      });

      // Node click: show info panel
      cy.on("tap", "node", (evt) => {
        const node = evt.target;
        const d = node.data();
        const fileData = data.files?.[d.id] || {};

        // Collect findings
        const findings = [];
        for (const cat of Object.values(data.categories || {})) {
          for (const f of cat.findings || []) {
            if (f.files?.includes(d.id)) findings.push(f);
          }
        }

        setSelectedNode({
          path: d.id,
          label: d.label,
          community: d.community,
          communityColor: getNodeColor(d.community),
          isOther: d.isOther,
          pagerank: d.pagerank,
          riskScore: d.risk_score,
          findingCount: d.finding_count,
          health: fileData.health,
          role: fileData.role,
          lines: fileData.lines,
          busFactor: fileData.bus_factor,
          blastRadius: fileData.blast_radius,
          inDegree: fileData.signals?.in_degree,
          outDegree: fileData.signals?.out_degree,
          findings: findings.slice(0, 5),
        });

        // Highlight connected nodes
        cy.batch(() => {
          cy.elements().removeClass("path-highlight faded");
          const neighborhood = node.neighborhood().add(node);
          cy.elements().not(neighborhood).addClass("faded");
          neighborhood.addClass("path-highlight");
        });
      });

      // Background click: deselect
      cy.on("tap", (evt) => {
        if (evt.target === cy) {
          setSelectedNode(null);
          setHighlightedCommunity(null);
          cy.elements().removeClass("faded path-highlight dimmed highlighted");
        }
      });

      cyRef.current = cy;

      setTimeout(() => {
        cy.fit(null, 40);
        cy.center();
        setLoading(false);
      }, 100);
    });
  }, [data, filter, layout, otherCommunityIds, getNodeColor, showLabels]);

  // Community highlight effect
  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;

    if (highlightedCommunity === null) {
      cy.elements().removeClass("dimmed highlighted");
      return;
    }

    cy.batch(() => {
      cy.nodes().forEach((node) => {
        const cid = node.data("community");
        const isOther = node.data("isOther");
        const match = highlightedCommunity === "other" ? isOther : cid === highlightedCommunity;

        if (match) {
          node.removeClass("dimmed").addClass("highlighted");
        } else {
          node.removeClass("highlighted").addClass("dimmed");
        }
      });

      cy.edges().forEach((edge) => {
        const srcMatch = highlightedCommunity === "other"
          ? edge.source().data("isOther")
          : edge.source().data("community") === highlightedCommunity;
        const tgtMatch = highlightedCommunity === "other"
          ? edge.target().data("isOther")
          : edge.target().data("community") === highlightedCommunity;

        if (srcMatch || tgtMatch) {
          edge.removeClass("dimmed");
        } else {
          edge.addClass("dimmed");
        }
      });
    });
  }, [highlightedCommunity]);

  // Initialize graph
  useEffect(() => {
    initGraph();
    return () => {
      if (cyRef.current) {
        cyRef.current.destroy();
        cyRef.current = null;
      }
    };
  }, [initGraph]);

  // Zoom controls
  const zoomIn = () => cyRef.current?.zoom({ level: cyRef.current.zoom() * 1.4, renderedPosition: { x: cyRef.current.width() / 2, y: cyRef.current.height() / 2 } });
  const zoomOut = () => cyRef.current?.zoom({ level: cyRef.current.zoom() / 1.4, renderedPosition: { x: cyRef.current.width() / 2, y: cyRef.current.height() / 2 } });
  const fitGraph = () => cyRef.current?.fit(undefined, 40);

  const handleLegendClick = (communityId) => {
    setHighlightedCommunity((prev) => (prev === communityId ? null : communityId));
  };

  if (!data) return null;

  const globalSignals = data.global_signals || {};
  const maxCommSize = communityStats.communities[0]?.size || 10;

  return (
    <div className="graph-screen-v2">
      {/* Header toolbar */}
      <header className="graph-toolbar">
        <div className="graph-toolbar-section">
          <span className="graph-toolbar-label">Filter</span>
          <div className="graph-btn-group">
            {[
              { key: "all", label: `All (${Object.keys(data.files || {}).length})` },
              { key: "top20", label: "Top 20%" },
              { key: "hotspots", label: "With Issues" },
            ].map((opt) => (
              <button
                key={opt.key}
                className={filter === opt.key ? "active" : ""}
                onClick={() => setFilter(opt.key)}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        <div className="graph-toolbar-section">
          <span className="graph-toolbar-label">Layout</span>
          <div className="graph-btn-group">
            <button className={layout === "dagre" ? "active" : ""} onClick={() => setLayout("dagre")}>
              Hierarchical
            </button>
            <button className={layout === "cose" ? "active" : ""} onClick={() => setLayout("cose")}>
              Force
            </button>
          </div>
        </div>

        <div className="graph-toolbar-section">
          <label className="graph-checkbox">
            <input type="checkbox" checked={showLabels} onChange={(e) => setShowLabels(e.target.checked)} />
            <span>Labels</span>
          </label>
        </div>

        <div className="graph-toolbar-section graph-toolbar-slider">
          <span className="graph-toolbar-label">Min cluster size: {minCommunitySize}</span>
          <input
            type="range"
            min="1"
            max={Math.min(20, maxCommSize)}
            value={minCommunitySize}
            onInput={(e) => setMinCommunitySize(parseInt(e.target.value))}
          />
        </div>

        <div className="graph-toolbar-stats">
          <span>{stats.nodes} nodes</span>
          <span>{stats.edges} edges</span>
          {globalSignals.modularity != null && (
            <span title="Louvain modularity score">Q = {globalSignals.modularity.toFixed(3)}</span>
          )}
        </div>
      </header>

      {/* Main content area */}
      <div className="graph-content">
        {/* Left sidebar: Legend */}
        <aside className="graph-sidebar">
          <div className="graph-legend-v2">
            <h3>Communities</h3>
            <p className="graph-legend-subtitle">
              {visibleCommunities.length} shown, {communityStats.totalCount - visibleCommunities.length} in "Other"
            </p>

            <div className="graph-legend-items">
              {visibleCommunities.slice(0, MAX_LEGEND_ITEMS).map((c, i) => (
                <button
                  key={c.id}
                  className={`graph-legend-row ${highlightedCommunity === c.id ? "active" : ""}`}
                  onClick={() => handleLegendClick(c.id)}
                >
                  <span className="graph-legend-color" style={{ background: COMMUNITY_COLORS[i % COMMUNITY_COLORS.length] }} />
                  <span className="graph-legend-label">Cluster {c.id}</span>
                  <span className="graph-legend-count">{c.size}</span>
                </button>
              ))}

              {visibleCommunities.length > MAX_LEGEND_ITEMS && (
                <div className="graph-legend-more">
                  +{visibleCommunities.length - MAX_LEGEND_ITEMS} more clusters
                </div>
              )}

              {otherFileCount > 0 && (
                <button
                  className={`graph-legend-row graph-legend-other ${highlightedCommunity === "other" ? "active" : ""}`}
                  onClick={() => handleLegendClick("other")}
                >
                  <span className="graph-legend-color" style={{ background: OTHER_COLOR }} />
                  <span className="graph-legend-label">Other (small)</span>
                  <span className="graph-legend-count">{otherFileCount}</span>
                </button>
              )}
            </div>

            {highlightedCommunity !== null && (
              <button className="graph-legend-clear" onClick={() => setHighlightedCommunity(null)}>
                Clear selection
              </button>
            )}
          </div>

          {/* Global metrics */}
          <div className="graph-metrics">
            <h3>Graph Metrics</h3>
            <div className="graph-metrics-grid">
              <div className="graph-metric">
                <span className="graph-metric-value">{globalSignals.centrality_gini?.toFixed(3) || "—"}</span>
                <span className="graph-metric-label">Centrality Gini</span>
              </div>
              <div className="graph-metric">
                <span className="graph-metric-value">{globalSignals.orphan_ratio != null ? (globalSignals.orphan_ratio * 100).toFixed(1) + "%" : "—"}</span>
                <span className="graph-metric-label">Orphan Ratio</span>
              </div>
              <div className="graph-metric">
                <span className="graph-metric-value">{globalSignals.cycle_count ?? "—"}</span>
                <span className="graph-metric-label">Cycles</span>
              </div>
              <div className="graph-metric">
                <span className="graph-metric-value">{globalSignals.fiedler_value?.toFixed(3) || "—"}</span>
                <span className="graph-metric-label">Connectivity</span>
              </div>
            </div>
          </div>
        </aside>

        {/* Graph viewport */}
        <main className="graph-viewport-v2">
          {loading && stats.nodes === 0 && (
            <div className="graph-loading-overlay">
              <div className="graph-spinner" />
              <span>Building graph...</span>
            </div>
          )}

          <div
            ref={containerRef}
            className="graph-canvas"
            style={{ opacity: loading && stats.nodes === 0 ? 0 : 1 }}
          />

          {/* Zoom controls */}
          <div className="graph-zoom">
            <button onClick={zoomIn} title="Zoom in (or scroll)">+</button>
            <button onClick={zoomOut} title="Zoom out (or scroll)">−</button>
            <button onClick={fitGraph} title="Fit to viewport">⊡</button>
          </div>

          {/* Empty state */}
          {!loading && stats.nodes === 0 && (
            <div className="graph-empty-state">
              <div className="graph-empty-icon">📊</div>
              <h3>No graph data</h3>
              <p>Run analysis with dependency scanning enabled to visualize the dependency graph.</p>
            </div>
          )}

          {/* Selected node info panel */}
          {selectedNode && (
            <div className="graph-node-panel">
              <header className="graph-panel-header">
                <div className="graph-panel-path" title={selectedNode.path}>
                  {selectedNode.path}
                </div>
                <button className="graph-panel-close" onClick={() => {
                  setSelectedNode(null);
                  cyRef.current?.elements().removeClass("faded path-highlight");
                }}>
                  ×
                </button>
              </header>

              {selectedNode.role && (
                <div className="graph-panel-role">{selectedNode.role.replace(/_/g, " ")}</div>
              )}

              <div className="graph-panel-metrics">
                {selectedNode.health != null && (
                  <div className="graph-panel-metric">
                    <span className="value" style={{ color: selectedNode.health >= 7 ? "var(--green)" : selectedNode.health >= 4 ? "var(--yellow)" : "var(--red)" }}>
                      {selectedNode.health.toFixed(1)}
                    </span>
                    <span className="label">Health</span>
                  </div>
                )}
                <div className="graph-panel-metric">
                  <span className="value">{selectedNode.pagerank?.toFixed(4) || "—"}</span>
                  <span className="label">PageRank</span>
                </div>
                <div className="graph-panel-metric">
                  <span className="value" style={{ color: selectedNode.riskScore > 0.6 ? "var(--red)" : "var(--text)" }}>
                    {selectedNode.riskScore?.toFixed(3) || "—"}
                  </span>
                  <span className="label">Risk</span>
                </div>
                <div className="graph-panel-metric">
                  <span className="value" style={{ color: selectedNode.communityColor }}>
                    {selectedNode.isOther ? "Other" : `#${selectedNode.community}`}
                  </span>
                  <span className="label">Cluster</span>
                </div>
              </div>

              <div className="graph-panel-metrics">
                {selectedNode.lines != null && (
                  <div className="graph-panel-metric">
                    <span className="value">{selectedNode.lines}</span>
                    <span className="label">Lines</span>
                  </div>
                )}
                {selectedNode.inDegree != null && (
                  <div className="graph-panel-metric">
                    <span className="value">{selectedNode.inDegree}</span>
                    <span className="label">In-degree</span>
                  </div>
                )}
                {selectedNode.outDegree != null && (
                  <div className="graph-panel-metric">
                    <span className="value">{selectedNode.outDegree}</span>
                    <span className="label">Out-degree</span>
                  </div>
                )}
                {selectedNode.blastRadius != null && (
                  <div className="graph-panel-metric">
                    <span className="value">{selectedNode.blastRadius}</span>
                    <span className="label">Blast Radius</span>
                  </div>
                )}
              </div>

              {selectedNode.findings.length > 0 && (
                <div className="graph-panel-findings">
                  <h4>Issues ({selectedNode.findingCount})</h4>
                  {selectedNode.findings.map((f, i) => (
                    <div key={i} className="graph-panel-finding">
                      <span className={`finding-dot sev-${f.severity_label?.toLowerCase() || "info"}`} />
                      <span>{f.label || f.finding_type}</span>
                    </div>
                  ))}
                </div>
              )}

              <a
                href={`#files/${encodeURIComponent(selectedNode.path)}`}
                className="graph-panel-link"
              >
                View file details →
              </a>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

/**
 * Build cytoscape elements from data
 */
function buildGraphElements(data, filter, otherCommunityIds, getNodeColor) {
  const files = data.files || {};
  const edges = data.dependency_edges || [];
  const communityMap = data.node_community || {};

  let nodePaths = Object.keys(files);

  // Apply filter
  if (filter === "top20") {
    nodePaths = nodePaths
      .sort((a, b) => (files[b].pagerank || 0) - (files[a].pagerank || 0))
      .slice(0, Math.max(1, Math.ceil(nodePaths.length * 0.2)));
  } else if (filter === "hotspots") {
    nodePaths = nodePaths.filter((p) => (files[p].finding_count || 0) > 0);
  }

  const nodeSet = new Set(nodePaths);

  // Compute scaling
  let maxPagerank = 0;
  for (const path of nodePaths) {
    const pr = files[path].pagerank || 0;
    if (pr > maxPagerank) maxPagerank = pr;
  }

  const nodes = nodePaths.map((path) => {
    const f = files[path];
    const communityId = communityMap[path] ?? f.signals?.community ?? 0;
    const isOther = otherCommunityIds.has(communityId);
    const color = getNodeColor(communityId);
    const hasFindings = (f.finding_count || 0) > 0;

    return {
      data: {
        id: path,
        label: path.split("/").pop(),
        pagerank: f.pagerank || 0,
        risk_score: f.risk_score || 0,
        community: communityId,
        finding_count: f.finding_count || 0,
        isOther,
        nodeColor: color,
        nodeSize: maxPagerank > 0
          ? Math.max(12, Math.sqrt((f.pagerank || 0) / maxPagerank) * 45)
          : 16,
        hasBorder: hasFindings,
      },
    };
  });

  const edgeElements = edges
    .filter(([src, tgt]) => nodeSet.has(src) && nodeSet.has(tgt))
    .map(([src, tgt], i) => ({
      data: { id: `e${i}`, source: src, target: tgt },
    }));

  return { nodes, edges: edgeElements };
}

/**
 * Cytoscape stylesheet
 */
function getCytoscapeStyles(showLabels) {
  return [
    {
      selector: "node",
      style: {
        "background-color": "data(nodeColor)",
        width: "data(nodeSize)",
        height: "data(nodeSize)",
        label: showLabels ? "data(label)" : "",
        "font-size": "9px",
        "font-family": "'JetBrains Mono', monospace",
        color: "#e5e5e5",
        "text-valign": "bottom",
        "text-margin-y": 3,
        "text-halign": "center",
        "text-max-width": "70px",
        "text-wrap": "ellipsis",
        "border-width": (ele) => (ele.data("hasBorder") ? 2.5 : 0),
        "border-color": RISK_BORDER_COLOR,
        opacity: (ele) => (ele.data("isOther") ? 0.5 : 0.9),
      },
    },
    {
      selector: "edge",
      style: {
        width: 1.5,
        "line-color": "#3f3f46",
        "target-arrow-color": "#52525b",
        "target-arrow-shape": "triangle",
        "curve-style": "bezier",
        opacity: 0.4,
        "arrow-scale": 0.6,
      },
    },
    {
      selector: "node.highlighted",
      style: {
        opacity: 1,
        "border-width": 3,
        "border-color": "#ffffff",
        "z-index": 10,
      },
    },
    {
      selector: "node.dimmed",
      style: {
        opacity: 0.08,
        "text-opacity": 0,
      },
    },
    {
      selector: "edge.dimmed",
      style: {
        opacity: 0.03,
      },
    },
    {
      selector: "node.path-highlight",
      style: {
        opacity: 1,
        "border-width": 2,
        "border-color": "#3b82f6",
      },
    },
    {
      selector: "node.faded",
      style: {
        opacity: 0.15,
        "text-opacity": 0,
      },
    },
    {
      selector: "edge.faded",
      style: {
        opacity: 0.05,
      },
    },
  ];
}
