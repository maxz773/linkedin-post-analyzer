from llm_interface import AihubmixClient

def analyze_post_potential(client: AihubmixClient, post_text: str, model: str = "gpt-5-nano"):
    system_prompt = """
    You are a top-tier LinkedIn Growth Hacker and Copywriting Expert. Your mission is to evaluate the "Virality Potential" of a given LinkedIn post text.
    Please assess the post based on the following dimensions:
    Hook: Do the first two sentences grab attention and stop the scroll?
    Readability: Are the paragraphs clear? Does it make effective use of white space and lists?
    Value: Is the content useful to the reader (educational, inspirational, or emotionally resonant)?
    CTA (Call to Action): Is there a clear instruction guiding readers to comment or click?
    Strictly output in JSON format with the following two fields:
    "score": An integer from 1–10 (10 represents massive viral potential, 1 represents ignored bot-like copy).
    "reason": A brief explanation in English (approx. 50–80 characters) highlighting its strengths and fatal flaws (e.g., weak hook / missing CTA / sounds too much like a PR release).
    """
    messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": post_text}
    ]

    return client.chat_completion(model, messages)