import pytest
from app.agent import Agent

def test_agent_initialization():
    agent = Agent(name="TestAgent", level=1)
    assert agent.name == "TestAgent"
    assert agent.level == 1

def test_agent_perform_action():
    agent = Agent(name="ActionAgent", level=2)
    result = agent.perform_action("greet")
    assert isinstance(result, str)
    assert "greet" in result.lower()