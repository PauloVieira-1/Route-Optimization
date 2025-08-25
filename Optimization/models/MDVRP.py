import pulp

class MDVRPHeterogeneous:
    def __init__(self, distance_matrix, depots, customers, demands, vehicles):
        self.distance_matrix = distance_matrix
        self.depots = depots
        self.customers = customers
        self.demands = demands
        self.vehicles = vehicles
        self.nodes = depots + customers
        
        # Validate inputs
        self._validate_inputs()

    def _validate_inputs(self):
        """Validate that all required distance matrix entries exist"""
        missing_entries = []
        
        for i in self.nodes:
            for j in self.nodes:
                if (i, j) not in self.distance_matrix:
                    missing_entries.append((i, j))
        
        if missing_entries:
            print("Missing distance matrix entries:")
            for entry in missing_entries[:10]:  # Show first 10
                print(f"  {entry}")
            if len(missing_entries) > 10:
                print(f"  ... and {len(missing_entries) - 10} more")
            raise ValueError(f"Distance matrix missing {len(missing_entries)} entries")
        
        # Check for invalid characters or unexpected formats in node names
        all_nodes = self.depots + self.customers
        for node in all_nodes:
            if not isinstance(node, str):
                raise ValueError(f"Node names must be strings, got {type(node)}: {node}")
            if len(node) > 50:  # Reasonable length check
                print(f"Warning: Very long node name: {node}")

    def solve(self):
        prob = pulp.LpProblem("MDVRP_Heterogeneous", pulp.LpMinimize)

        # Binary variables: x[(i,j,v)] = 1 if vehicle v goes from i to j
        x = {}
        for i in self.nodes:
            for j in self.nodes:
                for v in self.vehicles.keys():
                    if i != j:  # No self-loops
                        x[(i, j, v)] = pulp.LpVariable(f"x_{i}_{j}_{v}", 0, 1, pulp.LpBinary)

        # MTZ load variables per vehicle
        u = {}
        for c in self.customers:
            for v in self.vehicles.keys():
                u[(c, v)] = pulp.LpVariable(f"u_{c}_{v}", 0, None, pulp.LpContinuous)

        # Objective: minimize total distance
        prob += pulp.lpSum(
            self.distance_matrix[i, j] * x[(i, j, v)]
            for i in self.nodes 
            for j in self.nodes 
            for v in self.vehicles.keys()
            if i != j
        )

        # Each customer is visited exactly once (incoming and outgoing)
        for c in self.customers:
            prob += pulp.lpSum(x[(i, c, v)] for i in self.nodes if i != c for v in self.vehicles.keys()) == 1
            prob += pulp.lpSum(x[(c, j, v)] for j in self.nodes if j != c for v in self.vehicles.keys()) == 1

        # Flow conservation for vehicles
        for v in self.vehicles.keys():
            for node in self.nodes:
                prob += pulp.lpSum(x[(i, node, v)] for i in self.nodes if i != node) == \
                        pulp.lpSum(x[(node, j, v)] for j in self.nodes if j != node)

        # Vehicle can start from its assigned depot at most once
        for v, info in self.vehicles.items():
            depot = info['depot']
            prob += pulp.lpSum(x[(depot, j, v)] for j in self.nodes if j != depot) <= 1

        # MTZ subtour elimination and capacity constraints
        for v, info in self.vehicles.items():
            Q = info['capacity']
            for i in self.customers:
                for j in self.customers:
                    if i != j:
                        prob += u[(i, v)] - u[(j, v)] + Q * x[(i, j, v)] <= Q - self.demands[j]

        # Customer load bounds - only if customer is visited by vehicle v
        for v, info in self.vehicles.items():
            Q = info['capacity']
            for c in self.customers:
                # If customer c is visited by vehicle v, then u[c,v] >= demand[c]
                prob += u[(c, v)] >= self.demands[c] * pulp.lpSum(x[(i, c, v)] for i in self.nodes if i != c)
                # Load cannot exceed capacity
                prob += u[(c, v)] <= Q

        # Solve
        prob.solve(pulp.PULP_CBC_CMD(msg=False))

        # Extract routes
        routes = []
        for v, info in self.vehicles.items():
            depot = info['depot']
            route = [depot]
            visited = set()
            while True:
                next_nodes = [j for j in self.nodes if j != route[-1] and 
                             (route[-1], j, v) in x and x[(route[-1], j, v)].value() == 1]
                if not next_nodes:
                    break
                next_node = next_nodes[0]
                if next_node in visited:
                    break
                route.append(next_node)
                visited.add(next_node)
                if next_node in self.depots:
                    break
            if len(route) > 1:
                routes.append({"vehicle": v, "route": route, "capacity": info['capacity']})

        return {
            "status": pulp.LpStatus[prob.status],
            "total_cost": pulp.value(prob.objective),
            "routes": routes
        }


# Debug function to help identify the issue
def debug_inputs(distance_matrix, depots, customers, demands, vehicles):
    """Helper function to debug your inputs"""
    print("=== INPUT DEBUG INFO ===")
    print(f"Depots: {depots}")
    print(f"Customers: {customers}")
    print(f"Demands keys: {list(demands.keys())}")
    print(f"Vehicle info: {vehicles}")
    
    all_nodes = depots + customers
    print(f"All nodes: {all_nodes}")
    
    print("\nDistance matrix keys (first 10):")
    keys = list(distance_matrix.keys())[:10]
    for key in keys:
        print(f"  {key}")
    
    print(f"\nTotal distance matrix entries: {len(distance_matrix)}")
    print(f"Expected entries: {len(all_nodes) * len(all_nodes)}")
    
    # Check for problematic node names
    for node in all_nodes:
        if '20250825090155' in str(node):
            print(f"WARNING: Found timestamp in node name: {node}")


# ---------------- Example usage ---------------- #
if __name__ == "__main__":
    depots = ["D1", "D2"]
    customers = ["C1", "C2", "C3", "C4"]

    demands = {
        "C1": 4,
        "C2": 6,
        "C3": 5,
        "C4": 7,
    }

    vehicles = {
        "V1": {"depot": "D1", "capacity": 10},
        "V2": {"depot": "D1", "capacity": 15},
        "V3": {"depot": "D2", "capacity": 20},
    }

    dist = {
        ("D1","D1"):0, ("D1","D2"):10, ("D1","C1"):5, ("D1","C2"):7, ("D1","C3"):12, ("D1","C4"):15,
        ("D2","D1"):10, ("D2","D2"):0, ("D2","C1"):8, ("D2","C2"):6, ("D2","C3"):5, ("D2","C4"):9,
        ("C1","D1"):5, ("C1","D2"):8, ("C1","C1"):0, ("C1","C2"):4, ("C1","C3"):6, ("C1","C4"):7,
        ("C2","D1"):7, ("C2","D2"):6, ("C2","C1"):4, ("C2","C2"):0, ("C2","C3"):5, ("C2","C4"):3,
        ("C3","D1"):12, ("C3","D2"):5, ("C3","C1"):6, ("C3","C2"):5, ("C3","C3"):0, ("C3","C4"):4,
        ("C4","D1"):15, ("C4","D2"):9, ("C4","C1"):7, ("C4","C2"):3, ("C4","C3"):4, ("C4","C4"):0,
    }

    # Debug your inputs first
    debug_inputs(dist, depots, customers, demands, vehicles)
    
    solver = MDVRPHeterogeneous(dist, depots, customers, demands, vehicles)
    result = solver.solve()
    print(result)