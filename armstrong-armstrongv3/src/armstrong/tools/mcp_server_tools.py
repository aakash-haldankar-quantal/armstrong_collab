# File: src/armstrong/tools/mcp_server_tools.py
# (This is the script that SERVER_SCRIPT_PATH in FinancialAnalysisMCPTool points to)
from typing import List, Dict, Union, Optional, Any
from mcp.server.fastmcp import FastMCP # Using FastMCP for simplicity
from datetime import datetime, date
import sys # For logging to stderr if needed
import datetime
from typing import Union
import json
from datetime import datetime
# --- Initialize FastMCP Server ---
# The name "FinancialOperationsServer" is for MCP identification, not directly used by your agent's operation_name.
mcp_server = FastMCP(name="FinancialOperationsServer", version="1.0.0")

def log_to_stderr(message): # Optional: for debugging the server script itself
    print(f"MCP_SERVER_SCRIPT_LOG: {message}", file=sys.stderr, flush=True)

# --- Helper for age calculation (internal to this server script) ---
def _calculate_age_from_dob_and_current(dob_str: str, current_date_str: str) -> int:
    log_to_stderr(f"Calculating age. DOB: {dob_str}, Current: {current_date_str}")
    try:
        dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
        current_d = datetime.strptime(current_date_str, "%Y-%m-%d").date()
        age = current_d.year - dob.year - ((current_d.month, current_d.day) < (dob.month, dob.day))
        log_to_stderr(f"Calculated age: {age}")
        return age
    except ValueError as e:
        log_to_stderr(f"Age calculation ValueError: {e}")
        raise ValueError(f"Invalid date format. DOB ('{dob_str}') and current_date ('{current_date_str}') must be YYYY-MM-DD.")
    except Exception as e:
        log_to_stderr(f"Generic age calculation error: {e}")
        raise Exception(f"Error in age calculation: {e}")
    
# --- Helper for parsing values (you might need this more broadly) ---
def _parse_value_flexible(value: Any) -> Optional[Union[int, float, str]]:
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, str):
        cleaned_value = value.replace(',', '').strip()
        if not cleaned_value or "not specified" in cleaned_value.lower() or "n/a" in cleaned_value.lower():
            return None
        try:
            return int(cleaned_value)
        except ValueError:
            try:
                return float(cleaned_value)
            except ValueError:
                return cleaned_value # Return as string if not number
    return None






######################################################### Agent 3 : Client Profiler Agent #########################################################
@mcp_server.tool()
def calculate_current_age(date_of_birth: str, current_date: str) -> str:
    """
    Calculates the current age of an individual.
    Args:
        date_of_birth (str): The date of birth in "YYYY-MM-DD" format.
        current_date (str): The date to calculate the age as of, also in "YYYY-MM-DD" format.
    Returns:
        str: A JSON string containing the calculated age or an error.
             Example success: '{"calculated_age": 37, "date_of_birth_used": "1985-07-25", "current_date_used": "2023-04-05"}'
             Example error: '{"error": "Invalid date format for date_of_birth: YYYY-MM-DD required."}'
    """
    log_to_stderr(f"MCP: calculate_current_age called with dob: {date_of_birth}, current: {current_date}")
    try:
        dob_date = datetime.datetime.strptime(date_of_birth, "%Y-%m-%d").date()
        current_date_date = datetime.datetime.strptime(current_date, "%Y-%m-%d").date()
        age = current_date_date.year - dob_date.year - ((current_date_date.month, current_date_date.day) < (dob_date.month, dob_date.day))
        return json.dumps({
            "calculated_age": age,
            "date_of_birth_used": date_of_birth,
            "current_date_used": current_date
        })
    except ValueError as e:
        log_to_stderr(f"MCP: calculate_current_age error: {e}")
        return json.dumps({"error": f"Invalid date format. Details: {e}. Ensure date_of_birth ('{date_of_birth}') and current_date ('{current_date}') are YYYY-MM-DD."})
    except Exception as e:
        log_to_stderr(f"MCP: calculate_current_age generic error: {e}")
        return json.dumps({"error": f"An unexpected error occurred during age calculation: {e}"})

@mcp_server.tool()
def calculate_duration_in_years(start_value: Union[int, str], end_value: Union[int, str], duration_description: str) -> str:
    """
    Calculates the duration in years between a start value (age/year) and an end value (age/year).
    Args:
        start_value (Union[int, str]): The starting year or age.
        end_value (Union[int, str]): The ending year or age.
        duration_description (str): A description of what this duration represents.
    Returns:
        str: A JSON string with the calculated duration.
             Example: '{"duration_years": 18, "start_value_used": 37, "end_value_used": 55, "description": "years to retirement"}'
    """
    log_to_stderr(f"MCP: calculate_duration_in_years called with start: {start_value}, end: {end_value}, desc: {duration_description}")
    try:
        parsed_start_value = int(_parse_value_flexible(start_value)) # Ensure conversion to int after parsing
        parsed_end_value = int(_parse_value_flexible(end_value))     # Ensure conversion to int
        
        if parsed_start_value is None or parsed_end_value is None:
             raise ValueError("Start or end value could not be parsed to a number.")

        years = parsed_end_value - parsed_start_value
        return json.dumps({
            "duration_years": years,
            "start_value_used": parsed_start_value,
            "end_value_used": parsed_end_value,
            "description": duration_description
        })
    except (ValueError, TypeError) as e:
        log_to_stderr(f"MCP: calculate_duration_in_years error: {e}")
        return json.dumps({"error": f"Invalid input for duration calculation. Start ('{start_value}') and end ('{end_value}') must be numbers. Details: {e}", "description": duration_description})
    except Exception as e:
        log_to_stderr(f"MCP: calculate_duration_in_years generic error: {e}")
        return json.dumps({"error": f"An unexpected error occurred: {e}", "description": duration_description})


@mcp_server.tool()
def classify_investment_horizon(years_to_goal: Union[int, float, str]) -> str:
    """
    Classifies investment horizon based on years to a goal.
    Logic: >5 years = Long-Term; 3-5 years = Medium-Term; <3 years = Short-Term.
    Args:
        years_to_goal (Union[int, float, str]): The number of years until the financial goal.
    Returns:
        str: A JSON string with the horizon classification.
             Example: '{"horizon_classification": "Long-Term", "years_to_goal_used": 18}'
    """
    log_to_stderr(f"MCP: classify_investment_horizon called with years: {years_to_goal}")
    try:
        parsed_years = float(_parse_value_flexible(years_to_goal)) # Ensure conversion to float after parsing
        if parsed_years is None:
            raise ValueError("Years to goal could not be parsed to a number.")

        if parsed_years > 5:
            horizon = "Long-Term"
        elif 3 <= parsed_years <= 5:
            horizon = "Medium-Term"
        elif parsed_years >= 0: # Allow 0 years for short-term
            horizon = "Short-Term"
        else: # Negative years are invalid
            return json.dumps({"error": f"Invalid input: years_to_goal ('{parsed_years}') cannot be negative."})
            
        return json.dumps({
            "horizon_classification": horizon,
            "years_to_goal_used": parsed_years
        })
    except (ValueError, TypeError) as e:
        log_to_stderr(f"MCP: classify_investment_horizon error: {e}")
        return json.dumps({"error": f"Invalid input for horizon classification. Years_to_goal ('{years_to_goal}') must be a number. Details: {e}"})
    except Exception as e:
        log_to_stderr(f"MCP: classify_investment_horizon generic error: {e}")
        return json.dumps({"error": f"An unexpected error occurred: {e}"})


