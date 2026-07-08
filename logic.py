import json
import os

DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        data = {
            "subjects": {}
        }
        save_data(data)
        return data

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    # --------- AUTO FIX OLD DATA ----------
    for name, sub in data.get("subjects", {}).items():

        # rename old keys → new keys
        if "total_classes" in sub:
            sub["total"] = sub.pop("total_classes")

        if "attended_classes" in sub:
            sub["attended"] = sub.pop("attended_classes")

        # add missing keys
        sub.setdefault("total", 0)
        sub.setdefault("attended", 0)
        sub.setdefault("importance", "Medium")
        sub.setdefault("classes_per_week", 3)

    return data
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)