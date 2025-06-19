import os
import google.generativeai as genai
from google.adk import Agent
from google.cloud import bigquery
from google.api_core.exceptions import GoogleAPIError

# --- Configuration ---
# Set your Google Cloud Project ID and BigQuery Dataset ID
GCP_PROJECT_ID = "hacker2025-team-199-dev" # e.g., "my-sales-analytics-2024"
BQ_DATASET_ID = "sales_analyst"
BQ_TABLE_ID = "artificial_sales" # Your main sales data table



# --- Define the BigQuery Tool ---

def execute_bigquery_query(sql_query: str) -> str:
    """
    Executes a BigQuery SQL query and returns the results.
    The query must be a valid BigQuery SELECT statement.
    Results are truncated to the first 50 rows for brevity if many rows are returned.

    Args:
        sql_query (str): The BigQuery SQL query to execute. MUST be a SELECT statement.
                         Always include the full table path, e.g., `your-gcp-project-id.sales_analyst_mvp.monthly_sales_data`.

    Returns:
        str: A string representation of the query results (first 50 rows), or an error message.
    """
    print(f"\n--- Tool Call: Executing BigQuery Query ---\n{sql_query}\n--- End Tool Call ---\n")
    # Initialize BigQuery Client
    bq_client = bigquery.Client(project=GCP_PROJECT_ID)

    try:
        # Basic validation to ensure it's a SELECT statement for safety
        if not sql_query.strip().upper().startswith("SELECT"):
            return "ERROR: Only SELECT queries are allowed for security reasons."

        query_job = bq_client.query(sql_query)
        rows = list(query_job.result(max_results=50)) # Limit results to 5 rows for LLM context

        if not rows:
            return "Query executed successfully, but no results were found."

        # Format results for the LLM
        # Get column names (headers)
        headers = [field.name for field in query_job.result().schema]
        result_str = ",".join(headers) + "\n"

        # Add rows
        for row in rows:
            values = [str(row[field.name]) for field in query_job.result().schema]
            result_str += ",".join(values) + "\n"

        return result_str

    except GoogleAPIError as e:
        return f"BigQuery API Error: {e}"
    except Exception as e:
        return f"An unexpected error occurred during query execution: {e}"

# --- Define the Agent ---

# This is where you provide the schema context to the LLM.
# Make it as precise and helpful as possible.
# Include descriptions for columns as that helps the LLM understand their meaning.
bigquery_schema_context = f"""
You have access to the following BigQuery table:
Table: `{GCP_PROJECT_ID}.{BQ_DATASET_ID}.{BQ_TABLE_ID}`

Columns:
  - `Date` (DATE): The first day of the month for sales data (e.g., '2023-01-01').
  - `ProductId` (STRING): Unique identifier for a product (e.g., 'P01', 'P02').
  - `ProductName` (STRING): Name of the product (e.g., 'Basic T-Shirt', 'Wireless Headphones').
  - `SalesRevenue` (NUMERIC): Total sales revenue for the month for this product.

Guidelines for generating SQL:
1. Always use the fully qualified table name: `{GCP_PROJECT_ID}.{BQ_DATASET_ID}.{BQ_TABLE_ID}`.
2. For date filtering, use `PARSE_DATE('%Y-%m-%d', 'YYYY-MM-DD')` or date functions like `DATE_TRUNC`, `CURRENT_DATE()`, `EXTRACT`.
3. If a question asks for "total" or "sum", use `SUM()`.
4. If a question asks for "average", use `AVG()`.
5. If a question asks for "count", use `COUNT()`.
6. If a question asks for "top" or "highest", use `ORDER BY` and `LIMIT`.
7. Always `GROUP BY` and `ORDER BY` appropriately when using aggregate functions.
8. Assume you are always asking about revenue, if not specified.
9. Consider the user's question, and respond concisely based on the query results.
10. If the query result is empty, clearly state that no data was found.
"""

# Create the Agent instance
root_agent = Agent(
    name="retail_agent",
    description="Answer questions about sales data using BigQuery",
    model='gemini-2.0-flash-001', # You can try 'gemini-1.5-pro' if you have access and need larger context
    tools=[execute_bigquery_query], # Register your BigQuery tool
    instruction=bigquery_schema_context,
    # enable_structured_response=True # Often helpful for more reliable tool calling
)