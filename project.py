import fastf1
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

def main():
    session = fastf1.get_session(2023, "Australia", "R")
    session.load()
    all_possible_drivers = [
    "AIT", "ALB", "ALO", "ANT", "BEA", 
    "BOT", "COL", "DEV", "DRU", "FIT", 
    "GAS", "GIO", "GRO", "HAM", "HUL", 
    "KVY", "LEC", "MAG", "MAZ", "MSC", 
    "NOR", "OCO", "PER", "PIA", "RAI", 
    "RIC", "RUS", "SAI", "SAR", "STR", 
    "TSU", "VER", "VET", "ZHO"
    ]
    driver_find = input("Driver: ")
    driver_find2 = input("Driver: ")
    checklist = [driver_find, driver_find2]
    results = {}
    for driver in checklist:
        if driver in all_possible_drivers:
            driver_name = get_driver_laps(driver, session)
            name1 = clean_data(driver_name)
            fit_check = fit(name1)
            results[driver] = fit_check
    comparison = compare(results)
    grid, interpolated = fastest_lap(driver_find, session)
    grid2, interpolated2 = fastest_lap(driver_find2, session)
    gap = delta(grid, interpolated, interpolated2)
    zones = brake_detect(driver_find, session)
    corners = brake_delta(zones, grid[:-1], gap)
    empty = go.Figure()
    empty.add_trace(go.Scatter(x = grid, y = interpolated, name = driver_find))
    empty.add_trace(go.Scatter(x = grid2, y = interpolated2, name = driver_find2))
    empty.show()
    empty2 = go.Figure()
    empty2.add_trace(go.Scatter(x = grid[:-1], y = gap, name = "Delta of the Two Drivers"))
    empty2.show()
    brake_result = brake_detect("VER", session)
    print(brake_result)
    print(results)
    print(comparison)
    print(corners)
    
os.makedirs("cache", exist_ok=True)
fastf1.Cache.enable_cache("cache")

def get_driver_laps(name, session):
    driver = session.laps.pick_drivers(name) 
    return driver

def clean_data(driver):
    small = driver[["LapTime", "LapNumber", "Compound", "Stint", "PitInTime", "PitOutTime", "TrackStatus"]] 
    small["LapSeconds"] = small["LapTime"].dt.total_seconds()  
    keepers = small[small["TrackStatus"].isin(["1", "12"])] 
    return keepers

def fit(keepers):
    sets_data = {}
    keepers = keepers.dropna(subset = ["LapSeconds"])
    for label, basket in keepers.groupby("Compound"):
        graph = np.polyfit(basket["LapNumber"], basket["LapSeconds"], deg = 1)
        print(label, graph)
        sets_data[label] = graph
    return sets_data

def compare(results):
    all_drivers = list(results.keys())
    name1 = all_drivers[0]
    name2 = all_drivers[1]
    first_tireset = list(results[name1].keys())
    second_tireset = list(results[name2].keys())
    dataset = {}
    for tire in first_tireset:
        if tire in second_tireset:
            slope1 = results[name1][tire][0]
            slope2 = results[name2][tire][0]
            verdict = ""
            if slope1 > slope2:
                verdict =  f"{name1}'s tires have higher degradation than {name2}'s tires!"
            elif slope1 < slope2:
                verdict = f"{name2}'s tires have higher degradation than {name1}'s tires!"
            else:
                verdict = "Both drivers have the same degradation!"
            dataset[tire] = {name1: slope1, name2: slope2, "verdict": verdict}
    return dataset

def fastest_lap(driver_find, session):
    fastest = session.laps.pick_driver(driver_find).pick_fastest()
    telemetry = fastest.get_telemetry()
    selected = telemetry[["Speed", "Distance"]]
    grid = np.linspace(0, selected["Distance"].max(), 1000) 
    interpolated = np.interp(grid, selected["Distance"], selected["Speed"])
    return grid, interpolated

def delta(grid, speed1, speed2):
    split = np.diff(grid)
    calc_speed = speed1 / 3.6
    calc_speed2 = speed2 / 3.6
    segment = split / calc_speed[:-1]
    segment2 = split / calc_speed2[:-1]
    difference = segment - segment2
    overall = np.cumsum(difference)
    return overall

def brake_detect(driver_find, session):
    best_lap = session.laps.pick_driver(driver_find).pick_fastest()
    telemetry = best_lap.get_telemetry()
    specific = telemetry[["Brake", "Distance"]]
    zones = []
    previous = False
    brake_start = None
    for i in range(len(specific)):
        value = specific["Brake"].iloc[i]
        distance = specific["Distance"].iloc[i]
        if value == True and previous == False:
            brake_start = distance
        if value == False and previous == True:
            zones.append((brake_start, distance))
        previous = value
    return zones

def brake_delta(zones, grid, delta):
    results = []
    for zone in zones:
        start = zone[0]
        end = zone[1]
        start_index = np.argmin(np.abs(grid - start))
        end_index = np.argmin(np.abs(grid - end))
        time_change = delta[end_index] - delta[start_index]
        results.append((zone, time_change))
    return results


        

if __name__ == "__main__":
    main()
   
