"""Read input-data.json and render input-data.jinja with raw JSON as data.

Run with the project's env: ./env/bin/python input-data.py
(or: source env/bin/activate && python input-data.py)
Install deps first: pip install -r requirements.txt
"""

import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader


def main():
    base_dir = Path(__file__).resolve().parent
    input_path = base_dir / "input-data.json"

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    jinja_env = Environment(loader=FileSystemLoader(str(base_dir)))
    template = jinja_env.get_template("input-data.jinja")
    output = template.render(data=data)
    data_out = json.loads(output)   # parse the JSON string
    with open("output-data.json", "w", encoding="utf-8") as f:
        json.dump(data_out, f, indent=2)   # or no indent= for compact

if __name__ == "__main__":
    main()
