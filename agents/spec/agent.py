#!/usr/bin/env python3
"""Main spec generation agent."""

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown

import llm
from layers import get_layer_order, get_layer_info
from probes import run_probes
from spec_output import format_spec, save_spec
from config import MIN_CONFIDENCE_TO_PROCEED

console = Console()


def load_system_prompt() -> str:
    """Load system prompt from file."""
    with open("system_prompt.md", "r") as f:
        return f.read()


def elaborate_layer(
    layer_name: str,
    idea: str,
    all_context: str,
    conversation_history: list
) -> tuple[str, list]:
    """
    Elaborate a single layer through conversation.

    Args:
        layer_name: Name of layer to elaborate
        idea: Original user idea
        all_context: Context from previous layers
        conversation_history: Ongoing conversation

    Returns:
        Tuple of (layer_content, updated_conversation_history)
    """
    layer_info = get_layer_info(layer_name)
    system_prompt = load_system_prompt()

    # Initial prompt for this layer
    initial_prompt = f"""You are now working on the {layer_info['name']}.

Original Idea: {idea}

Previous Context:
{all_context}

Focus Areas for this layer:
{chr(10).join(f"- {area}" for area in layer_info['focus_areas'])}

Please elaborate this layer by addressing each focus area. Be specific and concrete.
If you need to make assumptions, state them clearly.

Output your response in a structured format following this template:
{layer_info['output_template']}
"""

    messages = [
        {"role": "system", "content": system_prompt},
        *conversation_history,
        {"role": "user", "content": initial_prompt}
    ]

    with console.status(f"[bold green]Elaborating {layer_info['name']}..."):
        response = llm.chat(messages, temperature=0.7)

    conversation_history.append({"role": "user", "content": initial_prompt})
    conversation_history.append({"role": "assistant", "content": response})

    return response, conversation_history


def refine_layer(
    layer_name: str,
    layer_content: str,
    probe_results: list,
    conversation_history: list
) -> tuple[str, list]:
    """
    Refine a layer based on failed probes.

    Args:
        layer_name: Layer to refine
        layer_content: Current layer content
        probe_results: Failed probe results
        conversation_history: Conversation history

    Returns:
        Tuple of (refined_content, updated_history)
    """
    layer_info = get_layer_info(layer_name)

    # Build refinement prompt from failed probes
    concerns = []
    for probe_result in probe_results:
        if not probe_result["result"]["passed"]:
            concerns.extend(probe_result["result"].get("concerns", []))

    refinement_prompt = f"""The {layer_info['name']} needs refinement based on probe results.

Current Content:
{layer_content}

Issues Found:
{chr(10).join(f"- {concern}" for concern in concerns)}

Please refine this layer to address these concerns. Be specific about how you're addressing each issue.
"""

    messages = [
        *conversation_history,
        {"role": "user", "content": refinement_prompt}
    ]

    with console.status(f"[bold yellow]Refining {layer_info['name']}..."):
        response = llm.chat(messages, temperature=0.7)

    conversation_history.append({"role": "user", "content": refinement_prompt})
    conversation_history.append({"role": "assistant", "content": response})

    return response, conversation_history


