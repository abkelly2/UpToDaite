from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.team import Team

news_fetcher_agent = Agent(
    model = OpenAIChat(id = "gpt-4o-mini"),
    tools = [DuckDuckGoTools()],
    instructions = "Fetch 100 recent AI news articles with links and short excerpts. Keep in mind the end goal is to have information regarding new AI products, new AI research, and new AI news.",
    show_tool_calls = True,
    markdown = True
)

summarizer_agent = Agent(
    model = OpenAIChat(id = "gpt-4o-mini"),
    instructions = "Summarize a news excerpt in 2-3 sentences in plain english",
    markdown = True
)

trend_analyst_agent = Agent(
    model = OpenAIChat(id = "gpt-4o-mini"),
    instructions = "Analyze summaries for recurring themes, notable orgs / people / products, and group by topic",
    markdown = True
)


editor_agent = Agent(
    model = OpenAIChat(id = "gpt-4o-mini"),
    instructions = """Create a daily AI briefing. Give it a title, and structure the content by theme. Each theme should have a bold header and bullet point summaries. Keep it concise and readable""",
    markdown = True
)




ai_digest_team = Team(
    mode = "coordinate",
    members = [news_fetcher_agent, summarizer_agent, trend_analyst_agent, editor_agent],
    model = OpenAIChat(id="gpt-4o-mini"),
    instructions = ["Only return markdown formatted content",
    "Do not include tool internals in final output"],
    show_tool_calls = True,
    markdown = True
)


ai_digest_team.print_response("Generate today's AI briefing with latest developments and trends")

