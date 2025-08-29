import math 

def clean_name(name):
    """
    Remove leading and trailing whitespace from a string.
    """
    
    return name.strip()

def get_clean_depot_names(depots):
    """
    Return a list of strings, where each string is a cleaned version of
    depot["depot_name"] for each depot in depots.
    """
    
    return [clean_name(d["depot_name"]) for d in depots]

def get_clean_customer_names(customers):
    """
    Return a list of strings, where each string is a cleaned version of
    customer["customer_name"] for each customer in customers.
    """
    return [clean_name(c["customer_name"]) for c in customers]

def build_demands(customers):
    """
    Return a dict with customer names as keys and their demands as values.
    Cleans the customer names first.
    """
    
    return {clean_name(c["customer_name"]): c["demand"] for c in customers}

def build_vehicles_dict(vehicles, depots):
    """
    vehicles: list of dicts like {'id': 'V1', 'capacity': 100, 'depot_id': 1}
    depots: list of dicts like {'id': 1, 'depot_name': 'Leauven'}
    returns: dict keyed by vehicle id with depot names
    """
    # Map depot_id to depot_name
    depot_id_to_name = {d["id"]: d["depot_name"].strip() for d in depots}

    veh_dict = {}
    for v in vehicles:
        vid = str(v["id"])
        depot_name = depot_id_to_name.get(v["depot_id"])
        if depot_name is None:
            raise ValueError(f"Depot ID {v['depot_id']} not found in depots list")
        veh_dict[vid] = {
            "capacity": v["capacity"],
            "depot": depot_name
        }
    return veh_dict


def build_distance_matrix(depots, customers, cost_matrix):
    """
    Build a distance dictionary from depot/customer names using a precomputed cost_matrix.
    depots: list of dicts with 'depot_name'
    customers: list of dicts with 'customer_name'
    cost_matrix: 2D array of distances from depots to customers (rows=depots, cols=customers)
    """
    INF_REPLACE = 1e12
    dist = {}

    depot_names = [d["depot_name"].strip() for d in depots]
    customer_names = [c["customer_name"].strip() for c in customers]

    # depot -> depot distances
    for i, di in enumerate(depot_names):
        for j, dj in enumerate(depot_names):
            dist[(di, dj)] = 0 if i == j else INF_REPLACE

    # depot -> customer and customer -> depot distances
    for i, depot in enumerate(depot_names):
        for j, customer in enumerate(customer_names):
            val = cost_matrix[i][j]
            dist[(depot, customer)] = val if val is not None else INF_REPLACE
            dist[(customer, depot)] = val if val is not None else INF_REPLACE

    # customer -> customer distances (Euclidean fallback)
    for c1 in customers:
        name1 = c1["customer_name"].strip()
        for c2 in customers:
            name2 = c2["customer_name"].strip()
            if name1 == name2:
                dist[(name1, name2)] = 0
            else:
                dist[(name1, name2)] = math.hypot(
                    c1["customer_x"] - c2["customer_x"],
                    c1["customer_y"] - c2["customer_y"]
                ) * 111000

    return dist


def transform_supply(supply_list):
    """
    Takes a list of dictionaries, where each dict has keys "depot_name" and "capacity".
    Returns a dictionary with the same depot names as keys and their respective capacities as values.
    """
    new_dict = {}
    for dic in supply_list:
        new_dict[dic["depot_name"]] = dic["capacity"]
    return new_dict


def transform_demand(demand_list):
    """
    Takes a list of dictionaries, where each dict has keys "customer_name" and "demand".
    Returns a dictionary with the same customer names as keys and their respective demands as values.
    """
    new_dict = {}
    for dic in demand_list:
        new_dict[dic["customer_name"]] = dic["demand"]
    return new_dict
