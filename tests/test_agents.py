"""Tests for Agent Architecture and Knowledge Base Retrieval."""

from app.agents.legal_team import AGENT_NAMES, build_legal_team
from app.agents.tools import (
    clear_consulted_sources,
    get_last_consulted_sources,
    search_legal_library,
)


def test_agent_names_list():
    """Verify exactly 3 designated agents are present."""
    assert len(AGENT_NAMES) == 3
    assert "Legal Query Analyzer" in AGENT_NAMES
    assert "Legal Research Agent" in AGENT_NAMES
    assert "Legal Answer Reviewer" in AGENT_NAMES


def test_build_legal_team():
    """Verify Agno Team composition and configuration."""
    team = build_legal_team(api_key="mock_test_key_xyz")
    assert team.name == "Indian Legal Assistant Team"
    assert len(team.members) == 3

    member_names = [m.name for m in team.members]
    assert "Legal Query Analyzer" in member_names
    assert "Legal Research Agent" in member_names
    assert "Legal Answer Reviewer" in member_names

    # Check that Legal Research Agent has the search_legal_library tool
    research_agent = next(m for m in team.members if m.name == "Legal Research Agent")
    assert research_agent.tools is not None
    assert len(research_agent.tools) >= 1


def test_search_legal_library_tenancy():
    """Verify search tool returns lease guidelines for tenancy queries."""
    clear_consulted_sources()
    result = search_legal_library("tenant security deposit wear and tear")
    assert "Model Tenancy Act" in result
    sources = get_last_consulted_sources()
    assert any("Tenancy & Security Deposits" in s for s in sources)


def test_search_legal_library_nda():
    """Verify search tool returns NDA provisions for trade secret / confidentiality query."""
    clear_consulted_sources()
    result = search_legal_library("mutual non-disclosure confidentiality exclusions")
    assert "Indian Contract Act" in result
    sources = get_last_consulted_sources()
    assert any("Non-Disclosure Agreements" in s for s in sources)


def test_search_legal_library_empty_query():
    """Verify graceful message on empty search query."""
    result = search_legal_library("")
    assert "No query provided" in result
