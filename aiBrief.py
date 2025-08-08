from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from ddgs import DDGS
from agno.team import Team
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timezone
import json


cred = credentials.Certificate("firebase-credentials.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

 #----------------------FUNCTIONS----------------------#   

def now_date_str():
    """Returns (‘M-D-YYYY’, now_datetime local)"""
    now_local = datetime.now()
    date_str   = f"{now_local.month}-{now_local.day}-{now_local.year}"
    return date_str, now_local
    
def save_digest_to_firestore(markdown_text):
    date_str, now = now_date_str()
    doc_ref = db.collection("daily_digests").document(date_str)
    doc_ref.set({
        "content":   markdown_text,
        "timestamp": now
    })


def save_articles(category: str, articles: list, date_str: str):
    col = f"{category}_{date_str}"
    for art in articles:
        db.collection(col).add({
            "url":       art["url"],
            "title":     art.get("title",""),
            "excerpt":   art.get("excerpt",""),
            "timestamp": datetime.now(timezone.utc)
        })

def save_summaries(category: str, summaries: list, date_str: str):
    col = f"{category}_{date_str}"
    for summ in summaries:
        db.collection(col).add({
            "url":       summ["url"],
            "summary":   summ["summary"],
            "timestamp": datetime.now(timezone.utc)
        })


#--------------------------------------------------------------#
#----------------------AGENTS----------------------#

ai_news_fetcher_agent = Agent(
    model = OpenAIChat(id = "gpt-4o-mini"),
    tools = [DuckDuckGoTools()],
    instructions=(
        "Fetch 50 recent AI news announcements. "
        "Return exactly a JSON array of objects with keys "
        "`title`, `url`, and `summary` (2-3 sentence summary). "
        "Do NOT include any explanation, markdown, or extra text."
    ),
    show_tool_calls = True,
    markdown = False
)

product_news_fetcher_agent = Agent(
    model = OpenAIChat(id = "gpt-4o-mini"),
    tools = [DuckDuckGoTools()],
    instructions=(
        "Fetch 50 recent AI product announcements. "
        "Return exactly a JSON array of objects with keys "
        "`title`, `url`, and `summary` (2-3 sentence summary). "
        "Do NOT include any explanation, markdown, or extra text."
    ),
    show_tool_calls = True,
    markdown = False
)

research_news_fetcher_agent = Agent(
    model = OpenAIChat(id = "gpt-4o-mini"),
    tools = [DuckDuckGoTools()],
    instructions=(
        "Fetch 50 recent AI research related announcements. "
        "Return exactly a JSON array of objects with keys "
        "`title`, `url`, and `summary` (2-3 sentence summary). "
        "Do NOT include any explanation, markdown, or extra text."
    ),
    show_tool_calls = True,
    markdown = False
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
    instructions = """
You’re the Daily AI Briefing editor. For **each** of these categories—**Products**, **AI News**, and **Research**—do the following:

1. From the list, **select the 5 most important items**.  
2. For each selected item, use its `summary` field as a single bullet point.  
3. Structure the output in Markdown with three sections:

**Products**  
- <5 bullet-point summaries>

**AI News**  
- <5 bullet-point summaries>

**Research**  
- <5 bullet-point summaries>
  
Products list: {json.dumps(prods)}  
AI News list:  {json.dumps(news)}  
Research list: {json.dumps(research)}
""",
    markdown = True
)




# ai_digest_team = Team(
#     mode = "coordinate",
#     members = [news_fetcher_agent, summarizer_agent, trend_analyst_agent, editor_agent],
#     model = OpenAIChat(id="gpt-4o-mini"),
#     instructions = ["Only return markdown formatted content",
#     "Do not include tool internals in final output"],
#     show_tool_calls = True,
#     debug_mode = True,
#     markdown = True
# )



#news_fetcher_agent.print_response("Get 5 AI news articles with links and short summaries posted in the last 30 minutes.")


#ai_digest_team.print_response(
 
 #   "Generate today’s AI briefing with latest developments and trends."
#)









#----------------------------------------------------------------#




def init_day_doc(date_str: str, now: datetime):
    # top-level collection "7-31-2025", doc ID "7-31-2025"
    meta_ref = db.collection(date_str).document("metadata")
    meta_ref.set({"timestamp": now})
    return meta_ref

def save_articles_with_summary(day_ref, category: str, items: list):
    """
    day_ref: DocumentReference for the day
    category: one of "productNews","aiNews","researchNews"
    items: list of dicts each having 'title','url','summary'
    """
    col = day_ref.collection(category)
    for art in items:
        col.add({
            "title":     art["title"],
            "url":       art["url"],
            "summary":   art["summary"],
            "timestamp": datetime.now(timezone.utc)
        })


#----------------------MAIN FUNCTION----------------------#

def run_daily_pipeline(): 
    # 1) date & day_doc
    date_str, now = now_date_str()
    day_ref = init_day_doc(date_str, now)

    # 2) fetch+summarize in one go
    raw_p  = product_news_fetcher_agent.run(..., stream=False).content
    prods  = json.loads(raw_p)
    save_articles_with_summary(day_ref, "productNews", prods)

    raw_n  = ai_news_fetcher_agent.run(..., stream=False).content
    news   = json.loads(raw_n)
    save_articles_with_summary(day_ref, "aiNews", news)

    raw_r  = research_news_fetcher_agent.run(..., stream=False).content
    research = json.loads(raw_r)
    save_articles_with_summary(day_ref, "researchNews", research)

    # 3) build editor prompt
    prompt = f"""
Using these three inputs, produce a **Daily AI Briefing** in Markdown.
Bold headers for Products, AI News, and Research, with top-3 bullet takeaways each.

• Products: {json.dumps(prods)}  
• AI News:  {json.dumps(news)}  
• Research: {json.dumps(research)}
"""
    briefing_md = editor_agent.run(prompt, stream=False).content

    # 4) save final briefing as a field on the day document
    day_ref.update({"briefing": briefing_md})

    print(f"✅ Done! All data under collection “{date_str}” with subcollections for each category.")
    
if __name__ == "__main__":
    run_daily_pipeline()