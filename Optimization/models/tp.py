from pulp import *
import numpy as np
from typing import Dict, List, Any, Optional

class transportationProblem:
    def __init__(self, costMatrix, demand, supply):
        self.costMatrix = costMatrix
        self.demand = demand
        self.supply = supply
        self.solution = None
        self.x = None 

    def get_cost_dict(self):
        return makeDict([self.supply.keys(), self.demand.keys()], self.costMatrix, 0)

    def solve(self):
        prob = LpProblem("Transportation Problem", LpMinimize)
        self.prob = prob

        self.x = LpVariable.dicts(
            "x",
            ((i, j) for i in self.supply.keys() for j in self.demand.keys()),
            0,
            None,
            LpInteger
        )

        routes = [(i, j) for i in self.supply.keys() for j in self.demand.keys()]
        costs = self.get_cost_dict()

        prob += lpSum([costs[i][j] * self.x[i, j] for (i, j) in routes])

        for i in self.supply.keys():
            prob += lpSum([self.x[i, j] for j in self.demand.keys()]) <= self.supply[i]

        for j in self.demand.keys():
            prob += lpSum([self.x[i, j] for i in self.supply.keys()]) == self.demand[j]

        prob.solve()
        self.solution = prob

    def get_solution_json(self):
        solution = {
            "status": LpStatus[self.prob.status],
            "total_cost": value(self.prob.objective),
            "shipments": []
        }

        for i in self.supply.keys():
            for j in self.demand.keys():
                var = self.x[i, j]
                if var.varValue > 0:
                    solution["shipments"].append({
                        "from": i,
                        "to": j,
                        "quantity": int(var.varValue)
                    })
        return solution
