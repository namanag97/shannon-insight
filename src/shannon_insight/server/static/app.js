/* =====================================================
   Shannon Insight Dashboard
   ===================================================== */
(function() {
  "use strict";

  /* ═══════════════════════════════════════════════════════════
     SECTION: Constants
     ═══════════════════════════════════════════════════════════ */

  var SIGNAL_LABELS = {
    lines:"Lines of code",function_count:"Functions",class_count:"Classes/Structs",
    max_nesting:"Max nesting depth",cognitive_load:"Cognitive load",
    pagerank:"PageRank centrality",betweenness:"Betweenness centrality",
    in_degree:"Files that import this",out_degree:"Files this imports",
    blast_radius_size:"Blast radius",depth:"DAG depth",
    stub_ratio:"Stub/empty functions",is_orphan:"Is orphan",
    phantom_import_count:"Missing imports",compression_ratio:"Compression ratio",
    semantic_coherence:"Semantic coherence",
    total_changes:"Total commits",churn_trajectory:"Churn trend",
    churn_cv:"Churn volatility",bus_factor:"Bus factor",
    author_entropy:"Author diversity",fix_ratio:"Bugfix ratio",
    change_entropy:"Change distribution",
    risk_score:"Risk score",wiring_quality:"Wiring quality",
    file_health_score:"File health",raw_risk:"Raw risk"
  };

  var SIGNAL_CATEGORIES = [
    {key:"size",name:"Size & Complexity",signals:["lines","function_count","class_count","max_nesting","cognitive_load"]},
    {key:"structure",name:"Graph Position",signals:["pagerank","betweenness","in_degree","out_degree","blast_radius_size","depth"]},
    {key:"health",name:"Code Health",signals:["stub_ratio","is_orphan","phantom_import_count","compression_ratio","semantic_coherence"]},
    {key:"temporal",name:"Change History",signals:["total_changes","churn_trajectory","churn_cv","fix_ratio","change_entropy"]},
    {key:"team",name:"Team Context",signals:["author_entropy","bus_factor"]},
    {key:"risk",name:"Computed Risk",signals:["risk_score","wiring_quality","file_health_score","raw_risk"]}
  ];

  var SIGNAL_POLARITY = {
    risk_score:true,raw_risk:true,churn_cv:true,cognitive_load:true,
    max_nesting:true,stub_ratio:true,phantom_import_count:true,
    fix_ratio:true,blast_radius_size:true,
    wiring_quality:false,file_health_score:false,semantic_coherence:false,
    bus_factor:false,compression_ratio:false,
    pagerank:null,betweenness:null,in_degree:null,out_degree:null,
    depth:null,lines:null,function_count:null,class_count:null,
    total_changes:null,author_entropy:null
  };

  /* ── State ─────────────────────────────────────────── */

  var DATA = null;
  var currentScreen = "overview";
  var currentFileDetail = null;
  var issueTab = "incomplete";
  var fileSortKey = "risk_score";
  var fileSortAsc = false;
  var fileSearch = "";
  var fileFilters = new Set();
  var issueSortKey = "severity_desc";
  var issueSeverityFilter = new Set(["critical","high","medium","low","info"]);
  var selectedIndex = {};
  var moduleDetail = null;
  var moduleSortKey = "health_score";
  var moduleSortAsc = true;
  var fileViewMode = "table";

  /* ── Helpers ───────────────────────────────────────── */

  function $(sel) { return document.querySelector(sel); }
  function $$(sel) { return document.querySelectorAll(sel); }

  function esc(s) {
    if (!s) return "";
    var d = document.createElement("div");
    d.textContent = s;
    return d.innerHTML;
  }

  function fmtN(n) {
    if (n == null) return "--";
    if (n >= 1000) return (n / 1000).toFixed(1) + "k";
    return String(n);
  }

  function fmtF(n, d) {
    if (n == null) return "--";
    return n.toFixed(d != null ? d : 2);
  }

  function hColor(score) {
    if (score >= 8) return "var(--green)";
    if (score >= 6) return "var(--yellow)";
    if (score >= 4) return "var(--orange)";
    return "var(--red)";
  }

  function sevKey(sev) {
    if (sev >= 0.9) return "critical";
    if (sev >= 0.8) return "high";
    if (sev >= 0.6) return "medium";
    if (sev >= 0.4) return "low";
    return "info";
  }

  function polarColor(key, val) {
    var p = SIGNAL_POLARITY[key];
    if (p == null) return "var(--accent)";
    // Normalize unbounded integer signals to 0-1 range for thresholding
    var UNBOUNDED = {blast_radius_size:50, phantom_import_count:5, cognitive_load:25, max_nesting:10};
    var v = val;
    if (UNBOUNDED[key]) v = Math.min(val / UNBOUNDED[key], 1.0);
    if (p === true) return v > 0.5 ? "var(--red)" : v > 0.2 ? "var(--orange)" : "var(--text)";
    if (p === false) return v > 0.7 ? "var(--green)" : v < 0.3 ? "var(--orange)" : "var(--text)";
    return "var(--accent)";
  }

  function fmtSigVal(key, val) {
    if (val == null) return "--";
    if (typeof val === "boolean") return val ? "Yes" : "No";
    if (typeof val !== "number") return String(val);
    if (key === "stub_ratio" || key === "fix_ratio" || key === "compression_ratio" || key === "semantic_coherence")
      return (val * 100).toFixed(1) + "%";
    if (key === "risk_score" || key === "raw_risk" || key === "wiring_quality" || key === "file_health_score")
      return val.toFixed(3);
    if (key === "pagerank" || key === "betweenness" || key === "churn_cv" || key === "author_entropy" || key === "change_entropy" || key === "churn_trajectory")
      return val.toFixed(4);
    if (Number.isInteger(val)) return String(val);
    return val.toFixed(2);
  }

  /* ── SVG Renderers ─────────────────────────────────── */

  function renderSparkline(values, w, h, color) {
    if (!values || values.length < 2) return "";
    var mn = Infinity, mx = -Infinity;
    for (var i = 0; i < values.length; i++) {
      if (values[i] < mn) mn = values[i];
      if (values[i] > mx) mx = values[i];
    }
    var range = mx - mn || 1;
    var pts = [];
    for (var i = 0; i < values.length; i++) {
      var x = (i / (values.length - 1)) * w;
      var y = h - ((values[i] - mn) / range) * (h - 2) - 1;
      pts.push(x.toFixed(1) + "," + y.toFixed(1));
    }
    var line = pts.join(" ");
    var fill = pts.join(" ") + " " + w + "," + h + " 0," + h;
    return '<svg width="' + w + '" height="' + h + '" style="vertical-align:middle">' +
      '<polyline points="' + fill + '" fill="' + color + '" opacity="0.1" />' +
      '<polyline points="' + line + '" fill="none" stroke="' + color + '" stroke-width="1.5" /></svg>';
  }

  function polarToXY(cx, cy, radius, angleIdx, total, score) {
    var angle = (Math.PI * 2 * angleIdx / total) - Math.PI / 2;
    var r = radius * Math.min(score / 10, 1);
    return { x: cx + r * Math.cos(angle), y: cy + r * Math.sin(angle) };
  }

  function squarify(items, x, y, w, h) {
    if (!items.length) return [];
    if (items.length === 1) {
      items[0].x = x; items[0].y = y; items[0].w = w; items[0].h = h;
      return items;
    }
    var total = 0;
    for (var i = 0; i < items.length; i++) total += items[i].area;
    if (total <= 0) return items;
    var vertical = w >= h;
    var side = vertical ? h : w;
    var sum = 0, best = Infinity, split = 1;
    for (var i = 0; i < items.length - 1; i++) {
      sum += items[i].area;
      var frac = sum / total;
      var strip = vertical ? w * frac : h * frac;
      if (strip <= 0) continue;
      var worst = 0;
      var rowSum = 0;
      for (var j = 0; j <= i; j++) rowSum += items[j].area;
      for (var j = 0; j <= i; j++) {
        var rh = (items[j].area / rowSum) * side;
        var asp = rh > 0 ? Math.max(strip / rh, rh / strip) : Infinity;
        if (asp > worst) worst = asp;
      }
      if (worst < best) { best = worst; split = i + 1; }
    }
    var leftSum = 0;
    for (var i = 0; i < split; i++) leftSum += items[i].area;
    var frac = leftSum / total;
    var left = items.slice(0, split);
    var right = items.slice(split);
    if (vertical) {
      var lw = w * frac;
      var off = y;
      for (var i = 0; i < left.length; i++) {
        var ih = leftSum > 0 ? (left[i].area / leftSum) * h : 0;
        left[i].x = x; left[i].y = off; left[i].w = lw; left[i].h = ih;
        off += ih;
      }
      squarify(right, x + lw, y, w - lw, h);
    } else {
      var lh = h * frac;
      var off = x;
      for (var i = 0; i < left.length; i++) {
        var iw = leftSum > 0 ? (left[i].area / leftSum) * w : 0;
        left[i].x = off; left[i].y = y; left[i].w = iw; left[i].h = lh;
        off += iw;
      }
      squarify(right, x, y + lh, w, h - lh);
    }
    return items;
  }

  /* ── Shared Renderers ─────────────────────────────── */

  function renderEvidence(evidence, maxItems) {
    if (!evidence || !evidence.length) return "";
    var html = '<div class="finding-evidence">';
    var limit = Math.min(evidence.length, maxItems);
    for (var ei = 0; ei < limit; ei++) {
      var ev = evidence[ei];
      var sigName = ev.signal.replace(/_/g, ' ');
      var valStr = typeof ev.value === "number" ? (Number.isInteger(ev.value) ? String(ev.value) : ev.value.toFixed(2)) : String(ev.value);
      html += sigName + ': <strong>' + esc(valStr) + '</strong>';
      if (ev.percentile) html += ' <span class="pctl">(' + Math.round(ev.percentile) + 'th pctl)</span>';
      if (ei < limit - 1) html += '&nbsp;&nbsp;&nbsp;';
    }
    html += '</div>';
    return html;
  }

  function renderFindingRow(finding, opts) {
    opts = opts || {};
    var sk = sevKey(finding.severity);
    var classes = 'finding-row sev-' + sk;
    if (finding.confidence != null && finding.confidence < 0.5) classes += ' finding-low-confidence';
    var html = '<div class="' + classes + '">';
    html += '<div class="finding-head"><div class="sev-dot ' + sk + '"></div>';
    html += '<span class="finding-type-label">' + esc(finding.label) + '</span>';
    if (finding.effort) html += '<span class="effort-badge">' + esc(finding.effort) + '</span>';
    if (opts.chronicSet && opts.chronicSet.has(finding.finding_type)) html += '<span class="chronic-badge">CHRONIC</span>';
    html += '</div>';
    if (opts.showFiles && finding.files && finding.files.length) {
      html += '<div class="finding-files">';
      for (var fi = 0; fi < finding.files.length; fi++) {
        if (fi > 0) html += ', ';
        html += '<a href="#files/' + encodeURIComponent(finding.files[fi]) + '">' + esc(finding.files[fi]) + '</a>';
      }
      html += '</div>';
    }
    html += renderEvidence(finding.evidence, opts.maxEvidence || 4);
    if (finding.interpretation) html += '<div class="finding-interp">' + esc(finding.interpretation) + '</div>';
    if (finding.suggestion) html += '<div class="finding-suggestion">' + esc(finding.suggestion) + '</div>';
    html += '</div>';
    return html;
  }

  /* ── Screen: Overview ──────────────────────────────── */

  function renderOverview() {
    if (!DATA) return;

    // Health score
    var score = DATA.health;
    var color = hColor(score);
    var el = $("#healthScore");
    el.textContent = score.toFixed(1);
    el.style.color = color;

    // Verdict banner
    var vb = $("#verdictBanner");
    if (DATA.verdict) {
      vb.textContent = DATA.verdict;
      vb.style.color = DATA.verdict_color || color;
    } else {
      vb.textContent = "";
    }

    // Health label
    var lbl = $("#healthLabel");
    lbl.textContent = DATA.health_label || "";
    lbl.style.color = "var(--text-secondary)";

    // Stat strip values
    var totalIssues = 0;
    var cats = DATA.categories || {};
    for (var k in cats) totalIssues += cats[k].count;

    $("#statFiles").textContent = fmtN(DATA.file_count);
    $("#statModules").textContent = fmtN(DATA.module_count);
    $("#statCommits").textContent = fmtN(DATA.commits_analyzed);
    $("#statIssues").textContent = fmtN(totalIssues);
    var issueEl = $("#statIssues");
    if (issueEl && totalIssues > 0) {
      issueEl.style.color = "var(--orange)";
    }

    // Category summary
    var catOrder = ["incomplete","fragile","tangled","team"];
    var catLabels = {incomplete:"Incomplete",fragile:"Fragile",tangled:"Tangled",team:"Team"};
    var maxCount = 1;
    for (var i = 0; i < catOrder.length; i++) {
      var c = cats[catOrder[i]];
      if (c && c.count > maxCount) maxCount = c.count;
    }
    var catHtml = "";
    for (var i = 0; i < catOrder.length; i++) {
      var key = catOrder[i];
      var cat = cats[key];
      if (!cat) continue;
      var pct = maxCount > 0 ? (cat.count / maxCount) * 100 : 0;
      var barColor = cat.high_count > 0 ? "var(--orange)" : (cat.count > 0 ? "var(--yellow)" : "var(--border)");
      var fileCount = 0;
      var catFindings = cat.findings || [];
      var fileSet = {};
      for (var fi = 0; fi < catFindings.length; fi++) {
        var ff = catFindings[fi].files || [];
        for (var ffi = 0; ffi < ff.length; ffi++) fileSet[ff[ffi]] = true;
      }
      fileCount = Object.keys(fileSet).length;
      catHtml += '<div class="cat-row" data-cat="' + key + '">' +
        '<span class="cat-name">' + esc(catLabels[key] || key) + '</span>' +
        '<span class="cat-count" style="color:' + (cat.count > 0 ? "var(--text)" : "var(--text-tertiary)") + '">' + cat.count + '</span>' +
        '<span class="cat-file-count" style="color:var(--text-tertiary);font-size:10px;margin-left:4px">' + (fileCount > 0 ? fileCount + ' files' : '') + '</span>' +
        '<div class="cat-bar-track"><div class="cat-bar-fill" style="width:' + pct + '%;background:' + barColor + '"></div></div>' +
        '</div>';
    }
    if (DATA.recent_changes) {
      catHtml += '<div style="margin-top:8px;font-size:11px;color:var(--accent);font-family:var(--mono)">' +
        DATA.recent_changes.length + ' files changed</div>';
    }
    if (DATA.changes) {
      var newF = DATA.changes.new_findings || 0;
      var resF = DATA.changes.resolved_findings || 0;
      if (newF || resF) {
        catHtml += '<div style="font-size:11px;color:var(--text-secondary);font-family:var(--mono);margin-top:4px">';
        if (newF) catHtml += '<span style="color:var(--red)">+' + newF + ' new</span> ';
        if (resF) catHtml += '<span style="color:var(--green)">' + resF + ' resolved</span>';
        catHtml += '</div>';
      }
    }
    var catContainer = $("#categorySummary");
    catContainer.innerHTML = catHtml;
    catContainer.onclick = function(e) {
      var row = e.target.closest(".cat-row");
      if (!row) return;
      issueTab = row.dataset.cat;
      location.hash = "issues";
    };

    // Risk histogram
    var histDiv = $("#riskHistogram");
    if (DATA.files) {
      var bins = [0,0,0,0,0];
      var binLabels = ["0-0.2","0.2-0.4","0.4-0.6","0.6-0.8","0.8-1.0"];
      var binColors = ["var(--green)","var(--yellow)","var(--yellow)","var(--orange)","var(--red)"];
      for (var p in DATA.files) {
        var rs = DATA.files[p].risk_score || 0;
        var bi = Math.min(Math.floor(rs * 5), 4);
        bins[bi]++;
      }
      var maxBin = Math.max.apply(null, bins) || 1;
      var hSvg = '<div class="section-title" style="margin-top:8px">Risk Distribution</div>';
      hSvg += '<svg width="100%" height="100" viewBox="0 0 300 100" preserveAspectRatio="none">';
      for (var i = 0; i < 5; i++) {
        var bw = (bins[i] / maxBin) * 240;
        var by = i * 20;
        hSvg += '<rect x="50" y="' + by + '" width="' + bw + '" height="14" fill="' + binColors[i] + '" opacity="0.7" />';
        hSvg += '<text x="0" y="' + (by + 11) + '" fill="var(--text-tertiary)" font-size="8" font-family="var(--mono)">' + binLabels[i] + '</text>';
        hSvg += '<text x="' + (55 + bw) + '" y="' + (by + 11) + '" fill="var(--text-secondary)" font-size="8" font-family="var(--mono)">' + bins[i] + '</text>';
      }
      hSvg += '</svg>';
      histDiv.innerHTML = hSvg;
    }

    // Focus point
    var fp = $("#focusPoint");
    if (DATA.focus) {
      var f = DATA.focus;
      var html = '<div class="focus-path"><a href="#files/' + encodeURIComponent(f.path) + '">' + esc(f.path) + '</a></div>';

      // Score breakdown as 2x2 mini grid
      if (f.risk_score != null || f.impact_score != null) {
        html += '<div class="focus-scores">';
        if (f.risk_score != null) {
          html += '<div class="focus-score-item"><div class="focus-score-val">' + fmtF(f.risk_score, 2) + '</div><div class="focus-score-label">risk</div></div>';
        }
        if (f.impact_score != null) {
          html += '<div class="focus-score-item"><div class="focus-score-val">' + fmtF(f.impact_score, 2) + '</div><div class="focus-score-label">impact</div></div>';
        }
        if (f.tractability_score != null) {
          html += '<div class="focus-score-item"><div class="focus-score-val">' + fmtF(f.tractability_score, 2) + '</div><div class="focus-score-label">tractability</div></div>';
        }
        if (f.confidence_score != null) {
          html += '<div class="focus-score-item"><div class="focus-score-val">' + fmtF(f.confidence_score, 2) + '</div><div class="focus-score-label">confidence</div></div>';
        }
        html += '</div>';
      }

      html += '<div class="focus-why">' + esc(f.why) + '</div>';

      // Top findings
      var findings = f.findings || [];
      for (var j = 0; j < Math.min(findings.length, 3); j++) {
        var fi = findings[j];
        var sk = sevKey(fi.severity);
        html += '<div class="focus-finding"><div class="sev-dot ' + sk + '"></div>' +
          '<div class="focus-finding-text">' + esc(fi.label) + '</div></div>';
      }

      // Alternatives with accent border
      if (f.alternatives && f.alternatives.length > 0) {
        html += '<div style="margin-top:10px;font-size:11px;color:var(--text-tertiary)">Also consider:</div>';
        for (var a = 0; a < Math.min(f.alternatives.length, 3); a++) {
          var alt = f.alternatives[a];
          html += '<div class="alt-item">';
          html += '<a href="#files/' + encodeURIComponent(alt.path) + '">' + esc(alt.path) + '</a>';
          if (alt.why) html += '<span class="alt-why">' + esc(alt.why) + '</span>';
          html += '</div>';
        }
      }
      fp.innerHTML = html;
    } else {
      fp.innerHTML = '<div style="color:var(--text-tertiary);font-size:12px;padding:8px 0">No actionable focus point identified.</div>';
    }
  }

  /* ── Screen: Issues ────────────────────────────────── */

  function renderIssues() {
    if (!DATA) return;
    var cats = DATA.categories || {};
    var order = ["incomplete","fragile","tangled","team"];
    var labels = {incomplete:"Incomplete",fragile:"Fragile",tangled:"Tangled",team:"Team"};
    if (!cats[issueTab]) issueTab = order[0];

    // Filter bar
    var fbHtml = '<select class="sort-select" id="issueSortSel">' +
      '<option value="severity_desc"' + (issueSortKey === "severity_desc" ? " selected" : "") + '>Severity (high first)</option>' +
      '<option value="severity_asc"' + (issueSortKey === "severity_asc" ? " selected" : "") + '>Severity (low first)</option>' +
      '<option value="effort_asc"' + (issueSortKey === "effort_asc" ? " selected" : "") + '>Effort (low first)</option>' +
      '<option value="file_count"' + (issueSortKey === "file_count" ? " selected" : "") + '>File count</option></select> ';
    var sevLevels = ["critical","high","medium","low","info"];
    for (var i = 0; i < sevLevels.length; i++) {
      var sl = sevLevels[i];
      fbHtml += '<button class="sev-filter' + (issueSeverityFilter.has(sl) ? " active" : "") + '" data-sev="' + sl + '">' + sl.toUpperCase() + '</button> ';
    }
    $("#issueFilterBar").innerHTML = fbHtml;
    var sortSel = $("#issueSortSel");
    if (sortSel) sortSel.onchange = function() { issueSortKey = this.value; renderIssues(); };
    $$("#issueFilterBar .sev-filter").forEach(function(btn) {
      btn.onclick = function() {
        var s = btn.dataset.sev;
        if (issueSeverityFilter.has(s)) issueSeverityFilter.delete(s); else issueSeverityFilter.add(s);
        renderIssues();
      };
    });

    // Tabs
    var tabsHtml = "";
    for (var i = 0; i < order.length; i++) {
      var key = order[i];
      var cat = cats[key];
      if (!cat) continue;
      tabsHtml += '<button class="issue-tab' + (issueTab === key ? ' active' : '') + '" data-tab="' + key + '">' +
        esc(labels[key] || key) + '<span class="issue-tab-count">' + cat.count + '</span></button>';
    }
    $("#issueTabs").innerHTML = tabsHtml;

    // Content
    var cat = cats[issueTab];
    if (!cat || cat.count === 0) {
      $("#issueContent").innerHTML = '<div class="empty-state"><div class="empty-state-title">No ' + esc(labels[issueTab] || issueTab) + ' issues</div></div>';
    } else {
      var findings = (cat.findings || []).slice();

      // Filter by severity
      findings = findings.filter(function(f) { return issueSeverityFilter.has(sevKey(f.severity)); });

      // Sort
      var chronicSet = (DATA.trends && DATA.trends.chronic) ? new Set(DATA.trends.chronic.map(function(c){return c.finding_type||c.identity_key})) : new Set();
      if (issueSortKey === "severity_desc") findings.sort(function(a,b){ return b.severity - a.severity; });
      else if (issueSortKey === "severity_asc") findings.sort(function(a,b){ return a.severity - b.severity; });
      else if (issueSortKey === "effort_asc") {
        var eo = {LOW:0,MEDIUM:1,HIGH:2};
        findings.sort(function(a,b){ return (eo[a.effort]||1) - (eo[b.effort]||1); });
      } else if (issueSortKey === "file_count") findings.sort(function(a,b){ return (b.files?b.files.length:0) - (a.files?a.files.length:0); });

      // Render finding rows
      var html = "";
      for (var j = 0; j < findings.length; j++) {
        html += renderFindingRow(findings[j], { showFiles: true, chronicSet: chronicSet, maxEvidence: 4 });
      }
      $("#issueContent").innerHTML = html;
    }

    $("#issueTabs").onclick = function(e) {
      var btn = e.target.closest(".issue-tab");
      if (!btn) return;
      issueTab = btn.dataset.tab;
      renderIssues();
    };
  }

  /* ── Screen: Files ─────────────────────────────────── */

  function showFileList() {
    var listView = $("#fileListView");
    var detailView = $("#fileDetailView");
    listView.style.display = "block";
    detailView.style.display = "none";
    if (!DATA || !DATA.files) {
      listView.innerHTML = '<div class="empty-state"><div class="empty-state-title">No file data</div></div>';
      return;
    }

    var entries = [];
    for (var p in DATA.files) entries.push([p, DATA.files[p]]);
    var totalCount = entries.length;
    var changedSet = DATA.recent_changes ? new Set(DATA.recent_changes) : new Set();

    // Apply search
    if (fileSearch) {
      var q = fileSearch.toLowerCase();
      entries = entries.filter(function(e) { return e[0].toLowerCase().indexOf(q) !== -1; });
    }

    // Apply filters
    if (fileFilters.has("has_issues")) entries = entries.filter(function(e){ return (e[1].finding_count||0) > 0; });
    if (fileFilters.has("orphans")) entries = entries.filter(function(e){ return e[1].signals && e[1].signals.is_orphan; });
    var roleFilters = [];
    fileFilters.forEach(function(f) { if (["MODEL","SERVICE","ENTRY_POINT","TEST"].indexOf(f) !== -1) roleFilters.push(f); });
    if (roleFilters.length > 0) {
      var rs = new Set(roleFilters);
      entries = entries.filter(function(e){ return rs.has(e[1].role); });
    }

    // Sort
    entries.sort(function(a, b) {
      if (fileSortKey === "path") return fileSortAsc ? a[0].localeCompare(b[0]) : b[0].localeCompare(a[0]);
      var va = a[1][fileSortKey] != null ? a[1][fileSortKey] : 0;
      var vb = b[1][fileSortKey] != null ? b[1][fileSortKey] : 0;
      return fileSortAsc ? va - vb : vb - va;
    });

    // Filter bar
    var fbHtml = '<div class="filter-bar">';
    fbHtml += '<input class="search-input" type="text" id="fileSearchInput" placeholder="Search files..." value="' + esc(fileSearch) + '" />';
    var chips = [["has_issues","Has Issues"],["orphans","Orphans"],["MODEL","Model"],["SERVICE","Service"],["ENTRY_POINT","Entry Point"],["TEST","Test"]];
    for (var i = 0; i < chips.length; i++) {
      fbHtml += '<button class="filter-chip' + (fileFilters.has(chips[i][0]) ? " active" : "") + '" data-filter="' + chips[i][0] + '">' + chips[i][1] + '</button>';
    }
    fbHtml += '<div class="treemap-toggle"><button class="' + (fileViewMode === "table" ? "active" : "") + '" data-mode="table">Table</button>';
    fbHtml += '<button class="' + (fileViewMode === "treemap" ? "active" : "") + '" data-mode="treemap">Treemap</button></div>';
    fbHtml += '</div>';
    fbHtml += '<div style="font-size:11px;color:var(--text-tertiary);font-family:var(--mono);margin-bottom:8px">Showing ' + entries.length + ' of ' + totalCount + ' files</div>';

    if (fileViewMode === "treemap") {
      var tmItems = [];
      for (var i = 0; i < Math.min(entries.length, 300); i++) {
        var area = Math.max((entries[i][1].lines || 1), 1);
        tmItems.push({path:entries[i][0], area:area, color_value:entries[i][1].risk_score || 0});
      }
      tmItems.sort(function(a,b){return b.area - a.area;});
      var tmW = 800, tmH = 500;
      squarify(tmItems, 0, 0, tmW, tmH);
      var svg = '<svg viewBox="0 0 ' + tmW + ' ' + tmH + '" width="100%" style="max-height:500px;cursor:pointer" id="treemapSvg">';
      for (var i = 0; i < tmItems.length; i++) {
        var t = tmItems[i];
        if (!t.w || !t.h || t.w < 1 || t.h < 1) continue;
        var rc = hColor(10 - t.color_value * 10);
        svg += '<rect x="' + t.x.toFixed(1) + '" y="' + t.y.toFixed(1) + '" width="' + t.w.toFixed(1) + '" height="' + t.h.toFixed(1) + '" fill="' + rc + '" opacity="0.6" stroke="var(--bg)" stroke-width="1" data-path="' + esc(t.path) + '"><title>' + esc(t.path) + ' (' + Math.round(t.area) + ' lines, risk ' + t.color_value.toFixed(3) + ')</title></rect>';
        if (t.w > 60 && t.h > 14) {
          var name = t.path.split("/").pop();
          svg += '<text x="' + (t.x + 3).toFixed(1) + '" y="' + (t.y + 11).toFixed(1) + '" font-size="9" font-family="var(--mono)" fill="var(--text)" pointer-events="none">' + esc(name.slice(0,Math.floor(t.w/6))) + '</text>';
        }
      }
      svg += '</svg>';
      listView.innerHTML = fbHtml + svg;
      var tmSvg = $("#treemapSvg");
      if (tmSvg) tmSvg.onclick = function(e) {
        var rect = e.target.closest("rect[data-path]");
        if (rect) location.hash = "files/" + encodeURIComponent(rect.dataset.path);
      };
    } else {
      var cols = [
        {key:"path",label:"File",cls:"td-path"},
        {key:"risk_score",label:"Risk",cls:"td-risk"},
        {key:"total_changes",label:"Churn",cls:"td-num"},
        {key:"cognitive_load",label:"Complexity",cls:"td-num"},
        {key:"blast_radius",label:"Blast R.",cls:"td-num"},
        {key:"finding_count",label:"Issues",cls:"td-issues"},
      ];
      var html = fbHtml + '<table class="file-table"><thead><tr>';
      for (var c = 0; c < cols.length; c++) {
        var col = cols[c];
        var arrow = fileSortKey === col.key ? (fileSortAsc ? '<span class="sort-arrow">&#9650;</span>' : '<span class="sort-arrow">&#9660;</span>') : '';
        var thCls = col.key !== "path" ? ' class="num"' : '';
        html += '<th' + thCls + ' data-sort="' + col.key + '">' + col.label + arrow + '</th>';
      }
      html += '</tr></thead><tbody>';
      var limit = Math.min(entries.length, 200);
      var sel = selectedIndex["files"] || 0;
      for (var r = 0; r < limit; r++) {
        var path = entries[r][0];
        var f = entries[r][1];
        var riskColor = hColor(10 - (f.risk_score || 0) * 10);
        html += '<tr data-path="' + esc(path) + '"' + (r === sel ? ' class="kbd-selected"' : '') + '>';
        html += '<td class="td-path" title="' + esc(path) + '"><span>' + esc(path) + '</span>';
        if (changedSet.has(path)) html += '<span class="changed-badge">changed</span>';
        html += '</td>';
        var riskStyle = (f.risk_score || 0) > 0.05 ? 'color:' + riskColor : '';
        html += '<td class="td-risk" style="' + riskStyle + '">' + fmtF(f.risk_score, 3) + '</td>';
        html += '<td class="td-num">' + (f.total_changes || 0) + '</td>';
        html += '<td class="td-num">' + fmtF(f.cognitive_load, 1) + '</td>';
        html += '<td class="td-num">' + (f.blast_radius || 0) + '</td>';
        html += '<td class="td-issues">' + (f.finding_count || 0) + '</td>';
        html += '</tr>';
      }
      html += '</tbody></table>';
      if (entries.length > 200) html += '<div class="file-count-note">Showing 200 of ' + entries.length + ' files (filtered)</div>';
      listView.innerHTML = html;

      var thead = listView.querySelector("thead");
      if (thead) thead.onclick = function(e) {
        var th = e.target.closest("th[data-sort]");
        if (!th) return;
        var key = th.dataset.sort;
        if (fileSortKey === key) fileSortAsc = !fileSortAsc;
        else { fileSortKey = key; fileSortAsc = key === "path"; }
        showFileList();
      };
      listView.querySelectorAll("tbody tr[data-path]").forEach(function(row) {
        row.onclick = function() { location.hash = "files/" + encodeURIComponent(row.dataset.path); };
      });
    }

    // Bind filter bar events
    var si = $("#fileSearchInput");
    if (si) {
      si.oninput = function() { fileSearch = si.value; showFileList(); };
      si.onkeydown = function(e) { if (e.key === "Escape") { si.blur(); } };
    }
    $$("#fileListView .filter-chip").forEach(function(chip) {
      chip.onclick = function() {
        var f = chip.dataset.filter;
        if (fileFilters.has(f)) fileFilters.delete(f); else fileFilters.add(f);
        showFileList();
      };
    });
    $$("#fileListView .treemap-toggle button").forEach(function(btn) {
      btn.onclick = function() { fileViewMode = btn.dataset.mode; showFileList(); };
    });
  }

  function showFileDetail(path) {
    var listView = $("#fileListView");
    var detailView = $("#fileDetailView");
    listView.style.display = "none";
    detailView.style.display = "block";
    if (!DATA || !DATA.files || !DATA.files[path]) {
      detailView.innerHTML = '<a class="file-detail-back" href="#files">&larr; Files</a>' +
        '<div class="empty-state"><div class="empty-state-title">File not found</div><div>' + esc(path) + '</div></div>';
      return;
    }
    var f = DATA.files[path];
    var color = hColor(f.health);
    var html = '<a class="file-detail-back" href="#files">&larr; Files</a>';
    html += '<div class="file-detail-header">';
    html += '<span class="file-detail-path">' + esc(path) + '</span>';
    if (f.role && f.role !== "UNKNOWN") html += '<span class="file-detail-role">' + esc(f.role) + '</span>';
    html += '<span class="file-detail-health" style="color:' + color + '">' + fmtF(f.health, 1) + '</span>';
    html += '</div>';

    // Key metrics
    var metrics = [
      ["Lines", f.lines], ["Functions", f.signals ? f.signals.function_count : null],
      ["Risk Score", fmtF(f.risk_score, 3)], ["PageRank", fmtF(f.pagerank, 4)],
      ["Churn", f.total_changes], ["Bus Factor", fmtF(f.bus_factor, 1)],
      ["Blast Radius", f.blast_radius], ["Cognitive Load", fmtF(f.cognitive_load, 1)],
    ];
    html += '<div class="file-detail-metrics">';
    for (var m = 0; m < metrics.length; m++) {
      html += '<div class="fdm-cell"><div class="fdm-value">' + (metrics[m][1] != null ? metrics[m][1] : "--") + '</div>' +
        '<div class="fdm-label">' + metrics[m][0] + '</div></div>';
    }
    html += '</div>';

    // File findings
    var fileFindings = [];
    var cats = DATA.categories || {};
    for (var ck in cats) {
      var catFindings = cats[ck].findings || [];
      for (var fi = 0; fi < catFindings.length; fi++) {
        if (catFindings[fi].files && catFindings[fi].files.indexOf(path) !== -1) fileFindings.push(catFindings[fi]);
      }
    }
    if (fileFindings.length > 0) {
      html += '<div class="file-detail-section"><div class="file-detail-section-title">Issues (' + fileFindings.length + ')</div>';
      for (var j = 0; j < fileFindings.length; j++) {
        html += renderFindingRow(fileFindings[j], { showFiles: false, maxEvidence: 3 });
      }
      html += '</div>';
    }

    // Signals grouped by category
    var sigs = f.signals || {};
    var sigKeys = Object.keys(sigs);
    if (sigKeys.length > 0) {
      html += '<div class="file-detail-section">';
      var openCatCount = 0;
      for (var ci = 0; ci < SIGNAL_CATEGORIES.length; ci++) {
        var cat = SIGNAL_CATEGORIES[ci];
        var catSigs = cat.signals.filter(function(s) { return sigs[s] != null; });
        if (!catSigs.length) continue;

        // First 2 categories start open, rest collapsed
        var isOpen = openCatCount < 2;
        var toggleCls = 'file-detail-section-title signals-collapsible sig-cat-toggle';
        if (isOpen) toggleCls += ' sig-cat-open open';
        html += '<div class="' + toggleCls + '" data-cat="' + cat.key + '">' + esc(cat.name) + ' (' + catSigs.length + ')</div>';
        html += '<div class="signals-grid sig-cat-grid" data-cat="' + cat.key + '" style="display:' + (isOpen ? 'grid' : 'none') + '">';
        for (var s = 0; s < catSigs.length; s++) {
          var sk2 = catSigs[s];
          var sv = sigs[sk2];
          var label = SIGNAL_LABELS[sk2] || sk2.replace(/_/g, ' ');
          var display = fmtSigVal(sk2, sv);
          var valColor = typeof sv === "number" ? polarColor(sk2, sv) : "var(--text)";
          var sparkHtml = "";
          if (f.trends && f.trends[sk2]) sparkHtml = " " + renderSparkline(f.trends[sk2], 48, 14, valColor);
          html += '<div class="sig-row"><span class="sig-name">' + esc(label) + '</span>' +
            '<span class="sig-val" style="color:' + valColor + '">' + esc(display) + sparkHtml + '</span></div>';
        }
        html += '</div>';
        openCatCount++;
      }

      // Uncategorized signals
      var catted = new Set();
      SIGNAL_CATEGORIES.forEach(function(c){c.signals.forEach(function(s){catted.add(s);});});
      var uncatSigs = sigKeys.filter(function(s){return !catted.has(s) && sigs[s] != null;}).sort();
      if (uncatSigs.length) {
        html += '<div class="file-detail-section-title signals-collapsible sig-cat-toggle" data-cat="other">Other (' + uncatSigs.length + ')</div>';
        html += '<div class="signals-grid sig-cat-grid" data-cat="other" style="display:none">';
        for (var s = 0; s < uncatSigs.length; s++) {
          var sk2 = uncatSigs[s];
          var sv = sigs[sk2];
          var display = typeof sv === "number" ? (Number.isInteger(sv) ? String(sv) : sv.toFixed(4)) : String(sv);
          html += '<div class="sig-row"><span class="sig-name">' + esc(sk2.replace(/_/g, ' ')) + '</span>' +
            '<span class="sig-val">' + esc(display) + '</span></div>';
        }
        html += '</div>';
      }
      html += '</div>';
    }

    detailView.innerHTML = html;

    // Bind signal category toggles
    detailView.querySelectorAll(".sig-cat-toggle").forEach(function(toggle) {
      toggle.onclick = function() {
        var cat = toggle.dataset.cat;
        var grid = detailView.querySelector('.sig-cat-grid[data-cat="' + cat + '"]');
        if (!grid) return;
        var open = grid.style.display !== "none";
        grid.style.display = open ? "none" : "grid";
        toggle.classList.toggle("open", !open);
        toggle.classList.toggle("sig-cat-open", !open);
      };
    });
  }

  /* ── Screen: Modules ───────────────────────────────── */

  function renderModules() {
    var listView = $("#moduleListView");
    var detailView = $("#moduleDetailView");
    listView.style.display = "block";
    detailView.style.display = "none";
    if (!DATA || !DATA.modules) {
      listView.innerHTML = '<div class="empty-state"><div class="empty-state-title">No module data</div></div>';
      return;
    }
    var modules = DATA.modules;
    var entries = [];
    for (var p in modules) entries.push([p, modules[p]]);

    entries.sort(function(a, b) {
      if (moduleSortKey === "path") return moduleSortAsc ? a[0].localeCompare(b[0]) : b[0].localeCompare(a[0]);
      var va = a[1][moduleSortKey] != null ? a[1][moduleSortKey] : 0;
      var vb = b[1][moduleSortKey] != null ? b[1][moduleSortKey] : 0;
      return moduleSortAsc ? va - vb : vb - va;
    });

    var cols = [
      {key:"path",label:"Module",cls:"td-path"},
      {key:"health_score",label:"Health",cls:"td-risk"},
      {key:"instability",label:"Instability",cls:"td-num"},
      {key:"abstractness",label:"Abstractness",cls:"td-num"},
      {key:"file_count",label:"Files",cls:"td-num"},
      {key:"velocity",label:"Velocity",cls:"td-num"},
    ];
    var html = '<table class="module-table"><thead><tr>';
    for (var c = 0; c < cols.length; c++) {
      var col = cols[c];
      var arrow = moduleSortKey === col.key ? (moduleSortAsc ? '<span class="sort-arrow">&#9650;</span>' : '<span class="sort-arrow">&#9660;</span>') : '';
      var thCls = col.key !== "path" ? ' class="num"' : '';
      html += '<th' + thCls + ' data-sort="' + col.key + '">' + col.label + arrow + '</th>';
    }
    html += '</tr></thead><tbody>';
    for (var r = 0; r < entries.length; r++) {
      var p = entries[r][0];
      var m = entries[r][1];
      var hc = hColor(m.health_score || 5);
      html += '<tr data-mod="' + esc(p) + '">';
      html += '<td class="td-path"><span>' + esc(p) + '</span></td>';
      html += '<td class="td-risk" style="color:' + hc + '">' + fmtF(m.health_score, 1) + '</td>';
      html += '<td class="td-num">' + fmtF(m.instability, 2) + '</td>';
      html += '<td class="td-num">' + fmtF(m.abstractness, 2) + '</td>';
      html += '<td class="td-num">' + (m.file_count || 0) + '</td>';
      html += '<td class="td-num">' + fmtF(m.velocity, 1) + '</td>';
      html += '</tr>';
    }
    html += '</tbody></table>';
    listView.innerHTML = html;

    var thead = listView.querySelector("thead");
    if (thead) thead.onclick = function(e) {
      var th = e.target.closest("th[data-sort]");
      if (!th) return;
      var key = th.dataset.sort;
      if (moduleSortKey === key) moduleSortAsc = !moduleSortAsc;
      else { moduleSortKey = key; moduleSortAsc = key === "path"; }
      renderModules();
    };
    listView.querySelectorAll("tbody tr[data-mod]").forEach(function(row) {
      row.onclick = function() { location.hash = "modules/" + encodeURIComponent(row.dataset.mod); };
    });
  }

  function showModuleDetail(path) {
    var listView = $("#moduleListView");
    var detailView = $("#moduleDetailView");
    listView.style.display = "none";
    detailView.style.display = "block";
    if (!DATA || !DATA.modules || !DATA.modules[path]) {
      detailView.innerHTML = '<a class="file-detail-back" href="#modules">&larr; Modules</a>' +
        '<div class="empty-state"><div class="empty-state-title">Module not found</div><div>' + esc(path) + '</div></div>';
      return;
    }
    var m = DATA.modules[path];
    var color = hColor(m.health_score || 5);
    var html = '<a class="file-detail-back" href="#modules">&larr; Modules</a>';
    html += '<div class="file-detail-header">';
    html += '<span class="file-detail-path">' + esc(path) + '</span>';
    html += '<span class="file-detail-health" style="color:' + color + '">' + fmtF(m.health_score, 1) + '</span>';
    html += '</div>';
    html += '<div class="file-detail-metrics">';
    var stats = [["Files",m.file_count],["Instability",fmtF(m.instability,2)],["Abstractness",fmtF(m.abstractness,2)],["Velocity",fmtF(m.velocity,1)]];
    for (var i = 0; i < stats.length; i++) {
      html += '<div class="fdm-cell"><div class="fdm-value">' + (stats[i][1] != null ? stats[i][1] : "--") + '</div><div class="fdm-label">' + stats[i][0] + '</div></div>';
    }
    html += '</div>';
    if (m.files && m.files.length) {
      html += '<div class="file-detail-section"><div class="file-detail-section-title">Files (' + m.files.length + ')</div>';
      for (var i = 0; i < m.files.length; i++) {
        html += '<div style="font-family:var(--mono);font-size:11px;padding:2px 0"><a href="#files/' + encodeURIComponent(m.files[i]) + '">' + esc(m.files[i]) + '</a></div>';
      }
      html += '</div>';
    }
    if (m.violations && m.violations.length) {
      html += '<div class="file-detail-section"><div class="file-detail-section-title">Violations (' + m.violations.length + ')</div>';
      for (var i = 0; i < m.violations.length; i++) {
        html += '<div style="font-size:11px;color:var(--orange);padding:2px 0">' + esc(m.violations[i]) + '</div>';
      }
      html += '</div>';
    }
    detailView.innerHTML = html;
  }

  /* ── Screen: Health ────────────────────────────────── */

  function renderHealth() {
    if (!DATA) return;
    var trendsHtml = "";

    // Trend chart
    if (DATA.trends && DATA.trends.health) {
      var vals = DATA.trends.health.map(function(h){ return typeof h === "object" ? h.health : h; });
      var tw = 600, th = 200;
      trendsHtml += '<div class="health-section"><div class="section-title">Health Trend</div>';
      trendsHtml += renderSparkline(vals, tw, th, "var(--accent)");
      trendsHtml += '</div>';
    }

    // Top movers
    if (DATA.trends && DATA.trends.movers) {
      var movers = DATA.trends.movers;
      trendsHtml += '<div class="health-section"><div class="section-title">Top Movers</div>';
      for (var i = 0; i < movers.length; i++) {
        var m = movers[i];
        var dc = m.delta > 0 ? "var(--red)" : "var(--green)";
        var ds = m.delta > 0 ? "+" + m.delta.toFixed(3) : m.delta.toFixed(3);
        trendsHtml += '<div style="font-family:var(--mono);font-size:11px;padding:3px 0">' +
          '<a href="#files/' + encodeURIComponent(m.path) + '">' + esc(m.path) + '</a> ' +
          '<span style="color:' + dc + '">' + ds + '</span></div>';
      }
      trendsHtml += '</div>';
    }

    // Chronic findings
    if (DATA.trends && DATA.trends.chronic && DATA.trends.chronic.length) {
      var chronic = DATA.trends.chronic;
      trendsHtml += '<div class="health-section"><div class="section-title">Chronic Findings</div>';
      for (var i = 0; i < chronic.length; i++) {
        trendsHtml += '<div style="font-size:11px;padding:3px 0;color:var(--orange)">' + esc(chronic[i].title || chronic[i].finding_type) +
          ' <span style="color:var(--text-tertiary)">(' + (chronic[i].count || '?') + ' snapshots)</span></div>';
      }
      trendsHtml += '</div>';
    }
    $("#healthTrends").innerHTML = trendsHtml;

    // Radar chart for concerns
    var concerns = DATA.concerns || [];
    if (concerns.length >= 3) {
      var cx = 150, cy = 150, radius = 120;
      var n = concerns.length;
      var svg = '<svg width="300" height="300" viewBox="0 0 300 300">';
      // Grid rings
      for (var ring = 2; ring <= 10; ring += 2) {
        var pts = [];
        for (var i = 0; i < n; i++) {
          var p = polarToXY(cx, cy, radius, i, n, ring);
          pts.push(p.x.toFixed(1) + "," + p.y.toFixed(1));
        }
        svg += '<polygon points="' + pts.join(" ") + '" fill="none" stroke="var(--border)" stroke-width="0.5" />';
      }
      // Axes
      for (var i = 0; i < n; i++) {
        var p = polarToXY(cx, cy, radius, i, n, 10);
        svg += '<line x1="' + cx + '" y1="' + cy + '" x2="' + p.x.toFixed(1) + '" y2="' + p.y.toFixed(1) + '" stroke="var(--border)" stroke-width="0.5" />';
        var lp = polarToXY(cx, cy, radius + 16, i, n, 10);
        svg += '<text x="' + lp.x.toFixed(1) + '" y="' + lp.y.toFixed(1) + '" text-anchor="middle" font-size="9" font-family="var(--mono)" fill="var(--text-secondary)">' + esc(concerns[i].name) + '</text>';
      }
      // Data polygon
      var dataPts = [];
      for (var i = 0; i < n; i++) {
        var p = polarToXY(cx, cy, radius, i, n, concerns[i].score);
        dataPts.push(p.x.toFixed(1) + "," + p.y.toFixed(1));
      }
      svg += '<polygon points="' + dataPts.join(" ") + '" fill="var(--accent)" fill-opacity="0.15" stroke="var(--accent)" stroke-width="1.5" />';
      for (var i = 0; i < n; i++) {
        var p = polarToXY(cx, cy, radius, i, n, concerns[i].score);
        svg += '<circle cx="' + p.x.toFixed(1) + '" cy="' + p.y.toFixed(1) + '" r="3" fill="var(--accent)" />';
      }
      svg += '</svg>';
      $("#concernBars").innerHTML = svg;
    } else {
      // Fallback to bars
      var barsHtml = "";
      for (var i = 0; i < concerns.length; i++) {
        var c = concerns[i];
        var pct = (c.score / 10) * 100;
        var color = hColor(c.score);
        barsHtml += '<div class="concern-row">' +
          '<span class="concern-name">' + esc(c.name) + '</span>' +
          '<div class="concern-track"><div class="concern-fill" style="width:' + pct + '%;background:' + color + '"></div></div>' +
          '<span class="concern-score" style="color:' + color + '">' + c.score.toFixed(1) + '</span></div>';
      }
      $("#concernBars").innerHTML = barsHtml;
    }

    // Global signals
    var gs = DATA.global_signals || {};
    var keys = Object.keys(gs).sort();
    var tbody = $("#globalSignalsTable tbody");
    var rows = "";
    for (var k = 0; k < keys.length; k++) {
      var key = keys[k];
      var v = gs[key];
      if (v == null) continue;
      var display = typeof v === "number" ? (Number.isInteger(v) ? String(v) : v.toFixed(4)) : String(v);
      rows += '<tr><td class="gs-name">' + esc(key.replace(/_/g, ' ')) + '</td>' +
        '<td class="gs-val">' + esc(display) + '</td></tr>';
    }
    tbody.innerHTML = rows;
  }

  /* ── Navigation ────────────────────────────────────── */

  function navigate(screen, detail) {
    currentScreen = screen;
    $$(".screen").forEach(function(s) { s.classList.remove("active"); });
    var el = $("#screen-" + screen);
    if (el) el.classList.add("active");
    $$(".topbar-nav a").forEach(function(a) {
      a.classList.toggle("active", a.dataset.screen === screen);
    });
    if (screen === "files" && detail) {
      currentFileDetail = detail;
      showFileDetail(detail);
    } else if (screen === "files") {
      currentFileDetail = null;
      showFileList();
    }
    if (screen === "overview") renderOverview();
    if (screen === "issues") renderIssues();
    if (screen === "health") renderHealth();
    if (screen === "modules" && detail) {
      moduleDetail = detail;
      showModuleDetail(detail);
    } else if (screen === "modules") {
      moduleDetail = null;
      renderModules();
    }
  }

  function render() {
    renderOverview();
    if (currentScreen === "issues") renderIssues();
    if (currentScreen === "health") renderHealth();
    if (currentScreen === "files") {
      if (currentFileDetail) showFileDetail(currentFileDetail);
      else showFileList();
    }
    if (currentScreen === "modules") {
      if (moduleDetail) showModuleDetail(moduleDetail);
      else renderModules();
    }
    if (DATA) {
      var parts = [];
      if (DATA.commit_sha) parts.push(DATA.commit_sha.slice(0, 7));
      if (DATA.timestamp) {
        try { parts.push(new Date(DATA.timestamp).toLocaleTimeString()); } catch(e) {}
      }
      $("#metaInfo").textContent = parts.join(" \u00b7 ");
    }
  }

  /* ── Event Handlers ────────────────────────────────── */

  $("#nav").addEventListener("click", function(e) {
    var a = e.target.closest("a[data-screen]");
    if (!a) return;
    e.preventDefault();
    location.hash = a.dataset.screen;
  });

  window.addEventListener("hashchange", function() {
    var h = location.hash.slice(1) || "overview";
    var slashIdx = h.indexOf("/");
    if (slashIdx > -1) {
      navigate(h.slice(0, slashIdx), decodeURIComponent(h.slice(slashIdx + 1)));
    } else {
      navigate(h);
    }
  });

  document.addEventListener("click", function(e) {
    if (!e.target.closest(".export-dropdown")) {
      var m = $(".export-dropdown-menu");
      if (m) m.classList.remove("open");
    }
  });

  var exportBtn = $("#exportBtn");
  if (exportBtn) {
    exportBtn.addEventListener("click", function() {
      $(".export-dropdown-menu").classList.toggle("open");
    });
  }

  /* ── Keyboard ──────────────────────────────────────── */

  document.addEventListener("keydown", function(e) {
    var tag = (e.target.tagName || "").toLowerCase();
    if (tag === "input" || tag === "textarea" || tag === "select") {
      if (e.key === "Escape") e.target.blur();
      return;
    }
    var overlay = $("#kbdOverlay");
    if (e.key === "?") { overlay.classList.toggle("open"); e.preventDefault(); return; }
    if (overlay.classList.contains("open")) { if (e.key === "Escape") overlay.classList.remove("open"); return; }
    if (e.key === "Escape") {
      if (currentFileDetail) { location.hash = "files"; e.preventDefault(); }
      else if (moduleDetail) { location.hash = "modules"; e.preventDefault(); }
      return;
    }
    var screens = ["overview","issues","files","modules","health"];
    if (e.key >= "1" && e.key <= "5") { location.hash = screens[parseInt(e.key) - 1]; e.preventDefault(); return; }
    if (e.key === "/") {
      e.preventDefault();
      if (currentScreen !== "files") location.hash = "files";
      setTimeout(function() { var si = $("#fileSearchInput"); if (si) si.focus(); }, 100);
      return;
    }
    if (e.key === "j" || e.key === "k") {
      var rows = $$("#screen-" + currentScreen + " tbody tr");
      if (!rows.length) return;
      var idx = selectedIndex[currentScreen] || 0;
      if (e.key === "j") idx = Math.min(idx + 1, rows.length - 1);
      if (e.key === "k") idx = Math.max(idx - 1, 0);
      selectedIndex[currentScreen] = idx;
      rows.forEach(function(r, i) { r.classList.toggle("kbd-selected", i === idx); });
      rows[idx].scrollIntoView({block:"nearest"});
      e.preventDefault();
      return;
    }
    if (e.key === "Enter") {
      var rows = $$("#screen-" + currentScreen + " tbody tr.kbd-selected");
      if (rows.length) rows[0].click();
      return;
    }
  });

  $("#kbdHint").onclick = function() { $("#kbdOverlay").classList.toggle("open"); };
  $("#kbdOverlay").onclick = function(e) { if (e.target === this) this.classList.remove("open"); };

  /* ── WebSocket ─────────────────────────────────────── */

  var ws = null;
  var retryDelay = 1000;

  function connect() {
    var proto = location.protocol === "https:" ? "wss:" : "ws:";
    ws = new WebSocket(proto + "//" + location.host + "/ws");
    ws.onopen = function() {
      retryDelay = 1000;
      $("#reconnectBanner").classList.remove("active");
      setStatus("connected", "");
    };
    ws.onmessage = function(e) {
      try {
        var msg = JSON.parse(e.data);
        if (msg.type === "complete") {
          DATA = msg.state;
          setStatus("connected", "");
          hideProgress();
          render();
        } else if (msg.type === "progress") {
          setStatus("analyzing", msg.message || "analyzing");
          showProgress(msg);
        } else if (msg.type === "error") {
          setStatus("disconnected", "error");
          hideProgress();
        }
      } catch(err) { console.error("ws parse:", err); }
    };
    ws.onclose = function() {
      setStatus("disconnected", "");
      $("#reconnectBanner").classList.add("active");
      setTimeout(function() { retryDelay = Math.min(retryDelay * 1.5, 15000); connect(); }, retryDelay);
    };
    ws.onerror = function() { setStatus("disconnected", ""); };
  }

  function setStatus(cls, text) {
    $("#statusDot").className = "status-indicator " + cls;
    $("#statusText").textContent = text;
  }

  function showProgress(msg) {
    var bar = $("#progressBar");
    var fill = $("#progressFill");
    var pt = $("#progressText");
    bar.classList.add("active");
    if (msg.percent != null) {
      fill.style.animation = "none";
      fill.style.width = (msg.percent * 100) + "%";
      pt.textContent = Math.round(msg.percent * 100) + "%";
      pt.classList.add("active");
    } else {
      fill.style.animation = "";
      fill.style.width = "";
      pt.textContent = "";
      pt.classList.remove("active");
    }
  }

  function hideProgress() {
    $("#progressBar").classList.remove("active");
    var pt = $("#progressText");
    pt.textContent = "";
    pt.classList.remove("active");
  }

  /* ── Init ──────────────────────────────────────────── */

  fetch("/api/state").then(function(r) { return r.json(); }).then(function(data) {
    if (data && data.health != null) { DATA = data; render(); }
  }).catch(function() {});

  connect();

  var initHash = location.hash.slice(1) || "overview";
  var slashIdx = initHash.indexOf("/");
  if (slashIdx > -1) {
    navigate(initHash.slice(0, slashIdx), decodeURIComponent(initHash.slice(slashIdx + 1)));
  } else {
    navigate(initHash);
  }
})();
