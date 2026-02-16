# Stage 7: Output

Format findings and optionally persist snapshot.

---

## Output Formats

| Format | CLI Flag | Use Case |
|--------|----------|----------|
| Terminal | `--format terminal` (default) | Interactive use |
| JSON | `--format json` | CI/CD, scripting |
| HTML | `shannon-insight report` | Sharing, documentation |

---

## Terminal Output

```python
def format_terminal(
    result: AnalysisResult,
    console: Console,
) -> None:
    """
    Rich terminal output with colors and tables.
    """
    # Header
    console.print(Panel(
        f"[bold]Shannon Insight[/bold] - {result.context.root}",
        subtitle=f"{result.file_count} files analyzed",
    ))

    # Summary scores
    console.print("\n[bold]Health Scores[/bold]")
    table = Table(show_header=False)
    table.add_row("Codebase Health", format_score(result.codebase_health))
    table.add_row("Architecture Health", format_score(result.architecture_health))
    table.add_row("Wiring Score", format_score(result.wiring_score))
    console.print(table)

    # Findings by category
    if result.findings:
        console.print(f"\n[bold]Top Findings[/bold] ({len(result.findings)})")

        for finding in result.findings:
            severity_color = get_severity_color(finding.severity)
            console.print(
                f"  [{severity_color}]{finding.rank}. {finding.pattern}[/] "
                f"on [cyan]{format_target(finding.target)}[/]"
            )
            console.print(f"     {finding.description}")
            if finding.remediation:
                console.print(f"     [dim]→ {finding.remediation}[/]")
    else:
        console.print("\n[green]No findings. Codebase looks healthy![/]")

def format_score(score: float) -> str:
    """Format 0-1 score as 1-10 with color."""
    display = round(score * 10, 1)
    if display >= 8:
        return f"[green]{display}/10[/]"
    elif display >= 6:
        return f"[yellow]{display}/10[/]"
    else:
        return f"[red]{display}/10[/]"
```

---

## JSON Output

```python
def format_json(result: AnalysisResult) -> str:
    """
    JSON output for programmatic consumption.
    """
    return json.dumps({
        "version": "2.0",
        "timestamp": result.timestamp.isoformat(),
        "root": str(result.context.root),
        "file_count": result.file_count,
        "tier": result.context.tier.value,

        # Scores (both internal and display)
        "scores": {
            "codebase_health": result.codebase_health,
            "codebase_health_display": round(result.codebase_health * 10, 1),
            "architecture_health": result.architecture_health,
            "architecture_health_display": round(result.architecture_health * 10, 1),
            "wiring_score": result.wiring_score,
            "wiring_score_display": round(result.wiring_score * 10, 1),
        },

        # Findings
        "findings": [
            {
                "id": f.id,
                "pattern": f.pattern,
                "scope": f.scope.value,
                "target": format_target_json(f.target),
                "severity": f.severity,
                "confidence": f.confidence,
                "evidence": f.evidence,
                "description": f.description,
                "remediation": f.remediation,
            }
            for f in result.findings
        ],

        # Summary stats
        "summary": {
            "total_findings": len(result.findings),
            "by_severity": count_by_severity(result.findings),
            "by_pattern": count_by_pattern(result.findings),
        },
    }, indent=2)
```

### JSON Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["version", "timestamp", "root", "file_count", "scores", "findings"],
  "properties": {
    "version": { "type": "string" },
    "timestamp": { "type": "string", "format": "date-time" },
    "root": { "type": "string" },
    "file_count": { "type": "integer" },
    "tier": { "enum": ["absolute", "bayesian", "full"] },
    "scores": {
      "type": "object",
      "properties": {
        "codebase_health": { "type": "number", "minimum": 0, "maximum": 1 },
        "codebase_health_display": { "type": "number", "minimum": 1, "maximum": 10 }
      }
    },
    "findings": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "pattern", "scope", "target", "severity"],
        "properties": {
          "id": { "type": "string" },
          "pattern": { "type": "string" },
          "scope": { "enum": ["file", "file_pair", "module", "module_pair", "codebase"] },
          "target": { "oneOf": [
            { "type": "string" },
            { "type": "array", "items": { "type": "string" } }
          ]},
          "severity": { "type": "number", "minimum": 0, "maximum": 1 },
          "confidence": { "type": "number", "minimum": 0, "maximum": 1 },
          "evidence": { "type": "object" },
          "description": { "type": "string" },
          "remediation": { "type": "string" }
        }
      }
    }
  }
}
```

---

## HTML Report

Generated via `shannon-insight report`:

```python
def generate_html_report(result: AnalysisResult, output_path: Path) -> None:
    """
    Generate standalone HTML report with embedded CSS/JS.
    """
    template = load_template("report.html")

    html = template.render(
        title=f"Shannon Insight Report - {result.context.root.name}",
        timestamp=result.timestamp,
        scores=result.scores,
        findings=result.findings,
        treemap_data=generate_treemap_data(result),
        signal_table=generate_signal_table(result),
    )

    output_path.write_text(html)
