import os
from google.adk import Agent
from google.cloud import bigquery
from google.api_core.exceptions import GoogleAPIError
from google.genai import types
import datetime
import pickle # To store user credentials
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build # Calendar API client


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
    bq_client = bigquery.Client(project="hacker2025-team-199-dev")

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

# --- Define the Calendar Tools ---

def list_upcoming_events(max_events: int = 10) -> str:
    """
    Lists upcoming events from the authenticated Google Calendar.
    By default, lists up to 10 events within the next 7 days.

    Args:
        max_events (int, optional): The maximum number of events to return. Defaults to 10.

    Returns:
        str: A formatted string of upcoming events, or a message if none found.
    """
    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/calendar.events']
    TOKEN_FILE = 'token.pickle' # Stores user credentials
    CLIENT_SECRET_FILE = 'client_secret.json' # Downloaded from GCP Console
    def get_calendar_service():
        """Authenticates and returns a Google Calendar API service object."""
        creds = None
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(CLIENT_SECRET_FILE):
                    raise FileNotFoundError(
                        f"'{CLIENT_SECRET_FILE}' not found. Please download it from GCP Console -> APIs & Services -> Credentials."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)
        return build('calendar', 'v3', credentials=creds)

    # Initialize service once (will prompt for auth on first run)
    try:
        calendar_service = get_calendar_service()
        print("Google Calendar service initialized successfully.")
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        print("Please make sure you have 'client_secret.json' downloaded from GCP and in the script's directory.")
        calendar_service = None # So tools don't try to use it
    except Exception as e:
        print(f"Could not initialize Google Calendar service: {e}")
        print("Check your internet connection or OAuth setup.")
        calendar_service = None

    if not calendar_service:
        return "ERROR: Google Calendar service not available. Please check authentication setup."

    print(f"\n--- Tool Call: Listing Upcoming Events (Max {max_events}) ---\n--- End Tool Call ---\n")

    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    # Events for next 7 days
    seven_days_later = (datetime.datetime.utcnow() + datetime.timedelta(days=7)).isoformat() + 'Z'

    try:
        events_result = calendar_service.events().list(calendarId='primary', timeMin=now,
                                                    timeMax=seven_days_later,
                                                    maxResults=max_events, singleEvents=True,
                                                    orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            return "No upcoming events found in the next 7 days."

        events_str_list = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            events_str_list.append(f"- {event['summary']} (Start: {start}, End: {end})")
        return "Upcoming events:\n" + "\n".join(events_str_list)
    except Exception as e:
        return f"Error listing events: {e}. Please ensure service is authenticated."

def create_calendar_event(
    summary: str,
    start_time: str, # ISO 8601 format, e.g., "2024-03-25T10:00:00"
    end_time: str,   # ISO 8601 format, e.g., "2024-03-25T11:00:00"
    description: str = "",
    location: str = ""
) -> str:
    """
    Creates a new event on the authenticated Google Calendar.
    Requires event summary, start time, and end time.
    Times should be in ISO 8601 format (e.g., "YYYY-MM-DDTHH:MM:SS" for specific time, or "YYYY-MM-DD" for all-day).
    If no timezone is specified, it assumes UTC. Add 'Z' for UTC or '+HH:MM' for offset.
    For example: "2024-03-25T09:00:00-07:00" (for PST) or "2024-03-25" (for all-day event).

    Args:
        summary (str): The title of the event.
        start_time (str): The start date/time of the event (ISO 8601 string).
                          Examples: "2024-03-25T10:00:00", "2024-03-25"
        end_time (str): The end date/time of the event (ISO 8601 string).
                        Examples: "2024-03-25T11:00:00", "2024-03-26"
        description (str, optional): A detailed description of the event. Defaults to "".
        location (str, optional): The physical location of the event. Defaults to "".

    Returns:
        str: A confirmation message with the event link, or an error message.
    """
    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/calendar.events']
    TOKEN_FILE = 'token.pickle' # Stores user credentials
    CLIENT_SECRET_FILE = 'client_secret.json' # Downloaded from GCP Console
    def get_calendar_service():
        """Authenticates and returns a Google Calendar API service object."""
        creds = None
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(CLIENT_SECRET_FILE):
                    raise FileNotFoundError(
                        f"'{CLIENT_SECRET_FILE}' not found. Please download it from GCP Console -> APIs & Services -> Credentials."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)
        return build('calendar', 'v3', credentials=creds)

    # Initialize service once (will prompt for auth on first run)
    try:
        calendar_service = get_calendar_service()
        print("Google Calendar service initialized successfully.")
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        print("Please make sure you have 'client_secret.json' downloaded from GCP and in the script's directory.")
        calendar_service = None # So tools don't try to use it
    except Exception as e:
        print(f"Could not initialize Google Calendar service: {e}")
        print("Check your internet connection or OAuth setup.")
        calendar_service = None

    if not calendar_service:
        return "ERROR: Google Calendar service not available. Please check authentication setup."

    print(f"\n--- Tool Call: Creating Calendar Event ---\nSummary: {summary}, Start: {start_time}, End: {end_time}\n--- End Tool Call ---\n")

    event = {
        'summary': summary,
        'location': location,
        'description': description,
        'start': {
            'dateTime': start_time if 'T' in start_time else None,
            'date': start_time if 'T' not in start_time else None,
            'timeZone': 'UTC', # Or specify a default like 'America/Los_Angeles' or ask user
        },
        'end': {
            'dateTime': end_time if 'T' in end_time else None,
            'date': end_time if 'T' not in end_time else None,
            'timeZone': 'UTC',
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }

    try:
        event = calendar_service.events().insert(calendarId='primary', body=event).execute()
        return f"Event created: {event.get('htmlLink')}"
    except Exception as e:
        return f"Error creating event: {e}. Please ensure date/time format is correct (YYYY-MM-DDTHH:MM:SS or YYYY-MM-DD) and service is authenticated."




# --- Define the Agent ---

# This is where you provide the schema context to the LLM.
# Make it as precise and helpful as possible.
# Include descriptions for columns as that helps the LLM understand their meaning.
bigquery_schema_context = f"""
You have access to the following BigQuery table:
Table: `hacker2025-team-199-dev.sales_analyst.artificial_sales`

Columns:
  - `Date` (DATE): The first day of the month for sales data (e.g., '2023-01-01').
  - `ProductId` (STRING): Unique identifier for a product (e.g., 'P01', 'P02').
  - `ProductName` (STRING): Name of the product (e.g., 'Basic T-Shirt', 'Wireless Headphones').
  - `SalesRevenue` (NUMERIC): Total sales revenue for the month for this product.

Guidelines for generating SQL:
1. Always use the fully qualified table name: `hacker2025-team-199-dev.sales_analyst.artificial_sales`.
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
sales_agent = Agent(
    name="retail_agent",
    description="Answer questions about sales data using BigQuery. You have the access to data of following products: Basic T-Shirt, Camping Tent, Coffee Maker, Cookware Set, Denim Jeans, Novelty Mug, Running Shoes, Smartwatch, Weighted Blanket, Wireless Headphones.",
    model='gemini-2.0-flash-001', # You can try 'gemini-1.5-pro' if you have access and need larger context
    tools=[execute_bigquery_query], # Register your BigQuery tool
    instruction=bigquery_schema_context,
    # enable_structured_response=True # Often helpful for more reliable tool calling
)


# --- Define the Agent ---

# This is where you provide the schema context to the LLM.
# Make it as precise and helpful as possible.
# Include descriptions for columns as that helps the LLM understand their meaning.
bigquery_schema_context = f"""
You have access to the following BigQuery table:
Table: `hacker2025-team-199-dev.sales_and_promo.weekly_sales_data`

The table has many columns but for the analysis you should focus on the following ones:
  - `date` (DATE): The first day of the week for sales data (e.g., '2023-01-03').
  - `retailer_banner_geography` (STRING): Geogrphic identifier of retailer (e.g. 'NORTH EAST').
  - `promoted_group` (STRING): The name of a product (e.g. 'FACE CREAM').
  - `daily_weekly_value_sales` (FLOAT): Total sales revenue for the week of a given product.
  - `is_tpr` (INTEGER): Flag for Temporary Price Reduction promotion. 1 means that product was on TPR and 0 means it wasn't.
  - `is_feature` (INTEGER): Flag for promotion in magazine. 1 means that product was promoted in magazine and 0 means it wasn't.
  - `is_display` (INTEGER): Flag for promotion on display. 1 means that product was promoted on display and 0 means it wasn't.

Guidelines for generating SQL:
1. Always use the fully qualified table name: `hacker2025-team-199-dev.sales_and_promo.weekly_sales_data`.
2. For date filtering, use `PARSE_DATE('%Y-%m-%d', 'YYYY-MM-DD')` or date functions like `DATE_TRUNC`, `CURRENT_DATE()`, `EXTRACT`.
3. If a question asks for "total" or "sum", use `SUM()`.
4. If a question asks for "average", use `AVG()`.
5. If a question asks for "count", use `COUNT()`.
6. If a question asks for "top" or "highest", use `ORDER BY` and `LIMIT`.
7. Always `GROUP BY` and `ORDER BY` appropriately when using aggregate functions.
8. Assume you are always asking about revenue, if not specified.
9. Consider the user's question, and respond concisely based on the query results.
10. If the query result is empty, clearly state that no data was found.

You can also **Manage Google Calendar:** You can `create_calendar_event` and `list_upcoming_events`.
    -   When creating events, ensure you get all necessary details (summary, start time, end time).
    -   Tell the user the exact formats for dates and times (ISO 8601: "YYYY-MM-DDTHH:MM:SS" or "YYYY-MM-DD").
    -   Assume event times are in UTC unless specified.

When responding:
-   Be helpful and informative.
-   If you perform a task (like creating an event or listing details), confirm it to the user.
-   If you need more information, ask clarifying questions.
"""

# Create the Agent instance
promo_agent = Agent(
    name="promo_agent",
    description="Suggests promotion strategy based on sales data using BigQuery. You have the access to data of following products: FACE CREAM, MOISTURISER. You also have the access to the calendar.",
    model='gemini-2.0-flash-001', # You can try 'gemini-1.5-pro' if you have access and need larger context
    tools=[execute_bigquery_query, list_upcoming_events, create_calendar_event], # Register your BigQuery tool
    instruction=bigquery_schema_context,
    # enable_structured_response=True # Often helpful for more reliable tool calling
)


root_agent = Agent(
    name="steering",
    model='gemini-2.0-flash-001',
    description="Analyse sales data and provide promotion recommendations for different products.",
    instruction="""
        You have the access to two agents: sales_agent and promo_agent. Depending on which product the user asks, forward the task to proper agent.
        If the ask is about FACE CREAM, MOISTURISER, delegate the task to promo_agent.
        If the ask is about Basic T-Shirt, Camping Tent, Coffee Maker, Cookware Set, Denim Jeans, Novelty Mug, Running Shoes, Smartwatch, Weighted Blanket, Wireless Headphones delegate the task to sales_agent.
        Additionally, promo_agent has the access to calendar so any asks concerning calendar should be forwarded to promo_agent.
        Return only the final answer from the agent that contain the response to the user question.
        If the task requires planning, execute all the steps and only return the final answer.
        """,
    generate_content_config=types.GenerateContentConfig(
        temperature=0,
    ),
    sub_agents=[sales_agent, promo_agent]
)
