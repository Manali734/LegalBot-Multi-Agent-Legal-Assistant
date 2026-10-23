"""LegalBot Multi-Agent Team for Indian Legal System.

Coordinates three collaborating Agno agents:
1. Legal Query Analyzer: Categorizes inquiry and frames issues under Indian law.
2. Legal Research Agent: Investigates Indian statutes, precedents, and sample documents.
3. Legal Answer Reviewer: Audits findings, eliminates hallucinations, and authors final memo.
"""

from typing import Any, Dict, List, Optional
from agno.agent import Agent
from agno.team import Team, TeamMode

from app import config
from app.agents.tools import (
    clear_consulted_sources,
    get_last_consulted_sources,
    search_legal_library,
)

AGENT_NAMES = [
    "Legal Query Analyzer",
    "Legal Research Agent",
    "Legal Answer Reviewer",
]


def create_model_instance(api_key: Optional[str] = None, model_id: Optional[str] = None):
    """Instantiate the active LLM provider (Google Gemini or Groq)."""
    provider = config.MODEL_PROVIDER

    if provider == "google":
        from agno.models.google import Gemini

        key = api_key if api_key is not None else config.GEMINI_API_KEY
        m_id = model_id if model_id is not None else config.GEMINI_MODEL
        return Gemini(id=m_id, api_key=key)
    else:
        from agno.models.groq import Groq

        key = api_key if api_key is not None else config.GROQ_API_KEY
        m_id = model_id if model_id is not None else config.GROQ_MODEL
        return Groq(id=m_id, api_key=key)


def build_legal_team(api_key: Optional[str] = None, model_id: Optional[str] = None) -> Team:
    """Build the three collaborating Agno agents and coordinate them via an Agno Team."""
    model = create_model_instance(api_key=api_key, model_id=model_id)

    # Agent 1: Legal Query Analyzer (Indian Law)
    analyzer_agent = Agent(
        name="Legal Query Analyzer",
        role="Analyze user inquiries and classify them under Indian legal domains and statutes.",
        model=model,
        telemetry=False,
        description=(
            "An analytical legal expert specializing in Indian law (Indian Contract Act 1872, "
            "Transfer of Property Act 1882, Model Tenancy Act, Consumer Protection Act 2019, "
            "Copyright Act 1957, IT Act 2000). Classifies domain, extracts facts, and frames specific legal issues."
        ),
        instructions=[
            "1. Identify the relevant Indian Central or State statutory domain.",
            "2. Extract material facts and identify any missing factual elements.",
            "3. Formulate 2-3 precise legal questions for statutory investigation.",
        ],
    )

    # Agent 2: Legal Research Agent (Indian Statutes & Precedents)
    research_agent = Agent(
        name="Legal Research Agent",
        role="Research Indian statutory provisions, landmark Supreme Court rulings, and library documents.",
        model=model,
        tools=[search_legal_library],
        telemetry=False,
        description=(
            "An Indian legal researcher equipped with search_legal_library. Looks up specific sections "
            "(e.g. Sec 27 ICA, Sec 106 TPA, Sec 11 Model Tenancy Act), timelines, and landmark Supreme Court rulings."
        ),
        instructions=[
            "1. Invoke search_legal_library with keywords from the inquiry to find grounding Indian legal provisions.",
            "2. Identify statutory sections, permissible exceptions, limitation periods, and Supreme Court case laws.",
            "3. Explicitly cite the consulted document titles and statutory sections.",
        ],
    )

    # Agent 3: Legal Answer Reviewer
    reviewer_agent = Agent(
        name="Legal Answer Reviewer",
        role="Audit findings, eliminate unsupported claims, and author final Indian legal memo.",
        model=model,
        telemetry=False,
        description=(
            "A senior legal compliance auditor in Indian law. Scrutinizes findings, ensures strict adherence "
            "to Indian statutory doctrine (e.g. post-employment non-competes are void under Sec 27 ICA), "
            "eliminates foreign/US legal misconceptions, and formats the verified legal response."
        ),
        instructions=[
            "1. Audit the findings to ensure complete conformity with Indian statutes and judicial precedents.",
            "2. Strip out any unsupported claims or non-Indian legal concepts (e.g., at-will employment is not Indian law).",
            "3. Author the final response formatted with:",
            "   - **Legal Domain & Summary**: Applicable Indian statute and concise conclusion.",
            "   - **Key Statutory Provisions & Precedents**: Specific sections and rulings.",
            "   - **Applied Analysis & Practical Rights**: Concrete legal advice under Indian law.",
            "   - **Reviewer Audit Note**: Confirmation of statutory grounding.",
        ],
    )

    # Agno Team Coordinator
    legal_team = Team(
        name="Indian Legal Assistant Team",
        members=[analyzer_agent, research_agent, reviewer_agent],
        model=model,
        tools=[search_legal_library],
        add_member_tools_to_context=True,
        mode=TeamMode.coordinate,
        telemetry=False,
        instructions=[
            "Coordinate the three agents sequentially to produce an authoritative Indian legal advisory memo:",
            "1. Have Legal Query Analyzer frame the issue under Indian statutory law.",
            "2. Have Legal Research Agent search the legal library and provide grounded Indian citations.",
            "3. Have Legal Answer Reviewer audit and synthesize the verified final legal guidance.",
        ],
    )

    return legal_team


