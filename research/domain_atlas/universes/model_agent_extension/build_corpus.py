#!/usr/bin/env python3
"""Build the optional provider-neutral model/tool-agent extension universe.

This package is deliberately downstream of the deterministic SAN core.  It emits
research candidates and compiler contracts, never an autonomous application and
never authority for a generated proposal.
"""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
EDITION = 1
AS_OF = "2026-08-25"


def slug(value: str) -> str:
    return value.lower().replace("/", "_").replace("-", "_").replace(" ", "_")


def dump_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def dump_jsonl(path: Path, values: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(value, sort_keys=True) + "\n" for value in values), encoding="utf-8")


# id, name, sovereign subject, operation A, operation B, decision question, non-collapsing law
CONTEXT_ROWS = [
    ("task_intent", "Task intent", "the requested outcome, constraints and stopping condition", "declare task intent", "refine task intent", "Which outcome and non-goals are authoritative?", "task intent != prompt text"),
    ("task_identity", "Task identity", "stable task identity across attempts, providers and resumptions", "mint task identity", "relate task attempt", "Which attempts belong to the same task?", "task identity != invocation identity"),
    ("model_family_identity", "Model-family identity", "provider-neutral capability family identity", "classify model family", "compare model families", "Which capabilities define substitutability?", "model family != provider product name"),
    ("model_edition", "Model edition", "immutable or exactly identified model edition", "pin model edition", "invalidate model edition", "Is the invoked model exactly identified or merely aliased?", "model alias != model edition"),
    ("provider_deployment", "Provider deployment", "the concrete deployed model occurrence and mutable limits", "bind deployment occurrence", "probe deployment occurrence", "Which region, account and deployment served the request?", "documented model != deployed occurrence"),
    ("prompt_template_identity", "Prompt-template identity", "logical prompt-template identity independent of text storage", "mint prompt identity", "resolve prompt identity", "Which template is intended?", "prompt identity != prompt content"),
    ("prompt_edition", "Prompt edition", "immutable prompt content, variables and policy edition", "publish prompt edition", "compare prompt editions", "Which exact prompt and policy edition was used?", "prompt alias != prompt edition"),
    ("prompt_binding", "Prompt binding", "typed binding of declared variables to a prompt edition", "bind prompt variables", "validate prompt binding", "Are all variables typed and authorized?", "prompt binding != string interpolation"),
    ("context_bundle", "Context bundle", "ordered, attributed and sensitivity-labelled invocation context", "assemble context bundle", "verify context manifest", "Which items enter context and in what precedence?", "context bundle != concatenated text"),
    ("context_precedence", "Context precedence", "conflict and instruction-precedence policy among context sources", "assign context authority", "resolve context conflict", "Which source may instruct and which may only inform?", "content relevance != instruction authority"),
    ("invocation_identity", "Invocation identity", "one externally observable model-call attempt", "mint invocation identity", "relate invocation retry", "Is this a retry, fallback or new request?", "invocation retry != semantic replay"),
    ("input_schema", "Model input schema", "typed accepted input envelope and modality constraints", "declare input schema", "validate model input", "Which schema edition accepts this input?", "accepted input != semantically valid input"),
    ("output_schema", "Model output schema", "typed expected output independent of generation method", "declare output schema", "validate model output", "Which fields, partiality and unknowns are admissible?", "schema-valid output != true output"),
    ("structured_generation", "Structured generation", "constrained production of schema-shaped output", "compile output constraint", "decode constrained output", "Is structure enforced during decoding or checked afterward?", "grammar conformance != domain validity"),
    ("tool_definition", "Tool definition", "typed provider-neutral callable capability declaration", "register tool contract", "version tool contract", "Which input, output, error and effect contract applies?", "tool description != tool authority"),
    ("tool_visibility", "Tool visibility", "least-capability subset exposed for one invocation", "select visible tools", "prove tool minimization", "Which tools are necessary for this task stage?", "registered tool != visible tool"),
    ("tool_selection", "Tool selection", "model proposal to use a particular tool", "propose tool selection", "refuse tool proposal", "Is the proposed tool allowed for this task?", "tool selection != authorization"),
    ("tool_arguments", "Tool arguments", "typed proposed arguments with taint and provenance", "generate tool arguments", "validate tool arguments", "Are arguments schema-valid, authorized and untainted?", "valid JSON != authorized arguments"),
    ("tool_result", "Tool result", "typed observation returned by a core-executed effect", "ingest tool result", "classify tool result", "Is this result data, an error, or an instruction?", "tool result != trusted instruction"),
    ("multimodal_content", "Multimodal content", "typed text, image, audio, video and file content blocks", "classify content block", "normalize modality reference", "Which modality, encoding and trust label applies?", "modality support != semantic understanding"),
    ("streaming_response", "Streaming response", "partial output events, ordering and terminal disposition", "ingest output delta", "finalize output stream", "What makes a stream complete or unusable?", "last observed delta != completed response"),
    ("sampling_policy", "Sampling policy", "temperature, nucleus, seed and candidate-selection configuration", "bind sampling policy", "record sampling receipt", "Which stochastic controls were actually applied?", "low temperature != determinism"),
    ("nondeterminism", "Nondeterminism", "irreducible output variation and replay limitations", "classify nondeterminism", "measure output variation", "What equivalence, if any, is expected across reruns?", "same request != same output"),
    ("completion_disposition", "Completion disposition", "completed, truncated, refused, cancelled, failed and filtered outcomes", "classify completion", "record incomplete reason", "Did generation terminate with a usable result?", "transport success != usable completion"),
    ("retrieval_requirement", "Retrieval requirement", "whether external evidence retrieval is actually necessary", "declare retrieval need", "justify no retrieval", "Does this task require changing or private evidence?", "model recall != retrieved evidence"),
    ("retrieval_scope", "Retrieval scope", "authorized corpora, filters, time and tenant boundaries", "bind retrieval scope", "verify retrieval boundary", "Which sources may be searched for this task?", "retrieval access != disclosure authority"),
    ("retrieval_query", "Retrieval query", "typed query and expansion proposal with provenance", "propose retrieval query", "validate retrieval query", "May expansion alter the requested meaning?", "query expansion != user intent"),
    ("retrieval_result", "Retrieval result", "ranked observations with source identity and retrieval receipt", "ingest retrieval result", "deduplicate retrieval result", "What was observed and from which source edition?", "retrieval result != validated claim"),
    ("grounding", "Grounding", "support relation between output claims and admitted evidence", "link claim support", "measure support coverage", "Which claims are supported, contradicted or ungrounded?", "citation presence != grounding"),
    ("attribution", "Attribution", "source attribution and span-level support boundaries", "attach attribution", "verify attribution target", "Does the cited source directly support this claim?", "attribution != truth"),
    ("proposal", "Generated proposal", "a non-authoritative candidate plan, claim or action", "emit proposal", "withdraw proposal", "What type of downstream validation is required?", "proposal != decision"),
    ("plan", "Generated plan", "ordered proposed steps without execution authority", "construct plan", "revise plan", "Which preconditions and stop conditions govern the plan?", "plan != effect"),
    ("claim", "Generated claim", "a typed assertion awaiting evidence and validation", "extract generated claim", "link claim evidence", "Is the claim observed, inferred or speculative?", "generated claim != validated claim"),
    ("claim_validation", "Claim validation", "deterministic or human adjudication of generated claims", "submit claim for validation", "record validation verdict", "Which oracle can validate this claim class?", "model agreement != validation"),
    ("effect_intent_bridge", "Effect-intent bridge", "conversion of an admitted proposal into a core effect intent", "submit effect intent", "reject effect intent", "Which core authority admits this effect?", "tool call != effect intent"),
    ("effect_receipt_ingest", "Effect-receipt ingest", "observation of core-issued effect receipts", "ingest effect receipt", "correlate effect receipt", "Which executed effect does this receipt prove?", "model narration != effect receipt"),
    ("human_authority", "Human authority", "human identity, role, approval scope and revocation", "request human decision", "record human decision", "Which human has authority over this effect class?", "human presence != authorized approval"),
    ("machine_authority", "Machine authority", "delegated machine permissions bounded by policy", "request delegated authority", "verify delegation chain", "Which principal and policy grant this machine action?", "machine capability != machine authority"),
    ("approval", "Approval", "review and authorization decision over a specific proposal edition", "request approval", "invalidate approval", "Does approval bind the exact effect and inputs?", "approval != issuance != execution"),
    ("delegation", "Delegation", "scoped, expiring delegation among human and machine principals", "issue delegation request", "revoke delegation", "What scope, audience, expiry and depth apply?", "delegation != impersonation"),
    ("orchestration", "Agent orchestration", "coordination of bounded model and core stages", "schedule agent stage", "join agent stage", "Which stages may run concurrently and which require gates?", "orchestration != autonomy"),
    ("fallback", "Model fallback", "typed substitution after refusal, failure or budget exhaustion", "select fallback", "record fallback reason", "Is fallback semantically and legally compatible?", "available model != compatible fallback"),
    ("conversation_state", "Conversation state", "provider or application state associated with a conversation", "open conversation state", "close conversation state", "Where is state stored and for how long?", "conversation identifier != task identity"),
    ("working_memory", "Working memory", "ephemeral task-local notes and summaries", "write working memory", "expire working memory", "Which task and principal may read this memory?", "working memory != durable knowledge"),
    ("durable_memory", "Durable memory", "explicitly admitted cross-turn or cross-task retained facts", "propose memory write", "revoke memory item", "What consent, purpose and expiry authorize retention?", "generated summary != durable fact"),
    ("memory_partition", "Memory partition", "tenant, user, task and sensitivity isolation", "assign memory partition", "verify memory isolation", "Can this memory cross identity or purpose boundaries?", "shared vector index != shared authority"),
    ("context_compaction", "Context compaction", "loss-declared reduction of invocation history", "compact context", "verify compaction loss", "Which facts, constraints and provenance survived?", "shorter context != equivalent context"),
    ("token_budget", "Token budget", "finite input, output and reasoning-token admission", "reserve token budget", "settle token usage", "What happens before and after token exhaustion?", "token limit != cost limit"),
    ("time_budget", "Time budget", "deadlines and stage time allocations", "reserve time budget", "expire stage deadline", "Which deadline governs each call and effect?", "provider timeout != task cancellation"),
    ("cost_budget", "Cost budget", "finite monetary or credit admission and settlement", "precharge model cost", "settle model cost", "Which price edition and usage receipt apply?", "estimated cost != settled cost"),
    ("rate_quota", "Rate and quota", "provider occurrence request and token limits", "admit quota", "handle throttling", "Which mutable occurrence limit applies now?", "published quota != observed availability"),
    ("cancellation", "Cancellation", "requested cancellation and observed terminal disposition", "request cancellation", "confirm cancellation", "Did generation and downstream work actually stop?", "cancellation request != cancellation completion"),
    ("retry", "Retry", "bounded retry classification and replay safety", "classify retry", "schedule retry", "Is this call safe to replay and under what identity?", "retryable transport error != retry-safe effect"),
    ("evaluation_design", "Evaluation design", "task distribution, oracle, slices and admission thresholds", "declare evaluation design", "freeze evaluation edition", "Which claims may this evaluation support?", "benchmark score != universal fitness"),
    ("evaluation_dataset", "Evaluation dataset", "versioned cases, labels, licenses and contamination posture", "register evaluation dataset", "detect contamination", "Is the dataset representative and independent?", "test dataset != production distribution"),
    ("grader", "Evaluation grader", "deterministic, human or model-based scoring procedure", "run grader", "calibrate grader", "What validates the grader itself?", "model judge score != ground truth"),
    ("uncertainty", "Output uncertainty", "declared uncertainty, disagreement and abstention evidence", "estimate uncertainty", "trigger abstention", "Which uncertainty measure is meaningful for this task?", "verbal confidence != calibrated probability"),
    ("failure_slice", "Failure slice", "typed cohort of systematic errors or unsafe behavior", "define failure slice", "measure failure slice", "Which inputs and conditions concentrate failures?", "aggregate pass rate != slice safety"),
    ("red_team", "Adversarial evaluation", "hostile cases, attacker capability and defended outcome", "run adversarial case", "record exploit receipt", "Which threat model and privileges were exercised?", "no observed exploit != secure"),
    ("prompt_injection", "Prompt-injection boundary", "untrusted content attempting to alter instruction or tool behavior", "label untrusted instruction", "block injected control", "Which bytes are data and which principals may instruct?", "content sanitization != injection elimination"),
    ("data_exfiltration", "Data-exfiltration boundary", "unauthorized disclosure through output, tools or side channels", "classify disclosure sink", "refuse exfiltration path", "Can protected data reach this recipient or tool?", "read authorization != disclose authorization"),
    ("secret_boundary", "Secret boundary", "credential references and non-disclosure constraints", "bind secret reference", "redact secret observation", "May secret material enter model context?", "secret reference != secret value"),
    ("privacy_retention", "Privacy and retention", "provider processing, storage, residency and deletion posture", "bind retention policy", "record deletion request", "Which data may be retained by which processor?", "request storage flag != end-to-end deletion proof"),
    ("safety_policy", "Safety policy", "versioned classifier or policy intervention and appeal", "apply safety policy", "record safety refusal", "Which policy edition caused intervention?", "safety refusal != task impossibility"),
    ("provenance_trace", "Model provenance trace", "inputs, editions, transformations, outputs and receipts", "emit invocation trace", "verify trace linkage", "Can every material output be related to exact inputs and editions?", "trace != evidence of truth"),
    ("monitoring", "Model-system monitoring", "production quality, safety, cost and reliability observations", "emit model telemetry", "evaluate monitoring window", "Which thresholds trigger investigation or invalidation?", "telemetry presence != service health"),
    ("drift", "Model-system drift", "behavior change across provider, prompt, retrieval and data editions", "detect behavior drift", "classify drift cause", "What changed relative to the qualified baseline?", "provider alias stability != behavioral stability"),
    ("invalidation", "Qualification invalidation", "events that revoke prior model or system qualification", "invalidate qualification", "request requalification", "Which change makes prior evidence inadmissible?", "successful past eval != current qualification"),
    ("rollout", "Model rollout", "canary, shadow, parallel-run and rollback policy", "start shadow evaluation", "promote model edition", "Which evidence permits promotion?", "newer model != safe upgrade"),
    ("portability", "Provider portability", "portable requirement and provider-specific offer binding", "declare portable requirement", "compare provider offers", "Which semantics survive provider substitution?", "API compatibility != semantic portability"),
    ("local_remote_target", "Local and remote target", "deployment topology, hardware, trust and resource envelope", "bind inference target", "qualify inference target", "Which local or remote occurrence satisfies the contract?", "model weights != qualified serving target"),
]


