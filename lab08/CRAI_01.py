import warnings
# Suppress specific Pydantic UserWarning
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

import os
from crewai import Task, Crew, Process, Agent
from crewai_tools import SerperDevTool

# Optional: suppress Pydantic deprecation warning
warnings.filterwarnings("ignore", category=DeprecationWarning)
# Suppress specific Pydantic UserWarning
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

# Set API keys securely (uncomment and provide values)
# os.environ["SERPER_API_KEY"] = "your-serper-api-key"
# os.environ["OPENAI_API_KEY"] = "your-openai-api-key"

search_tool = SerperDevTool()

def suggest_answers(topic):
    # Define agents with formatted goals
    researcher = Agent(
        role='Senior Researcher',
        goal=f'Uncover groundbreaking technologies in {topic}',
        verbose=True,
        memory=True,
        backstory=(
            "Driven by curiosity, you're at the forefront of "
            "innovation, eager to explore and share knowledge that could change "
            "the world."
        ),
        tools=[search_tool],
        allow_delegation=True
    )

    writer = Agent(
        role='Writer',
        goal=f'Narrate compelling tech stories about {topic}',
        verbose=True,
        memory=True,
        backstory=(
            "With a flair for simplifying complex topics, you craft "
            "engaging narratives that captivate and educate, bringing new "
            "discoveries to light in an accessible manner."
        ),
        tools=[search_tool],
        allow_delegation=False
    )

    # Define tasks
    research_task = Task(
        description=(
            f"Identify the next big trend in {topic}. "
            "Focus on identifying pros and cons and the overall narrative. "
            "Your final report should clearly articulate the key points, "
            "its market opportunities, and potential risks."
        ),
        expected_output='A comprehensive 3-paragraph long report on the latest AI trends.',
        tools=[search_tool],
        agent=researcher,
    )

    write_task = Task(
        description=(
            f"Compose an insightful article on {topic}. "
            "Focus on the latest trends and how it's impacting the industry. "
            "This article should be easy to understand, engaging, and positive."
        ),
        expected_output='A 4-paragraph article on AI advancements formatted as markdown.',
        tools=[search_tool],
        agent=writer,
        async_execution=False,
        output_file='new-blog-post5.md'  # Make sure this is supported in your version
    )

    crew = Crew(
        agents=[researcher, writer],
        tasks=[research_task, write_task],
        process=Process.sequential,
        memory=True,
        cache=True,
        max_rpm=100,
        share_crew=True
    )

    # Run the workflow
    result = crew.kickoff(inputs={'topic': topic})
    print(result)

# Example usage
suggest_answers('AI')
