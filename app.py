import fastf1
import streamlit as st
import pandas as pd
from project import fastest_lap, delta, get_driver_laps, clean_data, fit, compare, brake_detect, brake_delta
import plotly.graph_objects as go
import numpy as np

st.set_page_config(layout="wide")

DRIVER1_COLOR = "#E10600"
DRIVER2_COLOR = "#1E88E5"

@st.cache_data(show_spinner="Loading race data...")
def load_session(year, race):
    session = fastf1.get_session(year, race, "R")
    session.load()
    return session

year = [
    "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"
]

st.markdown("<h1 style='text-align: center;'>Formula 1 Tire Degradation and Speed Analysis Tool</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: grey;'>Compare two drivers from a single race: fastest-lap speed traces, the time gap between them around the lap, and how fast their tires degrade by compound.</p>", unsafe_allow_html=True)

year_of_race = st.selectbox("Year of Race", year, index = None, placeholder = "Choose a Year")

if year_of_race:
    schedule = fastf1.get_event_schedule(int(year_of_race), include_testing = False)
    all_races = list(schedule["Country"])
    race = st.selectbox("What Race?", all_races, index = None, placeholder = "Choose a Race")

    if race:
        session = load_session(int(year_of_race), race)

        all_drivers = list(session.results["Abbreviation"])

        driver1 = st.selectbox("First Driver", all_drivers, index = None, placeholder = "Choose a Driver")
        driver2 = st.selectbox("Second Driver", all_drivers, index = None, placeholder = "Choose a Driver")

        if driver1 and driver2:
            try:
                grid1, speed1 = fastest_lap(driver1, session)
                grid2, speed2 = fastest_lap(driver2, session)
                change = delta(grid1, speed1, speed2)

                st.header("Speed Analysis")
                st.caption(f"Fastest-lap speed traces and the cumulative time gap. For the gap, a rising line means {driver2} is losing time relative to {driver1}; falling means gaining.")
                col1, col2 = st.columns(2)

                with col1:
                    fig1 = go.Figure()
                    fig1.add_trace(go.Scatter(x = grid1, y = speed1, name = driver1, line = dict(color = DRIVER1_COLOR, width = 2)))
                    fig1.add_trace(go.Scatter(x = grid2, y = speed2, name = driver2, line = dict(color = DRIVER2_COLOR, width = 2)))
                    fig1.update_layout(title = f"Speed: {driver1} vs {driver2}", xaxis_title = "Distance (m)", yaxis_title = "Speed (km/h)", template = "plotly_white", hovermode = "x unified")
                    st.plotly_chart(fig1, use_container_width = True)

                with col2:
                    fig2 = go.Figure()
                    fig2.add_trace(go.Scatter(x = grid1[:-1], y = change, name = "Time gap", line = dict(color = DRIVER2_COLOR, width = 2)))
                    fig2.update_layout(title = f"Time Gap: {driver2} vs {driver1}", xaxis_title = "Distance (m)", yaxis_title = "Time Gap (s)", template = "plotly_white", hovermode = "x unified")
                    st.plotly_chart(fig2, use_container_width = True)
            except Exception:
                st.error("Speed analysis could not be generated for these drivers!")
            try:
                checklist = [driver1, driver2]
                results = {}
                for driver in checklist:
                    driver_name = get_driver_laps(driver, session)
                    name1 = clean_data(driver_name)
                    fit_check = fit(name1)
                    results[driver] = fit_check
                comparison = compare(results)    
                st.header("Tire Degradation")
                st.caption("Degradation slope = seconds added per lap (linear fit of lap time vs lap number). A higher slope means the tires drop off faster.")
                rows = []
                for compound, detail in comparison.items():
                    names = [key for key in detail if key != "verdict"]
                    first, second = names[0], names[1]
                    rows.append({
                        "Compound": compound,
                        f"{first} (s/lap)": round(detail[first], 3),
                        f"{second} (s/lap)": round(detail[second], 3),
                        "Verdict": detail["verdict"],
                    })
                if rows:
                    table = pd.DataFrame(rows)
                    st.dataframe(table, use_container_width = True, hide_index = True)
                else:
                    st.info("These two drivers share no tire compounds to compare in this race.")
            except Exception:
                st.error("No Data to Compare Tire Degradation!")
            if driver1 and driver2:
                try:
                    zones = brake_detect(driver1, session)
                    corners = brake_delta(zones, grid1[:-1], change)
                    st.header("Braking Zone Analysis")
                    st.caption(f"Time gained or lost through each braking zone. A positive value means {driver1} gained time on {driver2} through that zone; negative means {driver2} gained. Braking zones are detected from {driver1}'s fastest lap.")
                    rows = []
                    for zone, time_change in corners:
                        rows.append({
                            "Breaking Zone (m)": f"{round(zone[0])} - {round(zone[1])}",
                            "Time Change (s)": round(time_change, 3)
                        })
                    table = pd.DataFrame(rows)
                    st.dataframe(table, use_container_width = True, hide_index = True)

                except Exception:
                    st.error("Braking zone analysis could not be generated for these drivers!")