# Only primary provider docs, normative/open standards, official project docs, and original papers.
SOURCE_ROWS = [
    ("openai_responses", "OpenAI", "Create a model response", "https://developers.openai.com/api/reference/cli/resources/responses/methods/create", "official_provider_contract"),
    ("openai_function_calling", "OpenAI", "Function calling", "https://platform.openai.com/docs/guides/function-calling", "official_provider_contract"),
    ("openai_structured_outputs", "OpenAI", "Structured Outputs", "https://platform.openai.com/docs/guides/structured-outputs", "official_provider_contract"),
    ("openai_tools", "OpenAI", "Using tools", "https://platform.openai.com/docs/guides/tools", "official_provider_contract"),
    ("openai_file_search", "OpenAI", "File search", "https://platform.openai.com/docs/guides/tools-file-search", "official_provider_contract"),
    ("openai_conversation_state", "OpenAI", "Conversation state", "https://platform.openai.com/docs/guides/conversation-state", "official_provider_contract"),
    ("openai_prompt_caching", "OpenAI", "Prompt caching", "https://platform.openai.com/docs/guides/prompt-caching", "official_provider_contract"),
    ("openai_evals", "OpenAI", "Evals", "https://platform.openai.com/docs/guides/evals", "official_provider_contract"),
    ("openai_data_controls", "OpenAI", "Data controls", "https://platform.openai.com/docs/models/default-usage-policies-by-endpoint", "official_provider_contract"),
    ("openai_model_versions", "OpenAI", "API backward compatibility", "https://platform.openai.com/docs/api-reference/backward-compatibility", "official_provider_contract"),
    ("anthropic_tool_use", "Anthropic", "Tool use", "https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/overview", "official_provider_contract"),
    ("anthropic_prompt_caching", "Anthropic", "Prompt caching", "https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching", "official_provider_contract"),
    ("anthropic_context_windows", "Anthropic", "Context windows", "https://docs.anthropic.com/en/docs/build-with-claude/context-windows", "official_provider_contract"),
    ("anthropic_citations", "Anthropic", "Citations", "https://docs.anthropic.com/en/docs/build-with-claude/citations", "official_provider_contract"),
    ("anthropic_structured_outputs", "Anthropic", "Structured outputs", "https://docs.anthropic.com/en/docs/build-with-claude/structured-outputs", "official_provider_contract"),
    ("anthropic_define_success", "Anthropic", "Define success criteria", "https://docs.anthropic.com/en/docs/test-and-evaluate/define-success", "official_provider_contract"),
    ("anthropic_eval_tool", "Anthropic", "Evaluation tool", "https://docs.anthropic.com/en/docs/test-and-evaluate/eval-tool", "official_provider_contract"),
    ("anthropic_jailbreaks", "Anthropic", "Mitigate jailbreaks and prompt injections", "https://docs.anthropic.com/en/docs/test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks", "official_provider_contract"),
    ("anthropic_batch", "Anthropic", "Message Batches", "https://docs.anthropic.com/en/docs/build-with-claude/batch-processing", "official_provider_contract"),
    ("anthropic_token_counting", "Anthropic", "Token counting", "https://docs.anthropic.com/en/docs/build-with-claude/token-counting", "official_provider_contract"),
    ("gemini_function_calling", "Google", "Gemini function calling", "https://ai.google.dev/gemini-api/docs/function-calling", "official_provider_contract"),
    ("gemini_structured_output", "Google", "Gemini structured output", "https://ai.google.dev/gemini-api/docs/structured-output", "official_provider_contract"),
    ("gemini_long_context", "Google", "Gemini long context", "https://ai.google.dev/gemini-api/docs/long-context", "official_provider_contract"),
    ("gemini_context_caching", "Google", "Gemini context caching", "https://ai.google.dev/gemini-api/docs/caching", "official_provider_contract"),
    ("gemini_safety_guidance", "Google", "Gemini safety and factuality guidance", "https://ai.google.dev/gemini-api/docs/safety-guidance", "official_provider_contract"),
    ("gemini_safety_settings", "Google", "Gemini safety settings", "https://ai.google.dev/gemini-api/docs/safety-settings", "official_provider_contract"),
    ("gemini_document_processing", "Google", "Gemini document processing", "https://ai.google.dev/gemini-api/docs/document-processing", "official_provider_contract"),
    ("gemini_embeddings", "Google", "Gemini embeddings", "https://ai.google.dev/gemini-api/docs/embeddings", "official_provider_contract"),
    ("gemini_tokens", "Google", "Gemini token counting", "https://ai.google.dev/gemini-api/docs/tokens", "official_provider_contract"),
    ("gemini_model_tuning", "Google", "Gemini model tuning", "https://ai.google.dev/gemini-api/docs/model-tuning", "official_provider_contract"),
    ("bedrock_converse", "AWS", "Amazon Bedrock Converse API", "https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html", "official_provider_contract"),
    ("bedrock_tool_use", "AWS", "Amazon Bedrock tool use", "https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use.html", "official_provider_contract"),
    ("bedrock_prompt_management", "AWS", "Amazon Bedrock Prompt management", "https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-management.html", "official_provider_contract"),
    ("bedrock_knowledge_bases", "AWS", "Amazon Bedrock Knowledge Bases", "https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html", "official_provider_contract"),
    ("bedrock_agents", "AWS", "Agents for Amazon Bedrock", "https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html", "official_provider_contract"),
    ("bedrock_guardrails", "AWS", "Amazon Bedrock Guardrails", "https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html", "official_provider_contract"),
    ("bedrock_model_evaluation", "AWS", "Amazon Bedrock model evaluation", "https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation.html", "official_provider_contract"),
    ("bedrock_automated_reasoning", "AWS", "Automated Reasoning checks", "https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-automated-reasoning-checks.html", "official_provider_contract"),
    ("azure_model_catalog", "Microsoft", "Microsoft Foundry model catalog", "https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/model-catalog-overview", "official_provider_contract"),
    ("azure_evaluation", "Microsoft", "Microsoft Foundry evaluation", "https://learn.microsoft.com/en-us/azure/foundry/how-to/evaluate-generative-ai-app", "official_provider_contract"),
    ("azure_risk_evaluators", "Microsoft", "Risk and safety evaluators", "https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/risk-safety-evaluators", "official_provider_contract"),
    ("azure_content_filter", "Microsoft", "Microsoft Foundry content filtering", "https://learn.microsoft.com/en-us/azure/ai-studio/concepts/content-filtering", "official_provider_contract"),
    ("azure_prompt_flow", "Microsoft", "Prompt flow", "https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/prompt-flow", "official_provider_contract"),
    ("azure_agents", "Microsoft", "Microsoft Foundry Agent Service", "https://learn.microsoft.com/en-us/azure/ai-foundry/agents/overview", "official_provider_contract"),
    ("cohere_tool_use", "Cohere", "Cohere tool use", "https://docs.cohere.com/docs/tool-use-overview", "official_provider_contract"),
    ("cohere_structured_outputs", "Cohere", "Cohere structured outputs", "https://docs.cohere.com/docs/structured-outputs", "official_provider_contract"),
    ("cohere_rag", "Cohere", "Cohere retrieval augmented generation", "https://docs.cohere.com/docs/retrieval-augmented-generation-rag", "official_provider_contract"),
    ("cohere_citations", "Cohere", "Cohere citations", "https://docs.cohere.com/docs/citations", "official_provider_contract"),
    ("cohere_embeddings", "Cohere", "Cohere embeddings", "https://docs.cohere.com/docs/embeddings", "official_provider_contract"),
    ("hf_chat_templates", "Hugging Face", "Transformers chat templates", "https://huggingface.co/docs/transformers/chat_templating", "official_project_documentation"),
    ("hf_generation", "Hugging Face", "Transformers text generation", "https://huggingface.co/docs/transformers/main_classes/text_generation", "official_project_documentation"),
    ("hf_tool_use", "Hugging Face", "Transformers tool use", "https://huggingface.co/docs/transformers/chat_extras", "official_project_documentation"),
    ("vllm_structured_outputs", "vLLM", "vLLM structured outputs", "https://docs.vllm.ai/en/latest/features/structured_outputs.html", "official_project_documentation"),
    ("vllm_serving", "vLLM", "vLLM OpenAI-compatible server", "https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html", "official_project_documentation"),
    ("mcp_spec", "Model Context Protocol", "MCP specification", "https://modelcontextprotocol.io/specification/2025-06-18", "normative_open_specification"),
    ("mcp_lifecycle", "Model Context Protocol", "MCP lifecycle", "https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle", "normative_open_specification"),
    ("mcp_authorization", "Model Context Protocol", "MCP authorization", "https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization", "normative_open_specification"),
    ("mcp_tools", "Model Context Protocol", "MCP tools", "https://modelcontextprotocol.io/specification/2025-06-18/server/tools", "normative_open_specification"),
    ("mcp_resources", "Model Context Protocol", "MCP resources", "https://modelcontextprotocol.io/specification/2025-06-18/server/resources", "normative_open_specification"),
    ("mcp_prompts", "Model Context Protocol", "MCP prompts", "https://modelcontextprotocol.io/specification/2025-06-18/server/prompts", "normative_open_specification"),
    ("mcp_sampling", "Model Context Protocol", "MCP sampling", "https://modelcontextprotocol.io/specification/2025-06-18/client/sampling", "normative_open_specification"),
    ("mcp_security", "Model Context Protocol", "MCP security best practices", "https://modelcontextprotocol.io/specification/2025-06-18/basic/security_best_practices", "normative_open_specification"),
    ("a2a_spec", "A2A Protocol", "Agent2Agent protocol specification", "https://a2a-protocol.org/v0.3.0/specification/", "normative_open_specification"),
    ("openapi_31", "OpenAPI Initiative", "OpenAPI Specification 3.1", "https://spec.openapis.org/oas/v3.1.0.html", "normative_open_specification"),
    ("json_schema_core", "IETF", "JSON Schema Core 2020-12", "https://json-schema.org/draft/2020-12/json-schema-core", "normative_open_specification"),
    ("json_schema_validation", "IETF", "JSON Schema Validation 2020-12", "https://json-schema.org/draft/2020-12/json-schema-validation", "normative_open_specification"),
    ("oauth_security", "IETF", "OAuth 2.0 Security Best Current Practice", "https://datatracker.ietf.org/doc/rfc9700/", "normative_open_specification"),
    ("oauth_resource_indicators", "IETF", "OAuth 2.0 Resource Indicators", "https://datatracker.ietf.org/doc/rfc8707/", "normative_open_specification"),
    ("oauth_dpop", "IETF", "OAuth 2.0 Demonstrating Proof of Possession", "https://datatracker.ietf.org/doc/rfc9449/", "normative_open_specification"),
    ("w3c_prov", "W3C", "PROV-O", "https://www.w3.org/TR/prov-o/", "normative_open_specification"),
    ("w3c_vc", "W3C", "Verifiable Credentials Data Model 2.0", "https://www.w3.org/TR/vc-data-model-2.0/", "normative_open_specification"),
    ("otel_genai", "OpenTelemetry", "Generative AI semantic conventions", "https://opentelemetry.io/docs/specs/semconv/gen-ai/", "normative_open_specification"),
    ("nist_ai_rmf", "NIST", "Artificial Intelligence Risk Management Framework 1.0", "https://www.nist.gov/itl/ai-risk-management-framework", "official_government_standard"),
    ("nist_genai_profile", "NIST", "Generative AI Profile NIST AI 600-1", "https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence", "official_government_standard"),
    ("owasp_prompt_injection", "OWASP", "LLM01 Prompt Injection", "https://genai.owasp.org/llmrisk/llm01-prompt-injection/", "official_security_project"),
    ("owasp_excessive_agency", "OWASP", "LLM06 Excessive Agency", "https://genai.owasp.org/llmrisk/llm062025-excessive-agency/", "official_security_project"),
    ("scitt_architecture", "IETF", "SCITT architecture", "https://datatracker.ietf.org/doc/rfc9943/", "normative_open_specification"),
    ("paper_rag", "Lewis et al.", "Retrieval-Augmented Generation", "https://arxiv.org/abs/2005.11401", "original_research_paper"),
    ("paper_react", "Yao et al.", "ReAct", "https://arxiv.org/abs/2210.03629", "original_research_paper"),
    ("paper_toolformer", "Schick et al.", "Toolformer", "https://arxiv.org/abs/2302.04761", "original_research_paper"),
    ("paper_gorilla", "Patil et al.", "Gorilla", "https://arxiv.org/abs/2305.15334", "original_research_paper"),
    ("paper_self_rag", "Asai et al.", "Self-RAG", "https://arxiv.org/abs/2310.11511", "original_research_paper"),
    ("paper_dspy", "Khattab et al.", "DSPy", "https://arxiv.org/abs/2310.03714", "original_research_paper"),
    ("paper_lmql", "Beurer-Kellner et al.", "Prompting Is Programming: LMQL", "https://arxiv.org/abs/2212.06094", "original_research_paper"),
    ("paper_jsonformer", "Willard and Louf", "Efficient Guided Generation for Large Language Models", "https://arxiv.org/abs/2307.09702", "original_research_paper"),
    ("paper_helm", "Liang et al.", "Holistic Evaluation of Language Models", "https://arxiv.org/abs/2211.09110", "original_research_paper"),
    ("paper_llm_judge", "Zheng et al.", "Judging LLM-as-a-Judge", "https://arxiv.org/abs/2306.05685", "original_research_paper"),
    ("paper_ragas", "Es et al.", "RAGAS", "https://arxiv.org/abs/2309.15217", "original_research_paper"),
    ("paper_ares", "Saad-Falcon et al.", "ARES", "https://arxiv.org/abs/2311.09476", "original_research_paper"),
    ("paper_selfcheckgpt", "Manakul et al.", "SelfCheckGPT", "https://arxiv.org/abs/2303.08896", "original_research_paper"),
    ("paper_semantic_uncertainty", "Kuhn et al.", "Semantic uncertainty", "https://arxiv.org/abs/2302.09664", "original_research_paper"),
    ("paper_webarena", "Zhou et al.", "WebArena", "https://arxiv.org/abs/2307.13854", "original_research_paper"),
    ("paper_agentbench", "Liu et al.", "AgentBench", "https://arxiv.org/abs/2308.03688", "original_research_paper"),
    ("paper_swebench", "Jimenez et al.", "SWE-bench", "https://arxiv.org/abs/2310.06770", "original_research_paper"),
    ("paper_osworld", "Xie et al.", "OSWorld", "https://arxiv.org/abs/2404.07972", "original_research_paper"),
    ("paper_injecagent", "Zhan et al.", "InjecAgent", "https://arxiv.org/abs/2403.02691", "original_research_paper"),
    ("paper_indirect_injection", "Greshake et al.", "Compromising real-world LLM-integrated applications", "https://arxiv.org/abs/2302.12173", "original_research_paper"),
    ("paper_lost_middle", "Liu et al.", "Lost in the Middle", "https://arxiv.org/abs/2307.03172", "original_research_paper"),
    ("paper_reflexion", "Shinn et al.", "Reflexion", "https://arxiv.org/abs/2303.11366", "original_research_paper"),
    ("paper_memgpt", "Packer et al.", "MemGPT", "https://arxiv.org/abs/2310.08560", "original_research_paper"),
    ("paper_tree_thoughts", "Yao et al.", "Tree of Thoughts", "https://arxiv.org/abs/2305.10601", "original_research_paper"),
    ("paper_constitutional", "Bai et al.", "Constitutional AI", "https://arxiv.org/abs/2212.08073", "original_research_paper"),
    ("paper_vllm", "Kwon et al.", "Efficient Memory Management for LLM Serving with PagedAttention", "https://arxiv.org/abs/2309.06180", "original_research_paper"),
    ("paper_speculative", "Leviathan et al.", "Fast Inference from Transformers via Speculative Decoding", "https://arxiv.org/abs/2211.17192", "original_research_paper"),
]


