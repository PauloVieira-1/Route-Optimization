# reset_and_insert.py
from data_handler import DataHandler

db_path = "../data/data.db"
db = DataHandler(db_path)

# --- Step 1: Clear tables ---
tables = ["scenarios", "depots", "vehicles", "customers"]
for table in tables:
    db.delete_table(table)
    print(f"Deleted table: {table}")

# --- Step 2: Recreate tables ---
db.create_table("scenarios", {
    "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
    "name": "TEXT",
    "date": "TEXT"
})

db.create_table("depots", {
    "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
    "scenario_id": "INTEGER",
    "depot_name": "TEXT",
    "depot_x": "INTEGER",
    "depot_y": "INTEGER",
    "capacity": "INTEGER",
    "max_distance": "INTEGER",
    "type": "TEXT"
})

db.create_table("vehicles", {
    "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
    "scenario_id": "INTEGER",
    "capacity": "INTEGER",
    "max_distance": "INTEGER"
})

db.create_table("customers", {
    "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
    "scenario_id": "INTEGER",
    "customer_name": "TEXT",
    "customer_x": "INTEGER",
    "customer_y": "INTEGER",
    "demand": "INTEGER"
})

# --- Step 3: Insert scenario ---
scenario_data = {"name": "Scenario A", "date": ""}
db.insert("scenarios", [None, scenario_data["name"], scenario_data["date"]])
scenario_id = db.cursor.lastrowid
print(f"Scenario inserted, ID: {scenario_id}")

# --- Step 4: Insert depots ---
depots = [
    {"depot_name": "Depot 1", "depot_x": 10, "depot_y": 5, "capacity": 100, "max_distance": 50, "type": "main"},
    {"depot_name": "Depot 2", "depot_x": 20, "depot_y": 15, "capacity": 80, "max_distance": 60, "type": "secondary"}
]

for depot in depots:
    db.insert("depots", [
        None,
        scenario_id,
        depot.get("depot_name"),
        depot.get("depot_x"),
        depot.get("depot_y"),
        depot.get("capacity"),
        depot.get("max_distance"),
        depot.get("type")
    ])
    print(f"Inserted depot: {depot['depot_name']}")

# --- Step 5: Insert vehicles ---
vehicles = [
    {"capacity": 50, "max_distance": 200},
    {"capacity": 40, "max_distance": 150}
]

for vehicle in vehicles:
    db.insert("vehicles", [
        None,
        scenario_id,
        vehicle.get("capacity", 0),
        vehicle.get("max_distance", 0)
    ])
    print(f"Inserted vehicle with capacity: {vehicle['capacity']}")

# --- Step 6: Insert customers ---
customers = [
    {"customer_name": "Customer 1", "customer_x": 2, "customer_y": 8, "demand": 10},
    {"customer_name": "Customer 2", "customer_x": 5, "customer_y": 12, "demand": 15}
]

for customer in customers:
    db.insert("customers", [
        None,
        scenario_id,
        customer.get("customer_name", ""),
        customer.get("customer_x", 0),
        customer.get("customer_y", 0),
        customer.get("demand", 0)
    ])
    print(f"Inserted customer: {customer['customer_name']}")

db.close()
print("Database reset and data inserted successfully!")

