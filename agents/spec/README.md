# Spec Generation Agent (GLM 4.7)

A probe-based specification generation agent that transforms ideas into validated, implementation-ready specs using GLM 4.7.

## Philosophy

**Never elaborate layer N+1 until layer N is validated through probes.**

This agent doesn't ask "is this complete?" — it asks "what would break if we proceeded?" Stability is verified through cheap tests (probes) that expose gaps before they become expensive problems.

## The Four-Layer Process

1. **Business Layer**: Problem, Users, Value, Constraints
2. **Product Layer**: Features, Flows, Data, Integrations
3. **Technical Layer**: Architecture, Stack, Scale, Security
4. **Implementation Layer**: Structure, APIs, DB, Deployment

Each layer must pass probe-based validation (confidence ≥ 0.7) before proceeding to the next.

## Setup

### Prerequisites

- Python 3.10+
- GLM API key ([Get one here](https://open.bigmodel.cn/))

### Installation

```bash
# Clone or navigate to the project
cd agents/spec

# Install dependencies
pip install -r requirements.txt

# Set your GLM API key
export GLM_API_KEY=your-glm-api-key-here
```

### Configuration

Edit `config.py` to adjust:

- **Model**: Change `GLM_MODEL` to `"glm-4"` or `"glm-4-plus"` based on your access
- **Token budgets**: Adjust per-layer token limits
- **Confidence thresholds**: Tune validation sensitivity

## Usage

### Basic Usage

```bash
python agent.py --idea "A marketplace for local farmers"
```

### Specify Output File

```bash
python agent.py --idea "Your idea here" --output my_spec.md
```

### Help

```bash
python agent.py --help
```

## How It Works

### 1. Layer Elaboration

The agent asks focused questions for each layer:
- Business: "What problem? Who are users? What's the value?"
- Product: "What features? What flows? What data?"
- Technical: "What architecture? What stack? What scale?"
- Implementation: "What structure? What APIs? What deployment?"

### 2. Probe Generation

Before moving to the next layer, the agent generates 2-3 probes:
- "If we assume real-time sync, does the architecture support it?"
- "If we need 10k concurrent users, does the DB choice hold?"
- "If payments are required, is there a clear integration path?"

### 3. Probe Execution

Each probe is evaluated:
- **PASS**: Confidence increases (+0.1)
- **FAIL**: Confidence decreases (-0.2) and layer is refined

### 4. Refinement Loop

If confidence < 0.7, the agent refines the layer and re-runs probes (up to 2 refinements).

### 5. Final Output

A structured markdown spec with:
- All layer outputs
- Validation summary
- Identified risks
- Confidence score
- Next steps

## Example Output

```markdown
# Specification: A marketplace for local farmers

**Generated:** 2024-01-15 10:30:00
**Confidence Score:** 0.85
**Status:** ✅ Ready for Implementation

---

## Business Layer
...

## Product Layer
...

## Technical Layer
...

## Implementation Layer
...

---

## Identified Risks
1. Payment gateway integration complexity
2. Peak load during Saturday markets

---

## Validation Summary
**Total Probes Run:** 10
**Passed:** 9
**Failed:** 1
**Final Confidence:** 0.85
```

## Project Structure

```
agents/spec/
├── agent.py              # Main orchestration loop
├── config.py             # GLM configuration
├── llm.py                # GLM API wrapper
├── layers.py             # Layer definitions
├── probes.py             # Probe generation & execution
├── spec_output.py        # Markdown formatting
├── system_prompt.md      # Agent system prompt
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

## Advanced Usage

### Tracer Bullet Mode

For large/ambiguous ideas, the agent automatically suggests:
> "Let's trace ONE narrow use case through all 4 layers first."

This validates the path before expanding scope.

### Confidence Tuning

Adjust in `config.py`:

```python
MIN_CONFIDENCE_TO_PROCEED = 0.7  # Lower = faster, Higher = more thorough
PROBE_PASS_BOOST = 0.1           # Confidence gain per passed probe
PROBE_FAIL_PENALTY = -0.2        # Confidence loss per failed probe
```

### Custom Models

GLM uses OpenAI-compatible API. To use a different model:

```python
# config.py
GLM_MODEL = "glm-4"  # or any compatible model
```

## Troubleshooting

### "GLM_API_KEY not found"

```bash
export GLM_API_KEY=your-key-here
```

### "Connection error"

Check that `GLM_BASE_URL` in `config.py` is correct:
```python
GLM_BASE_URL = "https://open.bigmodel.cn/api/paas/v4/"
```

### Probes keep failing

Try:
1. Refine your initial idea to be more specific
2. Lower `MIN_CONFIDENCE_TO_PROCEED` in config.py
3. Increase refinement iterations in agent.py

### JSON parsing errors

The agent has fallbacks for JSON extraction. If issues persist, check GLM model temperature (default: 0.3 for probes, 0.7 for elaboration).

## Contributing

This is a standalone agent. Feel free to:
- Adjust layer definitions in `layers.py`
- Add custom probe types in `probes.py`
- Modify output format in `spec_output.py`

## License

MIT

## Credits

Built with GLM 4.7 (ZhipuAI) using probe-based validation methodology.