LIBRARY_ROWS = [
    ("contract_core", "Model extension contract core", "semantic_pure", "task/model/prompt/context identities and typed gaps"),
    ("task_intent", "Task intent types", "semantic_pure", "task outcomes, non-goals, constraints and stopping rules"),
    ("prompt_contract", "Prompt contract types", "semantic_pure", "prompt identity, editions, variables and precedence"),
    ("context_manifest", "Context manifest types", "semantic_pure", "ordered attributed context and sensitivity labels"),
    ("schema_bridge", "Schema bridge", "semantic_pure", "provider-neutral input/output/tool schema normalization"),
    ("structured_output_oracle", "Structured-output oracle", "test_oracle", "grammar and schema conformance without truth claims"),
    ("tool_contract_registry", "Tool contract registry", "semantic_pure", "versioned typed tool declarations and visibility"),
    ("proposal_types", "Proposal and claim types", "semantic_pure", "non-authoritative plans, claims and effect proposals"),
    ("claim_validation_bridge", "Claim validation bridge", "core_adapter", "submission to deterministic or human validation oracles"),
    ("authority_gate_bridge", "Authority gate bridge", "core_adapter", "core authorization, approval, delegation and revocation requests"),
    ("effect_intent_bridge", "Effect-intent bridge", "core_adapter", "typed submission to deterministic effect execution"),
    ("effect_receipt_bridge", "Effect-receipt bridge", "core_adapter", "receipt correlation without model-authored execution claims"),
    ("retrieval_contract", "Retrieval contract", "semantic_pure", "retrieval necessity, scope, query and result identity"),
    ("citation_verifier", "Citation and grounding verifier", "test_oracle", "claim-to-evidence support and attribution checks"),
    ("memory_partition", "Memory partition contract", "semantic_pure", "task, user, tenant, purpose, retention and consent boundaries"),
    ("context_compactor", "Loss-aware context compactor", "runtime_mechanism", "summaries with explicit retained and lost obligations"),
    ("budget_meter", "Model budget meter", "core_adapter", "token, time, cost and tool-call admission and settlement"),
    ("model_client_spi", "Model client SPI", "provider_port", "provider-neutral invocation, streaming, cancellation and usage"),
    ("openai_adapter", "OpenAI provider adapter", "provider_adapter", "OpenAI request/response mapping only"),
    ("anthropic_adapter", "Anthropic provider adapter", "provider_adapter", "Anthropic request/response mapping only"),
    ("gemini_adapter", "Gemini provider adapter", "provider_adapter", "Gemini request/response mapping only"),
    ("bedrock_adapter", "Bedrock provider adapter", "provider_adapter", "Bedrock request/response mapping only"),
    ("azure_adapter", "Microsoft Foundry provider adapter", "provider_adapter", "Foundry request/response mapping only"),
    ("local_inference_adapter", "Local inference adapter", "provider_adapter", "local serving occurrence mapping and qualification"),
    ("retry_cancel_runtime", "Retry and cancellation runtime", "runtime_mechanism", "bounded retry, fallback and cancellation disposition"),
    ("eval_harness", "Evaluation harness", "test_oracle", "datasets, slices, graders, thresholds and immutable receipts"),
    ("adversarial_oracle", "Adversarial test oracle", "test_oracle", "prompt injection, exfiltration and excessive-agency fixtures"),
    ("trace_exporter", "Model trace exporter", "core_adapter", "OpenTelemetry and provenance emission with redaction"),
    ("qualification_monitor", "Qualification and drift monitor", "runtime_mechanism", "behavior drift, invalidation and requalification triggers"),
    ("portability_conformance", "Provider portability conformance", "test_oracle", "same-requirement cross-provider negative and positive tests"),
]


