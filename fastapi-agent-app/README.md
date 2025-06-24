# FastAPI Agent App

This project is a FastAPI application that provides a simple service for querying an agent with a question and returning the agent's response.

## Project Structure

```
fastapi-agent-app
├── app
│   ├── main.py          # Entry point of the FastAPI application
│   ├── agent_service.py # Logic for querying the agent
│   └── models.py       # Data models for request and response
├── requirements.txt     # Project dependencies
└── README.md            # Project documentation
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd fastapi-agent-app
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

To run the FastAPI application, execute the following command:

```
uvicorn app.main:app --reload
```

The application will be available at `http://127.0.0.1:8000`.

## API Endpoints

- **POST /query**
  - Description: Queries the agent with a question.
  - Request Body: A JSON object containing the question.
  - Response: A JSON object containing the agent's response.

## License

This project is licensed under the MIT License.