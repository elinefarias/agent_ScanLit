from crewai import Agent

class TextAgents():
    def summarizer_agent(self):
        return Agent(
            role='Text Summarizer',
            goal='Summarize given texts',
            backstory='An expert in condensing information into concise summaries.',
            allow_delegation=False,
            verbose=True
        )