# src/armstrong/crew.py
# This is the complete, final, and clean implementation of the "Smart Sequential" workflow.

import openai  

from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from typing import List
import os
from dotenv import load_dotenv
import litellm
from langchain_openai import AzureChatOpenAI
# ======================================================================================
# SECTION 1: IMPORTS
# This section imports all necessary Pydantic models and tools.
# ======================================================================================
# from .models import (
#     # The main state model that will be passed between tasks
#     FullClientData,
    
#     # The initial data model for the first task's output
#     InitialClientData,
    
#     # Intermediate models for multi-step "assembly line" tasks
#     TimelineCalculations,
#     RiskCalculations,
#     GoalCalculationOutput,
    
#     # Final data structure models for each analysis section
#     ClientProfile,
#     AssetLiabilityAnalysis,
#     FinancialGoal,
#     RetirementPlan,
#     EducationPlan,
#     DebtManagementPlan,
#     FinancialHealthAudit
# )
# from armstrong.tools.mcp_clients import (
#     client_profiler_tool,
#     asset_liability_analysis_mcp_tool,
#     goal_setting_mcp_tool,
#     financial_analysis_mcp_tool,
# )
# from armstrong.tools.custom_tool import (comprehensive_profile_calculator_tool,
#                                          client_data_merge_tool)




from .models import (
    FullClientData,
    InitialClientData,
    ClientProfileCalculations, 
    GoalCalculatorOutput,   
    AssetLiabilityAnalysis,    
    GoalCalculatorOutput,        
    FinancialGoal,  
    ClientProfile,
    AssetLiabilityAnalysis,
    FinancialGoal, 
    RetirementPlan,
    EducationPlan,
    DebtManagementPlan,
    FinancialHealthAudit,
    QuantifiedGoalsOutput,

)
from armstrong.tools.custom_tool import (
    comprehensive_goal_processing_tool,
    comprehensive_profile_calculator_tool,
    comprehensive_asset_liability_analysis_tool, 
    client_data_merge_tool,
    retirement_planning_tool_custom,
    json_snake_case_converter_tool
)
from armstrong.tools.mcp_clients import (
    asset_liability_analysis_mcp_tool, 
    goal_setting_mcp_tool,
    financial_analysis_mcp_tool,
    retirement_planning_mcp_tool
)

# ======================================================================================
# SECTION 2: SETUP
# ======================================================================================
# os.environ["OPEN_API_KEY"]=os.getenv("OPEN_API_KEY")
# load_dotenv()
# api_key = os.getenv("OPEN_API_KEY")
# Openai_llm = LLM(model="openai/gpt-4o", api_key=api_key)
# litellm.api_key=os.getenv("OPEN_API_KEY")


from dotenv import load_dotenv
import os
from crewai import LLM

load_dotenv()
os.environ["AZURE_API_KEY"]         = os.getenv("AZURE_API_KEY")
os.environ["AZURE_API_BASE"]        = os.getenv("AZURE_API_BASE")
os.environ["AZURE_API_VERSION"]     = os.getenv("AZURE_API_VERSION")
os.environ["AZURE_DEPLOYMENT_NAME"] = os.getenv("AZURE_DEPLOYMENT_NAME")

Openai_llm = LLM(
    model="azure/gpt-4o",
    api_key=os.getenv("AZURE_API_KEY"),
    api_base=os.getenv("AZURE_API_BASE"),
    api_version=os.getenv("AZURE_API_VERSION")
    #deployment_name=os.getenv("AZURE_DEPLOYMENT_NAME")
)

litellm.api_key = os.getenv("AZURE_API_KEY")

