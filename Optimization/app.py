# app.py
from flask import Flask, request, jsonify
from data_handler import DataHandler
from models.MDVRP import MDVRPHeterogeneous
from models.tp import transportationProblem
from flask_cors import CORS
import datetime
from utilities import *



app = Flask(__name__)
CORS(app) 

db = DataHandler("../data/data.db")
 
def get_current_date():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d")

def get_id():
    return datetime.datetime.now().strftime("%Y%m%d%H%M%S")

# ---------------- Scenarios ---------------- #

@app.route("/scenarios", methods=["GET"])
def get_scenarios():
    scenarios = db.get_all("scenarios")
    return jsonify([{"id":s[0], "name":s[1], "date":s[2]} for s in scenarios])

@app.route("/scenarios", methods=["DELETE"])
def delete_scenario():
    try:
        data = request.get_json()
        if not data or "scenario_id" not in data:
            return jsonify({"error": "Missing scenario_id"}), 400

        scenario_id = int(data["scenario_id"])

        db.delete_by_id("depots", scenario_id, column="scenario_id")
        db.delete_by_id("vehicles", scenario_id, column="scenario_id")
        db.delete_by_id("customers", scenario_id, column="scenario_id")
        db.delete_by_id("scenarios", scenario_id)

        return jsonify({"status": "success"}), 200

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

@app.route("/scenarios", methods=["PATCH"])
def change_name():
    try:
        data = request.get_json()
        if not data or "scenario_id" not in data or "new_name" not in data:
            return jsonify({"error": "Missing scenario_id or name"}), 400

        scenario_id = int(data["scenario_id"])
        name = data["new_name"]

        db.update_by_id("scenarios", scenario_id, "name", name)

        return jsonify({"status": "success"}), 200

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500
    

@app.route("/scenarios/full", methods=["POST"])
def add_full_scenario():
    try:
        data = request.get_json()
        print("Received JSON:", data)
        if not data:
            return jsonify({"error": "No JSON received"}), 400

        name = data.get("name", "Unnamed Scenario")
        date = data.get("date", get_current_date())
        depots = data.get("depots", [])
        vehicles = data.get("vehicles", [])
        customers = data.get("customers", [])

        scenario_id = db.insert("scenarios",[None, name, date])
        print("Scenario inserted, ID:", scenario_id)

        for depot in depots:
            print("Inserting depot:", depot)
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

        for vehicle in vehicles:
            print("Inserting vehicle:", vehicle)
            db.insert("vehicles", [
                None,
                scenario_id,
                vehicle.get("capacity", 0),
                vehicle.get("depot_id", 0),
            ])

        for customer in customers:
            print("Inserting customer:", customer)
            db.insert("customers", [
                None,
                scenario_id,
                customer.get("customer_name", ""),
                customer.get("customer_x", 0),
                customer.get("customer_y", 0),
                customer.get("demand", 0)
            ])

        return jsonify({
    "status": "success",
    "scenario": {
        "id": scenario_id,
        "name": name,
        "date": get_current_date()
    }
}), 201

    except Exception as e:
        print("SERVER ERROR:", e)
        return jsonify({"error": str(e)}), 500

@app.route("/scenarios_by_id", methods=["POST"])
def get_scenarios_by_id():
    try:
        data = request.get_json(force=True)
        scenario_id = data.get("scenario_id")

        if scenario_id is None:
            return jsonify({"error": "Missing scenario_id"}), 400

        scenario_id = int(scenario_id)

        scenario_row = db.get_by_id("scenarios", scenario_id)
        if not scenario_row:
            return jsonify({"error": "Scenario not found"}), 404

        _, name, date = scenario_row

        raw_customers = db.get_all_by_scenario_id("customers", scenario_id)
        raw_vehicles = db.get_all_by_scenario_id("vehicles", scenario_id)
        raw_depots = db.get_all_by_scenario_id("depots", scenario_id)

        customers = [
            {
                "id": row[0],
                "scenario_id": row[1],
                "customer_name": row[2],
                "customer_x": row[3],
                "customer_y": row[4],
                "demand": row[5]
            }
            for row in raw_customers
        ]

        vehicles = [
            {
                "id": row[0],
                "scenario_id": row[1],
                "capacity": row[2],
                "depot_id": row[3]
            }
            for row in raw_vehicles
        ]

        depots = [
            {
                "id": row[0],
                "scenario_id": row[1],
                "depot_name": row[2],
                "depot_x": row[3],
                "depot_y": row[4],
                "capacity": row[5],
                "max_distance": row[6],
                "type": row[7]
            }
            for row in raw_depots
        ]

        return jsonify({
            "scenario_id": scenario_id,
            "name": name,
            "date": date,
            "customers": customers,
            "vehicles": vehicles,
            "depots": depots
        })

    except ValueError:
        return jsonify({"error": "Invalid scenario_id"}), 400
    except Exception as e:
        print("SERVER ERROR:", e)
        return jsonify({"error": str(e)}), 500



# ---------------- Depots ---------------- #

@app.route("/depots", methods=["GET"])
def get_depots():
    scenario_id = request.args.get("scenario_id")
    if scenario_id is not None:
        try:
            scenario_id = int(scenario_id)
            depots = db.get_all_by_scenario_id("depots", scenario_id)
        except ValueError:
            return jsonify({"error": "Invalid scenario_id"}), 400
    else:
        depots = db.get_all("depots")

    return jsonify(depots)

