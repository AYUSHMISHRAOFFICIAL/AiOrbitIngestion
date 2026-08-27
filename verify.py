import json
import shutil
import sys
import os

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

if not os.path.exists("data/final/entities1.json"):
    shutil.copy("data/final/entities.json", "data/final/entities1.json")
    print("Copied run 1 output. Now run the pipeline again, then run this script.")
    sys.exit(0)

# Load both
e1 = load_json("data/final/entities1.json")
e2 = load_json("data/final/entities.json")

print(f"Run 1 entity count: {len(e1)}")
print(f"Run 2 entity count: {len(e2)}")

# Compare
if e1 == e2:
    print("Determinism check passed! Outputs are identical.")
else:
    print("Determinism check FAILED!")
