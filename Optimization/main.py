import data_handler
import csv
import pandas as pd


def main():

    db = data_handler.DataHandler("../data/data.db")

    db.create_table("depots", {"depot_id": "INTEGER PRIMARY KEY", "depot_name": "TEXT", "depot_x": "REAL", "depot_y": "REAL", "capacity": "INTEGER", "max_distance": "INTEGER", "type": "TEXT"})
    db.create_table("vehicles", {"vehicle_id": "INTEGER PRIMARY KEY", "capacity": "REAL", "max_distance": "REAL"})
    db.create_table("customers", {"customer_id": "INTEGER PRIMARY KEY", "customer_x": "REAL", "customer_y": "REAL", "demand": "INTEGER"})
    db.create_table("scenarios", {"scenario_id": "INTEGER PRIMARY KEY", "Nmae": "TEXT", "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP" })

    # db.print_table("depots")
    # db.print_table("vehicles")
    # db.print_table("customers")

    db.close()

if __name__ == '__main__':
    main()