@CrewBase
class Armstrong():
    """Armstrong crew orchestrating a smart sequential financial planning process."""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    # ======================================================================================
    # SECTION 3: AGENT DEFINITIONS
    # Each agent is defined here with its specific role, goal, and tools.
    # ======================================================================================

    @agent
    def data_extractor(self) -> Agent:
        return Agent(config=self.agents_config['data_extractor'], 
                     verbose=True, 
                     llm=Openai_llm,
                     tools=[json_snake_case_converter_tool],
                     )

    @agent
    def ClientProfilerAgent(self) -> Agent:
        return Agent(
            config=self.agents_config['ClientProfilerAgent'],
            verbose=True,
            llm=Openai_llm,
            tools=[comprehensive_profile_calculator_tool,
                   client_data_merge_tool]
        )

    @agent
    def AssetLiabilityAnalyzerAgent(self) -> Agent:
        return Agent(config=self.agents_config['AssetLiabilityAnalyzerAgent'], 
                     verbose=True, 
                     llm=Openai_llm, 
                     tools=[comprehensive_asset_liability_analysis_tool,
                            client_data_merge_tool])

    @agent
    def goal_quantification_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['goal_quantification_agent'],
            tools=[
                comprehensive_goal_processing_tool,
                goal_setting_mcp_tool # If it needs to make individual calls for fuzzy "other" goals
            ],
            llm=Openai_llm,
            verbose=True
        )

    @agent
    def goal_strategy_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['goal_strategy_agent'],
            llm=Openai_llm,
            verbose=True
        )
    
    @agent
    def goal_integrate_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['goal_integrate_agent'],
            tools=[client_data_merge_tool],
            llm=Openai_llm,
            verbose=True
        )

    @agent
    def RetirementPlannerAgent(self) -> Agent:
        return Agent(config=self.agents_config['RetirementPlannerAgent'], 
                     verbose=True, 
                     llm=Openai_llm, 
                     tools=[retirement_planning_tool_custom, client_data_merge_tool])

    # @agent
    # def EducationPlannerAgent(self) -> Agent:
    #     return Agent(config=self.agents_config['EducationPlannerAgent'], verbose=True, llm=Openai_llm, tools=[financial_analysis_mcp_tool])

    # @agent
    # def DebtManagerAgent(self) -> Agent:
    #     return Agent(config=self.agents_config['DebtManagerAgent'], verbose=True, llm=Openai_llm, tools=[financial_analysis_mcp_tool])

    # @agent
    # def FinancialHealthAuditorAgent(self) -> Agent:
    #     return Agent(config=self.agents_config['FinancialHealthAuditorAgent'], verbose=True, llm=Openai_llm, tools=[financial_analysis_mcp_tool])

    @agent
    def ReportGeneratorAgent(self) -> Agent:
        return Agent(config=self.agents_config['ReportGeneratorAgent'], verbose=True, llm=Openai_llm)

    # ======================================================================================
    # SECTION 4: TASK DEFINITIONS
    # Each task is assigned an agent and has a Pydantic output contract to ensure
    # the reliable passing of state through the sequential process.
    # ======================================================================================

    @task
    def data_extraction_task(self) -> Task:
        return Task(
            config=self.tasks_config['data_extraction_task'],
            agent=self.data_extractor(),
            output_json=InitialClientData,
            output_file="outputs/data_extraction_task.json" 
        )

    # We are back to ONE profiling task.
    @task
    def client_profiling_task(self) -> Task:
        return Task(
            config=self.tasks_config['client_profiling_task'],
            agent=self.ClientProfilerAgent(),
            context=[self.data_extraction_task()],
            output_pydantic=FullClientData,
            output_file="outputs/client_profiling_task.json" 
        )
    
    @task
    def asset_liability_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['asset_liability_analysis_task'],
            agent=self.AssetLiabilityAnalyzerAgent(),
            context=[self.client_profiling_task()],
            output_json=FullClientData,
            output_file="outputs/asset_liability_analysis_task.json"
        )

    @task
    def goal_quantification_task(self) -> Task:
        return Task(
            config=self.tasks_config['goal_quantification_task'],
            agent=self.goal_quantification_agent(),
            context=[self.asset_liability_analysis_task()], # Needs FullClientData up to ALA
            output_file='outputs/goal_quantification_task.json'
        )

    @task
    def goal_strategy_task(self) -> Task:
        return Task(
            config=self.tasks_config['goal_strategy_task'],
            agent=self.goal_strategy_agent(),
            context=[
                self.asset_liability_analysis_task(), # Provides the base FullClientData (up to ALA)
                self.goal_quantification_task()       # Provides QuantifiedGoalsOutput
            ],
            output_file='outputs/goal_strategy_task.json'
        )
    
    @task
    def goal_integration_task(self) -> Task:
        return Task(
            config=self.tasks_config['goal_integration_task'],
            agent=self.goal_integrate_agent(),
            context=[
                self.asset_liability_analysis_task(), 
                self.goal_strategy_task()
            ],
            output_file='outputs/goal_integration_task.json',
            output_json=FullClientData
        )

    @task
    def RetirementPlannerTask(self) -> Task:
        return Task(
            config=self.tasks_config['RetirementPlannerTask'],
            agent=self.RetirementPlannerAgent(),
            context=[self.client_profiling_task(), self.goal_integration_task()],
            output_file='outputs/RetirementPlannerTask.json', 
            output_json=FullClientData
        )

    # @task
    # def education_planning_task(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['education_planning_task'],
    #         agent=self.EducationPlannerAgent(),
    #         context=[self.RetirementPlannerTask()],
    #         output_pydantic=FullClientData
    #     )

    # @task
    # def debt_management_task(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['debt_management_task'],
    #         agent=self.DebtManagerAgent(),
    #         context=[self.education_planning_task()],
    #         output_pydantic=FullClientData
    #     )

    # @task
    # def financial_health_audit_task(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['financial_health_audit_task'],
    #         agent=self.FinancialHealthAuditorAgent(),
    #         context=[self.debt_management_task()],
    #         output_pydantic=FullClientData
    #     )

    @task
    def report_generation_task(self) -> Task:
        return Task(
            config=self.tasks_config['report_generation_task'],
            agent=self.ReportGeneratorAgent(),
            context=[self.RetirementPlannerTask()],
            output_file='outputs/final_financial_plan_report.md' 
        )

    # ======================================================================================
    # SECTION 5: CREW DEFINITION
    # This defines the exact sequential order of the "Assembly Line".
    # ======================================================================================
    @crew
    def crew(self) -> Crew:
        """Defines the sequential assembly line for financial planning."""
        return Crew(
            agents=[
                self.data_extractor(),
                self.ClientProfilerAgent(),
                self.AssetLiabilityAnalyzerAgent(),
                self.goal_quantification_agent(),
                self.goal_strategy_agent(),
                self.goal_integrate_agent(),
                self.RetirementPlannerAgent(),
                # self.EducationPlannerAgent(),
                # self.DebtManagerAgent(),
                # self.FinancialHealthAuditorAgent(),
                self.ReportGeneratorAgent()
            ],
            tasks=[
                self.data_extraction_task(),
                self.client_profiling_task(), 
                self.asset_liability_analysis_task(),
                self.goal_quantification_task(),
                self.goal_strategy_task(),  
                self.goal_integration_task(),        
                self.RetirementPlannerTask(),
                # self.education_planning_task(),
                # self.debt_management_task(),
                # self.financial_health_audit_task(),
                self.report_generation_task()
            ],
            process=Process.sequential,
            memory=False,
            verbose=True
        )
    