INNOVATION_ROWS = [
    ("structured_outputs", 2024, "Provider APIs began enforcing subsets of JSON Schema during generation rather than relying only on post-parse repair.", ["openai_structured_outputs", "gemini_structured_output"]),
    ("grammar_guided_decoding", 2023, "Grammar- and schema-guided decoding made syntactic conformance a runtime mechanism separable from semantic validation.", ["paper_jsonformer", "paper_lmql"]),
    ("typed_tool_calling", 2023, "Typed tool schemas became a first-class model interface across multiple providers.", ["openai_function_calling", "anthropic_tool_use", "gemini_function_calling"]),
    ("mcp_open_tool_protocol", 2024, "MCP separated tool, resource, prompt, lifecycle and authorization protocol surfaces.", ["mcp_spec", "mcp_tools", "mcp_authorization"]),
    ("a2a_task_artifact_protocol", 2025, "A2A specified agent cards, tasks, messages, artifacts and task-state interoperability.", ["a2a_spec"]),
    ("retrieval_attribution_interfaces", 2023, "Provider and research systems exposed citations and claim-support surfaces distinct from retrieval ranking.", ["anthropic_citations", "cohere_citations", "paper_ragas"]),
    ("self_reflective_retrieval", 2023, "Self-RAG made retrieval and critique decisions explicit generation-time actions.", ["paper_self_rag"]),
    ("prompt_program_compilation", 2023, "DSPy and LMQL treated prompt/model interaction as optimizable or constrained programs rather than opaque strings.", ["paper_dspy", "paper_lmql"]),
    ("context_caching", 2024, "Provider-managed prefix/context caching introduced explicit retention, identity, latency and cost decision points.", ["openai_prompt_caching", "anthropic_prompt_caching", "gemini_context_caching"]),
    ("long_context_failure_research", 2023, "Lost-in-the-Middle demonstrated that nominal context capacity does not imply uniform evidence use.", ["paper_lost_middle"]),
    ("paged_kv_cache", 2023, "PagedAttention improved serving memory utilization while making serving runtime qualification distinct from model identity.", ["paper_vllm"]),
    ("speculative_decoding", 2023, "Speculative decoding reduced latency while preserving a target distribution under stated algorithmic conditions.", ["paper_speculative"]),
    ("executable_agent_benchmarks", 2023, "WebArena, AgentBench and SWE-bench shifted evaluation toward executable state and outcome oracles.", ["paper_webarena", "paper_agentbench", "paper_swebench"]),
    ("computer_environment_benchmark", 2024, "OSWorld added reproducible computer-environment tasks with execution-based evaluators.", ["paper_osworld"]),
    ("indirect_injection_benchmarks", 2024, "InjecAgent operationalized indirect prompt injection across tool-integrated scenarios.", ["paper_injecagent", "paper_indirect_injection"]),
    ("semantic_uncertainty", 2023, "Semantic-equivalence grouping reframed uncertainty beyond raw token probabilities.", ["paper_semantic_uncertainty"]),
    ("provider_neutral_trace_semantics", 2025, "OpenTelemetry defined common generative-system events and attributes for interoperable tracing.", ["otel_genai"]),
    ("resource_bound_tool_loops", 2025, "Provider APIs exposed finite tool-call and token limits as explicit invocation controls.", ["openai_responses", "anthropic_token_counting"]),
    ("formal_policy_response_checks", 2025, "Automated reasoning checks separated detect-mode policy findings from execution or blocking authority.", ["bedrock_automated_reasoning"]),
    ("model_agent_security_taxonomy", 2024, "NIST and OWASP consolidated prompt injection, disclosure, excessive agency and resource-consumption risks.", ["nist_genai_profile", "owasp_prompt_injection", "owasp_excessive_agency"]),
    ("portable_local_serving_api", 2023, "Local serving engines exposed compatibility APIs while retaining separate runtime and qualification identity.", ["vllm_serving", "paper_vllm"]),
    ("signed_transparent_receipts", 2026, "SCITT standardized signed statements and transparency receipts useful for model artifact and evaluation provenance.", ["scitt_architecture"]),
]


GAP_ROWS = [
    ("cross_provider_semantics", "API-level compatibility does not establish equal tool, schema, safety, refusal or state semantics."),
    ("model_alias_mutation", "Provider aliases may change behavior without an immutable edition becoming available."),
    ("seed_reproducibility", "Seeds do not establish cross-hardware, cross-batch or cross-provider deterministic replay."),
    ("structured_truth", "No general mechanism makes schema-conformant output factually or semantically correct."),
    ("tool_output_taint", "Portable taint propagation from untrusted tool output into later proposals is immature."),
    ("prompt_injection_elimination", "No general defense proves elimination of direct, indirect and multimodal prompt injection."),
    ("effect_attribution", "Causal attribution from a user intent through retrieved content to a proposed tool effect remains incomplete."),
    ("human_approval_quality", "Human approval is often recorded without proving attention, comprehension or exact proposal binding."),
    ("memory_deletion_proof", "Provider and downstream cache deletion is rarely accompanied by end-to-end verifiable receipts."),
    ("context_compaction_equivalence", "There is no universal proof that a compacted context preserves all decision-relevant meaning."),
    ("citation_entailment", "Citation links rarely prove that the cited span entails the generated claim."),
    ("uncertainty_calibration", "Portable calibrated uncertainty is unavailable for many open-ended generation tasks."),
    ("grader_validity", "Model-based graders can share biases, blind spots and contamination with evaluated systems."),
    ("benchmark_contamination", "Training-data and benchmark contamination are difficult to establish for closed models."),
    ("evaluation_transfer", "Performance on static benchmarks does not establish fitness under a target occurrence and workflow."),
    ("mutable_safety_layers", "Provider safety classifiers and policies may change independently of the selected model edition."),
    ("cost_settlement_portability", "Token accounting, cached-token treatment and hidden reasoning usage vary by provider."),
    ("cancellation_finality", "Provider acknowledgement of cancellation may not prove all generation and tool work stopped."),
    ("stream_partial_safety", "Consumers may act on partial streamed output before final safety or schema disposition."),
    ("fallback_equivalence", "Fallback models rarely have evidence for semantic equivalence on every failure slice."),
    ("local_target_qualification", "Weights and compatible endpoints do not qualify kernels, quantization, templates or hardware."),
    ("provider_retention_evidence", "Documented retention policy is not occurrence-specific evidence that a particular datum was deleted."),
    ("multi_agent_authority", "Delegation and revocation across heterogeneous agent protocols lack a universal effect-level proof."),
    ("open_standard_version_drift", "MCP, A2A and telemetry conventions are evolving and require edition-pinned adapters."),
    ("independent_security_review", "The corpus needs independent adversarial appraisal against its threat and authority contracts."),
]


