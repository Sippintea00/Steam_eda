from pathlib import Path
import pandas as pd

script_folder = Path(__file__).resolve().parent
project_folder = script_folder.parents[1]

matches = list(project_folder.rglob("steamspy_data.csv"))

print("Script folder:", script_folder)
print("Searching inside:", project_folder)
print("Matches found:", matches)