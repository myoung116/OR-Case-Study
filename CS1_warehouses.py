import gurobipy as gp
from gurobipy import GRB
import pandas as pd
import numpy as np

### Importing Data--------------------------------------------------------------------------
df_plants = pd.read_excel(FilePath)
df_custs = pd.read_excel(FilePath)
df_prods = pd.read_excel(FilePath)
df_demands = pd.read_excel(FilePath)
df_caps = pd.read_excel(FilePath)
df_dists = pd.read_excel(FilePath)
df_changes = pd.read_excel(FilePath)
df_pc_dists = df_dists.iloc[:, [0,1,2]]
df_cc_dists = df_dists.iloc[:, [4,5,6]]

plants = list(range(1,5))
custs = list(range(1,51))
prods = list(range(1,6))
demands = []
dists_cc = []
coverage = []
demand_t = []


###Modifying to functional forms----------------------------------------------------
for i in range(150):
    demands.append([])
for j in range(1,51):
    dists_cc.append([])
    coverage.append([])
    demand_t.append([])

for i in range(1,51):
    demands[i-1] = df_demands[(df_demands['Customer ID'] == i) & (df_demands['Time Period'] == 2012)]['Demand'].values
    demands[i+49] = df_demands[(df_demands['Customer ID'] == i) & (df_demands['Time Period'] == 2013)]['Demand'].values
    demands[i+99] = df_demands[(df_demands['Customer ID'] == i) & (df_demands['Time Period'] == 2014)]['Demand'].values

for i in range(1,51):
    dists_cc[i-1] = df_cc_dists[df_cc_dists['Customer ID 1'] == i]['Distance'].values
    coverage[i-1] = df_cc_dists[(df_cc_dists['Customer ID 2'] == i) & (df_cc_dists['Distance'] <= 500)]['Customer ID 1'].values
    demand_t[i-1] = sum(df_demands[(df_demands['Customer ID'] == i)]['Demand'].values)

demands = [arr.tolist() for arr in demands]
dists_cc = [arr.tolist() for arr in dists_cc]
coverage = [arr.tolist() for arr in coverage]
#### Variable Generation--------------------------------------------------------
m = gp.Model('Warehouses')

x = {}
z = {}
for j in range(len(custs)):
    x[j] = m.addVar(vtype = GRB.BINARY, name="x_%d" %j)

for j in range(len(custs)):
    z[j] = m.addVar(obj = 1, vtype = GRB.BINARY, name="z_%d" %j)

m.update()

### Constraint Generation-------------------------------------------------------
for i in range(len(custs)):
    m.addConstr((gp.quicksum(z[j-1] for j in coverage[i]) >= x[i]), name = 'covered_by_%d'%i)

    
m.addConstr(gp.quicksum(x[j]*demand_t[j] for j in range(len(custs))) >= 1247186.054*.8, name = "budget")

m.update()

### Set Objective-----------------------------------------------------------------
m.ModelSense = GRB.MINIMIZE

m.optimize()
m.write("m_wh.lp")
m.write("m_wh.sol")


#for j in range(len(custs)):
#    print("x_{}: {}".format(j,x[j].x))

for j in range(len(custs)):
    print("z_{}: {}".format(j,z[j].x))
