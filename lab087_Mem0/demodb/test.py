

from agents import Agent, WebSearchTool, function_tool, Runner
from datetime import datetime
import psycopg2
import os
import re
from dotenv import load_dotenv

load_dotenv()


@function_tool
def save_results(title: str, summary: str, vendor: str, url: str, category: str, tags: str) -> str:
    print(f"DEBUG: save_results called with title: {title}")
    try:
        conn = psycopg2.connect(
            dbname=os.environ.get("DB_NAME"),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASSWORD"),
            host=os.environ.get("DB_HOST"),
            port=os.environ.get("DB_PORT")
        )
        print("DEBUG: Database connection successful")
        
        cur = conn.cursor()
        
        # Convert tags string to array
        tags_array = [tag.strip() for tag in tags.split(',') if tag.strip()]
        
        cur.execute(
            """
            INSERT INTO ai_research (title, summary, vendor, url, category, tags)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (url) DO NOTHING;
            """,
            (title, summary, vendor, url, category, tags_array)
        )
        
        # Check if any rows were affected
        rows_affected = cur.rowcount
        print(f"DEBUG: Rows inserted: {rows_affected}")
        
        conn.commit()
        cur.close()
        conn.close()
        
        return f"Result saved to PostgreSQL - {rows_affected} rows inserted"
        
    except Exception as e:
        print(f"DEBUG: Error saving to database: {e}")
        return f"Error saving to database: {e}"



agent = Agent(
        name="Web searcher",
        instructions="""You are a helpful agent that searches for information and saves it to a database. 
        
        After searching for information, always extract and save the results using the save_results tool with these parameters:
        - title: A concise title for the information found
        - summary: The main content/summary of the information
        - vendor: The source or company (e.g., OpenAI, Google, Meta, etc.)
        - url: The main URL or source link
        - category: The category (e.g., AI, technology, news, research, etc.)
        - tags: Comma-separated relevant tags (e.g., "AI, machine learning, LLM")
        
        Always call save_results with structured information after your search.""",
        tools=[WebSearchTool(), save_results],
    )

result = Runner.run_sync(agent, "What is the latest news on MCP in 2025? ")
print(result.final_output)