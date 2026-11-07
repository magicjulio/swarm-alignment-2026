import csv


def below_reorder(path: str):
    with open(path) as fh:
        for r in csv.DictReader(fh):
            if int(r["on_hand"]) - int(r["reserved"]) < int(r["reorder_point"]):
                yield r["sku"], r["warehouse"]
