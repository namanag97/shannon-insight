/**
 * Graph screen - dependency graph visualization using Cytoscape.js.
 *
 * Only rendered when currentScreen === "graph" (lazy loading).
 * Shows file dependency graph colored by Louvain community,
 * sized by PageRank, with yellow borders for files with findings.
 *
 * Features:
 * - Community size threshold filtering (slider)
 * - Small communities merged into "Other" (gray)
 * - Sorted, limited, clickable community legend
 * - Zoom controls (in/out/fit)
 * - Click-to-select info panel (stays on graph)
 * - Visual hierarchy: large community borders, faded isolates
 */

import { useEffect, useRef, useState, useCallback, useMemo } from "preact/hooks";
import useStore from "../../state/store.js";
import cytoscape from "cytoscape";
import dagre from "cytoscape-dagre";

// Register dagre layout once
cytoscape.use(dagre);

// Color palette for communities (20 distinct hues for better coverage)
const COMMUNITY_COLORS = [
  "#3b82f6", "#ef4444", "#10b981", "#f59e0b",
  "#8b5cf6", "#ec4899", "#06b6d4", "#84cc16",
  "#f97316", "#14b8a6", "#a855f7", "#e11d48",
  "#0ea5e9", "#65a30d", "#d946ef", "#0891b2",
  "#dc2626", "#059669", "#ca8a04", "#7c3aed",
];
const OTHER_COLOR = "#555555";
const MAX_LEGEND_ITEMS = 20;
const DEFAULT_MIN_COMMUNITY_SIZE = 3;

