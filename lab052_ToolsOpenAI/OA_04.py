import os
import json
import wikipedia
from openai import OpenAI

# Initialize OpenAI client
BASE_URL = os.getenv("OPENAI_BASE_URL")
API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL if BASE_URL else "https://api.openai.com/v1"
)

def search_security_innovators(query: str) -> str:
    """Search Wikipedia for information about security innovators and cybersecurity pioneers."""
    try:
        # Search for relevant pages
        search_results = wikipedia.search(query, results=3)
        
        if not search_results:
            return json.dumps({
                "status": "no_results",
                "message": f"No Wikipedia pages found for '{query}'"
            })
        
        # Get summary of the first relevant result
        page_title = search_results[0]
        try:
            summary = wikipedia.summary(page_title, sentences=3)
            page = wikipedia.page(page_title)
            
            return json.dumps({
                "status": "success",
                "title": page_title,
                "summary": summary,
                "url": page.url,
                "related_pages": search_results[1:3] if len(search_results) > 1 else []
            })
            
        except wikipedia.exceptions.DisambiguationError as e:
            # If ambiguous, try the first option
            try:
                summary = wikipedia.summary(e.options[0], sentences=3)
                page = wikipedia.page(e.options[0])
                
                return json.dumps({
                    "status": "success",
                    "title": e.options[0],
                    "summary": summary,
                    "url": page.url,
                    "note": "Disambiguated result",
                    "other_options": e.options[1:4]
                })
            except:
                return json.dumps({
                    "status": "disambiguation_error",
                    "message": f"Multiple pages found for '{query}'",
                    "options": e.options[:5]
                })
                
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Wikipedia search failed: {str(e)}"
        })

# Tool schema for OpenAI
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_security_innovators",
            "description": "Search Wikipedia for information about cybersecurity pioneers, security researchers, or security innovators",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search term for security innovators (e.g., person name, security concept, or 'cybersecurity pioneers')"
                    }
                },
                "required": ["query"]
            }
        }
    }
]

def security_research_llm(user_question, model="gpt-4o"):
    """LLM function with Wikipedia search capability for security innovators."""
    messages = [
        {
            "role": "system",
            "content": "You are a cybersecurity historian. Help users learn about security innovators, pioneers, and researchers by searching Wikipedia. Provide informative summaries about their contributions to cybersecurity."
        },
        {
            "role": "user",
            "content": user_question
        }
    ]
    
    try:
        # Step 1: Get tool call from LLM
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        
        response_message = response.choices[0].message
        messages.append(response_message)
        
        tool_calls = response_message.tool_calls
        if not tool_calls:
            return response_message.content
        
        # Step 2: Execute Wikipedia search
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            if function_name == "search_security_innovators":
                search_result = search_security_innovators(function_args["query"])
                
                # Add tool result to conversation
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": search_result
                })
        
        # Step 3: Get final analysis from LLM
        final_response = client.chat.completions.create(
            model=model,
            messages=messages
        )
        
        return final_response.choices[0].message.content
        
    except Exception as e:
        return f"❌ Error during research: {str(e)}"

# Example usage
if __name__ == "__main__":
    print("🔍 Security Innovators Research Tool")
    print("=" * 50)
    
    # Search for security innovators
    research = security_research_llm(
        "Tell me about famous cybersecurity pioneers and innovators. "
        "Search for information about people who made significant contributions to computer security."
    )
    
    print(research)
    print("\n" + "=" * 50)
    print("💡 Research Tip: Explore the links to learn more about these security pioneers!")