@mcp_server.tool()
def determine_equity_exposure(asset_list: List[Dict[str, Any]]) -> str:
    """
    Determines if there is equity exposure in a list of asset dictionaries.
    Checks 'asset_name', 'type', 'category', 'name' keys for equity-related keywords.
    Args:
        asset_list (List[Dict[str, Any]]): List of asset dictionaries, e.g., 
                                           [{'asset_name': 'Infosys Shares', 'value': 50000}, ...].
                                           The MCP tool will check the string values of common keys for keywords.
    Returns:
        str: JSON string: '{"has_equity_exposure": true/false, "reason": "details..."}'
    """
    log_to_stderr(f"MCP: determine_equity_exposure called with asset_list: {str(asset_list)[:200]}...") # Log snippet
    equity_keywords = {"equity", "stock", "stocks", "shares", "equity mf", "equitymf", "equity mutual fund"}
    # Keys within each asset dictionary to check for keywords.
    # The asset_list from your extractor now seems to have `asset_name` which contains the full description.
    keys_to_check_in_asset_dict = ['asset_name', 'type', 'category', 'name', 'description'] 
    
    found_equity_details = []

    if not isinstance(asset_list, list):
        return json.dumps({"has_equity_exposure": False, "reason": "Invalid input: asset_list must be a list.", "error": True})

    for asset in asset_list:
        if not isinstance(asset, dict):
            continue # Skip non-dict items in the list

        for key_to_search in keys_to_check_in_asset_dict:
            asset_description_value = asset.get(key_to_search)
            if isinstance(asset_description_value, str):
                value_lower = asset_description_value.lower()
                if any(keyword in value_lower for keyword in equity_keywords):
                    # Use `asset.get('asset_name')` if available for better context in reason
                    asset_identifier = asset.get('asset_name', str(asset)) 
                    found_equity_details.append(f"Keyword found in '{asset_identifier}' (key: '{key_to_search}')")

    if found_equity_details:
        return json.dumps({
            "has_equity_exposure": True,
            "reason": f"Equity exposure found. Details: {'; '.join(found_equity_details)}."
        })
    else:
        return json.dumps({
            "has_equity_exposure": False,
            "reason": "No direct equity, equity mutual funds, or company stocks identified in the asset list."
        })

@mcp_server.tool()
def assess_client_risk_appetite(years_to_retirement: Union[int, float, str], has_equity_exposure: Union[bool, str]) -> str:
    """
    Assesses client's risk appetite based on years to retirement and equity exposure status.
    Logic: YTR < 5: (Equity=Yes -> Medium, Equity=No -> Low). YTR >= 5: (Equity=Yes -> Medium to High, Equity=No -> Medium).
    Args:
        years_to_retirement (Union[int, float, str]): The number of years until retirement.
        has_equity_exposure (Union[bool, str]): True/False or "Yes"/"No" (case-insensitive) indicating equity exposure.
    Returns:
        str: JSON string: '{"risk_appetite": "Low/Medium/Medium to High", "reasoning_inputs": {...}}'
    """
    log_to_stderr(f"MCP: assess_client_risk_appetite called with ytr: {years_to_retirement}, equity: {has_equity_exposure}")
    try:
        parsed_ytr = float(_parse_value_flexible(years_to_retirement))
        if parsed_ytr is None:
             raise ValueError("Years to retirement could not be parsed to a number.")

        if isinstance(has_equity_exposure, str):
            equity_bool = has_equity_exposure.strip().lower() == "yes"
        elif isinstance(has_equity_exposure, bool):
            equity_bool = has_equity_exposure
        else:
            return json.dumps({"error": f"Invalid equity_exposure_status type: {type(has_equity_exposure)}. Expected bool or 'Yes'/'No' string."})

        risk_appetite = ""
        if parsed_ytr < 5:
            risk_appetite = "Medium" if equity_bool else "Low"
        else: # ytr >= 5
            risk_appetite = "Medium to High" if equity_bool else "Medium"
            
        return json.dumps({
            "risk_appetite": risk_appetite,
            "reasoning_inputs": {
                "years_to_retirement_used": parsed_ytr,
                "has_equity_exposure_used": equity_bool
            }
        })
    except (ValueError, TypeError) as e:
        log_to_stderr(f"MCP: assess_client_risk_appetite error: {e}")
        return json.dumps({"error": f"Invalid input for risk appetite assessment. years_to_retirement ('{years_to_retirement}') must be a number. has_equity_exposure ('{has_equity_exposure}') must be boolean or Yes/No. Details: {e}"})
    except Exception as e:
        log_to_stderr(f"MCP: assess_client_risk_appetite generic error: {e}")
        return json.dumps({"error": f"An unexpected error occurred: {e}"})

######################################################### Agent 3 : Client Profiler Agent Done #########################################################



######################################################### Agent 4 : AssetLiabilityAnalyzerAgent #########################################################

@mcp_server.tool()
def calculate_total_value(items_list: List[Dict[str, Any]], 
                          value_key: str = "present_value",  # Default to snake_case
                          item_type_description: str = "items") -> str:
    """
    Calculates sum of values from a list of item dictionaries.
    Args:
        items_list: List of dictionaries.
        value_key: Key in each dict holding the numerical value (snake_case).
        item_type_description: Describes what is being summed.
    Returns:
        JSON string: {"total_value": float, "item_type": str, "details": List[str]} or {"error": "message"}
    """
    log_to_stderr(f"MCP: calculate_total_value for '{item_type_description}', value_key='{value_key}', items='{str(items_list)[:100]}...'")
    total_value: float = 0.0
    calculation_details: List[str] = []
    
    if not isinstance(items_list, list):
        return json.dumps({"error": "items_list must be a list."})

    for i, item_dict in enumerate(items_list):
        if not isinstance(item_dict, dict):
            calculation_details.append(f"Item {i+1} is not a dict, skipped.")
            continue

        item_value_unparsed = item_dict.get(value_key)
        # Simplified item name for this generic function
        item_name_keys = ['asset_name', 'loan_type', 'name', 'type']
        item_name = next((str(item_dict[k]) for k in item_name_keys if k in item_dict), f"Item_{i+1}")

        parsed_value = _parse_value_flexible(item_value_unparsed)

        if parsed_value is not None and isinstance(parsed_value, (int, float)):
            total_value += float(parsed_value)
            calculation_details.append(f"{item_name}: {parsed_value}")
        else:
            calculation_details.append(f"{item_name}: Value for key '{value_key}' was '{item_value_unparsed}' (parsed as {parsed_value}), treated as 0 for sum.")
            
    return json.dumps({
        "total_value": total_value,
        "item_type_processed": item_type_description,
        "value_key_used": value_key,
        "calculation_details": calculation_details
    })


