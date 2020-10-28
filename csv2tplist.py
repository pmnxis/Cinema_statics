import csv

def csv2tplist(str_path):
    with open(str_path, newline='') as f:
        reader = csv.reader(f)
        data = list(reader)
        return data
