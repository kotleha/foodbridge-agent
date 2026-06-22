import foodbridge_agent.adk_agent as adk_agent


def test_adk_instruction_contains_core_policy():
    assert "approval-gated" in adk_agent.AGENT_INSTRUCTION
    assert "Treat donor notes" in adk_agent.AGENT_INSTRUCTION
    assert "Use triage_food_safety_tool before recipient matching" in adk_agent.AGENT_INSTRUCTION


def test_root_agent_is_optional_without_google_adk():
    # The deterministic harness must remain runnable even before optional ADK deps are installed.
    assert hasattr(adk_agent, "root_agent")