export function GraphScreen() {
  const data = useStore((s) => s.data);
  const containerRef = useRef(null);
  const cyRef = useRef(null);
  const [filter, setFilter] = useState("all");
  const [loading, setLoading] = useState(true);
  const [nodeCount, setNodeCount] = useState(0);
  const [edgeCount, setEdgeCount] = useState(0);
  const [selectedNode, setSelectedNode] = useState(null);
  const [minCommunitySize, setMinCommunitySize] = useState(DEFAULT_MIN_COMMUNITY_SIZE);
  const [highlightedCommunity, setHighlightedCommunity] = useState(null);

  // Compute community stats from data
  const communityStats = useMemo(() => {
    if (!data) return { communities: [], totalCount: 0, communityMap: {} };

    const rawCommunities = data.communities || [];
    const nodeCommunity = data.node_community || {};

    // Build community size map from communities array
    const sizeMap = {};
    for (const c of rawCommunities) {
      sizeMap[c.id] = c.size || (c.members ? c.members.length : 0);
    }

    // If no communities data but we have node_community, build from that
    if (rawCommunities.length === 0 && Object.keys(nodeCommunity).length > 0) {
      const counts = {};
      for (const cid of Object.values(nodeCommunity)) {
        counts[cid] = (counts[cid] || 0) + 1;
      }
      for (const [cid, count] of Object.entries(counts)) {
        sizeMap[parseInt(cid)] = count;
      }
    }

    const totalCount = Object.keys(sizeMap).length;

    // Sort by size descending
    const sorted = Object.entries(sizeMap)
      .map(([id, size]) => ({ id: parseInt(id), size }))
      .sort((a, b) => b.size - a.size);

    return { communities: sorted, totalCount, communityMap: sizeMap };
  }, [data]);

  // Compute which communities pass the threshold and which are "Other"
  const { visibleCommunities, otherCommunityIds, otherFileCount, shownCount } = useMemo(() => {
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

    return {
      visibleCommunities: visible,
      otherCommunityIds: otherIds,
      otherFileCount: otherFiles,
      shownCount: visible.length,
    };
  }, [communityStats, minCommunitySize]);

  // Map community id -> display color (accounting for "Other")
  const communityColorMap = useMemo(() => {
    const map = {};
    for (let i = 0; i < visibleCommunities.length; i++) {
      map[visibleCommunities[i].id] = COMMUNITY_COLORS[i % COMMUNITY_COLORS.length];
    }
    return map;
  }, [visibleCommunities]);

  const getNodeColor = useCallback((communityId) => {
    if (otherCommunityIds.has(communityId)) return OTHER_COLOR;
    return communityColorMap[communityId] || OTHER_COLOR;
  }, [communityColorMap, otherCommunityIds]);

  const initGraph = useCallback(() => {
    if (!data || !containerRef.current) return;

    // Destroy previous instance
    if (cyRef.current) {
      cyRef.current.destroy();
      cyRef.current = null;
    }

    setLoading(true);
    setSelectedNode(null);

    // Build graph elements
    const { nodes, edges } = buildGraphElements(data, filter, otherCommunityIds, getNodeColor);
    setNodeCount(nodes.length);
    setEdgeCount(edges.length);

    if (nodes.length === 0) {
      setLoading(false);
      return;
    }

    // Use requestAnimationFrame to let loading state render first
    requestAnimationFrame(() => {
      if (!containerRef.current) return;

      const cy = cytoscape({
        container: containerRef.current,
        elements: [...nodes, ...edges],
        layout: {
          name: "dagre",
          rankDir: "TB",
          nodeSep: 80,
          rankSep: 100,
          animate: false,
        },
        style: getCytoscapeStyles(),
        minZoom: 0.05,
        maxZoom: 5,
        wheelSensitivity: 0.3,
        boxSelectionEnabled: false,
      });

      // Click: select node and show info panel (do NOT navigate away)
      cy.on("tap", "node", (evt) => {
        const node = evt.target;
        const nodeData = node.data();

        // Collect findings for this file
        const filePath = nodeData.id;
        const fileData = data.files?.[filePath] || {};
        const allFindings = [];
        const categories = data.categories || {};
        for (const cat of Object.values(categories)) {
          for (const f of cat.findings || []) {
            if (f.files && f.files.includes(filePath)) {
              allFindings.push(f);
            }
          }
        }

        setSelectedNode({
          path: filePath,
          label: nodeData.label,
          community: nodeData.community,
          communityColor: getNodeColor(nodeData.community),
          isOther: nodeData.isOther,
          pagerank: nodeData.pagerank,
          riskScore: nodeData.risk_score,
          findingCount: nodeData.finding_count,
          health: fileData.health,
          role: fileData.role,
          lines: fileData.lines,
          busFactor: fileData.bus_factor,
          blastRadius: fileData.blast_radius,
          cognitiveLoad: fileData.cognitive_load,
          findings: allFindings.slice(0, 5),
        });
      });

      // Click background: deselect
      cy.on("tap", (evt) => {
        if (evt.target === cy) {
          setSelectedNode(null);
          setHighlightedCommunity(null);
          // Reset all node opacity
          cy.nodes().removeClass("dimmed highlighted");
          cy.edges().removeClass("dimmed");
        }
      });

      cyRef.current = cy;
      setLoading(false);
    });
  }, [data, filter, otherCommunityIds, getNodeColor]);

  // Effect: highlight/dim when a community is selected from legend
  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;

    if (highlightedCommunity === null) {
      cy.nodes().removeClass("dimmed highlighted");
      cy.edges().removeClass("dimmed");
      return;
    }

    cy.batch(() => {
      cy.nodes().forEach((node) => {
        const cid = node.data("community");
        const isOther = node.data("isOther");

        let match = false;
        if (highlightedCommunity === "other") {
          match = isOther;
        } else {
          match = cid === highlightedCommunity;
        }

        if (match) {
          node.removeClass("dimmed").addClass("highlighted");
        } else {
          node.removeClass("highlighted").addClass("dimmed");
        }
      });

      cy.edges().forEach((edge) => {
        const srcComm = edge.source().data("community");
        const tgtComm = edge.target().data("community");
        const srcOther = edge.source().data("isOther");
        const tgtOther = edge.target().data("isOther");

        let match = false;
        if (highlightedCommunity === "other") {
          match = srcOther || tgtOther;
        } else {
          match = srcComm === highlightedCommunity || tgtComm === highlightedCommunity;
        }

        if (match) {
          edge.removeClass("dimmed");
        } else {
          edge.addClass("dimmed");
        }
      });
    });
  }, [highlightedCommunity]);

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
  const handleZoomIn = useCallback(() => {
    const cy = cyRef.current;
    if (cy) cy.zoom({ level: cy.zoom() * 1.3, renderedPosition: { x: cy.width() / 2, y: cy.height() / 2 } });
  }, []);

  const handleZoomOut = useCallback(() => {
    const cy = cyRef.current;
    if (cy) cy.zoom({ level: cy.zoom() / 1.3, renderedPosition: { x: cy.width() / 2, y: cy.height() / 2 } });
  }, []);

  const handleFit = useCallback(() => {
    const cy = cyRef.current;
    if (cy) cy.fit(undefined, 40);
  }, []);

  // Legend click handler
  const handleLegendClick = useCallback((communityId) => {
    setHighlightedCommunity((prev) => (prev === communityId ? null : communityId));
  }, []);

  // Navigate to file detail from info panel
  const handleOpenFile = useCallback((path) => {
    location.hash = "files/" + encodeURIComponent(path);
  }, []);

  if (!data) return null;

  const modScore = data.modularity_score;

  // Compute max community size for slider max
  const maxCommunitySize = communityStats.communities.length > 0
    ? Math.min(20, communityStats.communities[0].size)
    : 10;

  return (
    <div class="graph-screen">
      {/* Top controls bar */}
      <div class="graph-controls">
        <button
          class={filter === "all" ? "active" : ""}
          onClick={() => setFilter("all")}
        >
          All ({Object.keys(data.files || {}).length})
        </button>
        <button
          class={filter === "top20" ? "active" : ""}
          onClick={() => setFilter("top20")}
        >
          Top 20%
        </button>
        <button
          class={filter === "hotspots" ? "active" : ""}
          onClick={() => setFilter("hotspots")}
        >
          Hotspots
        </button>

        <div class="graph-controls-separator" />

        {/* Community size threshold slider */}
        <div class="graph-slider-group">
          <label class="graph-slider-label">
            Min community size: {minCommunitySize}
          </label>
          <input
            type="range"
            min="1"
            max={maxCommunitySize}
            value={minCommunitySize}
            onInput={(e) => setMinCommunitySize(parseInt(e.target.value))}
            class="graph-slider"
          />
        </div>

        <div class="graph-stats">
          {nodeCount} nodes | {edgeCount} edges
          {communityStats.totalCount > 0 && (
            <span>
              {" | "}Showing {shownCount} of {communityStats.totalCount} communities
              {otherFileCount > 0 && ` (+${otherFileCount} in Other)`}
            </span>
          )}
          {modScore > 0 && ` | Q=${modScore.toFixed(3)}`}
        </div>
      </div>

      <div class="graph-main-area">
        {/* Community legend (left sidebar) */}
        {visibleCommunities.length > 0 && (
          <div class="graph-legend">
            <div class="graph-legend-title">Communities</div>
            <div class="graph-legend-list">
              {visibleCommunities.slice(0, MAX_LEGEND_ITEMS).map((c, i) => (
                <div
                  key={c.id}
                  class={`graph-legend-item ${highlightedCommunity === c.id ? "active" : ""}`}
                  onClick={() => handleLegendClick(c.id)}
                >
                  <span
                    class="graph-legend-swatch"
                    style={{ background: COMMUNITY_COLORS[i % COMMUNITY_COLORS.length] }}
                  />
                  <span class="graph-legend-id">#{c.id}</span>
                  <span class="graph-legend-size">{c.size} files</span>
                </div>
              ))}
              {visibleCommunities.length > MAX_LEGEND_ITEMS && (
                <div class="graph-legend-overflow">
                  +{visibleCommunities.length - MAX_LEGEND_ITEMS} more
                </div>
              )}
              {otherFileCount > 0 && (
                <div
                  class={`graph-legend-item graph-legend-other ${highlightedCommunity === "other" ? "active" : ""}`}
                  onClick={() => handleLegendClick("other")}
                >
                  <span
                    class="graph-legend-swatch"
                    style={{ background: OTHER_COLOR }}
                  />
                  <span class="graph-legend-id">Other</span>
                  <span class="graph-legend-size">
                    {otherFileCount} files ({communityStats.totalCount - shownCount} groups)
                  </span>
                </div>
              )}
            </div>
            {highlightedCommunity !== null && (
              <button
                class="graph-legend-clear"
                onClick={() => setHighlightedCommunity(null)}
              >
                Clear selection
              </button>
            )}
          </div>
        )}

        {/* Graph viewport */}
        <div class="graph-viewport">
          {loading && nodeCount === 0 && (
            <div class="graph-loading">
              <div class="graph-loading-text">Building graph</div>
            </div>
          )}
          <div
            ref={containerRef}
            class="graph-container"
            style={{ visibility: loading && nodeCount === 0 ? "hidden" : "visible" }}
          />

          {/* Zoom controls */}
          <div class="graph-zoom-controls">
            <button onClick={handleZoomIn} title="Zoom in">+</button>
            <button onClick={handleZoomOut} title="Zoom out">-</button>
            <button onClick={handleFit} title="Fit to viewport">Fit</button>
          </div>

          {/* Info panel (shown when node is selected) */}
          {selectedNode && (
            <div class="graph-info-panel">
              <div class="graph-info-header">
                <div class="graph-info-path">{selectedNode.path}</div>
                <button
                  class="graph-info-close"
                  onClick={() => setSelectedNode(null)}
                >
                  x
                </button>
              </div>

              {selectedNode.role && (
                <div class="graph-info-role">{selectedNode.role}</div>
              )}

              <div class="graph-info-grid">
                {selectedNode.health != null && (
                  <div class="graph-info-metric">
                    <span class="graph-info-metric-val">{selectedNode.health}</span>
                    <span class="graph-info-metric-label">Health</span>
                  </div>
                )}
                <div class="graph-info-metric">
                  <span class="graph-info-metric-val">{selectedNode.pagerank.toFixed(4)}</span>
                  <span class="graph-info-metric-label">PageRank</span>
                </div>
                <div class="graph-info-metric">
                  <span class="graph-info-metric-val">{selectedNode.riskScore.toFixed(3)}</span>
                  <span class="graph-info-metric-label">Risk</span>
                </div>
                <div class="graph-info-metric">
                  <span
                    class="graph-info-metric-val"
                    style={{ color: selectedNode.communityColor }}
                  >
                    {selectedNode.isOther ? "Other" : `#${selectedNode.community}`}
                  </span>
                  <span class="graph-info-metric-label">Community</span>
                </div>
              </div>

              <div class="graph-info-grid">
                {selectedNode.lines != null && (
                  <div class="graph-info-metric">
                    <span class="graph-info-metric-val">{selectedNode.lines}</span>
                    <span class="graph-info-metric-label">Lines</span>
                  </div>
                )}
                {selectedNode.blastRadius != null && (
                  <div class="graph-info-metric">
                    <span class="graph-info-metric-val">{selectedNode.blastRadius}</span>
                    <span class="graph-info-metric-label">Blast Radius</span>
                  </div>
                )}
                {selectedNode.busFactor != null && (
                  <div class="graph-info-metric">
                    <span class="graph-info-metric-val">{selectedNode.busFactor}</span>
                    <span class="graph-info-metric-label">Bus Factor</span>
                  </div>
                )}
                {selectedNode.cognitiveLoad != null && selectedNode.cognitiveLoad > 0 && (
                  <div class="graph-info-metric">
                    <span class="graph-info-metric-val">{selectedNode.cognitiveLoad}</span>
                    <span class="graph-info-metric-label">Cognitive Load</span>
                  </div>
                )}
              </div>

              {selectedNode.findings.length > 0 && (
                <div class="graph-info-findings">
                  <div class="graph-info-findings-title">
                    Findings ({selectedNode.findingCount})
                  </div>
                  {selectedNode.findings.map((f, i) => (
                    <div key={i} class="graph-info-finding-row">
                      <span class={`sev-dot ${f.severity_label?.toLowerCase() || "info"}`} />
                      <span class="graph-info-finding-text">
                        {f.label || f.finding_type}
                      </span>
                    </div>
                  ))}
                </div>
              )}

              <button
                class="graph-info-open-btn"
                onClick={() => handleOpenFile(selectedNode.path)}
              >
                Open file detail
              </button>
            </div>
          )}

          {!loading && nodeCount === 0 && (
            <div class="graph-empty">
              <div class="empty-state-title">No graph data available</div>
              <div class="empty-state-hint">
                Run analysis with dependency scanning enabled to visualize the graph.
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

/**
 * Build cytoscape elements from dashboard data and current filter.
 * Marks nodes in small communities as "isOther" and colors them gray.
 */
function buildGraphElements(data, filter, otherCommunityIds, getNodeColor) {
  const files = data.files || {};
  const edges = data.dependency_edges || [];
  const communityMap = data.node_community || {};

  // Determine which nodes to show
  let nodePaths = Object.keys(files);

  if (filter === "top20") {
    nodePaths = nodePaths
      .sort((a, b) => (files[b].pagerank || 0) - (files[a].pagerank || 0))
      .slice(0, Math.max(1, Math.ceil(nodePaths.length * 0.2)));
  } else if (filter === "hotspots") {
    nodePaths = nodePaths.filter((p) => (files[p].finding_count || 0) > 0);
  }

  const nodeSet = new Set(nodePaths);

  // Compute max pagerank for scaling
  let maxPagerank = 0;
  for (const path of nodePaths) {
    const pr = files[path].pagerank || 0;
    if (pr > maxPagerank) maxPagerank = pr;
  }

  // Build node elements
  const nodes = nodePaths.map((path) => {
    const f = files[path];
    const communityId = communityMap[path] ?? (f.signals?.community ?? 0);
    const isOther = otherCommunityIds.has(communityId);
    const color = getNodeColor(communityId);

    return {
      data: {
        id: path,
        label: path.split("/").pop(),
        pagerank: f.pagerank || 0,
        risk_score: f.risk_score || 0,
        community: communityId,
        finding_count: f.finding_count || 0,
        isOther: isOther,
        nodeColor: color,
        // Scaled size: use sqrt for better visual distribution
        nodeSize: maxPagerank > 0
          ? Math.max(16, Math.sqrt((f.pagerank || 0) / maxPagerank) * 50)
          : 20,
        // Large communities get thicker border for visual weight
        communityBorder: isOther ? 0 : 1,
      },
    };
  });

  // Build edge elements (only between visible nodes)
  const edgeElements = edges
    .filter(([src, tgt]) => nodeSet.has(src) && nodeSet.has(tgt))
    .map(([src, tgt], i) => ({
      data: { id: `e${i}`, source: src, target: tgt },
    }));

  return { nodes, edges: edgeElements };
}

/**
 * Cytoscape stylesheet.
 */
function getCytoscapeStyles() {
  return [
    {
      selector: "node",
      style: {
        "background-color": "data(nodeColor)",
        label: "data(label)",
        width: "data(nodeSize)",
        height: "data(nodeSize)",
        "font-size": "10px",
        "font-family": "'JetBrains Mono', 'Fira Code', 'SF Mono', monospace",
        "font-weight": "500",
        color: "#f0f0f0",
        "text-valign": "bottom",
        "text-margin-y": 4,
        "text-halign": "center",
        "border-width": function (ele) {
          if (ele.data("finding_count") > 0) return 3;
          return ele.data("communityBorder");
        },
        "border-color": function (ele) {
          if (ele.data("finding_count") > 0) return "#eab308";
          return ele.data("nodeColor");
        },
        "border-opacity": function (ele) {
          if (ele.data("finding_count") > 0) return 1;
          return 0.3;
        },
        "text-max-width": "80px",
        "text-wrap": "ellipsis",
        "overlay-padding": "4px",
        opacity: function (ele) {
          // Fade isolated "Other" nodes slightly
          return ele.data("isOther") ? 0.5 : 1;
        },
      },
    },
    {
      selector: "edge",
      style: {
        width: 2,
        "line-color": "#555555",
        "target-arrow-color": "#666666",
        "target-arrow-shape": "triangle",
        "curve-style": "bezier",
        opacity: 0.6,
        "arrow-scale": 0.8,
      },
    },
    {
      selector: "node:active",
      style: {
        "overlay-color": "#3b82f6",
        "overlay-opacity": 0.15,
      },
    },
    // Highlighted community
    {
      selector: "node.highlighted",
      style: {
        opacity: 1,
        "border-width": 3,
        "border-color": "#ffffff",
        "border-opacity": 0.6,
        "font-size": "10px",
        "z-index": 10,
      },
    },
    // Dimmed nodes (not in highlighted community)
    {
      selector: "node.dimmed",
      style: {
        opacity: 0.12,
        "text-opacity": 0,
      },
    },
    {
      selector: "edge.dimmed",
      style: {
        opacity: 0.04,
      },
    },
  ];
}
