"""Probe generation and execution for layer validation."""

import llm
from layers import get_layer_order, get_layer_info

def generate_probes(layer_name: str, layer_content: str, idea: str) -> list[dict]:
    """
    Generate probes to validate current layer before proceeding.

    Args:
        layer_name: Name of current layer
        layer_content: What has been decided in this layer
        idea: Original user idea

    Returns:
        List of probe dicts with 'question' and 'rationale'
    """
    layer_order = get_layer_order()
    current_idx = layer_order.index(layer_name)

    # Get next layer for context
    next_layer = None
    if current_idx < len(layer_order) - 1:
        next_layer = layer_order[current_idx + 1]
        next_layer_info = get_layer_info(next_layer)

    prompt = f"""You are validating the {layer_name} layer of a specification.

Original Idea: {idea}

Current Layer ({layer_name}) Decisions:
{layer_content}

Your task: Generate 2-3 probes to test if these decisions are stable enough to proceed to the next layer ({next_layer if next_layer else 'final spec'}).

A probe is a "what would break?" question that tests an assumption:
- Good: "If we need real-time updates, can the proposed architecture support it?"
- Bad: "Should we add real-time updates?" (not a probe, just a question)

Format your response as JSON:
[
  {{
    "question": "If [assumption from current layer], would [consequence at next layer] break?",
    "rationale": "Why this probe matters"
  }},
  ...
]

Generate 2-3 probes now."""

    messages = [
        {"role": "system", "content": "You are a technical probe generator. Output valid JSON only."},
        {"role": "user", "content": prompt}
    ]

    response = llm.chat(messages, temperature=0.3)

    # Parse JSON response
    import json
    try:
        probes = json.loads(response)
        return probes
    except json.JSONDecodeError:
        # Fallback: extract JSON from markdown code blocks
        import re
        json_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', response, re.DOTALL)
        if json_match:
            probes = json.loads(json_match.group(1))
            return probes
        else:
            # Return a default probe if parsing fails
            return [{
                "question": f"Are the {layer_name} decisions clear enough to proceed?",
                "rationale": "General validation probe"
            }]


def execute_probe(probe: dict, layer_name: str, layer_content: str, all_context: str) -> dict:
    """
    Execute a probe and determine if it passes or fails.

    Args:
        probe: Probe dict with 'question' and 'rationale'
        layer_name: Current layer name
        layer_content: Current layer decisions
        all_context: All previous context

    Returns:
        Dict with 'passed' (bool), 'reasoning' (str), 'concerns' (list)
    """
    prompt = f"""You are validating a specification layer using probe-based testing.

Context:
{all_context}

Current Layer ({layer_name}):
{layer_content}

Probe Question:
{probe['question']}

Probe Rationale:
{probe['rationale']}

Evaluate whether this probe PASSES or FAILS:
- PASS: The current layer decisions adequately address this concern
- FAIL: There's a gap or instability that would cause problems later

Respond in JSON format:
{{
  "passed": true/false,
  "reasoning": "Explain why this probe passes or fails",
  "concerns": ["specific concern 1", "specific concern 2"] (if failed)
}}
"""

    messages = [
        {"role": "system", "content": "You are a technical validator. Output valid JSON only."},
        {"role": "user", "content": prompt}
    ]

    response = llm.chat(messages, temperature=0.3)

    # Parse JSON response
    import json
    try:
        result = json.loads(response)
        return result
    except json.JSONDecodeError:
        # Fallback: extract JSON from markdown
        import re
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group(1))
            return result
        else:
            # Conservative fallback: assume probe failed
            return {
                "passed": False,
                "reasoning": "Could not parse probe result",
                "concerns": ["Parse error in probe execution"]
            }


def run_probes(layer_name: str, layer_content: str, idea: str, all_context: str) -> tuple[list[dict], float]:
    """
    Generate and run all probes for a layer.

    Args:
        layer_name: Current layer
        layer_content: Layer decisions
        idea: Original idea
        all_context: All previous context

    Returns:
        Tuple of (probe_results, confidence_delta)
    """
    probes = generate_probes(layer_name, layer_content, idea)

    results = []
    confidence_delta = 0.0

    from config import PROBE_PASS_BOOST, PROBE_FAIL_PENALTY

    for probe in probes:
        result = execute_probe(probe, layer_name, layer_content, all_context)
        results.append({
            "probe": probe,
            "result": result
        })

        if result["passed"]:
            confidence_delta += PROBE_PASS_BOOST
        else:
            confidence_delta += PROBE_FAIL_PENALTY  # Note: this is negative

    return results, confidence_delta
