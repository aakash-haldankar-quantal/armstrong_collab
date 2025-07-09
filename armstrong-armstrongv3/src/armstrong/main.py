#!/usr/bin/env python
import sys
import warnings
from datetime import datetime
from armstrong.crew import Armstrong
import fitz
import litellm
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")
import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from dotenv import load_dotenv
from timeit import default_timer as timer
load_dotenv()
# import openai
# from armstrong.token_meter import report_usage   
# OPEN_API_KEY=os.getenv("OPEN_API_KEY")
# os.environ["OPEN_API_KEY"]=os.getenv("OPEN_API_KEY")
# litellm.api_key=os.getenv("OPEN_API_KEY")



import os
from dotenv import load_dotenv
from crewai import LLM

load_dotenv()


input_sheet = """

### Summary of 'Input Sheet'

#### Personal Information
- **Name:** Hari Das
- **Date of Birth:** 1994-11-17
- **Year of Birth:** 1994
- **Retirement Age:** 45
- **Year of Birth - Spouse:** 1993
- **Current Year:** 2023

# #### Family Information
# - **first Child - Ahira Year of Birth:** 2019
# - **second Child - Hira Year of Birth:** 2020

#### Expenses
- **Household Expenses (Monthly):** 110,000.00

#### Assets
- **Provident Fund (PF):**
  - Present Values: 628,729.00
  - Monthly Contribution: 25,800.00
- **Public Provident Fund (PPF):**
  - Present Values: 451,600.00
  - Monthly Contribution: 3,600.00
- **Fixed Deposit (FD):**
  - Present Values: 300,000.00
- **Direct Equity:**
  - Present Values: 26,936.00
- **Mutual Funds:**
  - Present Values: 525,794.00
- **Cash or Cash at Bank:** 277,800.00
- **Gold ETF:** 2,500.00
- **Crypto:** 50,000.00
- **Other Investments (Ornamental Gold):** 250,000.00

#### Liabilities
- **Car Loan:**
  - Outstanding Amount: 213,000.00
  - Interest Rate: 0.12
  - EMI Amount: 17,800.00
  - Tenure: 12 months, ending in 2024
- **Personal Loan:**
  - Outstanding Amount: 467,150.00
  - Interest Rate: 0.10
  - EMI Amount: 24,500.00
  - Tenure: 19 months, ending in 2025

  ### Financial Goals

#### Assets
- **Emergency Funds**
  - Time: 1 year
  - Amount Required (Today): 600,000
  - Amount Available (Today): 600,000

#### Future Plans
- **Coast Retirement**
  - Time: 10 years
  - Amount Required (Today): 38,000,000
  # #### Future Plans
# - **First Child - Kahira:**
#   - Expected Current Cost for Undergraduate (UG): 4,000,000
#   - Expected Current Cost for Postgraduate (PG): 5,000,000

- **Sibling Wedding**
  - Time: 5 years
  - Amount Required (Today): 1,500,000

- **Higher Education**
  - Time: 3 years
  - Amount Required (Today): 10,000,000

- **Home Loan Down Payment**
  - Time: 10 years
  - Amount Required (Today): 5,000,000

- **Vacations**
  - Time: 1 year
  - Amount Required (Today): 500,000

- **Car**
  - Time: 4 years
  - Amount Required (Today): 4,500,000
  - Amount Available (Today): 0

- **Electronic Gadget / Clothes**
  - Time: 1 year
  - Amount Required (Today): 200,000
  - Amount Available (Today): 0

- **Car 2**
  - Time: 10 years
  - Amount Required (Today): 10,000,000
  - Amount Available (Today): 0

- **Car 3**
  - Time: 12 years
  - Amount Required (Today): 50,000,000
  - Amount Available (Today): 0


"""

def extract_pdf_text(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    return full_text

# Usage
pdf_path="C:/Users/Aakash/Projects/Armstrong_version3/armstrong-armstrongv3/armstrong-armstrongv3/General_Logic_FrameworkU.pdf"
Logic_Framework = extract_pdf_text(pdf_path)

def run():
    """
    Run the crew.
    """
    start_time=timer()
    inputs = {
        'input_sheet': input_sheet,
        'framework_logic_content': Logic_Framework
    }
    
    armstrong_crew_instance = Armstrong().crew()  # Get the crew instance

    try:
        print("\n--- STARTING CREW EXECUTION ---\n")
        crew_result = armstrong_crew_instance.kickoff(inputs=inputs)

        end_time=timer()

        print("\n--- CREW EXECUTION FINISHED ---\n")
        print(f"TOTAL TOKENS USAGE: {crew_result.token_usage}\n TOTAL TIME TAKEN: {end_time-start_time}")

        # --- DEBUGGING: Inspecting Task Outputs ---
        if crew_result and getattr(crew_result, 'tasks_output', None):
            print("\n\n======= DETAILED TASK OUTPUTS (from main.py) =======")
            for i, task_output_obj in enumerate(crew_result.tasks_output):
                task = armstrong_crew_instance.tasks[i]
                task_name  = task.description[:50] + "..."
                agent_name = task.agent.role if task.agent else "Unknown Agent"

                print(f"\n----- Task {i+1}: {task_name} -----")
                print(f"Agent: {agent_name}\n")

                # 1) Raw
                print("  --- Raw Output ---")
                print(task_output_obj.raw)

                # 2) Structured JSON
                print("\n  --- JSON‐Structured Output (if available) ---")
                if getattr(task_output_obj, 'output_json', None):
                    raw_json = task_output_obj.output_json
                    print(raw_json)
                    try:
                        parsed = json.loads(raw_json)
                        print(json.dumps(parsed, indent=2))
                    except Exception as e:
                        print(f"    (Could not parse JSON: {e})")

                elif getattr(task_output_obj, 'output_pydantic', None):
                    print(task_output_obj.output_pydantic.json())

                else:
                    print("    (no structured output; falling back to raw above)")

                # 3) Any error
                if getattr(task_output_obj, 'error', None):
                    print("\n  --- Task Error ---")
                    print(task_output_obj.error)

                print("----- End of Task Output -----")
            print("\n====================================================\n")

        else:
            print("No task outputs to display (crew_result.tasks_output is empty or missing).")

        # --- Print final result ---
        if crew_result:
            print("\n\n=== FINAL CREW RESULT ===\n")
            if getattr(crew_result, 'output_json', None):
                print(crew_result.output_json)
            elif getattr(crew_result, 'output_pydantic', None):
                print(crew_result.output_pydantic.json())
            elif getattr(crew_result, 'raw', None):
                print(crew_result.raw)
            else:
                print(crew_result)
            print("\nReport should have been saved to output/ directory if specified in the last task.")
        else:
            print("Crew execution did not produce a result object.")

    except Exception as e:
        import traceback
        print(f"\n\n!!! AN EXCEPTION OCCURRED DURING CREW KICKOFF in main.py !!!")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {e}")
        print("Traceback:")
        traceback.print_exc()

    # finally:
    #     # ------------------------------------------------------------------
    #     # 4️⃣  PRINT TOKEN USAGE SUMMARY WHENEVER THE SCRIPT EXITS
    #     # ------------------------------------------------------------------
    #     print("\n========= TOKEN USAGE SUMMARY =========")
    #     # report_usage() returns something like {"total_prompt_tokens": 1234, "total_completion_tokens": 4321}
    #     print(json.dumps(report_usage(), indent=2))

if __name__ == "__main__":
    run()