```

---

## Persistence

### TensorSnapshot

If `--save` is specified, persist snapshot to SQLite:

```python
@dataclass
class TensorSnapshot:
    """Point-in-time capture of analysis."""

    id: str                      # UUID
    timestamp: datetime
    commit: str | None           # Git HEAD

    # Serialized data
    entities: list[dict]         # Entity dicts
    signals: list[dict]          # SignalValue dicts
    relations: list[dict]        # Relation dicts
    findings: list[dict]         # Finding dicts

    # Summary
    file_count: int
    finding_count: int
    codebase_health: float
```

### Snapshot Persistence

```python
def persist_snapshot(
    result: AnalysisResult,
    store: FactStore,
    db_path: Path,
) -> str:
    """
    Persist snapshot to SQLite. Returns snapshot ID.
    """
    snapshot = TensorSnapshot(
        id=str(uuid.uuid4()),
        timestamp=result.timestamp,
        commit=result.context.head_commit,
        entities=serialize_entities(store.entities),
        signals=serialize_signals(store.signals),
        relations=serialize_relations(store.relations),
        findings=[asdict(f) for f in result.findings],
        file_count=result.file_count,
        finding_count=len(result.findings),
        codebase_health=result.codebase_health,
    )

    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            INSERT INTO snapshots (id, timestamp, commit, data, file_count, finding_count, health)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            snapshot.id,
            snapshot.timestamp.isoformat(),
            snapshot.commit,
            json.dumps(asdict(snapshot)),
            snapshot.file_count,
            snapshot.finding_count,
            snapshot.codebase_health,
        ))

    return snapshot.id
```

### Database Schema

```sql
CREATE TABLE IF NOT EXISTS snapshots (
    id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    commit TEXT,
    data TEXT NOT NULL,  -- JSON blob
    file_count INTEGER NOT NULL,
    finding_count INTEGER NOT NULL,
    health REAL NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_snapshots_timestamp ON snapshots(timestamp);
CREATE INDEX IF NOT EXISTS idx_snapshots_commit ON snapshots(commit);

CREATE TABLE IF NOT EXISTS finding_lifecycle (
    finding_id TEXT NOT NULL,
    snapshot_id TEXT NOT NULL,
    status TEXT NOT NULL,  -- 'open', 'resolved'
    first_seen TEXT NOT NULL,
    last_seen TEXT NOT NULL,
    persistence_count INTEGER DEFAULT 1,
    PRIMARY KEY (finding_id, snapshot_id),
    FOREIGN KEY (snapshot_id) REFERENCES snapshots(id)
);

CREATE TABLE IF NOT EXISTS signal_history (
    entity_key TEXT NOT NULL,
    signal TEXT NOT NULL,
    snapshot_id TEXT NOT NULL,
    value REAL NOT NULL,
    PRIMARY KEY (entity_key, signal, snapshot_id),
    FOREIGN KEY (snapshot_id) REFERENCES snapshots(id)
);
```

---

## CI/CD Integration

### Exit Codes

```python
class ExitCode(IntEnum):
    SUCCESS = 0
    FINDINGS_EXIST = 1
    HIGH_SEVERITY_FINDINGS = 2
    ERROR = 3

def determine_exit_code(
    findings: list[Finding],
    fail_on: str,  # "any", "high", "none"
) -> ExitCode:
    if fail_on == "none":
        return ExitCode.SUCCESS

    if not findings:
        return ExitCode.SUCCESS

    if fail_on == "any":
        return ExitCode.FINDINGS_EXIST

    if fail_on == "high":
        high_severity = [f for f in findings if f.severity >= 0.8]
        if high_severity:
            return ExitCode.HIGH_SEVERITY_FINDINGS

    return ExitCode.SUCCESS
```

### Usage in CI

```yaml
# GitHub Actions
- name: Run Shannon Insight
  run: |
    shannon-insight --json --fail-on high
  continue-on-error: true

# GitLab CI
shannon-insight:
  script:
    - shannon-insight --json --fail-on any
  allow_failure: true
```

---

## Analysis Result

The final output object:

```python
@dataclass
class AnalysisResult:
    """Complete analysis result."""

    # Context
    context: RuntimeContext
    timestamp: datetime

    # Counts
    file_count: int
    module_count: int
    finding_count: int

    # Scores (0-1 internal, display as 1-10)
    codebase_health: float
    architecture_health: float
    wiring_score: float

    # Findings (ranked)
    findings: list[Finding]

    # Optional snapshot ID
    snapshot_id: str | None = None
```
