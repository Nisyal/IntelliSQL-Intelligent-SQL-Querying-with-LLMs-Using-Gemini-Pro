"""
Service to handle LLM communication via OpenRouter using the OpenAI SDK.
Implements a pipelined approach to split the work:
1. Llama 3.3 70B acts as the Query Planner.
2. Qwen 2.5 Coder acts as the SQL Generator based on the plan.
"""

from openai import AsyncOpenAI
import re

from config import settings
from services.schema_service import get_schema_string


# ── Configuration ──────────────────────────────────────────────

client = AsyncOpenAI(
    api_key=settings.LLM_API_KEY,
    base_url=settings.LLM_BASE_URL,
)

MODELS = {
    "coder": "qwen/qwen-2.5-coder-32b-instruct",
    "planner": "meta-llama/llama-3.3-70b-instruct",
}


def get_available_models() -> list[dict]:
    """Return pipeline stages."""
    return [
        {"key": "pipeline", "name": "Planner (Llama) + Coder (Qwen)"}
    ]


# ── Step 1: Query Planner ──────────────────────────────────────

async def generate_query_plan(question: str, conversation_history: list[dict] | None = None) -> str:
    """
    Use Llama 3.3 70B to generate a step-by-step logical plan for the SQL query.
    """
    schema_str = get_schema_string()
    
    system_prompt = f"""You are an expert Database Architect.
Your job is to analyze a user's natural language question and the database schema, and write a clear, step-by-step logical plan for how to construct the SQL query.

### Database Schema:
{schema_str}

### Instructions:
1. Identify exactly which tables and columns are needed.
2. Specify the exact filtering conditions (e.g., ILIKE vs =).
3. Specify any aggregations, grouping, or sorting.
4. DO NOT write the actual SQL query. Only write the step-by-step English instructions for the SQL developer.
5. Keep it concise and strictly focused on the database logic.
"""

    messages = [{"role": "system", "content": system_prompt}]
    
    if conversation_history:
        for msg in conversation_history[-3:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
            
    messages.append({"role": "user", "content": question})
    
    response = await client.chat.completions.create(
        model=MODELS["planner"],
        messages=messages,
        temperature=0.1,
        max_tokens=300,
    )
    
    return response.choices[0].message.content.strip()


# ── Step 2: SQL Generator ──────────────────────────────────────

async def generate_sql_from_plan(question: str, plan: str) -> str:
    """
    Use Qwen 2.5 Coder to write the final SQL query based on the plan.
    """
    schema_str = get_schema_string()
    
    system_prompt = f"""You are an expert SQL Developer.
Your task is to write a highly optimized PostgreSQL query based on a provided Query Plan.

### Database Schema:
{schema_str}

### Instructions:
1. ONLY return the raw SQL query.
2. DO NOT wrap the SQL in markdown formatting (no ```sql).
3. DO NOT include any explanations, preambles, or conversational text.
4. Ensure the query strictly follows the provided Query Plan.
"""

    user_prompt = f"""### Original Question:
{question}

### Query Plan:
{plan}

Write the SQL query now:"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    response = await client.chat.completions.create(
        model=MODELS["coder"],
        messages=messages,
        temperature=0.0,
        max_tokens=500,
    )
    
    raw_sql = response.choices[0].message.content.strip()
    
    # Clean up markdown code blocks if the LLM ignored instructions
    if raw_sql.startswith("```"):
        raw_sql = re.sub(r"^```(?:sql|postgresql)?\s*", "", raw_sql, flags=re.IGNORECASE)
        raw_sql = re.sub(r"\s*```$", "", raw_sql)
        
    return raw_sql.strip()


# ── Pipeline Execution ─────────────────────────────────────────

async def execute_pipeline(question: str, conversation_history: list[dict] | None = None) -> dict:
    """
    Executes the full Pipeline:
    1. Llama generates the plan.
    2. Qwen generates the SQL based on the plan.
    """
    try:
        plan = await generate_query_plan(question, conversation_history)
        sql = await generate_sql_from_plan(question, plan)
        
        return {
            "plan": plan,
            "sql": sql,
            "planner_model": "Llama 3.3 70B",
            "coder_model": "Qwen 2.5 Coder 32B"
        }
    except Exception as e:
        raise Exception(f"Pipeline error: {str(e)}")
