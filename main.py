from argparse import ArgumentParser
from pathlib import Path
import tomllib
from datetime import datetime
import csv            

def read_csv(path: str, config: dict):
    records = []
    fields = config["fields"]
    date_column = config["date_column"]
    date_format = config["date_format"]
    encoding = config["encoding"]
    with open(path, encoding=encoding) as f:
        reader = csv.DictReader(f, fieldnames=fields)
        for i, row in enumerate(reader):
            if i < config["trim_top"]: continue
            for k in row:
                row[k] = row[k].strip()
            try:
                row[date_column] = datetime.strptime(row[date_column], date_format)
            except:
                continue
            records.append(row)
    return records

def write_csv(handle, table: dict, config: dict):   
    date_column = config["date_column"]
    date_format = config["date_format"]
    fields = config["fields"]
    column_map: dict = config["column_map"]
    export_table = []
    for row in table:
        new_row = dict()
        for k, v in column_map.items():
            new_row[v] = row[k] 
        new_row[date_column] = datetime.strftime(new_row[date_column],date_format)
        export_table.append(new_row)

    writer = csv.DictWriter(handle, fieldnames=fields)
    writer.writeheader()
    writer.writerows(export_table) 

def main():
    parser = ArgumentParser("Bank Normaliser")
    parser.add_argument("input")
    parser.add_argument("bank")
    parser.add_argument("--output","-o", default="./output")
    parser.add_argument("--grammars", default="./grammars.toml")
    args = parser.parse_args()

    with open(args.grammars, "rb") as f:
        grammars = tomllib.load(f)

    if args.bank not in grammars:
        raise ValueError(f"Couldn't find {args.bank} in grammars.")

    import_config = grammars[args.bank]["import"]
    filetype = import_config["filetype"]
    read_strats = {
        "csv": read_csv
    }

    table = read_strats[filetype](args.input, import_config) 

    output_config = grammars[args.bank]["export"]
    output_path = Path(args.output)
    if output_path.is_dir():
        output_path = output_path / "ynab.csv"

    with open(output_path, "w") as f:
        write_csv(f,table,output_config)
 
if __name__ == "__main__":
    main()