@mcp_server.tool()
def calculate_net_worth(total_assets: Union[int, float, str], 
                        total_liabilities: Union[int, float, str]) -> str:
    """
    Calculates net worth (Total Assets - Total Liabilities).
    Args:
        total_assets: Numerical total value of assets.
        total_liabilities: Numerical total value of liabilities.
    Returns:
        JSON string: {"net_worth": float, "total_assets_used": float, "total_liabilities_used": float} or {"error": "message"}
    """
    log_to_stderr(f"MCP: calculate_net_worth with assets: {total_assets}, liabilities: {total_liabilities}")
    try:
        assets_val_parsed = _parse_value_flexible(total_assets)
        liabilities_val_parsed = _parse_value_flexible(total_liabilities)

        if not isinstance(assets_val_parsed, (int, float)) or not isinstance(liabilities_val_parsed, (int, float)):
            missing = []
            if not isinstance(assets_val_parsed, (int, float)): missing.append("total_assets")
            if not isinstance(liabilities_val_parsed, (int, float)): missing.append("total_liabilities")
            return json.dumps({"error": f"Inputs must be numbers. Issues with: {', '.join(missing)}."})

        assets_val = float(assets_val_parsed)
        liabilities_val = float(liabilities_val_parsed)
        
        net_worth = assets_val - liabilities_val
        return json.dumps({
            "net_worth": net_worth,
            "total_assets_used": assets_val,
            "total_liabilities_used": liabilities_val
        })
    except Exception as e:
        log_to_stderr(f"MCP: calculate_net_worth error: {e}")
        return json.dumps({"error": f"Error calculating net worth: {e}"})


@mcp_server.tool()
def classify_assets_and_get_bucket_summary(asset_list: List[Dict[str, Any]], 
                                           classification_rules: Dict[str, List[str]], 
                                           value_key: str = "present_value") -> str: # value_key in snake_case
    """
    Classifies assets into buckets and calculates total value per bucket.
    Args:
        asset_list: List of asset dictionaries (e.g., [{'asset_name': 'Savings', 'present_value': 10000}]).
        classification_rules: Dict of bucket_name: [keywords] (all snake_case).
        value_key: Key in asset dicts for value (snake_case).
    Returns:
        JSON string: {"bucket_totals": {"bucket_a": float, ...}, "classified_assets_details": {...}, "unclassified_assets_count": int} or {"error": "message"}
    """
    log_to_stderr(f"MCP: classify_assets_and_get_bucket_summary, value_key='{value_key}', rules='{classification_rules}', assets='{str(asset_list)[:100]}...'")
    
    classified_assets_details: Dict[str, List[Dict[str, Any]]] = {bucket: [] for bucket in classification_rules}
    unclassified_items: List[Dict[str, Any]] = []
    bucket_totals: Dict[str, float] = {bucket: 0.0 for bucket in classification_rules}
    
    # Keys within each asset dictionary to check for keywords (should be snake_case)
    keys_to_search_in_asset_dict = ['asset_name', 'type', 'category', 'description'] # Example keys

    if not isinstance(asset_list, list):
        return json.dumps({"error": "asset_list must be a list."})
    if not isinstance(classification_rules, dict):
        return json.dumps({"error": "classification_rules must be a dictionary."})

    for asset_item in asset_list:
        if not isinstance(asset_item, dict):
            unclassified_items.append(asset_item) # Or log a warning
            continue
            
        found_bucket = None
        asset_value_unparsed = asset_item.get(value_key)
        parsed_asset_value = _parse_value_flexible(asset_value_unparsed)
        
        # Use 0 if value is not a number or missing, for sum, but log it or store separately
        asset_value_for_sum = float(parsed_asset_value) if isinstance(parsed_asset_value, (int, float)) else 0.0


        for bucket_name, keywords in classification_rules.items():
            # Ensure keywords are lowercase for case-insensitive matching
            normalized_keywords = [kw.lower() for kw in keywords]
            for key_in_asset in keys_to_search_in_asset_dict:
                asset_description = str(asset_item.get(key_in_asset, "")).lower()
                if any(keyword in asset_description for keyword in normalized_keywords):
                    asset_to_store = asset_item.copy()
                    # Add parsed value for clarity if needed, but primarily use for summation
                    asset_to_store['_parsed_value_for_classification'] = parsed_asset_value 
                    classified_assets_details[bucket_name].append(asset_to_store)
                    bucket_totals[bucket_name] += asset_value_for_sum
                    found_bucket = bucket_name
                    break 
            if found_bucket:
                break
        
        if not found_bucket:
            unclassified_items.append(asset_item)


    return json.dumps({
        "bucket_totals": bucket_totals, # Keys from classification_rules
        "classified_assets_details": classified_assets_details, # For detailed breakdown if needed
        "unclassified_assets_count": len(unclassified_items),
        "summary_message": f"Assets classified. Totals - {', '.join([f'{k}: {v:.2f}' for k,v in bucket_totals.items() if v > 0])}."
    })


