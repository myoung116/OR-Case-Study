import gurobipy as gp
from gurobipy import GRB
import pandas as pd

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
demands_2012 = []
demands_2013 = []
demands_2014 = []
revenue_2012 = []
revenue_2013 = []
revenue_2014 = []
caps = {}
costs = []
dists_pc_arr = []
dists_cc_arr = []
changes = []
rates = [100, 50, 50, 50]

###Modifying to functional forms----------------------------------------------------
for i in range(len(custs)):
    demands_2012.append([])
    demands_2012[i] = df_demands[(df_demands['Customer ID'] == i+1) & (df_demands['Time Period'] == 2012)]['Demand'].values
    demands_2013.append([])
    demands_2013[i] = df_demands[(df_demands['Customer ID'] == i+1) & (df_demands['Time Period'] == 2013)]['Demand'].values
    demands_2014.append([])
    demands_2014[i] = df_demands[(df_demands['Customer ID'] == i+1) & (df_demands['Time Period'] == 2014)]['Demand'].values
    revenue_2012.append([])
    revenue_2012[i] = df_demands[(df_demands['Customer ID'] == i+1) & (df_demands['Time Period'] == 2012)]['Revenue'].values
    revenue_2013.append([])
    revenue_2013[i] = df_demands[(df_demands['Customer ID'] == i+1) & (df_demands['Time Period'] == 2013)]['Revenue'].values
    revenue_2014.append([])
    revenue_2014[i] = df_demands[(df_demands['Customer ID'] == i+1) & (df_demands['Time Period'] == 2014)]['Revenue'].values

for i in range(len(df_prods)):
    changes.append([])
    changes[i] = df_changes[(df_changes['Start Color'] == i+1)]['Time'].values

for i in range(len(plants)):
    dists_pc_arr.append([])    
    dists_pc_arr[i] = (df_pc_dists[df_pc_dists['Plants'] == i+1]['Distances'].values)

for i in range(len(custs)):
    dists_cc_arr.append([])
    dists_cc_arr[i] = (df_cc_dists[df_cc_dists['Customer ID 1'] == i+1]['Distance'].values)

for i in range(len(plants)):
    costs.append([])
    costs[i] = df_caps[df_caps['Plant ID'] == i+1]['Production Cost'].values

for i in range(len(df_prods)):
    changes[i] = df_changes[(df_changes['Start Color'] == i+1)]['Time'].values

caps = [[300000,0,0,0,0],[0,73000,0,0,0],[0,0,30000,0,0],[0,0,0,12000,6000]]

demands_2012 = [arr.tolist() for arr in demands_2012]
demands_2013 = [arr.tolist() for arr in demands_2013]
demands_2014 = [arr.tolist() for arr in demands_2014]
changes = [arr.tolist() for arr in changes]
costs = [arr.tolist() for arr in costs]
revenue_2012 = [arr.tolist() for arr in revenue_2012]
revenue_2013 = [arr.tolist() for arr in revenue_2013]
revenue_2014 = [arr.tolist() for arr in revenue_2014]
dists_pc_arr = [arr.tolist() for arr in dists_pc_arr]
dists_cc_arr = [arr.tolist() for arr in dists_cc_arr]

c = 2

m_2012 = gp.Model('Flow_2012')
m_2013 = gp.Model('Flow_2013')
m_2014 = gp.Model('Flow_2014')




##################################################################################
#Model building for 2012
##################################################################################
#### Variable Generation--------------------------------------------------------
x_2012 = {}
s_2012 = {}
t_2012 = {}
ot_2012 = {}
p_2012 = {}
pot_2012 = {}
for i in range(len(plants)):
    for j in range(len(custs)):
        x_2012[i,j] = m_2012.addVar(vtype = GRB.INTEGER, obj = 2*dists_pc_arr[i][j], lb = 0, name="x_2012_%d,%d" %(i,j))

for i in range(len(plants)):
    for j in range(len(custs)):
        for k in range(len(prods)):
            s_2012[i,j,k] = m_2012.addVar(vtype = GRB.CONTINUOUS, lb = 0, name="s_2012_%d,%d,%d" %(i,j,k))

for i in range(len(plants)):
    t_2012[i] = m_2012.addVar(vtype = GRB.CONTINUOUS, lb = 0, ub = 720)

for i in range(len(plants)):
    ot_2012[i] = m_2012.addVar(vtype = GRB.CONTINUOUS, lb = 0, ub = 360)

for i in range(len(plants)):
    for k in range(len(prods)):
        p_2012[i,k] = m_2012.addVar(vtype = GRB.CONTINUOUS, obj = costs[i][k], lb = 0, name = 'p_2012_%d,%d'%(i,k))