CORE_IMPORT_ROWS = [
    ("canonical_identity", "../../compiler/compiler-metamodel.json", "identifier, edition, alias, occurrence and digest semantics"),
    ("data_types_shapes", "../data_shapes/README.md", "semantic types, carrier types, modality, encoding and loss"),
    ("connectors_protocols", "../connectors_protocols/README.md", "transport, protocol, source access and deployed connector occurrence"),
    ("runtime_resource", "../runtime_compute_resource/README.md", "resource admission, quota, allocation, cancellation and usage settlement"),
    ("security_privacy_trust", "../security_privacy_trust/README.md", "principal, authentication, authorization, approval, delegation, privacy and secrets"),
    ("lineage_provenance_evidence", "../lineage_provenance_evidence/README.md", "derivation, attribution, evidence evaluation and receipts"),
    ("quality_reconciliation", "../quality_observability_reconciliation/README.md", "declared versus observed, fitness, adjudication, correction and reconciliation"),
    ("provider_target", "../../compiler/provider_target_registry/README.md", "provider class, implementation artifact, offer, target and qualified occurrence"),
    ("library_registry", "../../compiler/library_registry/README.md", "library contribution, requirement, offer, dependency and removal seam"),
    ("messaging_channels", "../messaging_channels/README.md", "message delivery, replay, ordering, acknowledgement and dead-letter disposition"),
    ("pipeline_dataflow", "../pipeline_dataflow/README.md", "bounded orchestration, checkpoints, state and recovery"),
    ("classical_predictive_ml", "../method_kernels/README.md", "study, estimand, estimator, fitted model, evaluation and qualified kernel"),
]


# Evidence is routed by the semantic surface it supports.  No source is attached merely to
# increase a count: provider pages establish only concrete API mechanics, standards establish only
# their specified contracts, and papers establish only their reported methods or experiments.
EVIDENCE_GROUPS = [
    ({"task_intent", "task_identity", "invocation_identity"}, ["openai_responses", "a2a_spec", "mcp_lifecycle"]),
    ({"model_family_identity", "model_edition", "provider_deployment"}, ["openai_model_versions", "azure_model_catalog", "vllm_serving"]),
    ({"prompt_template_identity", "prompt_edition", "prompt_binding"}, ["bedrock_prompt_management", "openai_responses", "anthropic_define_success"]),
    ({"context_bundle", "context_precedence"}, ["anthropic_context_windows", "paper_lost_middle", "mcp_prompts"]),
    ({"input_schema", "output_schema", "structured_generation"}, ["json_schema_core", "openapi_31", "openai_structured_outputs", "gemini_structured_output"]),
    ({"tool_definition", "tool_visibility", "tool_selection", "tool_arguments", "tool_result"}, ["mcp_tools", "openai_function_calling", "anthropic_tool_use", "owasp_excessive_agency"]),
    ({"multimodal_content"}, ["openai_responses", "gemini_document_processing", "mcp_tools"]),
    ({"streaming_response", "completion_disposition"}, ["openai_responses", "bedrock_converse", "a2a_spec"]),
    ({"sampling_policy", "nondeterminism"}, ["openai_responses", "hf_generation", "paper_semantic_uncertainty"]),
    ({"retrieval_requirement", "retrieval_scope", "retrieval_query", "retrieval_result"}, ["paper_rag", "cohere_rag", "bedrock_knowledge_bases", "openai_file_search"]),
    ({"grounding", "attribution"}, ["anthropic_citations", "cohere_citations", "paper_ragas", "w3c_prov"]),
    ({"proposal", "plan"}, ["paper_react", "paper_tree_thoughts", "paper_reflexion", "a2a_spec"]),
    ({"claim", "claim_validation"}, ["paper_ares", "paper_selfcheckgpt", "bedrock_automated_reasoning", "w3c_prov"]),
    ({"effect_intent_bridge", "effect_receipt_ingest"}, ["mcp_tools", "owasp_excessive_agency", "scitt_architecture", "w3c_prov"]),
    ({"human_authority", "machine_authority", "approval", "delegation"}, ["mcp_authorization", "oauth_resource_indicators", "oauth_dpop", "owasp_excessive_agency"]),
    ({"orchestration", "fallback"}, ["a2a_spec", "paper_react", "openai_responses", "bedrock_agents"]),
    ({"conversation_state", "working_memory", "durable_memory", "memory_partition", "context_compaction"}, ["openai_conversation_state", "paper_memgpt", "openai_data_controls", "anthropic_context_windows"]),
    ({"token_budget", "time_budget", "cost_budget", "rate_quota"}, ["openai_responses", "anthropic_token_counting", "gemini_tokens", "gemini_context_caching"]),
    ({"cancellation", "retry"}, ["openai_responses", "mcp_lifecycle", "a2a_spec", "oauth_security"]),
    ({"evaluation_design", "evaluation_dataset", "grader", "failure_slice"}, ["paper_helm", "openai_evals", "azure_evaluation", "bedrock_model_evaluation"]),
    ({"uncertainty"}, ["paper_semantic_uncertainty", "paper_selfcheckgpt", "paper_llm_judge"]),
    ({"red_team"}, ["paper_injecagent", "paper_osworld", "azure_risk_evaluators", "nist_genai_profile"]),
    ({"prompt_injection"}, ["owasp_prompt_injection", "paper_indirect_injection", "paper_injecagent", "mcp_security"]),
    ({"data_exfiltration", "secret_boundary"}, ["owasp_excessive_agency", "owasp_prompt_injection", "mcp_authorization", "oauth_security"]),
    ({"privacy_retention"}, ["openai_data_controls", "nist_genai_profile", "mcp_authorization"]),
    ({"safety_policy"}, ["gemini_safety_guidance", "bedrock_guardrails", "azure_content_filter", "nist_genai_profile"]),
    ({"provenance_trace"}, ["otel_genai", "w3c_prov", "scitt_architecture"]),
    ({"monitoring", "drift", "invalidation", "rollout"}, ["otel_genai", "openai_evals", "openai_model_versions", "nist_ai_rmf"]),
    ({"portability", "local_remote_target"}, ["vllm_serving", "vllm_structured_outputs", "azure_model_catalog", "openai_model_versions"]),
]


EXTRA_SOURCE_CONTEXTS = {
    "anthropic_prompt_caching": ["context_bundle", "cost_budget"],
    "anthropic_batch": ["orchestration", "rate_quota"],
    "anthropic_eval_tool": ["evaluation_design", "grader"],
    "anthropic_jailbreaks": ["prompt_injection", "red_team"],
    "anthropic_structured_outputs": ["structured_generation", "output_schema"],
    "azure_agents": ["orchestration", "machine_authority"],
    "azure_prompt_flow": ["prompt_binding", "orchestration"],
    "bedrock_tool_use": ["tool_definition", "tool_arguments"],
    "cohere_embeddings": ["retrieval_query", "retrieval_result"],
    "cohere_structured_outputs": ["structured_generation", "output_schema"],
    "cohere_tool_use": ["tool_definition", "tool_selection"],
    "gemini_embeddings": ["retrieval_query", "retrieval_result"],
    "gemini_function_calling": ["tool_definition", "tool_arguments"],
    "gemini_long_context": ["context_bundle", "context_precedence"],
    "gemini_model_tuning": ["model_edition", "provider_deployment"],
    "gemini_safety_settings": ["safety_policy", "failure_slice"],
    "hf_chat_templates": ["prompt_edition", "prompt_binding"],
    "hf_tool_use": ["tool_definition", "tool_selection"],
    "json_schema_validation": ["input_schema", "output_schema"],
    "mcp_resources": ["retrieval_scope", "retrieval_result"],
    "mcp_sampling": ["sampling_policy", "nondeterminism"],
    "mcp_spec": ["tool_definition", "orchestration"],
    "openai_prompt_caching": ["context_bundle", "cost_budget"],
    "openai_tools": ["tool_definition", "tool_visibility"],
    "paper_constitutional": ["safety_policy", "claim_validation"],
    "paper_agentbench": ["evaluation_design", "failure_slice"],
    "paper_dspy": ["prompt_binding", "evaluation_design"],
    "paper_gorilla": ["tool_selection", "tool_arguments"],
    "paper_jsonformer": ["structured_generation", "output_schema"],
    "paper_lmql": ["structured_generation", "prompt_binding"],
    "paper_self_rag": ["retrieval_requirement", "grounding"],
    "paper_speculative": ["local_remote_target", "time_budget"],
    "paper_swebench": ["evaluation_dataset", "failure_slice"],
    "paper_toolformer": ["tool_selection", "tool_result"],
    "paper_vllm": ["local_remote_target", "cost_budget"],
    "paper_webarena": ["evaluation_dataset", "evaluation_design"],
    "w3c_vc": ["machine_authority", "provenance_trace"],
}


def evidence_for_context(context_id: str) -> list[str]:
    for context_ids, source_ids in EVIDENCE_GROUPS:
        if context_id in context_ids:
            return [f"source.mae.{source_id}" for source_id in source_ids]
    raise ValueError(f"No evidence routing for context {context_id}")