@mcp_server.tool()
def calculate_category_proportions(category_values_dict: Dict[str, Union[int, float, str]], 
                                   total_value: Union[int, float, str]) -> str:
    """
    Calculates percentage proportion of each category relative to a total.
    Args:
        category_values_dict: Dict of category_name (snake_case): numerical_total.
        total_value: Overall total value.
    Returns:
        JSON string: {"proportions_percentage": {"category_a": float, ...}, "total_value_used": float} or {"error": "message"}
    """
    log_to_stderr(f"MCP: calculate_category_proportions, categories: {category_values_dict}, total: {total_value}")
    proportions_percentage: Dict[str, float] = {}
    
    try:
        parsed_total_value_num = _parse_value_flexible(total_value)
        if not isinstance(parsed_total_value_num, (int, float)):
            return json.dumps({"error": "total_value must be a number."})
        parsed_total_value = float(parsed_total_value_num)

        if not isinstance(category_values_dict, dict):
            return json.dumps({"error": "category_values_dict must be a dictionary."})

        for category_snake_case, value_unparsed in category_values_dict.items():
            parsed_value_num = _parse_value_flexible(value_unparsed)
            if not isinstance(parsed_value_num, (int, float)):
                proportions_percentage[category_snake_case] = 0.0 # Or handle error
                log_to_stderr(f"Warning: Value for category '{category_snake_case}' is not numeric: {value_unparsed}")
                continue
            
            parsed_value = float(parsed_value_num)
            proportion = round((parsed_value / parsed_total_value) * 100, 2) if parsed_total_value != 0 else 0.0
            proportions_percentage[category_snake_case] = proportion
            
        return json.dumps({
            "proportions_percentage": proportions_percentage,
            "total_value_used": parsed_total_value
        })
    except Exception as e:
        log_to_stderr(f"MCP: calculate_category_proportions error: {e}")
        return json.dumps({"error": f"Error calculating category proportions: {e}"})


@mcp_server.tool()
def calculate_individual_asset_proportions(asset_list: List[Dict[str, Any]], 
                                           total_asset_value: Union[int, float, str], 
                                           asset_name_key: str = "asset_name", # snake_case
                                           value_key: str = "present_value") -> str:  # snake_case
    """
    Calculates percentage proportion of each individual original asset.
    Args:
        asset_list: List of original asset dictionaries (e.g., [{"asset_name": "Equity", "present_value": "100"}]).
        total_asset_value: Total value of all assets.
        asset_name_key: Key in asset dicts for asset name/category (snake_case).
        value_key: Key in asset dicts for asset value (snake_case).
    Returns:
        JSON string: {"individual_proportions": [{"asset_category": str, "value": float, "proportion_percentage": float}, ...], "total_asset_value_used": float} or {"error": message}
    """
    log_to_stderr(f"MCP: calculate_individual_asset_proportions for {len(asset_list)} assets, total: {total_asset_value}, name_key='{asset_name_key}', val_key='{value_key}'")
    individual_proportions_list: List[Dict[str, Any]] = []
    
    try:
        parsed_total_asset_value_num = _parse_value_flexible(total_asset_value)
        if not isinstance(parsed_total_asset_value_num, (int, float)):
            return json.dumps({"error": "total_asset_value must be a number."})
        parsed_total_asset_value_float = float(parsed_total_asset_value_num)

        if not isinstance(asset_list, list):
            return json.dumps({"error": "asset_list must be a list."})

        for item_dict in asset_list:
            if not isinstance(item_dict, dict):
                # Log or skip malformed item
                continue

            asset_name = str(item_dict.get(asset_name_key, "Unknown Asset"))
            item_value_unparsed = item_dict.get(value_key)
            proportion = 0.0

            parsed_item_value_num = _parse_value_flexible(item_value_unparsed)
            
            item_value_for_calc = 0.0
            if isinstance(parsed_item_value_num, (int, float)):
                item_value_for_calc = float(parsed_item_value_num)
                if parsed_total_asset_value_float != 0:
                    proportion = round((item_value_for_calc / parsed_total_asset_value_float) * 100, 2)
            
            individual_proportions_list.append({
                "asset_category": asset_name, # snake_case key
                "value": item_value_for_calc, # snake_case key
                "proportion_percentage": proportion # snake_case key
            })
            
        return json.dumps({
            "individual_proportions": individual_proportions_list,
            "total_asset_value_used": parsed_total_asset_value_float
        })
    except Exception as e:
        log_to_stderr(f"MCP: calculate_individual_asset_proportions error: {e}")
        return json.dumps({"error": f"Error calculating individual asset proportions: {e}"})

######################################################### Agent 4 : AssetLiabilityAnalyzerAgent Done #########################################################




######################################################### Agent 5 : GoalSetterAgent  #########################################################
# @mcp_server.tool()
# def project_future_cost(current_cost: Union[int, float, str], inflation_rate_pa: Union[float, str], number_of_years: Union[int, str]) -> str:
#     """
#     Projects the future cost of a goal, adjusting for a given annual inflation rate over a number of years.
#     Formula: Future Cost = Current Cost * (1 + Inflation Rate) ^ Number of Years.

#     Args:
#         current_cost (Union[int, float, str]): The estimated current cost of the goal.
#                                                Can be a number or a string convertible to a float (e.g., "4,000,000").
#         inflation_rate_pa (Union[float, str]): The assumed annual inflation rate as a decimal (e.g., 0.06 for 6%, or "0.06").
#         number_of_years (Union[int, str]): The number of years until the goal, over which inflation will compound.
#                                            Can be an integer or a string convertible to an integer.

#     Returns:
#         str: A string containing the projected future cost and an explanation of the calculation.
#              Example: "Projected future cost for current cost 4000000.0 at 6.0% inflation over 13 years: 8532345.12"
#              Returns an error string if inputs are invalid or cannot be parsed.
#     """
#     log_to_stderr(f"MCP Tool: project_future_cost called with CurrentCost: {current_cost}, InflationRate: {inflation_rate_pa}, Years: {number_of_years}")
#     try:
#         parsed_current_cost = _parse_value_strict(current_cost) # Assuming _parse_value_strict handles comma strings
#         parsed_inflation_rate = float(inflation_rate_pa) # e.g., 0.06
#         parsed_number_of_years = int(number_of_years)

#         if parsed_inflation_rate < 0 or parsed_inflation_rate > 1: # Basic sanity check for decimal rate
#             log_to_stderr(f"MCP Tool: project_future_cost warning: Inflation rate {parsed_inflation_rate} seems unusual. Ensure it's a decimal (e.g., 0.06 for 6%).")
        
#         future_cost = parsed_current_cost * ((1 + parsed_inflation_rate) ** parsed_number_of_years)
        
#         result_str = (f"Projected future cost for current cost {parsed_current_cost:.2f} "
#                       f"at {parsed_inflation_rate*100:.1f}% annual inflation over {parsed_number_of_years} years: {future_cost:.2f}")
#         log_to_stderr(f"MCP Tool: project_future_cost result: {result_str}")
#         return result_str
#     except ValueError as e:
#         error_msg = (f"Error in project_future_cost: Invalid input. "
#                      f"Current_cost ('{current_cost}'), inflation_rate_pa ('{inflation_rate_pa}'), "
#                      f"and number_of_years ('{number_of_years}') must be valid numbers. Details: {e}")
#         log_to_stderr(f"MCP Tool: project_future_cost error: {error_msg}")
#         return error_msg
#     except Exception as e:
#         error_msg = f"Unexpected error in project_future_cost: {type(e).__name__} - {str(e)}"
#         log_to_stderr(f"MCP Tool: project_future_cost error: {error_msg}")
#         return error_msg




