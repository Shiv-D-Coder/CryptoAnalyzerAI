import os
import json
import requests
from crewai import Crew, Agent, Task, Process
from langchain_groq import ChatGroq
from google.colab import userdata

# Ensure the API keys are set in the environment variables
os.environ["GROQ_API_KEY"] = userdata.get('GROQ_API_KEY')
SERP_API_KEY = userdata.get('SERP_API_KEY')
if SERP_API_KEY is None:
    raise ValueError("SERP_API_KEY secret not found in Colab. Please add it in the secrets section.")
os.environ["SERP_API_KEY"] = SERP_API_KEY

# Initialize the Groq language model
GROQ_LLM = ChatGroq(model="llama3-70b-8192")

# Define the function to fetch data from the API
def fetch_data():
    response = requests.get("https://api.wazirx.com/sapi/v1/tickers/24hr")
    return response.json()[:5]  # Limit to first 5 entries for simplicity

# Define the agents
class TestAgents:
    def make_data_fecher(self):
        return Agent(
            role='Data Fecher Agent',
            goal="""Fetch all the data from the given API.""",
            backstory="""You are skilled at fetching data from APIs.""",
            llm=GROQ_LLM,
            verbose=True,
            allow_delegation=False,
            max_iter=5,
            memory=True,
        )

    def make_summary_agent(self):
        return Agent(
            role='Data Summary Agent',
            goal="""Summarize the Crypto data and compare it with Bitcoin and give a rating from one to ten on if you should invest in this coin or not.""",
            backstory="""You are very good at making decisions on crypto money and analyzing it.""",
            llm=GROQ_LLM,
            verbose=True,
            allow_delegation=False,
            max_iter=6,
            memory=True,
        )

    def make_max_agent(self):
        return Agent(
            role='Max Value Agent',
            goal="""Extract high price from crypto data.""",
            backstory="""You are very good at finding many statistical values.""",
            llm=GROQ_LLM,
            verbose=True,
            allow_delegation=False,
            max_iter=6,
            memory=True,
        )

# Define the tasks
class TestTasks:
    def data_feche(self):
        return Task(
            description="""Fetch data from the API.""",
            expected_output="""Data in the following format:
            {
                "symbol": "trxinr",
                "baseAsset": "trx",
                "quoteAsset": "inr",
                "openPrice": "9.8324",
                "lowPrice": "9.7003",
                "highPrice": "9.9861",
                "lastPrice": "9.72",
                "volume": "352842.0",
                "bidPrice": "9.72",
                "askPrice": "9.724",
                "at": 1716804798000
            }
            """,
            output_file="crypto_data.json",
            agent=data_fecher_agent
        )

    def summarize_data(self, data):
        return Task(
            description="""Summarize the Crypto data that has been fetched.""",
            expected_output="""A summary of the Crypto data in two to three lines.""",
            context=[{
                "description": "Context for summarizing data",
                "expected_output": "Expected summary output",
                "data": data
            }],
            agent=summary_agent
        )

    def extract_max_value(self, data):
        return Task(
            description="""Fetch the high price from the data that has been given to you.""",
            expected_output="""The highest price in the provided data.""",
            context=[{
                "description": "Context for extracting max value",
                "expected_output": "Expected max value output",
                "data": data
            }],
            agent=max_agent
        )

# Instantiate agents
agents = TestAgents()
data_fecher_agent = agents.make_data_fecher()
summary_agent = agents.make_summary_agent()
max_agent = agents.make_max_agent()

# Fetch data using the data fetcher agent
data = fetch_data()

# Save the fetched data to a JSON file
with open('crypto_data.json', 'w') as f:
    json.dump(data, f, indent=4)

# Process the fetched data and create tasks
tasks = TestTasks()
data_fecher_task = tasks.data_feche()

# Create summary and max value tasks for each item
task_list = []
for item in data:
    summary_task = tasks.summarize_data(item)
    max_value_task = tasks.extract_max_value(item)
    task_list.extend([summary_task, max_value_task])

# Instantiate your crew with a sequential process
crew = Crew(
    agents=[data_fecher_agent, summary_agent, max_agent],
    tasks=task_list,
    verbose=2,
    process=Process.sequential,
    full_output=True,
    share_crew=False,
    step_callback=lambda x: print(f"Step completed: {x}")
)

results = crew.kickoff()

print("Crew Work Results:")
# Access the results using the appropriate methods
print(results.raw)  # Access the raw output

# Inspect the structure of the raw output
tasks_outputs = results.raw.get('tasks_outputs', [])
print(f"Tasks Outputs: {tasks_outputs}")

# Format the results and write to report.txt
with open('report.txt', 'w') as report_file:
    for i, item in enumerate(data):
        report_file.write(json.dumps(item, indent=4))
        report_file.write("\nsummary:\n")

        # Always expect summary and max value outputs
        summary_output = tasks_outputs[i*2].get('exported_output', 'Summary not available')
        max_value_output = tasks_outputs[i*2 + 1].get('exported_output', 'Max value not available')

        report_file.write(f"{summary_output}\n")
        report_file.write(f"{max_value_output}\n")
        report_file.write("\n")

print("Report generated: report.txt")
