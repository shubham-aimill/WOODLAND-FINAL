import json
import re
from Text2SQL_V2.config import config
from Text2SQL_V2.utils.llm_factory import load_llm
import logging

def setup_logger():
    """
    Sets up a logger with a console handler.
    """
    # Create a logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)  # Set minimum log level

    # Prevent adding multiple handlers if setup_logger is called multiple times
    if not logger.handlers:
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)  # Handler log level

        # Create formatter for log messages
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(console_handler)

    return logger
logger = setup_logger()

# -----------------------------
# Load LLM
# -----------------------------
def get_llm(max_tokens: int):
    # Reload model with token limit for retries
    return load_llm(temp=0, max_tokens=max_tokens)

logger.info(f"🤖 LLM Provider: {config.LLM_PROVIDER}")

# -----------------------------
# LLM PROMPT
# -----------------------------
PROMPT_TEMPLATE = """
Role:
You are an expert business communication assistant.

Task:
You will be given a SQL query. Convert it into a clear and professional email alert.

Instructions:
1. Understand what the SQL query is doing (filters, metrics, time window).
2. Write:
   - A short subject line.
   - A concise, well-structured email body in HTML.
   - Use <b> for important phrases.
   - Use a clear header and short paragraphs.
   - Don't include any technical jargon.
   - Use a professional and positive tone.
   - Don't mention "forecasted date".
   - Don't repeat yourself.
   - Don't make any recommendations or suggestions.
   - Don't use word like "Manual".
   - Subject and body must have proper html tags.
3. Keep language business-friendly and action-oriented.
4. Do NOT mention SQL explicitly in the email body.
5. Your entire JSON response must be complete and under 500 tokens.

Output Format (strict):
Return ONLY a valid JSON object:

{{
  "subject": "<email subject>",
  "body": "<HTML formatted email body>"
}}

Rules:
- No markdown.
- Only valid HTML in body (e.g., <h3>, <p>, <b>, <br>).
- Do not wrap HTML in code blocks.
- No explanation.
- Output only JSON.

For Example:
{{
  "subject": "Order Successfully Created for Dubai Hypermarkets",
  "body": "<h3>Order Confirmation</h3><p>This is to confirm that your request has been <b>successfully processed</b>.</p><p>A new order for <b>SKU_101</b> has been created based on the total predicted demand across all Dubai hypermarkets.</p><p><b>Status:</b> Completed successfully.</p>"
}}


SQL Query:
{operation}

Row Count: {rows}
"""

# -----------------------------
# Robust JSON extractor
# -----------------------------
def extract_json(text: str) -> dict:
    text = text.strip()
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise ValueError("No valid JSON boundaries found")

    json_text = text[start:end + 1]
    return json.loads(json_text)

# -----------------------------
# Fallback
# -----------------------------
def fallback_summary(row_count: int | None) -> dict:
    return {
        "subject": "Operation Completed Successfully",
        "body": f"{row_count or 0} record(s) were successfully processed."
    }

# -----------------------------
# LLM Call (NO API)
# -----------------------------
def call_llm(prompt: str, llm) -> str:
    response = llm.invoke(prompt)
    return response.content

# -----------------------------
# Main Summary Generator
# -----------------------------
def generate_llm_summary(sql_query: str, row_count: int | None = None) -> dict:
    prompt = PROMPT_TEMPLATE.format(
        operation=sql_query,
        rows=row_count or 0
    )

    max_tokens_list = [800, 700, 600]

    for attempt, max_tokens in enumerate(max_tokens_list, start=1):
        try:
            logger.info(f"🚀 Calling LLM (attempt {attempt}, max_tokens={max_tokens})...")
            llm = get_llm(max_tokens)

            raw_text = call_llm(prompt, llm)

            logger.info("🧠 RAW LLM OUTPUT ↓↓↓")
            logger.info(raw_text)
            logger.info("🧠 RAW LLM OUTPUT ↑↑↑")

            parsed = extract_json(raw_text)

            return {
                "subject": parsed.get("subject", f"Operation Completed ({row_count or 0} rows)"),
                "body": parsed.get("body", f"{row_count or 0} record(s) were successfully processed.")
            }

        except Exception as e:
            logger.info(f"❌ LLM attempt {attempt} failed:", e)

    logger.info("⚠️ All LLM attempts failed. Using fallback.")
    return fallback_summary(row_count)