@mcp_server.tool()
def project_future_cost(current_cost: Union[int, float, str], 
                        inflation_rate_pa: Union[float, str], 
                        number_of_years: Union[int, str]) -> str:
    """
    Projects the future cost of a goal.
    Formula: Future Cost = Current Cost * (1 + Inflation Rate)^Number of Years.
    Args:
        current_cost: Estimated current cost.
        inflation_rate_pa: Assumed annual inflation rate (decimal, e.g., 0.06 for 6%).
        number_of_years: Number of years for inflation compounding.
    Returns:
        JSON string: {"projected_future_cost": float, "current_cost_used": float, "inflation_rate_pa_used": float, "number_of_years_used": int, "formatted_string": "Projected future cost..."} or {"error": "message"}
    """
    log_to_stderr(f"MCP: project_future_cost with cost: {current_cost}, rate: {inflation_rate_pa}, years: {number_of_years}")
    try:
        parsed_current_cost_num = _parse_value_flexible(current_cost)
        parsed_inflation_rate_num = _parse_value_flexible(inflation_rate_pa) # Should be float
        parsed_number_of_years_num = _parse_value_flexible(number_of_years) # Should be int

        if not isinstance(parsed_current_cost_num, (int, float)):
            raise ValueError(f"current_cost ('{current_cost}') must be a number.")
        if not isinstance(parsed_inflation_rate_num, (int, float)): # Allow int if it's like "6" for 6% but then normalize
            raise ValueError(f"inflation_rate_pa ('{inflation_rate_pa}') must be a number (decimal e.g. 0.06).")
        if not isinstance(parsed_number_of_years_num, (int, float)): # Allow float if years have decimals, but usually int
            raise ValueError(f"number_of_years ('{number_of_years}') must be a number.")

        parsed_current_cost = float(parsed_current_cost_num)
        parsed_inflation_rate = float(parsed_inflation_rate_num) # e.g., 0.06
        parsed_number_of_years = int(parsed_number_of_years_num)


        if not (0 <= parsed_inflation_rate <= 1): # decimal format check
             log_to_stderr(f"MCP: project_future_cost warning: Inflation rate {parsed_inflation_rate} seems unusual. Ensure it's a decimal (e.g., 0.06 for 6%). Treating as decimal.")
        if parsed_number_of_years < 0:
            return json.dumps({"error": f"number_of_years ('{parsed_number_of_years}') cannot be negative."})

        future_cost_val = parsed_current_cost * ((1 + parsed_inflation_rate) ** parsed_number_of_years)
        
        formatted_str = (f"Projected future cost for current cost {parsed_current_cost:.2f} "
                         f"at {parsed_inflation_rate*100:.1f}% annual inflation over {parsed_number_of_years} years: {future_cost_val:.2f}")
        
        return json.dumps({
            "projected_future_cost": round(future_cost_val, 2),
            "current_cost_used": parsed_current_cost,
            "inflation_rate_pa_used": parsed_inflation_rate,
            "number_of_years_used": parsed_number_of_years,
            "formatted_string": formatted_str 
        })
    except ValueError as e:
        log_to_stderr(f"MCP: project_future_cost ValueError: {e}")
        return json.dumps({"error": f"Invalid input. Details: {str(e)}"})
    except Exception as e:
        error_msg = f"Unexpected error in project_future_cost: {type(e).__name__} - {str(e)}"
        log_to_stderr(f"MCP: project_future_cost Exception: {error_msg}")
        return json.dumps({"error": error_msg})

######################################################### Agent 5 : GoalSetterAgent Done  #########################################################


####################################################### Retirement Planning Tools ###########################################################################
@mcp_server.tool()
def extract_client_info(data) -> dict:
    """
    Extract and summarize all key fields from the client data for retirement planning.
    """
    if isinstance(data, str):
        try:
           data = json.loads(data)
        except Exception as e:
           return json.dumps({"error": f"Input could not be parsed as JSON: {str(e)}"})
    if not isinstance(data, dict):
        return json.dumps({"error": "Input must be a dictionary or JSON string representing a dict."})

    try:
        if not isinstance(data, dict):
            return json.dumps({"error": "Input 'data' must be a dictionary."})

        personal = data.get('personal_information', {})
        misc = data.get('miscellaneous', {})
        profile = data.get('client_profile', {})
        expenses = data.get("expenses", {})

        summary = {
            "name": personal.get("name"),
            "date_of_birth": personal.get("date_of_birth"),
            "current_year": int(misc.get("current_year")) if misc.get("current_year") is not None else None,
            "retirement_age": int(misc.get("retirement_age")) if misc.get("retirement_age") is not None else 55,
            "current_age": int(profile.get("current_client_age")) if profile.get("current_client_age") is not None else None,
            "years_to_retirement": int(profile.get("years_to_retirement")) if profile.get("years_to_retirement") is not None else None,
            "monthly_expense_now": float(expenses.get("household_expenses_monthly")) if expenses.get("household_expenses_monthly") is not None else None,
            "assets": data.get("assets", []),
            "liabilities": data.get("liabilities", {}),
            "risk_appetite": profile.get("risk_appetite"),
            "equity_exposure": profile.get("equity_exposure_status"),
            "future_plans": data.get("future_plans", {})
        }
        return json.dumps(summary)
    except Exception as e:
        return json.dumps({"error": f"extract_client_info failed: {str(e)}"})

@mcp_server.tool()
def calculate_retirement_timeline(data) -> dict:
    """
    Extracts DOB, retirement_age, current_year from the profile and computes retirement timeline info.
    """
    if isinstance(data, str):
        try:
           data = json.loads(data)
        except Exception as e:
           return json.dumps({"error": f"Input could not be parsed as JSON: {str(e)}"})
    if not isinstance(data, dict):
        return json.dumps({"error": "Input must be a dictionary or JSON string representing a dict."})

    try:
        misc = data.get('miscellaneous', {})
        personal = data.get('personal_information', {})
        profile = data.get('client_profile', {})

        dob = personal.get('date_of_birth')
        retirement_age = int(misc.get('retirement_age')) if misc.get('retirement_age') is not None else 55
        current_year = int(misc.get('current_year'))
        life_expectancy = int(misc.get('life_expectancy', 85))  # allow optional override in future

        if not dob or not isinstance(dob, str) or len(dob) < 4:
            return json.dumps({"error": "Missing or invalid date_of_birth"})

        birth_year = int(dob[:4])
        current_age = current_year - birth_year
        years_to_retirement = retirement_age - current_age
        years_in_retirement = life_expectancy - retirement_age

        return json.dumps({
            "current_age": current_age,
            "years_to_retirement": years_to_retirement,
            "years_in_retirement": years_in_retirement
        })
    except Exception as e:
        return json.dumps({"error": f"calculate_retirement_timeline failed: {str(e)}"})


