/**
 * Graph screen - dependency graph visualization using Cytoscape.js.
 *
 * Only rendered when currentScreen === "graph" (lazy loading).
 * Shows file dependency graph colored by Louvain community,
 * sized by PageRank, with yellow borders for files with findings.
 */

import { useEffect, useRef, useState, useCallback } from "preact/hooks";
import useStore from "../../state/store.js";
import cytoscape from "cytoscape";
import dagre from "cytoscape-dagre";

// Register dagre layout once
cytoscape.use(dagre);

// Color palette for communities (8 distinct hues)
const COMMUNITY_COLORS = [
  "#3b82f6", "#ef4444", "#10b981", "#f59e0b",
  "#8b5cf6", "#ec4899", "#06b6d4", "#84cc16",
];

export function GraphScreen() {
  const data = useStore((s) => s.data);
  const containerRef = useRef(null);
  const cyRef = useRef(null);
  const [filter, setFilter] = useState("all");
  const [loading, setLoading] = useState(true);
  const [nodeCount, setNodeCount] = useState(0);
  const [edgeCount, setEdgeCount] = useState(0);
  const [hoveredNode, setHoveredNode] = useState(null);

  const initGraph = useCallback(() => {
    if (!data || !containerRef.current) return;

    // Destroy previous instance
    if (cyRef.current) {
      cyRef.current.destroy();
      cyRef.current = null;
    }

    setLoading(true);

    // Build graph elements
    const { nodes, edges } = buildGraphElements(data, filter);
    setNodeCount(nodes.length);
    setEdgeCount(edges.length);

    if (nodes.length === 0) {
      setLoading(false);
      return;
    }

    // Use requestAnimationFrame to let loading state render first
    requestAnimationFrame(() => {
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
        minZoom: 0.1,
        maxZoom: 3,
        wheelSensitivity: 0.3,
        boxSelectionEnabled: false,
      });

      // Hover tooltip
      cy.on("mouseover", "node", (evt) => {
        const node = evt.target;
        setHoveredNode({
          label: node.data("label"),
          fullPath: node.data("id"),
          community: node.data("community"),
          pagerank: node.data("pagerank"),
          riskScore: node.data("risk_score"),
          findingCount: node.data("finding_count"),
        });
      });

      cy.on("mouseout", "node", () => {
        setHoveredNode(null);
      });

      // Click: navigate to file detail
      cy.on("tap", "node", (evt) => {
        const path = evt.target.data("id");
        location.hash = "files/" + encodeURIComponent(path);
      });

      cyRef.current = cy;
      setLoading(false);
    });
  }, [data, filter]);

  useEffect(() => {
    initGraph();
    return () => {
      if (cyRef.current) {
        cyRef.current.destroy();
        cyRef.current = null;
      }
    };
  }, [initGraph]);

  if (!data) return null;

  const communityCount = data.communities?.length || 0;
  const modScore = data.modularity_score;

  return (
    <div class="graph-screen">
      <div class="graph-controls">
        <button
          class={filter === "all" ? "active" : ""}
          onClick={() => setFilter("all")}
        >
          All Files ({Object.keys(data.files || {}).length})
        </button>
        <button
          class={filter === "top20" ? "active" : ""}
          onClick={() => setFilter("top20")}
        >
          Top 20% (PageRank)
        </button>
        <button
          class={filter === "hotspots" ? "active" : ""}
          onClick={() => setFilter("hotspots")}
        >
          Hotspots Only
        </button>
        <div class="graph-stats">
          {nodeCount} nodes | {edgeCount} edges
          {communityCount > 0 && ` | ${communityCount} communities`}
          {modScore > 0 && ` | Q=${modScore.toFixed(3)}`}
        </div>
      </div>
      <div class="graph-viewport">
        {loading && nodeCount === 0 && (
          <div class="graph-loading">
            <div class="graph-loading-text">Building graph...</div>
          </div>
        )}
        <div
          ref={containerRef}
          class="graph-container"
          style={{ visibility: loading && nodeCount === 0 ? "hidden" : "visible" }}
        />
        {hoveredNode && (
          <div class="graph-tooltip">
            <div class="graph-tooltip-path">{hoveredNode.fullPath}</div>
            <div class="graph-tooltip-row">
              <span>Community</span>
              <span
                class="graph-tooltip-community"
                style={{ color: COMMUNITY_COLORS[hoveredNode.community % COMMUNITY_COLORS.length] }}
              >
                {hoveredNode.community}
              </span>
            </div>
            <div class="graph-tooltip-row">
              <span>PageRank</span>
              <span>{hoveredNode.pagerank.toFixed(4)}</span>
            </div>
            <div class="graph-tooltip-row">
              <span>Risk</span>
              <span>{hoveredNode.riskScore.toFixed(3)}</span>
            </div>
            {hoveredNode.findingCount > 0 && (
              <div class="graph-tooltip-row">
                <span>Findings</span>
                <span style={{ color: "var(--yellow)" }}>{hoveredNode.findingCount}</span>
              </div>
            )}
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
  );
}

/**
 * Build cytoscape elements from dashboard data and current filter.
 */
function buildGraphElements(data, filter) {
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

  // Build node elements
  const nodes = nodePaths.map((path) => {
    const f = files[path];
    const communityId = communityMap[path] ?? (f.signals?.community ?? 0);
    return {
      data: {
        id: path,
        label: path.split("/").pop(),
        pagerank: f.pagerank || 0,
        risk_score: f.risk_score || 0,
        community: communityId,
        finding_count: f.finding_count || 0,
        colorIdx: communityId % COMMUNITY_COLORS.length,
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
 * Cytoscape stylesheet using mappers for community coloring and PageRank sizing.
 */
function getCytoscapeStyles() {
  return [
    {
      selector: "node",
      style: {
        "background-color": function (ele) {
          return COMMUNITY_COLORS[ele.data("colorIdx")];
        },
        label: "data(label)",
        width: function (ele) {
          return Math.max(20, ele.data("pagerank") * 300);
        },
        height: function (ele) {
          return Math.max(20, ele.data("pagerank") * 300);
        },
        "font-size": "9px",
        "font-family": "'JetBrains Mono', 'Fira Code', 'SF Mono', monospace",
        color: "#e5e5e5",
        "text-valign": "bottom",
        "text-margin-y": 4,
        "text-halign": "center",
        "border-width": function (ele) {
          return ele.data("finding_count") > 0 ? 3 : 0;
        },
        "border-color": "#eab308",
        "text-max-width": "80px",
        "text-wrap": "ellipsis",
        "overlay-padding": "4px",
      },
    },
    {
      selector: "edge",
      style: {
        width: 1,
        "line-color": "#333",
        "target-arrow-color": "#444",
        "target-arrow-shape": "triangle",
        "curve-style": "bezier",
        opacity: 0.4,
        "arrow-scale": 0.6,
      },
    },
    {
      selector: "node:active",
      style: {
        "overlay-color": "#3b82f6",
        "overlay-opacity": 0.15,
      },
    },
  ];
}
