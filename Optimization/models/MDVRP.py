import pulp

class MDVRPHeterogeneous:
    def __init__(self, distance_matrix, depots, customers, demands, vehicles):
        self.distance_matrix = distance_matrix
        self.depots = depots
        self.customers = customers
        self.demands = demands
        self.vehicles = vehicles
        self.nodes = depots + customers
        self._validate_inputs()

    def _validate_inputs(self):
        missing = []
        for i in self.nodes:
            for j in self.nodes:
                if (i, j) not in self.distance_matrix:
                    missing.append((i, j))
        if missing:
            raise ValueError(f"Distance matrix missing {len(missing)} entries. Examples: {missing[:5]}")
        for node in self.nodes:
            if not isinstance(node, str):
                raise ValueError(f"Node names must be strings, got {type(node)}: {node}")

    def _arc_allowed(self, i, j, v):
        """Only allow arcs that start/end at the vehicle's own depot or customers.
           No self-loops. No cross-depot moves."""
        if i == j:
            return False
        depot_v = self.vehicles[v]['depot']
        # disallow leaving from other depots
        if i in self.depots and i != depot_v:
            return False
        # disallow entering other depots
        if j in self.depots and j != depot_v:
            return False
        return True

    def solve(self):
        prob = pulp.LpProblem("MDVRP_Heterogeneous", pulp.LpMinimize)

        # Vehicle activation
        y = {v: pulp.LpVariable(f"y_{v}", 0, 1, pulp.LpBinary) for v in self.vehicles}

        # Decision variables x[i,j,v]
        x = {}
        for i in self.nodes:
            for j in self.nodes:
                for v in self.vehicles:
                    if self._arc_allowed(i, j, v):
                        x[(i, j, v)] = pulp.LpVariable(f"x_{i}_{j}_{v}", 0, 1, pulp.LpBinary)

        # MTZ load variables (customers only)
        u = {(c, v): pulp.LpVariable(f"u_{c}_{v}", 0, None, pulp.LpContinuous)
             for c in self.customers for v in self.vehicles}

        # Objective: minimize total distance
        prob += pulp.lpSum(self.distance_matrix[i, j] * x[(i, j, v)]
                           for (i, j, v) in x.keys())

        # Each customer visited exactly once (incoming and outgoing across all vehicles)
        for c in self.customers:
            prob += pulp.lpSum(x[(i, c, v)] for (i, j, v) in x if j == c) == 1
            prob += pulp.lpSum(x[(c, j, v)] for (i, j, v) in x if i == c) == 1

        # Flow conservation per vehicle on customers
        for v in self.vehicles:
            for c in self.customers:
                prob += pulp.lpSum(x[(i, c, v)] for (i, j, vv) in x if vv == v and j == c) == \
                        pulp.lpSum(x[(c, j, v)] for (i, j, vv) in x if vv == v and i == c)

        # Start/end at own depot once if vehicle is used
        for v, info in self.vehicles.items():
            d = info['depot']
            # departures from depot == y[v]
            prob += pulp.lpSum(x[(d, j, v)] for (i, j, vv) in x if vv == v and i == d) == y[v]
            # arrivals to depot == y[v]
            prob += pulp.lpSum(x[(i, d, v)] for (i, j, vv) in x if vv == v and j == d) == y[v]

        # MTZ subtour elimination + capacity (per vehicle)
        for v, info in self.vehicles.items():
            Q = info['capacity']
            for i in self.customers:
                for j in self.customers:
                    if i != j and (i, j, v) in x:
                        prob += u[(i, v)] - u[(j, v)] + Q * x[(i, j, v)] <= Q - self.demands[j]
            # bounds link to visit
            for c in self.customers:
                prob += u[(c, v)] >= self.demands[c] * pulp.lpSum(
                    x[(i, c, v)] for (i, j, vv) in x if vv == v and j == c
                )
                prob += u[(c, v)] <= Q

        # Solve
        prob.solve(pulp.PULP_CBC_CMD(msg=False))

        # ---- Debug arcs (optional) ----
        print("\n=== Active arcs ===")
        for (i, j, v), var in x.items():
            if var.value() == 1:
                print(f"Vehicle {v}: {i} -> {j}")

        # ---- Route reconstruction ----
        routes = []
        for v, info in self.vehicles.items():
            d = info['depot']
            arcs_v = {(i, j) for (i, j, vv) in x if vv == v and x[(i, j, v)].value() == 1}
            if not arcs_v:
                continue
            # chain from depot
            route = [d]
            current = d
            seen = set()
            while True:
                nexts = [j for (i, j) in arcs_v if i == current]
                if not nexts:
                    break
                nxt = nexts[0]
                route.append(nxt)
                if nxt in seen:
                    break
                seen.add(nxt)
                current = nxt
                if current == d:
                    break
            if len(route) > 1:
                routes.append({"vehicle": v, "route": route, "capacity": info['capacity']})

        return {
            "status": pulp.LpStatus[prob.status],
            "total_cost": pulp.value(prob.objective),
            "routes": routes
        }


# ---------------- Example usage ---------------- #
if __name__ == "__main__":
    depots = ["D1", "D2"]
    customers = ["C1", "C2", "C3", "C4"]

    demands = {"C1": 4, "C2": 6, "C3": 5, "C4": 7}

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

    solver = MDVRPHeterogeneous(dist, depots, customers, demands, vehicles)
    result = solver.solve()
    print("\n=== Final Result ===")
    print(result)
