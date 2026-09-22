import csv
from pathlib import Path

total = 0
highest = 0
top_student = ""

with open(file_path = Path(__file__).parent / "p03_data.csv") as file:
    reader = csv.DictReader(file)
    data = list(reader)


for student in data:
    marks = int(student["marks"])
    total += marks

    if marks > highest:
        highest = marks
        top_student = student["name"]


print("\n--- Report ---")
print("Total Students:", len(data))
print("Average Marks:", total / len(data))
print("Highest Score:", highest)
print("Top Student:", top_student)