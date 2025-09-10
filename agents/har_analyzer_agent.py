from agents import Agent


har_analyzer_agent = Agent(
    name="har_analyzer_agent",
    instructions="You are an expert in analyzing HAR (HTTP Archive) files. Your task is to analyze the provided HAR file and deliver a detailed report highlighting performance bottlenecks, errors, and optimization opportunities. Provide actionable insights to help debug and improve web performance in real time."
)