def run_legal_workflow(
    question: str,
    team: Optional[Team] = None,
    image_bytes: Optional[bytes] = None,
    image_filename: Optional[str] = None,
    image_mime_type: Optional[str] = None,
) -> Dict[str, Any]:
    """Execute the multi-agent legal collaboration on a user question and optional document image."""
    clear_consulted_sources()

    evidence_context = ""
    candidate_models = [config.GEMINI_MODEL, "gemini-3-flash-preview", "gemini-3.5-flash", "gemini-flash-latest"]
    # De-duplicate preserving order
    seen = set()
    models_to_try = [m for m in candidate_models if not (m in seen or seen.add(m))]

    # 1. Document Image OCR / Vision Extraction
    if image_bytes and config.MODEL_PROVIDER == "google" and config.GEMINI_API_KEY:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=config.GEMINI_API_KEY)
        mime = image_mime_type or "image/jpeg"

        for model_id in models_to_try:
            try:
                ocr_response = client.models.generate_content(
                    model=model_id,
                    contents=[
                        types.Part.from_bytes(data=image_bytes, mime_type=mime),
                        (
                            "You are an Indian legal document analyst. Inspect this uploaded document image. "
                            "Transcribe all legible clauses, parties, dates, covenants, stamp details, "
                            "and factual terms for legal analysis under Indian law."
                        ),
                    ],
                    config={"http_options": {"timeout": 15000}},
                )
                if ocr_response and ocr_response.text:
                    evidence_context = (
                        f"\n\n[ATTACHED DOCUMENT EVIDENCE: {image_filename or 'Uploaded Image'}]\n"
                        f"{ocr_response.text.strip()}\n"
                        f"[END OF ATTACHED EVIDENCE]\n"
                    )
                    break
            except Exception:
                continue

    # 2. Search Grounding Statutory Documents
    search_query = f"{question} {evidence_context[:300]}"
    statutory_docs = search_legal_library(search_query)
    sources = get_last_consulted_sources()

    # 3. Multi-Agent Synthesis (Analyzer, Researcher, Reviewer)
    workflow_prompt = (
        f"You are LegalBot, an authoritative Indian Legal Advisory Team composed of:\n"
        f"1. Legal Query Analyzer: Categorize under Indian law (Contract Act 1872, Model Tenancy Act, Copyright Act, etc.) and extract material facts.\n"
        f"2. Legal Research Agent: Ground recommendations in Indian statutory sections, Supreme Court case law, and the library.\n"
        f"3. Legal Answer Reviewer: Audit findings, eliminate foreign/US legal concepts, and author a clear, professional memorandum.\n\n"
        f"USER LEGAL INQUIRY:\n"
        f"\"\"\"{question}\"\"\"\n"
        f"{evidence_context}\n"
        f"GROUNDING REFERENCE STATUTORY LIBRARY:\n"
        f"{statutory_docs}\n\n"
        f"Generate the verified Indian Legal Memorandum formatted with:\n"
        f"- **Legal Domain & Summary**: Specific Indian statutes and clear executive summary.\n"
        f"- **Key Statutory Provisions & Precedents**: Applicable sections and judicial rulings.\n"
        f"- **Applied Analysis & Practical Rights**: Direct, concrete advice addressing the question and any attached document.\n"
        f"- **Reviewer Audit Note**: Confirmation of statutory grounding under Indian law."
    )

    content_text = ""
    # Execute with fallback across flash models
    if config.MODEL_PROVIDER == "google" and config.GEMINI_API_KEY:
        from google import genai

        client = genai.Client(api_key=config.GEMINI_API_KEY)
        for model_id in models_to_try:
            try:
                resp = client.models.generate_content(
                    model=model_id,
                    contents=workflow_prompt,
                    config={"http_options": {"timeout": 25000}},
                )
                if resp and resp.text:
                    content_text = resp.text.strip()
                    break
            except Exception:
                continue

    # Fallback to Agno Team run if direct generation was empty
    if not content_text:
        try:
            active_team = team if team is not None else build_legal_team()
            run_output = active_team.run(workflow_prompt)
            if hasattr(run_output, "get_content_as_string"):
                content_text = run_output.get_content_as_string()
            elif hasattr(run_output, "content") and run_output.content:
                content_text = str(run_output.content)
            else:
                content_text = str(run_output)
        except Exception as e:
            content_text = f"Unable to generate response: {e}"

    return {
        "answer": content_text,
        "sources": sources,
    }
