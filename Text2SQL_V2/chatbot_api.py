# chatbot_api.py
import json, os
from Text2SQL_V2.core.db_builder import build_database, execute_sql
from Text2SQL_V2.core.schema_loader import SchemaLoader
from Text2SQL_V2.agents.text2sql_agent import Text2SQLAgent
from Text2SQL_V2.agents.summarizer_agent import SummarizerAgent
from Text2SQL_V2.utils.intent import wants_chart
from Text2SQL_V2.utils.persist import persist_order_log
import os
from Text2SQL_V2.mailer import send_success_email
from Text2SQL_V2.summary_generator import generate_llm_summary
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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# go UP from Text2SQL_V2 → WoodLand_Forecasting 2
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

DATASETS_DIR = os.path.join(PROJECT_ROOT, "datasets")

schema = [
    {
        "table_name": "sku_daily_forecast",
        "path": os.path.join(DATASETS_DIR, "sku_daily_forecast.csv"),
    },
    {
        "table_name": "order_log",
        "path": os.path.join(DATASETS_DIR, "order_log.csv"),
    },
    {
        "table_name": "sku_daily_sales",
        "path": os.path.join(DATASETS_DIR, "sku_daily_sales.csv"),
    },
     {
        "table_name": "raw_material_log",
        "path": os.path.join(DATASETS_DIR, "raw_material_log.csv")
    },
    {
        "table_name": "raw_material_inventory",
        "path": os.path.join(DATASETS_DIR, "raw_material_inventory.csv"),
    },
]



# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# DATASETS_DIR = os.path.join(BASE_DIR, "datasets")

# schema = [
#     {
#         "table_name": "sku_daily_forecast",
#         "path": os.path.join(DATASETS_DIR, "sku_daily_forecast.csv")
#     },
#     {
#         "table_name": "order_log",
#         "path": os.path.join(DATASETS_DIR, "order_log.csv")
#     },
#     {
#         "table_name": "sku_daily_sales",
#         "path": os.path.join(DATASETS_DIR, "sku_daily_sales.csv")
#     },
#     {
#         "table_name": "raw_material_inventory",
#         "path": os.path.join(DATASETS_DIR, "raw_material_inventory.csv")
#     },
# ]

schema_loader = SchemaLoader(schema)
loaded_schema = schema_loader.load()

db_path = os.path.join(BASE_DIR, "chatbot.db")
build_database(schema, db_path)

with open(os.path.join(BASE_DIR, "schema_metadata.json")) as f:
    schema_metadata = json.load(f)

t2s = Text2SQLAgent(db_path, loaded_schema, schema_metadata)
summarizer = SummarizerAgent()


def run_chatbot_query(question: str):
    sql = t2s.run(question)
    result = execute_sql(db_path, sql)

    # --------------------
    # INSERT handling
    # --------------------
    if isinstance(result, int):
        rows_affected = result

        # Detect target table
        table = (
            "raw_material_log"
            if "raw_material_log" in sql.lower()
            else "order_log"
        )

        # --------------------
        # Generate LLM email summary
        # --------------------
        email_content = None
        try:
            email_content = generate_llm_summary(
                sql_query=sql,
                row_count=rows_affected
            )

            logger.info("✅ Email summary generated successfully")
        except Exception as e:
            logger.warning(f"Email summary generation failed: {str(e)}")

        # --------------------
        # Persist correct CSV
        # --------------------
        try:
            persist_order_log(db_path, table)
            logger.info(f"✅ {table} persisted successfully")
        except Exception as e:
            logger.warning(f"Failed to persist {table}: {str(e)}")

        # --------------------
        # Send success email
        # --------------------
        try:
            if email_content:
                send_success_email(
                    subject=email_content["subject"],
                    body=email_content["body"]
                )
                logger.info("✅ Success email sent")
        except Exception as e:
            logger.warning(f"Failed to send email: {str(e)}")

        # --------------------
        # API response
        # --------------------
        return {
            "sql": sql,
            "summary": f"✅ Successfully inserted {rows_affected} record(s) into {table}.",
            "rows_affected": rows_affected,
            "email_subject": email_content["subject"] if email_content else None,
            "email_body": email_content["body"] if email_content else None,
            "data": [],
            "viz": None,
            "mime": None
        }

    # --------------------
    # SELECT handling
    # --------------------
    summary = summarizer.summarize(question, result)
    data = result.to_dict(orient="records")

    if wants_chart(question) and not result.empty:
        viz, mime = summarizer.generate_viz(question, result)
    else:
        viz, mime = None, None

    return {
        "sql": sql,
        "data": data,
        "summary": summary,
        "viz": viz,
        "mime": mime
    }
