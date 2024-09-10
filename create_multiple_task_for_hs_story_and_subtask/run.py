import sys
import pandas as pd
from jira import JIRA
from datetime import datetime
import pytz  # For timezone conversion
import json  # For debugging the JSON payload

def test_jira_connection(jira_cli):
    """
    Test JIRA connection by fetching a list of projects.
    """
    try:
        projects = jira_cli.projects()
        print("Connection successful! You have access to the following projects:")
        for project in projects:
            print(f"  - {project.key}: {project.name}")
        return True
    except Exception as e:
        print(f"Failed to connect to JIRA: {e}")
        return False
        

def create_subtask(jira_cli, parent_issue_key, subtask_summary, subtask_description, project_key, subtask_change_start_date, subtask_change_completion_date):
    """
    Create a subtask linked to the parent issue.
    """
    subtask_fields = {
        "project": {"key": project_key},
        "summary": subtask_summary,
        "description": subtask_description,
        "issuetype": {"name": "Sub-task"},  # Sub-task type
        "parent": {"key": parent_issue_key},  # Link to parent (Story or Task)
        "labels": ["ops-planned"],  # Include the labels in subtask creation
        "customfield_10008": subtask_change_start_date,  # Subtask change start date (in UTC)
        "customfield_10009": subtask_change_completion_date  # Subtask change completion date (in UTC)
    }

    # Debugging: Print the JSON payload for the subtask before sending it to Jira
    # print("Subtask fields being sent to Jira:")
    # print(json.dumps(subtask_fields, indent=4))

    try:
        # Create the Sub-task
        subtask = jira_cli.create_issue(fields=subtask_fields)
        print(f"Created Subtask: {subtask.key} under Story {parent_issue_key}")
        return subtask
    except Exception as e:
        print(f"Error creating the Subtask for Story {parent_issue_key}: {e}")
        return None  # Return None if there's an error, continue to next

def main():
    """
    Entry function
    """

    # JIRA configuration
    # jira_user_email = '' #Your Email
    # jira_user_token = '' # Your token 
    project_key = "HS"  # Hosted Solutions (HS) project
    jira_url = "https://woodwing.atlassian.net"
    # account_id = "6017c55f20445000698eaab9"  # Your accountId
    priority = "C - Medium"  # Set priority
    excel_file_path = 'details_hs.xlsx'  # Update this with the actual path to your Excel file

    # Initialize JIRA client
    jira_cli = JIRA(jira_url, basic_auth=(jira_user_email, jira_user_token))

    # Define the timezone for your local time
    local_tz = pytz.timezone('Asia/Kuala_Lumpur')

    # Read tasks from Excel file
    df = pd.read_excel(excel_file_path)

    last_story_key = None  # To keep track of the last created Story

    # Create tasks (Stories or Subtasks)
    for index, row in df.iterrows():
        # Convert Story dates to UTC
        story_change_start_date = row['story_change_start_date']
        story_change_completion_date = row['story_change_completion_date']
        
        if isinstance(story_change_start_date, pd.Timestamp) and pd.notna(story_change_start_date):
            story_change_start_date = local_tz.localize(story_change_start_date).astimezone(pytz.utc).isoformat()
        else:
            story_change_start_date = None

        if isinstance(story_change_completion_date, pd.Timestamp) and pd.notna(story_change_completion_date):
            story_change_completion_date = local_tz.localize(story_change_completion_date).astimezone(pytz.utc).isoformat()
        else:
            story_change_completion_date = None

        # If the row contains Story information
        if pd.notna(row['summary']) and pd.notna(row['description']):
            issue_fields = {
                "project": {"key": project_key},
                "summary": row['summary'],
                "description": row['description'],
                "issuetype": {"name": "Story"},
                "priority": {"name": priority},
                # "assignee": {"id": account_id},
                "labels": ["ops-planned"],
                "customfield_10008": story_change_start_date,  # Change start date for Story
                "customfield_10009": story_change_completion_date  # Change completion date for Story
            }

            # Debugging: Print the Story JSON payload
            # print("Story fields being sent to Jira:")
            # print(json.dumps(issue_fields, indent=4))

            try:
                created_issue = jira_cli.create_issue(fields=issue_fields)
                print(f"Created Story: {created_issue.key}")
                last_story_key = created_issue.key  # Keep track of the Story's issue key for Subtasks
            except Exception as e:
                print(f"Error creating the Story: {e}")
                continue  # Skip to the next row in case of an error

        # If the row contains Subtask information, link to the last created Story
        if pd.notna(row['subtask_summary']) and pd.notna(row['subtask_description']) and last_story_key:
            subtask_change_start_date = row['subtask_change_start_date']
            subtask_change_completion_date = row['subtask_change_completion_date']

            if isinstance(subtask_change_start_date, pd.Timestamp) and pd.notna(subtask_change_start_date):
                subtask_change_start_date = local_tz.localize(subtask_change_start_date).astimezone(pytz.utc).isoformat()
            else:
                subtask_change_start_date = None

            if isinstance(subtask_change_completion_date, pd.Timestamp) and pd.notna(subtask_change_completion_date):
                subtask_change_completion_date = local_tz.localize(subtask_change_completion_date).astimezone(pytz.utc).isoformat()
            else:
                subtask_change_completion_date = None

            try:
                create_subtask(jira_cli, last_story_key, row['subtask_summary'], row['subtask_description'], project_key, subtask_change_start_date, subtask_change_completion_date)
            except Exception as e:
                print(f"Failed to create subtask for {last_story_key}: {e}")

if __name__ == "__main__":
    main()