def process_layer(
    layer_name: str,
    idea: str,
    all_context: str,
    conversation_history: list,
    confidence: float
) -> tuple[str, float, list, list]:
    """
    Process a single layer: elaborate, probe, refine if needed.

    Args:
        layer_name: Layer to process
        idea: Original idea
        all_context: Previous context
        conversation_history: Conversation history
        confidence: Current confidence score

    Returns:
        Tuple of (layer_output, new_confidence, probe_results, updated_history)
    """
    layer_info = get_layer_info(layer_name)
    console.print(f"\n[bold blue]{'='*60}[/bold blue]")
    console.print(f"[bold blue]Processing: {layer_info['name']}[/bold blue]")
    console.print(f"[bold blue]{'='*60}[/bold blue]\n")

    # Elaborate layer
    layer_content, conversation_history = elaborate_layer(
        layer_name, idea, all_context, conversation_history
    )

    console.print(Panel(
        Markdown(layer_content),
        title=f"{layer_info['name']} Output",
        border_style="green"
    ))

    # Run probes
    console.print(f"\n[bold yellow]Running probes for {layer_info['name']}...[/bold yellow]\n")

    probe_results, confidence_delta = run_probes(
        layer_name,
        layer_content,
        idea,
        all_context + "\n\n" + layer_content
    )

    confidence += confidence_delta

    # Display probe results
    for i, probe_result in enumerate(probe_results, 1):
        probe = probe_result["probe"]
        result = probe_result["result"]

        status = "✅ PASS" if result["passed"] else "❌ FAIL"
        color = "green" if result["passed"] else "red"

        console.print(f"[{color}]{status}[/{color}] Probe {i}: {probe['question']}")
        console.print(f"  → {result['reasoning']}\n")

    console.print(f"[bold]Confidence: {confidence:.2f}[/bold]\n")

    # Refine if needed
    max_refinements = 2
    refinement_count = 0

    while confidence < MIN_CONFIDENCE_TO_PROCEED and refinement_count < max_refinements:
        console.print(f"[yellow]Confidence below threshold ({MIN_CONFIDENCE_TO_PROCEED}). Refining...[/yellow]\n")

        layer_content, conversation_history = refine_layer(
            layer_name,
            layer_content,
            probe_results,
            conversation_history
        )

        console.print(Panel(
            Markdown(layer_content),
            title=f"{layer_info['name']} (Refined)",
            border_style="yellow"
        ))

        # Re-run probes
        probe_results, confidence_delta = run_probes(
            layer_name,
            layer_content,
            idea,
            all_context + "\n\n" + layer_content
        )

        confidence += confidence_delta
        refinement_count += 1

        console.print(f"[bold]New Confidence: {confidence:.2f}[/bold]\n")

    if confidence < MIN_CONFIDENCE_TO_PROCEED:
        console.print(f"[red]Warning: Proceeding with confidence {confidence:.2f} < {MIN_CONFIDENCE_TO_PROCEED}[/red]\n")

    return layer_content, confidence, probe_results, conversation_history


def generate_spec(idea: str, output_file: str = None):
    """
    Main spec generation loop.

    Args:
        idea: User's idea
        output_file: Optional output filename
    """
    console.print(Panel.fit(
        f"[bold green]Spec Generation Agent[/bold green]\n\n"
        f"Idea: {idea}\n\n"
        f"This will take a few minutes. The agent will work through 4 layers:\n"
        f"1. Business\n"
        f"2. Product\n"
        f"3. Technical\n"
        f"4. Implementation",
        border_style="blue"
    ))

    # Initialize
    confidence = 0.5
    conversation_history = []
    all_context = f"Original Idea: {idea}\n\n"
    layer_outputs = {}
    all_probe_results = []
    risks = []

    # Process each layer
    layer_order = get_layer_order()

    for layer_name in layer_order:
        layer_content, confidence, probe_results, conversation_history = process_layer(
            layer_name,
            idea,
            all_context,
            conversation_history,
            confidence
        )

        layer_outputs[layer_name] = layer_content
        all_probe_results.extend(probe_results)

        # Extract risks from failed probes
        for probe_result in probe_results:
            if not probe_result["result"]["passed"]:
                concerns = probe_result["result"].get("concerns", [])
                risks.extend(concerns)

        # Update context for next layer
        all_context += f"\n\n{layer_content}\n"

        # Ensure minimum confidence for layer completion
        confidence = max(confidence, 0.7) if all(
            p["result"]["passed"] for p in probe_results
        ) else confidence

    # Generate final spec
    console.print("\n[bold green]Generating final specification...[/bold green]\n")

    spec = format_spec(
        idea,
        layer_outputs,
        all_probe_results,
        confidence,
        list(set(risks))  # Remove duplicates
    )

    # Save spec
    filename = save_spec(spec, output_file)

    console.print(Panel.fit(
        f"[bold green]✅ Specification Complete![/bold green]\n\n"
        f"Confidence: {confidence:.2f}\n"
        f"Saved to: {filename}\n\n"
        f"{'✅ Ready for implementation!' if confidence >= 0.7 else '⚠️ Consider refinement before implementation'}",
        border_style="green"
    ))

    # Display spec
    console.print("\n[bold]Generated Specification:[/bold]\n")
    console.print(Markdown(spec))


@click.command()
@click.option(
    "--idea",
    "-i",
    required=True,
    help="The idea to generate a spec for"
)
@click.option(
    "--output",
    "-o",
    default=None,
    help="Output filename (default: spec_TIMESTAMP.md)"
)
def main(idea: str, output: str):
    """Spec Generation Agent - Transform ideas into validated specs."""
    try:
        generate_spec(idea, output)
    except KeyboardInterrupt:
        console.print("\n[yellow]Generation interrupted by user.[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        raise


if __name__ == "__main__":
    main()
