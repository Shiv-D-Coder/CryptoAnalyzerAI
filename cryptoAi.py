# !pip uninstall crewai -y
# !pip install crewai 'crewai[tools]'
# !pip install google-generativeai
# !pip install langchain-groq

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
    return response.json()[:20]  # Limit to first 20 entries

# Define the agents
class TestAgents():
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
            goal="""Summarize the Crypto data and compare it with Bitcoin and gives rating from one to 10 on if you should invest in this coin or not.""",
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
class TestTasks():
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
            output_file=f"crypto_data.json",
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

# Process each item individually for summary and max value tasks
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
print(results)

print(crew.usage_metrics)

# Create a structured report
report_lines = []
for idx, (item, result) in enumerate(zip(data, results['tasks_outputs'])):
    report_lines.append(f"** REPORT FOR COIN {idx + 1} **")
    report_lines.append(f"symbol: {item['symbol']}")
    report_lines.append(f"baseAsset: {item['baseAsset']}")
    report_lines.append(f"quoteAsset: {item['quoteAsset']}")
    report_lines.append(f"openPrice: {item['openPrice']}")
    report_lines.append(f"lowPrice: {item['lowPrice']}")
    report_lines.append(f"highPrice: {item['highPrice']}")
    report_lines.append(f"lastPrice: {item['lastPrice']}")
    report_lines.append(f"volume: {item['volume']}")
    report_lines.append(f"bidPrice: {item['bidPrice']}")
    report_lines.append(f"askPrice: {item['askPrice']}")
    report_lines.append(f"at: {item['at']}")

    # Extract and add the summary, comparison to Bitcoin, and ratings
    summary = result.exported_output if result.exported_output else "N/A"
    comparison_to_bitcoin = "Comparision to bitcoin: " + result.raw_output if result.raw_output else "N/A"
    ratings = "Ratings: " + (result.raw_output.split(':')[-1] if result.raw_output else "N/A")

    report_lines.append("\nSummary: " + summary)
    report_lines.append("Comparision to bitcoin: " + comparison_to_bitcoin)
    report_lines.append("Ratings: " + ratings)
    report_lines.append("\n")

# Save the report to a file
with open('report.txt', 'w') as f:
    f.write("\n".join(report_lines))