def schemas() -> dict[str, dict]:
    ref = {"type": "string", "pattern": "^[a-z][a-z0-9_.:-]+$"}
    base = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "additionalProperties": False,
    }
    return {
        "context": {**base, "required": ["context_id", "edition", "status", "name", "sovereign_subject", "owns", "does_not_own", "operation_refs", "decision_ref", "law_ref", "evidence_refs"], "properties": {"context_id": ref, "edition": {"const": 1}, "status": {"const": "candidate"}, "name": {"type": "string"}, "sovereign_subject": {"type": "string"}, "owns": {"type": "array", "minItems": 1}, "does_not_own": {"type": "array", "minItems": 3}, "operation_refs": {"type": "array", "minItems": 2}, "decision_ref": ref, "law_ref": ref, "evidence_refs": {"type": "array", "minItems": 1}}},
        "operation": {**base, "required": ["operation_id", "edition", "status", "name", "context_ref", "effect_posture", "input_contract", "output_contract", "failures", "receipts"], "properties": {"operation_id": ref, "edition": {"const": 1}, "status": {"const": "candidate"}, "name": {"type": "string"}, "context_ref": ref, "effect_posture": {"enum": ["pure", "read_observation", "proposal_only", "core_request", "evaluation", "control"]}, "input_contract": {"type": "object"}, "output_contract": {"type": "object"}, "failures": {"type": "array", "minItems": 2}, "receipts": {"type": "array", "minItems": 1}}},
        "decision": {**base, "required": ["decision_id", "edition", "status", "context_ref", "question", "allowed_values", "default", "binding_phase", "required_evidence"], "properties": {"decision_id": ref, "edition": {"const": 1}, "status": {"const": "candidate"}, "context_ref": ref, "question": {"type": "string"}, "allowed_values": {"type": "array", "minItems": 3}, "default": {"const": "refuse_material_unknown"}, "binding_phase": {"enum": ["intent_check", "logical_planning", "physical_binding", "runtime_admission", "post_effect_verification"]}, "required_evidence": {"type": "array", "minItems": 1}}},
        "law": {**base, "required": ["law_id", "edition", "status", "context_ref", "expression", "violation", "compiler_response", "test_oracle"], "properties": {"law_id": ref, "edition": {"const": 1}, "status": {"const": "candidate"}, "context_ref": ref, "expression": {"type": "string"}, "violation": {"type": "string"}, "compiler_response": {"const": "refuse_or_emit_typed_gap"}, "test_oracle": {"type": "string"}}},
        "source": {**base, "required": ["source_id", "edition", "status", "issuer", "title", "url", "authority", "source_kind", "retrieved_on", "use_limit"], "properties": {"source_id": ref, "edition": {"const": 1}, "status": {"const": "candidate"}, "issuer": {"type": "string"}, "title": {"type": "string"}, "url": {"type": "string", "pattern": "^https://"}, "authority": {"const": "primary"}, "source_kind": {"type": "string"}, "retrieved_on": {"type": "string"}, "use_limit": {"type": "string"}}},
        "source-coverage": {**base, "required": ["coverage_id", "edition", "status", "source_ref", "context_refs", "support_posture", "does_not_prove"], "properties": {"coverage_id": ref, "edition": {"const": 1}, "status": {"const": "candidate"}, "source_ref": ref, "context_refs": {"type": "array", "minItems": 1, "uniqueItems": True}, "support_posture": {"enum": ["documented_interface", "normative_contract", "reported_experiment", "risk_or_governance_guidance", "reference_implementation_mechanism"]}, "does_not_prove": {"type": "array", "minItems": 2}}},
        "library": {**base, "required": ["library_id", "edition", "status", "name", "library_kind", "owns", "must_not_own", "dependency_direction", "removal_seam", "test_boundary", "semantic_owner_context"], "properties": {"library_id": ref, "edition": {"const": 1}, "status": {"const": "candidate"}, "name": {"type": "string"}, "library_kind": {"type": "string"}, "owns": {"type": "string"}, "must_not_own": {"type": "array", "minItems": 3}, "dependency_direction": {"const": "extension_to_core_only"}, "removal_seam": {"type": "string"}, "test_boundary": {"type": "string"}, "semantic_owner_context": ref}},
        "compiler-mapping": {**base, "required": ["mapping_id", "edition", "status", "context_ref", "requirement", "offer_shape", "binding_phase", "proof_refs", "fallback", "core_valid_without_extension"], "properties": {"mapping_id": ref, "edition": {"const": 1}, "status": {"const": "candidate"}, "context_ref": ref, "requirement": {"type": "object"}, "offer_shape": {"type": "object"}, "binding_phase": {"type": "string"}, "proof_refs": {"type": "array", "minItems": 1}, "fallback": {"const": "refuse_or_explicit_non_model_path"}, "core_valid_without_extension": {"const": True}}},
        "proof": {**base, "required": ["proof_id", "edition", "status", "context_ref", "claim", "required_receipts", "invalidators", "negative_twin"], "properties": {"proof_id": ref, "edition": {"const": 1}, "status": {"const": "candidate"}, "context_ref": ref, "claim": {"type": "string"}, "required_receipts": {"type": "array", "minItems": 2}, "invalidators": {"type": "array", "minItems": 2}, "negative_twin": {"type": "string"}}},
        "innovation": {**base, "required": ["innovation_id", "edition", "status", "name", "year", "change", "evidence_refs", "limitations"], "properties": {"innovation_id": ref, "edition": {"const": 1}, "status": {"const": "candidate"}, "name": {"type": "string"}, "year": {"type": "integer", "minimum": 2021, "maximum": 2026}, "change": {"type": "string"}, "evidence_refs": {"type": "array", "minItems": 1}, "limitations": {"type": "array", "minItems": 1}}},
        "gap": {**base, "required": ["gap_id", "edition", "status", "known", "unknown", "blocking", "resolution_condition", "prohibited_assumption"], "properties": {"gap_id": ref, "edition": {"const": 1}, "status": {"const": "open"}, "known": {"type": "string"}, "unknown": {"type": "string"}, "blocking": {"type": "boolean"}, "resolution_condition": {"type": "string"}, "prohibited_assumption": {"type": "string"}}},
        "core-import": {**base, "required": ["import_id", "edition", "status", "core_path", "imports", "direction", "core_valid_without_extension", "extension_valid_without_core"], "properties": {"import_id": ref, "edition": {"const": 1}, "status": {"const": "candidate"}, "core_path": {"type": "string"}, "imports": {"type": "string"}, "direction": {"const": "extension_to_core"}, "core_valid_without_extension": {"const": True}, "extension_valid_without_core": {"const": False}}},
        "negative-twin": {**base, "required": ["twin_id", "left", "right", "unsafe_collapse", "expected"], "properties": {"twin_id": ref, "left": {"type": "string"}, "right": {"type": "string"}, "unsafe_collapse": {"type": "string"}, "expected": {"type": "string"}}},
        "useful-example": {**base, "required": ["example_id", "name", "intent", "stages", "core_effects", "required_proofs", "useful_outcome"], "properties": {"example_id": ref, "name": {"type": "string"}, "intent": {"type": "string"}, "stages": {"type": "array", "minItems": 3}, "core_effects": {"type": "array"}, "required_proofs": {"type": "array", "minItems": 2}, "useful_outcome": {"type": "string"}}},
    }


