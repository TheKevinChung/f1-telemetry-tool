from project import compare
from project import fit
from project import clean_data
import pytest
import pandas as pd

def test_compare():
    answers = {"VER": {"HARD": [-0.5]}, "HAM": {"HARD": [-0.1]}}
    assert compare(answers)["HARD"]["verdict"] == "VER's tires have higher degredation than HAM's tires!"


def test_fit():
    data = {
        "LapNumber": [1,2,3,4],
        "LapSeconds": [80,81,82,83],
        "Compound": ["HARD","HARD","HARD","HARD"]
    }
    table = pd.DataFrame(data)
    catch_data = fit(table)
    assert round((catch_data)["HARD"][0]) == 1.0
    
def test_clean_data():
    race_data = {
        "LapTime": pd.to_timedelta(["1:00:00", "1:00:00", "1:00:00", "1:00:00"]), 
        "LapNumber": [1,2,3,4],
        "Compound": ["HARD","HARD","HARD","HARD"],
        "Stint": [1,1,1,1],
        "PitInTime": [None, None, None, None],
        "PitOutTime": [None, None, None, None],
        "TrackStatus": ["1","12","4","6"]
    }
    table = pd.DataFrame(race_data)
    result = clean_data(table)
    assert len(result) == 2