import streamlit as st
import json
import os
from datetime import datetime


# Function to calculate daily working hours
def calculate_daily_hours(start_time, end_time):
    lunch_start = datetime.strptime("12:00", "%H:%M")
    lunch_end = datetime.strptime("13:00", "%H:%M")

    start_time = datetime.strptime(start_time, "%H:%M")
    end_time = datetime.strptime(end_time, "%H:%M")

    if start_time < lunch_start < end_time:
        working_time_before_lunch = (lunch_start - start_time).total_seconds() / 3600
        working_time_after_lunch = max((end_time - lunch_end).total_seconds() / 3600, 0)
        total_working_hours = working_time_before_lunch + working_time_after_lunch
    else:
        total_working_hours = (end_time - start_time).total_seconds() / 3600

    return max(total_working_hours, 0)


# Load and save defaults
def load_defaults():
    if os.path.exists("defaults.json"):
        try:
            with open("defaults.json", "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            pass
    return []


def save_defaults(data):
    with open("defaults.json", "w") as file:
        json.dump(data, file)


# Streamlit app
st.title("Attendance Tracker")

# Sidebar for inputting week name and adding weeks
st.sidebar.header("Add New Week")
week_name = st.sidebar.text_input("Enter Week Name")
if st.sidebar.button("Add Week"):
    if not week_name.strip():
        st.sidebar.warning("Please enter a valid week name!")
    else:
        if "weeks" not in st.session_state:
            st.session_state["weeks"] = []
        st.session_state["weeks"].append({"week_name": week_name, "times": {}})

# Initialize weeks data
if "weeks" not in st.session_state:
    st.session_state["weeks"] = load_defaults()

# Display saved weeks
for week_index, week in enumerate(st.session_state["weeks"]):
    st.subheader(f"Week: {week['week_name']}")

    # Input times for each day
    week_entries = {}
    for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
        col1, col2 = st.columns(2)
        with col1:
            start_time = st.text_input(f"{day} Start Time", value=week["times"].get(day, {}).get("start", "09:00"), key=f"start-{week_index}-{day}")
        with col2:
            end_time = st.text_input(f"{day} End Time", value=week["times"].get(day, {}).get("end", "18:00"), key=f"end-{week_index}-{day}")
        week_entries[day] = {"start": start_time, "end": end_time}

    # Save entered times
    if st.button(f"Save Week: {week['week_name']}", key=f"save-{week_index}"):
        week["times"] = week_entries
        st.success(f"Saved data for {week['week_name']}!")

    # Calculate daily hours for the week
    if st.button(f"Calculate Hours: {week['week_name']}", key=f"calculate-{week_index}"):
        total_hours = 0
        try:
            for day, times in week_entries.items():
                total_hours += calculate_daily_hours(times["start"], times["end"])
            st.info(f"Total Hours for {week['week_name']}: {total_hours:.2f} hours (excluding lunch)")
        except Exception as e:
            st.error(f"Error calculating hours: {e}")

    # Option to delete the week
    if st.button(f"Delete Week: {week['week_name']}", key=f"delete-{week_index}"):
        st.session_state["weeks"].pop(week_index)
        st.experimental_rerun()  # Refresh the app state


# Save all data to file
if st.button("Save All Data"):
    save_defaults(st.session_state["weeks"])
    st.success("All data saved successfully!")

# Exit button (not applicable for Streamlit, but added for feature parity)
if st.button("Exit App"):
    st.warning("This is a web app. Simply close the tab to exit.")

