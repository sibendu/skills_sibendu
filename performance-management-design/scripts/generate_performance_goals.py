#!/usr/bin/env python3
"""
Generate SMART performance goals and KPIs for team roles based on performance categories.

This script reads categories and roles from Excel files, generates SMART goals using Claude API,
and outputs a structured Excel file with goals organized by category.
"""
import os
from dotenv import load_dotenv
import argparse
import os
import sys
from typing import List, Dict

import pandas as pd

from anthropic import Anthropic
from anthropic import AnthropicFoundry
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

load_dotenv()

def load_excel_data(file_path: str, expected_columns: List[str]) -> pd.DataFrame:
    """Load and validate Excel data."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    df = pd.read_excel(file_path)

    # Check if expected columns exist (case-insensitive)
    df.columns = df.columns.str.strip()
    actual_cols = [col.lower() for col in df.columns[:len(expected_columns)]]
    expected_cols_lower = [col.lower() for col in expected_columns]

    if actual_cols != expected_cols_lower:
        raise ValueError(
            f"Expected columns {expected_columns} but found {list(df.columns[:len(expected_columns)])}"
        )

    # Rename to standard names
    df = df.iloc[:, :len(expected_columns)]
    df.columns = expected_columns

    return df


def generate_goals_for_role_category(
    client: Anthropic,
    role: str,
    job_description: str,
    category: str,
    category_description: str,
    num_goals: int,
    time_period: int
) -> str:
    """Generate SMART goals for a specific role and category using Claude API."""

    prompt = f"""Generate {num_goals} SMART performance goals for the following role and performance category.

Role: {role}
Job Description: {job_description}

Performance Category: {category}
Category Description: {category_description}

Time Period: {time_period} months

Requirements:
1. Each goal must be SMART (Specific, Measurable, Achievable, Relevant, Time-bound)
2. Goals must align with both the role's responsibilities and the performance category
3. Include 2-4 specific, measurable KPI measures for each goal
4. KPIs should be reportable at the end of the appraisal period
5. Tailor goals to the specific role - avoid generic templates
6. Mix quantitative metrics (numbers, percentages) with qualitative outcomes where appropriate

Format each goal exactly as follows:

Goal: [Clear, specific goal statement]

KPIs:
- [Specific measurable outcome 1]
- [Specific measurable outcome 2]
- [Specific measurable outcome 3]

---

Generate all {num_goals} goals with this exact format, separating each goal with "---"."""

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text


def format_goals_for_excel(goals_text: str) -> str:
    """Format generated goals for Excel cell (preserving line breaks)."""
    # Replace the separator with double line breaks for better readability
    formatted = goals_text.replace("\n---\n", "\n\n")
    return formatted.strip()


def generate_performance_goals(
    categories_file: str,
    roles_file: str,
    time_period: int,
    output_file: str,
    api_key: str = None
):
    """Main function to generate performance goals."""

    client = None

    # Initialize Anthropic client
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key :    
        client = Anthropic(api_key=api_key)
    else:
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(),
            os.getenv("ANTHROPIC_AZURE_AD_SCOPE")
        )

        client = AnthropicFoundry(
            base_url=os.getenv("ANTHROPIC_FOUNDRY_BASE_URL"),
            azure_ad_token_provider=token_provider  
        )

    # Load input data
    print("Loading input files...")
    categories = load_excel_data(categories_file, ["Category", "Description", "Number_of_Goals"])
    roles = load_excel_data(roles_file, ["Role", "Job Description"])

    print(f"Loaded {len(categories)} categories and {len(roles)} roles")

    # Initialize output DataFrame
    output_data = {
        "Role": [],
        "Job Description": []
    }

    # Add category columns
    for category in categories["Category"]:
        output_data[category] = []

    # Generate goals for each role
    total_iterations = len(roles) * len(categories)
    current_iteration = 0

    for _, role_row in roles.iterrows():
        role = role_row["Role"]
        job_desc = role_row["Job Description"]

        print(f"\nGenerating goals for: {role}")

        # Add role and job description
        output_data["Role"].append(role)
        output_data["Job Description"].append(job_desc)

        # Generate goals for each category
        for _, cat_row in categories.iterrows():
            category = cat_row["Category"]
            cat_desc = cat_row["Description"]
            num_of_goals = cat_row["Number_of_Goals"] 

            current_iteration += 1
            print(f"  [{current_iteration}/{total_iterations}] Generating {num_of_goals} goals for category: {category}")

            try:
                goals_text = generate_goals_for_role_category(
                    client=client,
                    role=role,
                    job_description=job_desc,
                    category=category,
                    category_description=cat_desc,
                    num_goals=num_of_goals,
                    time_period=time_period
                )

                formatted_goals = format_goals_for_excel(goals_text)
                output_data[category].append(formatted_goals)

            except Exception as e:
                print(f"    Error generating goals: {e}")
                output_data[category].append(f"Error: {str(e)}")

    # Create output DataFrame
    output_df = pd.DataFrame(output_data)

    # Save to Excel with proper formatting
    print(f"\nSaving output to: {output_file}")
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        output_df.to_excel(writer, index=False, sheet_name='Performance Goals')

        # Get the worksheet
        worksheet = writer.sheets['Performance Goals']

        # Adjust column widths
        worksheet.column_dimensions['A'].width = 20  # Role
        worksheet.column_dimensions['B'].width = 40  # Job Description

        # Category columns
        for idx, category in enumerate(categories["Category"], start=3):
            col_letter = chr(64 + idx)  # C=3, D=4, etc.
            worksheet.column_dimensions[col_letter].width = 50

        # Set text wrapping for all cells
        from openpyxl.styles import Alignment
        for row in worksheet.iter_rows():
            for cell in row:
                cell.alignment = Alignment(wrap_text=True, vertical='top')

    print(f"\n✓ Successfully generated performance goals!")
    print(f"  Output file: {output_file}")
    print(f"  Total goals generated: {len(roles)} roles × {len(categories)} categories × ")


def main():
    parser = argparse.ArgumentParser(
        description="Generate SMART performance goals and KPIs for team roles"
    )
    parser.add_argument(
        "--categories",
        required=True,
        help="Path to Excel file with categories (columns: Category, Description)"
    )
    parser.add_argument(
        "--roles",
        required=True,
        help="Path to Excel file with roles (columns: Role, Job Description)"
    )
    parser.add_argument(
        "--time-period",
        type=int,
        default=12,
        help="Time period for goals in months (default: 12)"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to output Excel file"
    )
    parser.add_argument(
        "--api-key",
        help="Anthropic API key (or set ANTHROPIC_API_KEY environment variable)"
    )

    args = parser.parse_args()

    try:
        generate_performance_goals(
            categories_file=args.categories,
            roles_file=args.roles,
            time_period=args.time_period,
            output_file=args.output,
            api_key=args.api_key
        )
    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
