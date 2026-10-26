import csv
import re
import sys

import pdfplumber

TITLE_RE = re.compile(r"Table\s+\d+\W+Community Board\s+(\d+)\s+Roster")
HEADER = ["Name", "Role", "Nominating Office", "First Appt Year", "Term Exp Year"]


def clean(cell):
    return " ".join((cell or "").split())


def extract(pdf_path):
    rows = []
    board = None
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            titles = [
                (m["top"], int(m["groups"][0]))
                for m in page.search(TITLE_RE.pattern, regex=True)
            ]
            for table in page.find_tables():
                # Board = nearest title above this table; otherwise the table
                # continues from the previous page.
                above = [b for top, b in titles if top < table.bbox[1]]
                if above:
                    board = above[-1]
                for raw in table.extract():
                    row = [clean(c) for c in raw]
                    if row[0] == "Name" or not any(row):
                        continue
                    rows.append([board] + row)
    return rows


def main():
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else "m_roster.pdf"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "m_roster.csv"
    rows = extract(pdf_path)
    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Community Board"] + HEADER)
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {out_path}")


if __name__ == "__main__":
    main()