def build_records() -> dict[str, object]:
    contexts = []
    operations = []
    decisions = []
    laws = []
    mappings = []
    proofs = []
    for i, (cid, name, subject, op_a, op_b, question, law) in enumerate(CONTEXT_ROWS):
        op_refs = [f"operation.mae.{cid}.{slug(op_a)}", f"operation.mae.{cid}.{slug(op_b)}"]
        decision_id = f"decision.mae.{cid}"
        law_id = f"law.mae.{cid}"
        source_refs = evidence_for_context(cid)
        contexts.append({
            "context_id": f"context.mae.{cid}", "edition": EDITION, "status": "candidate", "name": name,
            "sovereign_subject": subject, "owns": [subject],
            "does_not_own": ["business-domain truth", "core authorization or effect execution", "classical predictive-model lifecycle"],
            "operation_refs": op_refs, "decision_ref": decision_id, "law_ref": law_id, "evidence_refs": source_refs,
        })
        posture_a = "proposal_only" if any(word in op_a for word in ("propose", "emit", "construct", "generate", "submit")) else "pure"
        posture_b = "evaluation" if any(word in op_b for word in ("validate", "verify", "measure", "evaluate", "detect", "calibrate")) else "control"
        for op_id, op_name, posture in zip(op_refs, (op_a, op_b), (posture_a, posture_b)):
            operations.append({
                "operation_id": op_id, "edition": EDITION, "status": "candidate", "name": op_name,
                "context_ref": f"context.mae.{cid}", "effect_posture": posture,
                "input_contract": {"schema_edition_required": True, "authority_labels_required": True},
                "output_contract": {"typed_outcome": True, "never_self_authorizing": True},
                "failures": ["invalid_or_unsupported_input", "material_authority_or_evidence_gap"],
                "receipts": ["operation_attempt_receipt", "typed_disposition_receipt"],
            })
        decisions.append({
            "decision_id": decision_id, "edition": EDITION, "status": "candidate", "context_ref": f"context.mae.{cid}",
            "question": question, "allowed_values": ["explicitly_admitted", "explicitly_refused", "unknown_or_inconclusive"],
            "default": "refuse_material_unknown", "binding_phase": ["intent_check", "logical_planning", "physical_binding", "runtime_admission", "post_effect_verification"][i % 5],
            "required_evidence": ["exact identities and editions", "typed authority and occurrence receipt"],
        })
        laws.append({
            "law_id": law_id, "edition": EDITION, "status": "candidate", "context_ref": f"context.mae.{cid}",
            "expression": law, "violation": f"Collapsing the two sides of '{law}' creates an unsafe or unprovable compiler inference.",
            "compiler_response": "refuse_or_emit_typed_gap", "test_oracle": f"negative twin must distinguish {law}",
        })
        proof_id = f"proof.mae.{cid}"
        proofs.append({
            "proof_id": proof_id, "edition": EDITION, "status": "candidate", "context_ref": f"context.mae.{cid}",
            "claim": f"The compiled plan preserves the {name.lower()} boundary.",
            "required_receipts": ["exact_identity_and_edition_receipt", "core_authority_or_evaluation_receipt"],
            "invalidators": ["mutable alias changed", "required receipt absent or expired"],
            "negative_twin": law,
        })
        mappings.append({
            "mapping_id": f"mapping.mae.{cid}", "edition": EDITION, "status": "candidate", "context_ref": f"context.mae.{cid}",
            "requirement": {"capability": cid, "semantic_law": law},
            "offer_shape": {"declared_capability": cid, "provider_occurrence_required": True, "qualification_receipt_required": True},
            "binding_phase": "physical_binding", "proof_refs": [proof_id],
            "fallback": "refuse_or_explicit_non_model_path", "core_valid_without_extension": True,
        })

    sources = [{
        "source_id": f"source.mae.{sid}", "edition": EDITION, "status": "candidate", "issuer": issuer,
        "title": title, "url": url, "authority": "primary", "source_kind": kind, "retrieved_on": AS_OF,
        "use_limit": "Supports only the documented mechanism or reported experiment; it does not prove provider portability, universal safety, or production fitness.",
    } for sid, issuer, title, url, kind in SOURCE_ROWS]

    reverse_evidence: dict[str, set[str]] = {row[0]: set() for row in SOURCE_ROWS}
    for context_ids, source_ids in EVIDENCE_GROUPS:
        for source_id in source_ids:
            reverse_evidence[source_id].update(context_ids)
    for source_id, context_ids in EXTRA_SOURCE_CONTEXTS.items():
        reverse_evidence[source_id].update(context_ids)
    kind_to_posture = {
        "official_provider_contract": "documented_interface",
        "official_project_documentation": "reference_implementation_mechanism",
        "normative_open_specification": "normative_contract",
        "official_government_standard": "risk_or_governance_guidance",
        "official_security_project": "risk_or_governance_guidance",
        "original_research_paper": "reported_experiment",
    }
    source_coverage = []
    for sid, _issuer, _title, _url, kind in SOURCE_ROWS:
        if not reverse_evidence[sid]:
            raise ValueError(f"No semantic coverage routing for source {sid}")
        source_coverage.append({
            "coverage_id": f"coverage.mae.{sid}", "edition": EDITION, "status": "candidate",
            "source_ref": f"source.mae.{sid}",
            "context_refs": [f"context.mae.{context_id}" for context_id in sorted(reverse_evidence[sid])],
            "support_posture": kind_to_posture[kind],
            "does_not_prove": ["universal correctness or safety", "fitness of an unqualified provider or target occurrence"],
        })

    libraries = [{
        "library_id": f"library.mae.{lid}", "edition": EDITION, "status": "candidate", "name": name,
        "library_kind": kind, "owns": owns,
        "must_not_own": ["business-domain decisions", "core effect authority", "implicit provider qualification"],
        "dependency_direction": "extension_to_core_only",
        "removal_seam": "Removing this library disables only its declared optional model capability; deterministic core plans remain valid.",
        "test_boundary": "Provider adapters, effects and nondeterministic outputs are replaced by transcript fixtures and typed receipts.",
    } for lid, name, kind, owns in LIBRARY_ROWS]

    library_context = {
        "contract_core": "task_intent",
        "task_intent": "task_intent",
        "prompt_contract": "prompt_binding",
        "context_manifest": "context_bundle",
        "schema_bridge": "output_schema",
        "structured_output_oracle": "structured_generation",
        "tool_contract_registry": "tool_definition",
        "proposal_types": "proposal",
        "claim_validation_bridge": "claim_validation",
        "authority_gate_bridge": "machine_authority",
        "effect_intent_bridge": "effect_intent_bridge",
        "effect_receipt_bridge": "effect_receipt_ingest",
        "retrieval_contract": "retrieval_requirement",
        "citation_verifier": "attribution",
        "memory_partition": "memory_partition",
        "context_compactor": "context_compaction",
        "budget_meter": "cost_budget",
        "model_client_spi": "provider_deployment",
        "openai_adapter": "provider_deployment",
        "anthropic_adapter": "provider_deployment",
        "gemini_adapter": "provider_deployment",
        "bedrock_adapter": "provider_deployment",
        "azure_adapter": "provider_deployment",
        "local_inference_adapter": "local_remote_target",
        "retry_cancel_runtime": "retry",
        "eval_harness": "evaluation_design",
        "adversarial_oracle": "red_team",
        "trace_exporter": "provenance_trace",
        "qualification_monitor": "monitoring",
        "portability_conformance": "portability",
    }
    for library in libraries:
        library_slug = library["library_id"].split(".")[-1]
        library["semantic_owner_context"] = f"context.mae.{library_context[library_slug]}"
    context_by_id = {row["context_id"]: row for row in contexts}

    def extension_capability_kind(kind: str) -> str:
        if kind == "semantic_pure":
            return "semantic_contract"
        if kind == "test_oracle":
            return "evidence"
        if kind == "core_adapter":
            return "assurance"
        if kind in {"provider_port", "provider_adapter"}:
            return "provider"
        return "runtime_mechanism"

    requirements = []
    for library in libraries:
        library_slug = library["library_id"].split(".")[-1]
        owner_ref = f"context.mae.{library_context[library_slug]}"
        owner = context_by_id[owner_ref]
        requirements.append({
            "record_kind": "capability_requirement",
            "requirement_id": f"requirement.mae.{library_slug}",
            "edition": EDITION,
            "status": "declared",
            "subject_ref": library["library_id"],
            "capability_kind": extension_capability_kind(library["library_kind"]),
            "contract_refs": [f"contract.mae.{library_slug}"],
            "operation_refs": owner["operation_refs"],
            "type_refs": ["type.mae.extension_contract"],
            "required_guarantees": [
                "The contribution is admitted only by explicit optional or intent-required extension intent.",
                "Generated output remains a non-authoritative proposal until deterministic validation and authority gates pass.",
                "Removing the extension leaves deterministic core proofs unchanged.",
            ],
            "applicability": {
                "when": ["The declared intent explicitly requests this optional model/agent capability."],
                "unless": ["The deterministic path satisfies the intent without the extension or policy prohibits it."],
                "scope_refs": [library["library_id"]],
            },
            "cardinality": "exactly_one",
            "binding_phase": "physical_binding",
            "criticality": "optional",
            "selection_laws": ["Select by exact immutable model/provider/target occurrence and qualification evidence; never by alias, marketing name or ambient availability."],
            "fallback_law": "omit_optional",
            "prohibited_traits": ["ambient model insertion", "self-authorization", "self-validation", "direct protected effect", "model self-report as evidence"],
            "evidence_gates": ["exact identity/edition", "schema and semantic validation", "representative and adversarial evaluation", "resource/security/privacy review", "core-issued receipts"],
            "owner_ref": owner_ref,
            "gaps": ["No provider occurrence is qualified by this candidate corpus."],
        })

    provider_offer_specs = [
        ("openai", "OpenAI", "openai_adapter", ["source.mae.openai_responses", "source.mae.openai_model_versions"], "target.mae.remote_api"),
        ("anthropic", "Anthropic", "anthropic_adapter", ["source.mae.anthropic_tool_use", "source.mae.anthropic_define_success"], "target.mae.remote_api"),
        ("gemini", "Google Gemini", "gemini_adapter", ["source.mae.gemini_function_calling", "source.mae.gemini_structured_output"], "target.mae.remote_api"),
        ("bedrock", "Amazon Bedrock", "bedrock_adapter", ["source.mae.bedrock_converse", "source.mae.bedrock_tool_use"], "target.mae.remote_api"),
        ("azure", "Microsoft Foundry", "azure_adapter", ["source.mae.azure_model_catalog", "source.mae.azure_evaluation"], "target.mae.remote_api"),
        ("local_inference", "Local inference occurrence", "local_inference_adapter", ["source.mae.vllm_serving", "source.mae.hf_generation"], "target.mae.local_runtime"),
    ]
    offers = [{
        "record_kind": "capability_offer",
        "offer_id": f"offer.mae.{slug}",
        "edition": EDITION,
        "status": "declared",
        "provider_ref": f"provider.mae.{slug}",
        "capability_kind": "provider",
        "contract_refs": ["contract.mae.model_client_spi", f"contract.mae.{adapter}"],
        "operation_refs": context_by_id["context.mae.provider_deployment"]["operation_refs"],
        "type_refs": ["type.mae.extension_contract"],
        "guarantees": [f"Official material documents parts of the {name} interface; no semantic portability, safety, correctness or production qualification is implied."],
        "limits": ["Exact immutable model edition, deployment occurrence, prompt/context, schema subset, tools, safety policy, cost, retention, cancellation and behavior require independent qualification."],
        "decision_refs": ["decision.mae.model_edition", "decision.mae.provider_deployment", "decision.mae.sampling_policy", "decision.mae.fallback"],
        "target_refs": [target],
        "applicability": {
            "when": ["The extension is explicitly requested and every required occurrence-specific qualification gate passes."],
            "unless": ["The extension is omitted, prohibited, unqualified or a deterministic alternative is selected."],
            "scope_refs": [f"provider.mae.{slug}"],
        },
        "exclusions": ["Provider documentation is not a conformance receipt.", "Generated output has no authority.", "The offer does not satisfy any deterministic core contract."],
        "conformance_receipts": [],
        "evidence_refs": evidence_refs,
        "validity": {"from": AS_OF, "until": None, "recheck_triggers": ["model alias/edition change", "provider deployment change", "prompt/tool/schema change", "policy/safety change", "evaluation expiry"]},
        "gaps": ["No exact provider/model/target occurrence has an executed SAN qualification receipt."],
    } for slug, name, adapter, evidence_refs, target in provider_offer_specs]

    qualification_profiles = []
    for library in libraries:
        library_slug = library["library_id"].split(".")[-1]
        qualification_profiles.append({
            "receipt_id": f"receipt.mae.{library_slug}",
            "edition": EDITION,
            "record_kind": "qualification_profile",
            "status": "template_not_executed",
            "subject_ref": library["library_id"],
            "claim": f"The exact {library['name']} occurrence preserves its typed optional-extension boundary without acquiring core truth, authority or effect ownership.",
            "scope": ["exact immutable model/provider/target occurrence", "exact prompt/context/tool/schema editions", "exact policy and resource configuration", "declared evaluation population and slices"],
            "environment": {},
            "configuration": {},
            "fixtures": ["representative task corpus", "schema and semantic negative twins", "provider refusal/error/cancellation cases", "prompt-injection and excessive-agency cases", "extension-removal case"],
            "oracles": ["typed schema and domain validator", "core authority/effect refusal", "execution-based task oracle where applicable", "resource/security/privacy receipt", "removal-seam proof"],
            "results": [],
            "limitations": ["This is an unexecuted qualification profile and proves no provider or model capability.", "Passing one profile proves only its exact occurrence, population, claim and validity window."],
            "evidence_refs": [],
            "validity": {"from": None, "until": None},
            "invalidation_triggers": ["model/provider/target change", "prompt/context/tool/schema change", "policy or data-distribution change", "evaluation/oracle edition change", "security/privacy incident"],
        })

    innovations = [{
        "innovation_id": f"innovation.mae.{iid}", "edition": EDITION, "status": "candidate", "name": iid.replace("_", " "),
        "year": year, "change": change, "evidence_refs": [f"source.mae.{ref}" for ref in refs],
        "limitations": ["A recent mechanism or evidence surface is not a universal correctness, safety, or substitutability guarantee."],
    } for iid, year, change, refs in INNOVATION_ROWS]

    gaps = [{
        "gap_id": f"gap.mae.{gid}", "edition": EDITION, "status": "open", "known": statement,
        "unknown": f"The portable proof and occurrence-specific evidence needed to close {gid.replace('_', ' ')}.",
        "blocking": True, "resolution_condition": "Independent tests produce exact-edition, exact-occurrence receipts over representative and adversarial slices.",
        "prohibited_assumption": "Do not infer closure from vendor documentation, aggregate benchmarks, model self-report, or a successful demo.",
    } for gid, statement in GAP_ROWS]

    imports = [{
        "import_id": f"import.mae.{iid}", "edition": EDITION, "status": "candidate", "core_path": path, "imports": imports,
        "direction": "extension_to_core", "core_valid_without_extension": True, "extension_valid_without_core": False,
    } for iid, path, imports in CORE_IMPORT_ROWS]

    examples = [
        {
            "example_id": "example.mae.evidence_synthesis", "name": "Evidence synthesis without effects",
            "intent": "Compare two exact-edition technical claims using admitted sources.",
            "stages": ["declare task intent", "bind exact model and prompt editions", "retrieve only admitted primary sources", "emit generated claims", "verify claim-attribution links", "return validated and unvalidated claims separately"],
            "core_effects": [], "required_proofs": ["citation target directly supports claim", "retrieved content never gains instruction authority", "uncertainty and uncovered claims are explicit"],
            "useful_outcome": "A typed evidence map that remains useful if the model extension is replaced by deterministic extraction.",
        },
        {
            "example_id": "example.mae.proposed_data_repair", "name": "Proposed data repair with governed effect",
            "intent": "Draft a repair for a diagnosed data-quality defect without granting the model write authority.",
            "stages": ["ingest deterministic defect receipt", "generate non-authoritative repair proposal", "validate schema and invariants", "obtain exact human approval", "submit core effect intent", "execute through core adapter", "ingest core effect receipt", "reconcile outcome"],
            "core_effects": ["effect intent is authorized and executed by deterministic core"],
            "required_proofs": ["proposal differs from approval", "approval differs from effect intent", "effect receipt is core-issued", "reconciliation observes target state"],
            "useful_outcome": "Human and deterministic gates retain control even when generation is nondeterministic or absent.",
        },
    ]
    negative_twins = [
        {"twin_id": "twin.mae.generated_validated_claim", "left": "generated claim", "right": "validated claim", "unsafe_collapse": "Fluent output would become accepted domain truth.", "expected": "compiler requires an admitted validation oracle or labels the claim unvalidated"},
        {"twin_id": "twin.mae.tool_effect_receipt", "left": "tool-call proposal", "right": "effect receipt", "unsafe_collapse": "The system would report an effect that was never authorized or executed.", "expected": "compiler submits a typed core effect intent and waits for a core-issued receipt"},
        {"twin_id": "twin.mae.retrieved_instruction", "left": "retrieved content", "right": "authorized instruction", "unsafe_collapse": "Indirect prompt injection gains control authority.", "expected": "compiler labels retrieved bytes as untrusted data and rejects control-flow influence"},
        {"twin_id": "twin.mae.alias_edition", "left": "provider model alias", "right": "immutable model edition", "unsafe_collapse": "Prior evaluation evidence is silently reused after behavior changes.", "expected": "compiler refuses exact-edition proof or forces requalification on alias resolution change"},
        {"twin_id": "twin.mae.retry_replay", "left": "retryable invocation", "right": "retry-safe downstream effect", "unsafe_collapse": "A transport retry duplicates a non-idempotent effect.", "expected": "compiler reuses no effect intent without the core idempotency and receipt contract"},
        {"twin_id": "twin.mae.shared_memory_authority", "left": "memory retrievability", "right": "memory disclosure authority", "unsafe_collapse": "Cross-tenant or cross-purpose facts leak into model context.", "expected": "compiler enforces identity, tenant, purpose, consent and expiry before retrieval"},
    ]

    return {
        "contexts.jsonl": contexts, "operations.jsonl": operations, "decisions.jsonl": decisions,
        "laws.jsonl": laws, "sources.jsonl": sources, "library-boundaries.jsonl": libraries,
        "source-coverage.jsonl": source_coverage,
        "innovations-2021-2026.jsonl": innovations, "gaps.jsonl": gaps,
        "compiler-mappings.jsonl": mappings, "proof-contracts.jsonl": proofs,
        "compiler-requirements-offers.jsonl": requirements + offers,
        "qualification-receipts.jsonl": qualification_profiles,
        "core-imports.jsonl": imports, "examples/useful-examples.json": examples,
        "examples/negative-twins.jsonl": negative_twins,
    }