@mcp_server.tool()
def project_expenses(data) -> float:
    """
    Extracts current_expense and years_to_retirement, applies inflation to project retirement monthly expense.
    """
    
    if isinstance(data, str):
        try:
           data = json.loads(data)
        except Exception as e:
           return json.dumps({"error": f"Input could not be parsed as JSON: {str(e)}"})
    if not isinstance(data, dict):
        return json.dumps({"error": "Input must be a dictionary or JSON string representing a dict."})

    try:
        d = dict(data) if isinstance(data, dict) else json.loads(data)
        current_expense = float(d.get("monthly_expense_now", 0))
        years_to_retirement = int(d.get("years_to_retirement", 0))
        inflation = float(d.get("inflation", 0.07))  # default or allow override

        if current_expense < 0 or years_to_retirement < 0:
            d["error"] = "Invalid argument values for project_expenses."
            return json.dumps(d)

        future_expense = current_expense * ((1 + inflation) ** years_to_retirement)
        return json.dumps({"future_expense": future_expense})
    except Exception as e:
        return json.dumps({"error": f"project_expenses failed: {str(e)}"})


@mcp_server.tool()
def estimate_corpus_flat(data) -> float:
    """
    Extracts future_expense (projected) and years_in_retirement and computes flat corpus requirement.
    """

    if isinstance(data, str):
        try:
           data = json.loads(data)
        except Exception as e:
           return json.dumps({"error": f"Input could not be parsed as JSON: {str(e)}"})
    if not isinstance(data, dict):
        return json.dumps({"error": "Input must be a dictionary or JSON string representing a dict."})


    try:
        # Assume previous step outputs are merged back in, or re-calc if not
        profile = data.get("client_profile", {})
        expenses = data.get("expenses", {})
        misc = data.get("miscellaneous", {})
        timeline = data.get("retirement_timeline", {})

        # Use the already projected future_expense if available
        future_expense = float(data.get("future_expense") or expenses.get("household_expenses_monthly", 0))
        years_in_retirement = int(timeline.get("years_in_retirement", 30))
        inflation = 0.07
        post_ret_return = 0.07

        annual_expense = future_expense * 12
        real_return = ((1 + post_ret_return) / (1 + inflation)) - 1
        if real_return == 0:
            corpus = annual_expense * years_in_retirement
        else:
            corpus = annual_expense * (1 - (1 + real_return) ** -years_in_retirement) / real_return
        return json.dumps({"corpus_flat": corpus})
    except Exception as e:
        return json.dumps({"error": f"estimate_corpus_flat failed: {str(e)}"})


@mcp_server.tool()
def estimate_corpus_segmented(data) -> float:
    """
    Extracts future_expense and years_in_retirement; computes segmented corpus requirement.
    """
    if isinstance(data, str):
        try:
           data = json.loads(data)
        except Exception as e:
           return json.dumps({"error": f"Input could not be parsed as JSON: {str(e)}"})
    if not isinstance(data, dict):
        return json.dumps({"error": "Input must be a dictionary or JSON string representing a dict."})

    try:
        d = dict(data) if isinstance(data, dict) else json.loads(data)
        future_expense = float(d.get("future_expense", 0))
        years_in_retirement = int(d.get("years_in_retirement", 30))
        inflation = float(d.get("inflation", 0.07))
        post_ret_return = float(d.get("post_ret_return", 0.07))

        # Defensive: Ensure years_in_retirement >= 0
        years_in_retirement = max(years_in_retirement, 0)

        # Split years into three segments, last segment gets remainder
        seg1 = years_in_retirement // 3
        seg2 = years_in_retirement // 3
        seg3 = years_in_retirement - seg1 - seg2

        segment_1_years = seg1
        segment_2_years = seg2
        segment_3_years = seg3

        annual_exp_base = future_expense * 12
        segments = [
            (annual_exp_base * 1.10, segment_1_years),
            (annual_exp_base, segment_2_years),
            (annual_exp_base * 1.20, segment_3_years)
        ]

        real_return = ((1 + post_ret_return) / (1 + inflation)) - 1
        corpus = 0.0
        start_year = 0

        for amount, n_years in segments:
            if n_years <= 0:
                continue
            if real_return == 0:
                # Avoid division by zero: Use simple multiplication
                pv = amount * n_years
            else:
                pv = amount * (1 - (1 + real_return) ** -n_years) / real_return
            pv_discounted = pv / ((1 + real_return) ** start_year) if real_return != 0 else pv
            corpus += pv_discounted
            start_year += n_years

        return json.dumps({"corpus_segmented": corpus})
    except Exception as e:
        return json.dumps({"error": f"estimate_corpus_segmented failed: {str(e)}"})


@mcp_server.tool()
def aggregate_assets_liabilities(data) -> dict:
    """
    Extracts assets and liabilities from the input and aggregates net corpus.
    """
    
    if isinstance(data, str):
        try:
           data = json.loads(data)
        except Exception as e:
           return json.dumps({"error": f"Input could not be parsed as JSON: {str(e)}"})
    if not isinstance(data, dict):
        return json.dumps({"error": "Input must be a dictionary or JSON string representing a dict."})

    try:
        d = dict(data) if isinstance(data, dict) else json.loads(data)
        assets = d.get("assets", [])
        liabilities = d.get("liabilities", {})

        eligible_types = {
            "provident_fund", "public_provident_fund", "mutual_funds",
            "fixed_deposit", "direct_equity", "cash_or_cash_at_bank", "cash_at_bank"
        }
        eligible_assets = [
            float(a['present_value'])
            for a in assets
            if isinstance(a, dict) and a.get('type') in eligible_types
        ]
        total_assets = sum(eligible_assets)
        loans = liabilities.get('loans', [])
        total_loans = sum(float(l.get('outstanding_amount', 0)) for l in loans if isinstance(l, dict))
        net_assets = total_assets - total_loans

        return json.dumps({
            "eligible_assets_total": total_assets,
            "net_assets": net_assets
        })
    except Exception as e:
        return json.dumps({"error": f"aggregate_assets_liabilities failed: {str(e)}"})


@mcp_server.tool()
def feasibility_analysis(data) -> dict:
    """
    Extracts required_corpus and corpus_available from the input and computes feasibility.
    """
    
    if isinstance(data, str):
        try:
           data = json.loads(data)
        except Exception as e:
           return json.dumps({"error": f"Input could not be parsed as JSON: {str(e)}"})
    if not isinstance(data, dict):
        return json.dumps({"error": "Input must be a dictionary or JSON string representing a dict."})

    try:
        d = dict(data) if isinstance(data, dict) else json.loads(data)
        required_corpus = float(d.get("corpus_flat"))
        corpus_available = float(d.get("net_assets"))

        gap = required_corpus - corpus_available
        surplus = corpus_available - required_corpus
        feasible = corpus_available >= required_corpus

        return json.dumps({
            "feasible": feasible,
            "gap": gap if gap > 0 else 0,
            "surplus": surplus if surplus > 0 else 0
        })
    except Exception as e:
        return json.dumps({"error": f"feasibility_analysis failed: {str(e)}"})


