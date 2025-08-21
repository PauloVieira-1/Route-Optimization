# app.py
from flask import Flask, request, jsonify
from data_handler import DataHandler

app = Flask(__name__)
db = DataHandler("../data/data.db")

# -------------------
# SCENARIOS
# -------------------
@app.route("/scenarios", methods=["GET"])
def get_scenarios():
    scenarios = db.get_all("scenarios")
    return jsonify(scenarios)

@app.route("/scenarios", methods=["POST"])
def add_scenario():
    data = request.json
    name = data.get("name")

    if not name:
        return jsonify({"error": "Missing name"}), 400

    db.insert("scenarios", [None, name, None])
    return jsonify({"status": "success"}), 201


# -------------------
# DEPOTS
# -------------------
@app.route("/depots", methods=["GET"])
def get_depots():
    depots = db.get_all("depots")
    return jsonify(depots)

@app.route("/depots", methods=["POST"])
def add_depot():
    data = request.json
    values = [
        None,  # depot_id auto
        data.get("depot_name"),
        data.get("depot_x"),
        data.get("depot_y"),
        data.get("capacity"),
        data.get("max_distance"),
        data.get("type"),
    ]
    db.insert("depots", values)
    return jsonify({"status": "success"}), 201


# -------------------
# CUSTOMERS
# -------------------
@app.route("/customers", methods=["GET"])
def get_customers():
    customers = db.get_all("customers")
    return jsonify(customers)

@app.route("/customers", methods=["POST"])
def add_customer():
    data = request.json
    values = [
        None,  # customer_id auto
        data.get("customer_x"),
        data.get("customer_y"),
        data.get("demand"),
    ]
    db.insert("customers", values)
    return jsonify({"status": "success"}), 201


# -------------------
# VEHICLES
# -------------------
@app.route("/vehicles", methods=["GET"])
def get_vehicles():
    vehicles = db.get_all("vehicles")
    return jsonify(vehicles)

@app.route("/vehicles", methods=["POST"])
def add_vehicle():
    data = request.json
    values = [
        None,  # vehicle_id auto
        data.get("capacity"),
        data.get("max_distance"),
    ]
    db.insert("vehicles", values)
    return jsonify({"status": "success"}), 201


if __name__ == "__main__":
    app.run(debug=True, port=5000)