def manifest(records: dict[str, object]) -> dict:
    count = lambda name: len(records[name])  # noqa: E731
    return {
        "package_id": "san.domain-atlas.model-agent-extension", "edition": EDITION,
        "status": "researched_candidate_optional_extension", "as_of": AS_OF,
        "dependency_law": "extension_to_deterministic_core_only",
        "core_valid_without_extension": True,
        "classical_predictive_ml_owned_here": False,
        "counts": {
            "contexts": count("contexts.jsonl"), "operations": count("operations.jsonl"),
            "decisions": count("decisions.jsonl"), "laws": count("laws.jsonl"),
            "operations_decisions_laws": count("operations.jsonl") + count("decisions.jsonl") + count("laws.jsonl"),
            "primary_sources": count("sources.jsonl"), "source_coverage_mappings": count("source-coverage.jsonl"), "library_boundaries": count("library-boundaries.jsonl"),
            "innovations_2021_2026": count("innovations-2021-2026.jsonl"), "gaps": count("gaps.jsonl"),
            "compiler_mappings": count("compiler-mappings.jsonl"), "proof_contracts": count("proof-contracts.jsonl"),
            "compiler_requirements_offers": count("compiler-requirements-offers.jsonl"),
            "qualification_profiles": count("qualification-receipts.jsonl"),
            "core_imports": count("core-imports.jsonl"), "useful_examples": count("examples/useful-examples.json"),
            "negative_twins": count("examples/negative-twins.jsonl"),
        },
    }


def classical_ml_boundary() -> dict:
    return {
        "boundary_id": "boundary.mae.classical_predictive_ml", "edition": EDITION, "status": "candidate",
        "neighbor": "classical predictive and statistical learning", "owned_here": False,
        "owner_path": "../method_kernels/README.md",
        "neighbor_owns": ["study design", "target and label semantics", "features", "estimands", "estimators", "training", "fitted-model identity", "calibration", "predictive evaluation", "drift and qualified inference kernels"],
        "extension_owns": ["generative model invocation", "prompt and context editions", "structured generation", "tool-call proposals", "retrieval-grounding interfaces", "model/agent evaluation slices", "optional memory and provider adapters"],
        "integration_law": "A classical predictive model may be exposed through a core qualified-model operation; it does not become an LLM/agent extension merely because a service API invokes it.",
        "forbidden_collapses": ["generation model == predictive estimator", "prompt == feature vector", "verbal confidence == calibrated probability", "agent evaluation == predictive-model validation"],
    }


def metamodel() -> dict:
    return {
        "metamodel_id": "metamodel.mae.v1", "edition": EDITION,
        "purpose": "Optional provider-neutral model and tool-agent extension over deterministic core contracts.",
        "identities": ["task", "task_attempt", "model_family", "model_edition", "provider_deployment_occurrence", "prompt_template", "prompt_edition", "context_bundle", "invocation", "proposal", "claim", "effect_intent", "effect_receipt", "evaluation_run", "qualification_receipt"],
        "constitutional_laws": [
            "extension -> deterministic core; deterministic core never depends on extension",
            "generated output -> proposal; proposal never self-authorizes",
            "plan != validated claim != effect intent != effect receipt",
            "tool definition != visibility != selection != authorization != execution",
            "retrieval result != trusted instruction != validated evidence",
            "model alias != immutable edition != deployed occurrence",
            "schema conformance != domain validity != factual truth",
            "same request != same output; nondeterminism is recorded, bounded and evaluated",
            "classical predictive ML remains a neighboring core universe",
            "absence of the extension leaves every deterministic compiler proof valid",
        ],
        "binding_chain": ["intent", "extension capability requirement", "provider-neutral offer", "exact provider/model/prompt/target occurrence", "qualification receipt", "runtime resource admission", "generated proposal", "core validation/authorization", "core effect intent", "core effect receipt"],
    }


def emit(base: Path) -> None:
    records = build_records()
    for name, value in records.items():
        if name.endswith(".jsonl"):
            dump_jsonl(base / name, value)  # type: ignore[arg-type]
        else:
            dump_json(base / name, value)
    for name, value in schemas().items():
        dump_json(base / "schemas" / f"{name}.schema.json", value)
    dump_json(base / "manifest.json", manifest(records))
    dump_json(base / "metamodel.json", metamodel())
    dump_json(base / "classical-predictive-ml-boundary.json", classical_ml_boundary())


def comparable_files(base: Path) -> list[Path]:
    return sorted(
        path.relative_to(base)
        for path in base.rglob("*")
        if path.is_file()
        and "__pycache__" not in path.parts
        and path.suffix != ".pyc"
        and path.name not in {"README.md", "validate_corpus.py", "build_corpus.py"}
    )


def check() -> int:
    with tempfile.TemporaryDirectory(prefix="mae-build-") as tmp:
        temp = Path(tmp)
        emit(temp)
        expected = comparable_files(temp)
        actual = comparable_files(HERE)
        if expected != actual:
            print("FAIL generated file set differs")
            return 1
        for rel in expected:
            if (temp / rel).read_bytes() != (HERE / rel).read_bytes():
                print(f"FAIL generated artifact differs: {rel}")
                return 1
    print("PASS deterministic regeneration")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        return check()
    emit(HERE)
    print(f"built {manifest(build_records())['counts']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