for i in range(len(plants)):
    for k in range(len(prods)):
        pot_2012[i,k] = m_2012.addVar(vtype = GRB.CONTINUOUS, obj = 1.5*costs[i][k], lb = 0, name = 'pot_2012_%d,%d'%(i,k))

m_2012.update()
### Constraint Generation-------------------------------------------------------
for j in range(len(custs)):
    for k in range(len(prods)):
        m_2012.addConstr((gp.quicksum(s_2012[i,j,k] for i in range(len(plants))) >= .25*demands_2012[j][k]), name = 'demand_%d%d'%(j,k))

for i in range(len(plants)):
    for j in range(len(custs)):
        m_2012.addConstr((gp.quicksum(s_2012[i,j,k] for k in range(len(prods))) <= 10*x_2012[i,j]), name = 'trucks_%d%d'%(i,j))

for i in range(len(plants)):
    for k in range(len(prods)):
        m_2012.addConstr((gp.quicksum(s_2012[i,j,k] for j in range(len(custs))) <= caps[i][k]), name = 'production_caps_%d%d'%(i,k))

for i in rangege(len(plants)):
    for k in range(len(prods)):
        m_2012.addConstr((gp.quicksum(s_2012[i,j,k] for j in range(len(custs))) <= (p_2012[i,k] + pot_2012[i,k])), name = 'costs_%d,%d'%(i,k))

for i in range(len(plants)):
    m_2012.addConstr((gp.quicksum(s_2012[i,j,k] for j in range(len(custs)) for k in range(len(prods))) <= rates[i]*(t_2012[i] + ot_2012[i])), name = 'time_%d'%i)

m_2012.update()

### Set Objective-----------------------------------------------------------------
m_2012.ModelSense = GRB.MINIMIZE
##################################################################################
#End Model building for 2012
##################################################################################




##################################################################################
#Model building for 2013
##################################################################################
#### Variable Generation--------------------------------------------------------
x_2013 = {}
s_2013 = {}
t_2013 = {}
ot_2013 = {}
p_2013 = {}
pot_2013 = {}
for i in range(len(plants)):
    for j in range(len(custs)):
        x_2013[i,j] = m_2013.addVar(vtype = GRB.INTEGER, obj = 2*dists_pc_arr[i][j], lb = 0, name="x_2013_%d,%d" %(i,j))

for i in range(len(plants)):
    for j in range(len(custs)):
        for k in range(len(prods)):
            s_2013[i,j,k] = m_2013.addVar(vtype = GRB.CONTINUOUS, lb = 0, name="s_2013_%d,%d,%d" %(i,j,k))

for i in range(len(plants)):
    t_2013[i] = m_2013.addVar(vtype = GRB.CONTINUOUS, lb = 0, ub = 720)

for i in range(len(plants)):
    ot_2013[i] = m_2013.addVar(vtype = GRB.CONTINUOUS, lb = 0, ub = 360) 

for i in range(len(plants)):
    for k in range(len(prods)):
        p_2013[i,k] = m_2013.addVar(vtype = GRB.CONTINUOUS, obj = costs[i][k], lb = 0, name = 'p_2013_%d,%d'%(i,k))

for i in range(len(plants)):
    for k in range(len(prods)):
        pot_2013[i,k] = m_2013.addVar(vtype = GRB.CONTINUOUS, obj = 1.5*costs[i][k], lb = 0, name = 'pot_2013_%d,%d'%(i,k))

m_2013.update()

### Constraint Generation-------------------------------------------------------
for j in range(len(custs)):
    for k in range(len(prods)):
        m_2013.addConstr((gp.quicksum(s_2013[i,j,k] for i in range(len(plants))) >= .25*demands_2013[j][k]), name = 'demand_%d%d'%(j,k))

for i in range(len(plants)):
    for j in range(len(custs)):
        m_2013.addConstr((gp.quicksum(s_2013[i,j,k] for k in range(len(prods))) <= 10*x_2013[i,j]), name = 'trucks_%d%d'%(i,j))

for i in range(len(plants)):
    for k in range(len(prods)):
        m_2013.addConstr((gp.quicksum(s_2013[i,j,k] for j in range(len(custs))) <= caps[i][k]), name = 'production_caps_%d%d'%(i,k))

for i in range(len(plants)):
    for k in range(len(prods)):
        m_2013.addConstr((gp.quicksum(s_2013[i,j,k] for j in range(len(custs))) <= (p_2013[i,k] + pot_2013[i,k])), name = 'costs_%d,%d'%(i,k))

for i in range(len(plants)):
    m_2013.addConstr((gp.quicksum(s_2013[i,j,k] for j in range(len(custs)) for k in range(len(prods))) <= rates[i]*(t_2013[i] + ot_2013[i])), name = 'time_%d'%i)

m_2013.update()

