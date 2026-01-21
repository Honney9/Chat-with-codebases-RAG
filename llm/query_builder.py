from llm.prompt import SYSTEM_PROMPT

def build_llm_input(user_query: str, context: str, max_chars=4000):

    # Constructs the final prompt sent to the LLM.

    prompt= f"""
    {SYSTEM_PROMPT}

    Context:
    {context}

    Question:
    {user_query}

    Answer:
    """

    return prompt.strip()[:max_chars]