@app.route("/depots", methods=["POST"])
def add_depot():
    data = request.json
    values = [
        data.get("depot_id"),
        data.get("scenario_id"),
        data.get("depot_name"),
        data.get("depot_x"),
        data.get("depot_y"),
        data.get("capacity"),
        data.get("max_distance"),
        data.get("type"),
    ]

    new_id = db.insert("depots", values)

    new_depot = {
        "id": new_id,
        "scenario_id": data.get("scenario_id"),
        "depot_name": data.get("depot_name"),
        "depot_x": data.get("depot_x"),
        "depot_y": data.get("depot_y"),
        "capacity": data.get("capacity"),
        "max_distance": data.get("max_distance"),
        "type": data.get("type"),
    }

    return jsonify(new_depot), 201

@app.route("/depots", methods=["DELETE"])
def delete_depot():
    try:
        data = request.get_json()
        if not data or "depot_id" not in data:
            return jsonify({"error": "Missing depot_id"}), 400

        depot_id = int(data["depot_id"])

        db.delete_by_id("depots", depot_id)

        return jsonify({"status": "success"}), 200

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

# ---------------- Customers ---------------- #

@app.route("/customers", methods=["GET"])
def get_customers():
    try:
        raw_customers = db.get_all("customers")
        customers = [
            {
                "id": row[0],
                "scenario_id": row[1],
                "customer_name": row[2],
                "customer_x": row[3],
                "customer_y": row[4],
                "demand": row[5]
            }
            for row in raw_customers
        ]
        return jsonify(customers), 200
    except Exception as e:
        print("SERVER ERROR:", e)
        return jsonify({"error": str(e)}), 500


@app.route("/customers", methods=["POST"])
def add_customer():
    data = request.json
    values = [
        data.get("customer_id"),  
        data.get("scenario_id"),
        data.get("customer_name"),
        data.get("customer_x"),
        data.get("customer_y"),
        data.get("demand"),
    ]

    new_id = db.insert("customers", values)

    new_customer = {
        "id": new_id,  
        "scenario_id": data.get("scenario_id"),
        "customer_name": data.get("customer_name"),
        "customer_x": data.get("customer_x"),
        "customer_y": data.get("customer_y"),
        "demand": data.get("demand"),
    }

    return jsonify(new_customer), 201



@app.route("/customers", methods=["DELETE"])
def delete_customer():
    try:
        data = request.get_json()
        if not data or "customer_id" not in data:
            return jsonify({"error": "Missing customer_id"}), 400

        customer_id = int(data["customer_id"])

        db.delete_by_id("customers", customer_id)

        return jsonify({"status": "success"}), 200

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500



# ---------------- Vehicles ---------------- #

@app.route("/vehicles", methods=["GET"])
def get_vehicles():
    vehicles = db.get_all("vehicles")
    return jsonify(vehicles)


@app.route("/vehicles", methods=["POST"])
def add_vehicle():
    data = request.json
    values = [
        data.get("vehicle_id"),
        data.get("scenario_id"),
        data.get("capacity"),   
        data.get("depot_id"), 
    ]
    new_id = db.insert("vehicles", values)
    new_vehicle = {
        "vehicle_id": new_id,
        "scenario_id": data.get("scenario_id"),
        "depot_id": data.get("depot_id"),
        "capacity": data.get("capacity"),
    }
    return jsonify([new_vehicle]), 201

@app.route("/vehicles", methods=["DELETE"])
def delete_vehicle():
    try:
        data = request.get_json()
        if not data or "vehicle_id" not in data:
            return jsonify({"error": "Missing vehicle_id"}), 400

        vehicle_id = int(data["vehicle_id"])

        db.delete_by_id("vehicles", vehicle_id)

        return jsonify({"status": "success"}), 200

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500
    

# ---------------- Other ---------------- #

@app.route("/reset-database", methods=["POST"])
def reset_database():
    try:
        db.cursor.execute("DELETE FROM customers")
        db.cursor.execute("DELETE FROM vehicles")
        db.cursor.execute("DELETE FROM depots")
        db.cursor.execute("DELETE FROM scenarios")
        db.connection.commit()
        return jsonify({"status": "success", "message": "Database cleared"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ---------------- Solvers ---------------- #

@app.route("/mdvrp", methods=["POST"])
def solve_mdvrp():
    try:
        data = request.get_json(force=True)
        depots = data.get("depots", [])
        customers = data.get("customers", [])
        vehicles = data.get("vehicles", [])
        cost_matrix = data.get("costMatrix", [])

        # Clean depot and customer names
        depot_names = [d["depot_name"].strip() for d in depots]
        customer_names = [c["customer_name"].strip() for c in customers]

        # Build demands dict
        demands = {c["customer_name"].strip(): c["demand"] for c in customers}

        # Build vehicles dict
        vehicles_dict = build_vehicles_dict(vehicles, depots)

        # Build distance matrix
        distance_matrix = build_distance_matrix(depots, customers, cost_matrix)

        # ---------------- Debug ---------------- #
        print("Depot names:", depot_names)
        print("Customer names:", customer_names)
        print("Demands:", demands)
        print("Vehicles dict:", vehicles_dict)
        print("Distance matrix sample:", distance_matrix)
        # -------------------------------------- #

        # Solve MDVRP
        problem = MDVRPHeterogeneous(distance_matrix, depot_names, customer_names, demands, vehicles_dict)
        result = problem.solve()

        return jsonify(result), 200

    except Exception as e:
        print("SERVER ERROR:", e)
        return jsonify({"error": str(e)}), 500
    
@app.route("/solvetp", methods=["POST"])
def solve():

    try:
        data = request.get_json(force=True)
        costMatrix = data.get("costMatrix")
        demand = data.get("demand")
        supply = data.get("supply")

    except Exception as e:
        print("SERVER ERROR:", e)
        return jsonify({"error": str(e)}), 500

    print(demand)
    d = transform_demand(demand)
    s = transform_supply(supply)

    problem = transportationProblem(costMatrix, d, s)
    problem.solve()

    return jsonify(problem.get_solution_json()), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5100, debug=True)