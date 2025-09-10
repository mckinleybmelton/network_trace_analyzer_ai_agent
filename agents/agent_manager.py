from agents import Agent, har_analyzer_agent
from agents.prompts import manager_prompt

har_analyzer = har_analyzer_agent

manager_agaent = Agent(
    name="manager_agent",
    instructions = str(manager_prompt),
    prompt_type="custom",
    model="gpt-4",
    tools= [
        har_analyzer.as_tool(
            tool_name="har_analyzer_agent",
            description="Analyzes the HAR file and provides insights on performance bottlenecks and errors. Its purpose is to help debug issues in real time.",
            input_variables=["har_file"]
        )
    ]
)