@mcp_server.tool()
def gap_management(data) -> dict:
    """
    Extracts current_expense, other_goals, savings, and gap from input, suggests strategies to bridge the gap.
    """
    
    if isinstance(data, str):
        try:
           data = json.loads(data)
        except Exception as e:
           return json.dumps({"error": f"Input could not be parsed as JSON: {str(e)}"})
    if not isinstance(data, dict):
        return json.dumps({"error": "Input must be a dictionary or JSON string representing a dict."})

    try:
        d = dict(data) if isinstance(data, dict) else json.loads(data)
        current_expense = float(d.get("monthly_expense_now", 0))
        required_corpus = float(d.get("corpus_flat"))
        #savings = float(d.get("savings", 0))
        gap = float(d.get("gap", 0))
        if gap > 0:
            
            max_reduction = float(d.get("max_reduction", 0.4))

            reduced_expense = current_expense * (1 - max_reduction)
            expense_reduction = current_expense - reduced_expense
            years_to_retire=d.get("years_to_retirement")
            new_gap=gap-expense_reduction*12*years_to_retire

        return json.dumps({
            "expense_after_40%_reduction": reduced_expense,
            "expense_reduced": expense_reduction,
            "new_gap": new_gap
        })
    except Exception as e:
        return json.dumps({"error": f"gap_management failed: {str(e)}"})

####################################################### Retirement Planning Tools Done ######################################################################



############################################################ Retirement Planning Tools ####################################################################################
# @mcp_server.tool()
# def extract_client_info(client_data) -> dict:
#     """
#     Extract and summarize all key fields needed by subsequent functions, producing a flat JSON for further calculations.
#     """
#     try:
#         if not isinstance(client_data, dict):
#             return json.dumps({"error": "Input 'client_data' must be a dictionary."})

#         personal = client_data.get('personal_information', {})
#         misc = client_data.get('miscellaneous', {})
#         profile = client_data.get('client_profile', {})
#         expenses = client_data.get("expenses", {})
#         future_plans = client_data.get("future_plans", {})
#         liabilities = client_data.get("liabilities", {})
#         assets = client_data.get("assets", [])

#         summary = dict(client_data)  # Shallow copy base

#         # Add/normalize the keys we need for downstream steps
#         summary.update({
#             "name": personal.get("name"),
#             "date_of_birth": personal.get("date_of_birth"),
#             "current_year": int(misc.get("current_year")) if misc.get("current_year") is not None else None,
#             "retirement_age": int(misc.get("retirement_age")) if misc.get("retirement_age") is not None else 55,
#             "life_expectancy": int(misc.get("life_expectancy", 85)),
#             "current_age": int(profile.get("current_client_age")) if profile.get("current_client_age") is not None else None,
#             "years_to_retirement": int(profile.get("years_to_retirement")) if profile.get("years_to_retirement") is not None else None,
#             "monthly_expense_now": float(expenses.get("household_expenses_monthly")) if expenses.get("household_expenses_monthly") is not None else None,
#             "assets": assets,
#             "liabilities": liabilities,
#             "risk_appetite": profile.get("risk_appetite"),
#             "equity_exposure": profile.get("equity_exposure_status"),
#             "future_plans": future_plans
#         })
#         return json.dumps(summary)
#     except Exception as e:
#         out = dict(client_data)
#         out["error"] = f"extract_client_info failed: {str(e)}"
#         return json.dumps(out)


# @mcp_server.tool()
# def calculate_retirement_timeline(data) -> dict:
#     """
#     Appends calculated current_age, years_to_retirement, years_in_retirement to the input.
#     """
#     try:
#         d = dict(data) if isinstance(data, dict) else json.loads(data)
#         dob = d.get("date_of_birth")
#         retirement_age = int(d.get("retirement_age", 55))
#         current_year = int(d.get("current_year"))
#         life_expectancy = int(d.get("life_expectancy", 85))

#         if not dob or not isinstance(dob, str) or len(dob) < 4:
#             d["error"] = "Missing or invalid date_of_birth"
#             return json.dumps(d)

#         birth_year = int(dob[:4])
#         current_age = current_year - birth_year
#         years_to_retirement = retirement_age - current_age
#         years_in_retirement = life_expectancy - retirement_age

#         d["current_age"] = current_age
#         d["years_to_retirement"] = years_to_retirement
#         d["years_in_retirement"] = years_in_retirement

#         return json.dumps(d)
#     except Exception as e:
#         d = dict(data) if isinstance(data, dict) else json.loads(data)
#         d["error"] = f"calculate_retirement_timeline failed: {str(e)}"
#         return json.dumps(d)


# @mcp_server.tool()
# def project_expenses(data) -> float:
#     """
#     Appends projected future_expense (monthly, at retirement) to the input JSON.
#     """
#     try:
#         d = dict(data) if isinstance(data, dict) else json.loads(data)
#         current_expense = float(d.get("monthly_expense_now", 0))
#         years_to_retirement = int(d.get("years_to_retirement", 0))
#         inflation = float(d.get("inflation", 0.07))  # default or allow override

#         if current_expense < 0 or years_to_retirement < 0:
#             d["error"] = "Invalid argument values for project_expenses."
#             return json.dumps(d)

#         future_expense = current_expense * ((1 + inflation) ** years_to_retirement)
#         d["future_expense"] = future_expense
#         return json.dumps(d)
#     except Exception as e:
#         d = dict(data) if isinstance(data, dict) else json.loads(data)
#         d["error"] = f"project_expenses failed: {str(e)}"
#         return json.dumps(d)
    
# @mcp_server.tool()
# def estimate_corpus_flat(data) -> float:
#     """
#     Appends corpus_flat value to the JSON.
#     """
#     try:
#         d = dict(data) if isinstance(data, dict) else json.loads(data)
#         future_expense = float(d.get("future_expense", 0))
#         years_in_retirement = int(d.get("years_in_retirement", 30))
#         inflation = float(d.get("inflation", 0.07))
#         post_ret_return = float(d.get("post_ret_return", 0.07))

#         annual_expense = future_expense * 12
#         real_return = ((1 + post_ret_return) / (1 + inflation)) - 1
#         if real_return == 0:
#             corpus = annual_expense * years_in_retirement
#         else:
#             corpus = annual_expense * (1 - (1 + real_return) ** -years_in_retirement) / real_return

