from crewai import Crew, Process
from textwrap import dedent
import json  # Import the JSON module to parse JSON strings
from langchain_core.agents import AgentFinish
import json
from typing import Union, List, Tuple, Dict
from langchain.schema import AgentFinish
from stock_analysis_agents import StockAnalysisAgents
from stock_analysis_tasks import StockAnalysisTasks
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
load_dotenv()


ClaudeHaiku = ChatAnthropic(
    model="claude-3-haiku-20240307"
)

ClaudeSonnet = ChatAnthropic(
    model="claude-3-sonnet-20240229"
)

ClaudeOpus = ChatAnthropic(
    model="claude-3-opus-20240229"
)
class FinancialCrew:


  def __init__(self, company):
    self.company = company

  def run(self):
    agents = StockAnalysisAgents()
    tasks = StockAnalysisTasks()

    research_analyst_agent = agents.research_analyst()
    financial_analyst_agent = agents.financial_analyst()
    investment_advisor_agent = agents.investment_advisor()

    research_task = tasks.research(research_analyst_agent, self.company)
    financial_task = tasks.financial_analysis(financial_analyst_agent)
    filings_task = tasks.filings_analysis(financial_analyst_agent)
    recommend_task = tasks.recommend(investment_advisor_agent)

    crew = Crew(
      agents=[
        research_analyst_agent,
        financial_analyst_agent,
        investment_advisor_agent
      ],
      tasks=[
        research_task,
        financial_task,
        filings_task,
        recommend_task
      ],
      verbose=True
      # process=Process.hierarchical,
      # full_output=True,
      # share_crew=False,
      # manager_llm=ClaudeHaiku, #ClaudeOpus。ClaudeSonnet
      # max_iter=15,
      # step_callback=lambda x: print_agent_output(x,"MasterCrew Agent")
    )

    result = crew.kickoff()
    return result
  

 


if __name__ == "__main__":
  print("## Welcome to Financial Analysis Crew")
  print('-------------------------------')
  company = input(
    dedent("""
      What is the company you want to analyze?
    """))
  
  financial_crew = FinancialCrew(company)
  result = financial_crew.run()
  print("\n\n########################")
  print("## Here is the Report")
  print("########################\n")
  print(result)


def print_agent_output(agent_output: Union[str, List[Tuple[Dict, str]], AgentFinish], agent_name: str = 'Generic call'):
  global call_number  # Declare call_number as a global variable
  call_number += 1
  agent_finishes  = []

  with open("crew_callback_logs.txt", "a") as log_file:
      # Try to parse the output if it is a JSON string
      if isinstance(agent_output, str):
          try:
              agent_output = json.loads(agent_output)  # Attempt to parse the JSON string
          except json.JSONDecodeError:
              pass  # If there's an error, leave agent_output as is

      # Check if the output is a list of tuples as in the first case
      if isinstance(agent_output, list) and all(isinstance(item, tuple) for item in agent_output):
          print(f"-{call_number}----Dict------------------------------------------", file=log_file)
          for action, description in agent_output:
              # Print attributes based on assumed structure
              print(f"Agent Name: {agent_name}", file=log_file)
              print(f"Tool used: {getattr(action, 'tool', 'Unknown')}", file=log_file)
              print(f"Tool input: {getattr(action, 'tool_input', 'Unknown')}", file=log_file)
              print(f"Action log: {getattr(action, 'log', 'Unknown')}", file=log_file)
              print(f"Description: {description}", file=log_file)
              print("--------------------------------------------------", file=log_file)

      # Check if the output is a dictionary as in the second case
      elif isinstance(agent_output, AgentFinish):
          print(f"-{call_number}----AgentFinish---------------------------------------", file=log_file)
          print(f"Agent Name: {agent_name}", file=log_file)
          agent_finishes.append(agent_output)
          # Extracting 'output' and 'log' from the nested 'return_values' if they exist
          output = agent_output.return_values
          # log = agent_output.get('log', 'No log available')
          print(f"AgentFinish Output: {output['output']}", file=log_file)
          # print(f"Log: {log}", file=log_file)
          # print(f"AgentFinish: {agent_output}", file=log_file)
          print("--------------------------------------------------", file=log_file)

      # Handle unexpected formats
      else:
          # If the format is unknown, print out the input directly
          print(f"-{call_number}-Unknown format of agent_output:", file=log_file)
          print(type(agent_output), file=log_file)
          print(agent_output, file=log_file)
