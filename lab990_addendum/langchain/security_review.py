from typing import List
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
import json
import sys
from pathlib import Path


# Define the Pydantic model for structured output
class SecurityAnalysis(BaseModel):
    """Security analysis results for generated code."""
    vulnerabilities: List[str] = Field(description="List of identified security vulnerabilities")
    mitigation_suggestions: List[str] = Field(description="Suggested fixes for each vulnerability")
    risk_level: str = Field(description="Overall risk assessment: Low, Medium, High, Critical")


# Initialize the output parser with the Pydantic model
parser = PydanticOutputParser(pydantic_object=SecurityAnalysis)

# Create the prompt template with format instructions from the parser
security_prompt = PromptTemplate(
    template=(
        """Analyze the following code for security vulnerabilities:\n"""
        "{code}\n"
        "Consider:\n"
        "SQL injection vulnerabilities\n"
        "Cross-site scripting (XSS) risks\n"
        "Insecure direct object references\n"
        "Authentication and authorization weaknesses\n"
        "Sensitive data exposure\n"
        "Missing input validation\n"
        "Command injection opportunities\n"
        "Insecure dependency usage\n"
        "{format_instructions}"
    ),
    input_variables=["code"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

# Initialize the language model (ensure OPENAI_API_KEY is set in env)
llm = ChatOpenAI(model="gpt-5", temperature=1)

# Compose the chain using LCEL
security_chain = security_prompt | llm | parser


def analyze_code(code: str) -> SecurityAnalysis:
    """Run the security analysis chain on provided source code."""
    return security_chain.invoke({"code": code})


def analyze_file(path: Path) -> SecurityAnalysis:
    """Read a file and analyze its contents."""
    with path.open("r", encoding="utf-8") as f:
        content = f.read()
    return analyze_code(content)


if __name__ == "__main__":
    # Default to sample.py in the same directory unless a path is supplied
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "sample.py"
    if not target.exists():
        print(f"❌ File not found: {target}")
        sys.exit(1)
    print(f"🔍 Analyzing file: {target}")
    result = analyze_file(target)
    print(json.dumps(result.model_dump(), indent=2))