### Set Objective-----------------------------------------------------------------
m_2013.ModelSense = GRB.MINIMIZE
##################################################################################
#End Model building for 2013
##################################################################################




##################################################################################
#Model building for 2014
##################################################################################
#### Variable Generation--------------------------------------------------------
x_2014 = {}
s_2014 = {}
t_2014 = {}
ot_2014 = {}
p_2014 = {}
pot_2014 = {}
for i in range(len(plants)):
    for j in range(len(custs)):
        x_2014[i,j] = m_2014.addVar(vtype = GRB.INTEGER, obj = 2*dists_pc_arr[i][j], lb = 0, name="x_2014_%d,%d" %(i,j))

for i in range(len(plants)):
    for j in range(len(custs)):
        for k in range(len(prods)):
            s_2014[i,j,k] = m_2014.addVar(vtype = GRB.CONTINUOUS, lb = 0, name="s_2014_%d,%d,%d" %(i,j,k))

for i in range(len(plants)):
    t_2014[i] = m_2014.addVar(vtype = GRB.CONTINUOUS, lb = 0, ub = 720)

for i in range(len(plants)):
    ot_2014[i] = m_2014.addVar(vtype = GRB.CONTINUOUS, lb = 0, ub = 360) 

for i in range(len(plants)):
    for k in range(len(prods)):
        p_2014[i,k] = m_2014.addVar(vtype = GRB.CONTINUOUS, obj = costs[i][k], lb = 0, name = 'p_2014_%d,%d'%(i,k))

for i in range(len(plants)):
    for k in range(len(prods)):
        pot_2014[i,k] = m_2014.addVar(vtype = GRB.CONTINUOUS, obj = 1.5*costs[i][k], lb = 0, name = 'pot_2014_%d,%d'%(i,k))

m_2014.update()

### Constraint Generation-------------------------------------------------------
for j in range(len(custs)):
    for k in range(len(prods)):
        m_2014.addConstr((gp.quicksum(s_2014[i,j,k] for i in range(len(plants))) >= .25*demands_2014[j][k]), name = 'demand_%d%d'%(j,k))

for i in range(len(plants)):
    for j in range(len(custs)):
        m_2014.addConstr((gp.quicksum(s_2014[i,j,k] for k in range(len(prods))) <= 10*x_2014[i,j]), name = 'trucks_%d%d'%(i,j))

for i in range(len(plants)):
    for k in range(len(prods)):
        m_2014.addConstr((gp.quicksum(s_2014[i,j,k] for j in range(len(custs))) <= caps[i][k]), name = 'production_caps_%d%d'%(i,k))

for i in range(len(plants)):
    for k in range(len(prods)):
        m_2014.addConstr((gp.quicksum(s_2014[i,j,k] for j in range(len(custs))) <= (p_2014[i,k] + pot_2014[i,k])), name = 'costs_%d,%d'%(i,k))

for i in range(len(plants)):
    m_2014.addConstr((gp.quicksum(s_2014[i,j,k] for j in range(len(custs)) for k in range(len(prods))) <= rates[i]*(t_2014[i] + ot_2014[i])), name = 'time_%d'%i)

m_2014.update()

### Set Objective-----------------------------------------------------------------
m_2014.ModelSense = GRB.MINIMIZE
##################################################################################
#End Model building for 2014
##################################################################################





#Uncomment whichever model's optimizing command you would like to solve for
#if you would like details on a model, uncomment the for loops below the optimizing command

m_2012.optimize()
m_2012.write("m_in_2012.lp")
m_2012.write("m_in_2012.sol")
print('--------------------------------------------------------------------------------------------------------------------------------')
#for i in range(len(plants)):
#    for j in range(len(custs)):
#        print(x_2012[i,j].x)

#for i in range(len(plants)):
#    for j in range(len(custs)):
#       for k in range(len(prods)):
#           print(s_2012[i,j,k].x)

m_2013.optimize()
m_2013.write("m_in_2013.lp")
m_2013.write("m_in_2013.sol")
print('--------------------------------------------------------------------------------------------------------------------------------')
#for i in range(len(plants)):
#    for j in range(len(custs)):
#        print(x_2013[i,j].x)

#for i in range(len(plants)):
#    for j in range(len(custs)):
#       for k in range(len(prods)):
#           print(s_2013[i,j,k].x)

m_2014.optimize()
m_2014.write("m_in_2014.lp")
m_2014.write("m_in_2014.sol")
print('----------------------------------------------------------------------------------------------------------------------------------')
#for i in range(len(plants)):
#    for j in range(len(custs)):
#        print(x_2014[i,j].x)

#for i in range(len(plants)):
#    for j in range(len(custs)):
#       for k in range(len(prods)):
#           print(s_2014[i,j,k].x)