#         d["corpus_flat"] = corpus
#         return json.dumps(d)
#     except Exception as e:
#         d = dict(data) if isinstance(data, dict) else json.loads(data)
#         d["error"] = f"estimate_corpus_flat failed: {str(e)}"
#         return json.dumps(d)

# @mcp_server.tool()
# def estimate_corpus_segmented(data) -> float:
#     """
#     Appends corpus_segmented to the JSON, using robust segment year allocation and safe division.
#     """
#     try:
#         d = dict(data) if isinstance(data, dict) else json.loads(data)
#         future_expense = float(d.get("future_expense", 0))
#         years_in_retirement = int(d.get("years_in_retirement", 30))
#         inflation = float(d.get("inflation", 0.07))
#         post_ret_return = float(d.get("post_ret_return", 0.07))

#         # Defensive: Ensure years_in_retirement >= 0
#         years_in_retirement = max(years_in_retirement, 0)

#         # Split years into three segments, last segment gets remainder
#         seg1 = years_in_retirement // 3
#         seg2 = years_in_retirement // 3
#         seg3 = years_in_retirement - seg1 - seg2

#         segment_1_years = seg1
#         segment_2_years = seg2
#         segment_3_years = seg3

#         annual_exp_base = future_expense * 12
#         segments = [
#             (annual_exp_base * 1.10, segment_1_years),
#             (annual_exp_base, segment_2_years),
#             (annual_exp_base * 1.20, segment_3_years)
#         ]

#         real_return = ((1 + post_ret_return) / (1 + inflation)) - 1
#         corpus = 0.0
#         start_year = 0

#         for amount, n_years in segments:
#             if n_years <= 0:
#                 continue
#             if real_return == 0:
#                 # Avoid division by zero: Use simple multiplication
#                 pv = amount * n_years
#             else:
#                 pv = amount * (1 - (1 + real_return) ** -n_years) / real_return
#             pv_discounted = pv / ((1 + real_return) ** start_year) if real_return != 0 else pv
#             corpus += pv_discounted
#             start_year += n_years

#         d["corpus_segmented"] = corpus
#         return json.dumps(d)
#     except Exception as e:
#         d = dict(data) if isinstance(data, dict) else json.loads(data)
#         d["error"] = f"estimate_corpus_segmented failed: {str(e)}"
#         return json.dumps(d)



# @mcp_server.tool()
# def aggregate_assets_liabilities(data) -> dict:
#     """
#     Appends eligible_assets_total and net_assets to the JSON.
#     """
#     try:
#         d = dict(data) if isinstance(data, dict) else json.loads(data)
#         assets = d.get("assets", [])
#         liabilities = d.get("liabilities", {})

#         eligible_types = {
#             "provident_fund", "public_provident_fund", "mutual_funds",
#             "fixed_deposit", "direct_equity", "cash_or_cash_at_bank", "cash_at_bank"
#         }
#         eligible_assets = [
#             float(a['present_value'])
#             for a in assets
#             if isinstance(a, dict) and a.get('type') in eligible_types
#         ]
#         total_assets = sum(eligible_assets)
#         loans = liabilities.get('loans', [])
#         total_loans = sum(float(l.get('outstanding_amount', 0)) for l in loans if isinstance(l, dict))
#         net_assets = total_assets - total_loans

#         d["eligible_assets_total"] = total_assets
#         d["net_assets"] = net_assets
#         return json.dumps(d)
#     except Exception as e:
#         d = dict(data) if isinstance(data, dict) else json.loads(data)
#         d["error"] = f"aggregate_assets_liabilities failed: {str(e)}"
#         return json.dumps(d)


# @mcp_server.tool()
# def feasibility_analysis(data) -> dict:
#     """
#     Appends feasibility, gap, and surplus fields to the JSON.
#     """
#     try:
#         d = dict(data) if isinstance(data, dict) else json.loads(data)
#         required_corpus = float(d.get("corpus_flat"))
#         corpus_available = float(d.get("net_assets"))

#         gap = required_corpus - corpus_available
#         surplus = corpus_available - required_corpus
#         feasible = corpus_available >= required_corpus

#         d["feasible"] = feasible
#         d["gap"] = gap if gap > 0 else 0
#         d["surplus"] = surplus if surplus > 0 else 0
#         return json.dumps(d)
#     except Exception as e:
#         d = dict(data) if isinstance(data, dict) else json.loads(data)
#         d["error"] = f"feasibility_analysis failed: {str(e)}"
#         return json.dumps(d)


# @mcp_server.tool()
# def gap_management(data) -> dict:
#     """
#     Appends expense_reduction, goals_eliminated, required_savings_increase fields to JSON.
#     """
#     try:
#         d = dict(data) if isinstance(data, dict) else json.loads(data)
#         current_expense = float(d.get("monthly_expense_now", 0))
#         required_corpus = float(d.get("corpus_flat"))
#         #future_plans = d.get("future_plans", {})
#         #other_goals = [v for v in future_plans.values() if isinstance(v, dict) and 'amount_required_today' in v]
#         savings = float(d.get("savings", 0))
#         gap = float(d.get("gap", 0))
#         if gap > 0:
            
#             max_reduction = float(d.get("max_reduction", 0.4))

#             reduced_expense = current_expense * (1 - max_reduction)
#             expense_reduction = current_expense - reduced_expense
#             years_to_retire=d.get("years_to_retirement")
#             new_gap=gap-expense_reduction*12*years_to_retire
            
#         # goals_eliminated = []
#         # temp_gap = gap
#         # for goal in reversed(other_goals):
#         #     amount = goal.get('amount_required_today', 0)
#         #     try:
#         #         amount = float(amount)
#         #     except Exception:
#         #         amount = 0
#         #     if temp_gap <= 0:
#         #         break
#         #     goals_eliminated.append(goal)
#         #     temp_gap -= amount

#         # required_savings_increase = max(0, temp_gap)

#         d["expense_after_40%_reduction"] = reduced_expense
#         d["new_gap"]=new_gap
#         #d["goals_eliminated"] = goals_eliminated
#         #d["required_savings_increase"] = required_savings_increase
#         return json.dumps(d)
#     except Exception as e:
#         d = dict(data) if isinstance(data, dict) else json.loads(data)
#         d["error"] = f"gap_management failed: {str(e)}"
#         return json.dumps(d)

############################################################## Retirement Planning Tools ###########################################################################################






if __name__ == "__main__":
    log_to_stderr("Starting MCP Server for Financial Operations via FastMCP...")
    # FastMCP's run method handles the stdio communication loop.
    mcp_server.run(transport='stdio')
    log_to_stderr("MCP Server for Financial Operations stopped.")