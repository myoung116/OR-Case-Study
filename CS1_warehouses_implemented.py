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
changes = []
dists_pc_arr = []
dists_cc_arr = []
rates = [100, 50, 50, 50]


###Modifying to functional forms----------------------------------------------------
for i in range(len(custs)):
    demands_2012.append([])
    demands_2013.append([])
    demands_2014.append([])
    revenue_2012.append([])
    revenue_2013.append([])
    revenue_2014.append([])
    dists_cc_arr.append([])

for j in range(len(plants)):
    dists_pc_arr.append([])

for i in range(len(df_prods)):
    changes.append([])

for i in range(1,51):
    demands_2012[i-1] = df_demands[(df_demands['Customer ID'] == i) & (df_demands['Time Period'] == 2012)]['Demand'].values
    revenue_2012[i-1] = df_demands[(df_demands['Customer ID'] == i) & (df_demands['Time Period'] == 2012)]['Revenue'].values
    demands_2013[i-1] = df_demands[(df_demands['Customer ID'] == i) & (df_demands['Time Period'] == 2013)]['Demand'].values
    revenue_2013[i-1] = df_demands[(df_demands['Customer ID'] == i) & (df_demands['Time Period'] == 2013)]['Revenue'].values
    demands_2014[i-1] = df_demands[(df_demands['Customer ID'] == i) & (df_demands['Time Period'] == 2014)]['Demand'].values
    revenue_2014[i-1] = df_demands[(df_demands['Customer ID'] == i) & (df_demands['Time Period'] == 2014)]['Revenue'].values

for i in range(len(plants)):
    dists_pc_arr[i] = (df_pc_dists[df_pc_dists['Plants'] == i+1]['Distances'].values)

for i in range(len(custs)):
    dists_cc_arr[i] = (df_cc_dists[df_cc_dists['Customer ID 1'] == i+1]['Distance'].values)

for i in range(len(df_prods)):
    changes[i] = df_changes[(df_changes['Start Color'] == i+1)]['Time'].values

for i in range(len(plants)):
    costs.append([])
    costs[i] = df_caps[df_caps['Plant ID'] == i+1]['Production Cost'].values

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
wh = [0,0,0,0,0,0,0,1,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]   #wh is the vector of warehouses resulting from CS1_warehouses.py



##################################################################################
#Create the models
##################################################################################
m_2012 = gp.Model('Flow_with_wh_2012')
m_2013 = gp.Model('Flow_with_wh_2013')
m_2014 = gp.Model('Flow_with_wh_2014')

##################################################################################
#Model building for 2012
##################################################################################
#### Variable Generation--------------------------------------------------------
x_2012 = {} #trucks from plants to custs
y_2012 = {} #trucks from plants to warehouses
z_2012 = {} #trucks from warehouses to custs
u_2012 = {} #tons of products from plants to customers
v_2012 = {} #tons of products from plants to warehouses
w_2012 = {} #tons of products from warehouses to customers
t_2012 = {}
ot_2012 = {}
p_2012 = {}
pot_2012 = {}
for i in range(len(plants)):
    for j in range(len(custs)):
        x_2012[i,j] = m_2012.addVar(vtype = GRB.INTEGER, obj = 2*dists_pc_arr[i][j], name="x_2012_%d,%d" %(i,j))

for i in range(len(plants)):
    for h in range(len(wh)):
        y_2012[i,h] = m_2012.addVar(vtype = GRB.INTEGER, obj = 2*dists_pc_arr[i][h], name="y_2012_%d,%d" %(i,h))

for h in range(len(wh)):
    for j in range(len(custs)):
        z_2012[h,j] = m_2012.addVar(vtype = GRB.INTEGER, obj = 2*dists_cc_arr[h][j], name="z_2012_%d,%d" %(h,j))

for i in range(len(plants)):
    for j in range(len(custs)):
        for k in range(len(prods)):
            u_2012[i,j,k] = m_2012.addVar(vtype = GRB.CONTINUOUS, name="u_2012_%d,%d,%d" %(i,j,k))

for i in range(len(plants)):
    for h in range(len(wh)):
        for k in range(len(prods)):
            v_2012[i,h,k] = m_2012.addVar(vtype = GRB.CONTINUOUS, name="v_2012_%d,%d,%d" %(i,h,k))

for h in range(len(wh)):
    for j in range(len(custs)):
        for k in range(len(prods)):
            w_2012[h,j,k] = m_2012.addVar(vtype = GRB.CONTINUOUS, name="w_2012_%d,%d,%d" %(h,j,k))

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
        m_2012.addConstr((gp.quicksum(u_2012[i,j,k] for i in range(len(plants))) + gp.quicksum(w_2012[h, j, k] for h in range(len(wh))) >= .25*demands_2012[j][k]), name = "demand_2012_%d,%d"%(j,k))

for h in range(len(wh)):
    for k in range(len(prods)):
        m_2012.addConstr((gp.quicksum(w_2012[h,j,k] for j in range(len(custs))) <= gp.quicksum(v_2012[i,h,k] for i in range(len(plants)))), name = 'supply_2012_%d,%d'%(h,k))

for i in range(len(plants)):
    for j in range(len(custs)):
        m_2012.addConstr((gp.quicksum(u_2012[i,j,k] for k in range(len(prods))) <= 10*x_2012[i,j]), name = 'trucks_pc_%d%d'%(i,j))

for i in range(len(plants)):
    for h in range(len(wh)):
        m_2012.addConstr((gp.quicksum(v_2012[i,h,k] for k in range(len(prods))) <= 10*y_2012[i,h]), name = 'trucks_pwh_%d%d'%(i,h))

for h in range(len(wh)):
    for j in range(len(custs)):
        m_2012.addConstr((gp.quicksum(w_2012[h,j,k] for k in range(len(prods))) <= 10*z_2012[h,j]), name = 'trucks_whc_%d%d'%(h,j))

for i in range(len(plants)):
    for k in range(len(prods)):
        m_2012.addConstr((gp.quicksum(u_2012[i,j,k] for j in range(len(custs))) + gp.quicksum(v_2012[i, h, k] for h in range(len(wh))) <= caps[i][k]), name = 'production_caps_2012_%d,%d'%(i,k))

for h in range(len(wh)):
    m_2012.addConstr((gp.quicksum(w_2012[h,j,k] for j in range(len(custs)) for k in range(len(prods))) <=  gp.quicksum(w_2012[h,j,k] for j in range(len(custs)) for k in range(len(prods)))*wh[h]), name = 'warehouse_2012_%d'%h)

for i in range(len(plants)):
    for k in range(len(prods)):
        m_2012.addConstr((gp.quicksum(u_2012[i,j,k] for j in range(len(custs))) + gp.quicksum(v_2012[i, h, k] for h in range(len(wh))) <= (p_2012[i,k] + pot_2012[i,k])), name = 'costs_%d,%d'%(i,k))

for i in range(len(plants)):
    m_2012.addConstr((gp.quicksum(u_2012[i,j,k] for j in range(len(custs)) for k in range(len(prods))) + gp.quicksum(v_2012[i, h, k] for h in range(len(wh)) for k in range(len(prods))) <= rates[i]*(t_2012[i] + ot_2012[i])), name = 'time_%d'%i)

m_2012.update()
### Set Objective----------------------------------------------------------------- 
m_2012.ModelSense = GRB.MINIMIZE
m_2012.Params.MIPGap = 0.0005

###################################################################################
#End Model for 2012
###################################################################################






##################################################################################
#Model building for 2013
##################################################################################
#### Variable Generation--------------------------------------------------------
x_2013 = {} #trucks from plants to custs
y_2013 = {} #trucks from plants to warehouses
z_2013 = {} #trucks from warehouses to custs
u_2013 = {} #tons of products from plants to customers
v_2013 = {} #tons of products from plants to warehouses
w_2013 = {} #tons of products from warehouses to customers
t_2013 = {}
ot_2013 = {}
p_2013 = {}
pot_2013 = {}
for i in range(len(plants)):
    for j in range(len(custs)):
        x_2013[i,j] = m_2013.addVar(vtype = GRB.INTEGER, obj = dists_pc_arr[i][j], name="x_2013_%d,%d" %(i,j))

for i in range(len(plants)):
    for h in range(len(wh)):
        y_2013[i,h] = m_2013.addVar(vtype = GRB.INTEGER, obj = dists_pc_arr[i][h], name="y_2013_%d,%d" %(i,h))

for h in range(len(wh)):
    for j in range(len(custs)):
        z_2013[h,j] = m_2013.addVar(vtype = GRB.INTEGER, obj = dists_cc_arr[h][j], name="z_2013_%d,%d" %(h,j))

for i in range(len(plants)):
    for j in range(len(custs)):
        for k in range(len(prods)):
            u_2013[i,j,k] = m_2013.addVar(vtype = GRB.CONTINUOUS, name="u_2013_%d,%d,%d" %(i,j,k))

for i in range(len(plants)):
    for h in range(len(wh)):
        for k in range(len(prods)):
            v_2013[i,h,k] = m_2013.addVar(vtype = GRB.CONTINUOUS, name="v_2013_%d,%d,%d" %(i,h,k))

for h in range(len(wh)):
    for j in range(len(custs)):
        for k in range(len(prods)):
            w_2013[h,j,k] = m_2013.addVar(vtype = GRB.CONTINUOUS, name="w_2013_%d,%d,%d" %(h,j,k))

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
        m_2013.addConstr((gp.quicksum(u_2013[i,j,k] for i in range(len(plants))) + gp.quicksum(w_2013[h, j, k] for h in range(len(wh))) >= .25*demands_2013[j][k]), name = "demand_2013_%d,%d"%(j,k))

for h in range(len(wh)):
    for k in range(len(prods)):
        m_2013.addConstr((gp.quicksum(w_2013[h,j,k] for j in range(len(custs))) <= gp.quicksum(v_2013[i,h,k] for i in range(len(plants)))), name = 'supply_2013_%d,%d'%(h,k))

for i in range(len(plants)):
    for j in range(len(custs)):
        m_2013.addConstr((gp.quicksum(u_2013[i,j,k] for k in range(len(prods))) <= 10*x_2013[i,j]), name = 'trucks_pc_2013_%d%d'%(i,j))

for i in range(len(plants)):
    for h in range(len(wh)):
        m_2013.addConstr((gp.quicksum(v_2013[i,h,k] for k in range(len(prods))) <= 10*y_2013[i,h]), name = 'trucks_pwh_2013_%d%d'%(i,h))

for h in range(len(wh)):
    for j in range(len(custs)):
        m_2013.addConstr((gp.quicksum(w_2013[h,j,k] for k in range(len(prods))) <= 10*z_2013[h,j]), name = 'trucks_whc_2013_%d%d'%(h,j))

for i in range(len(plants)):
    for k in range(len(prods)):
        m_2013.addConstr((gp.quicksum(u_2013[i,j,k] for j in range(len(custs))) + gp.quicksum(v_2013[i, h, k] for h in range(len(wh))) <= caps[i][k]), name = 'production_caps_2013_%d,%d'%(i,k))

for h in range(len(wh)):
    m_2013.addConstr((gp.quicksum(w_2013[h,j,k] for j in range(len(custs)) for k in range(len(prods))) <=  gp.quicksum(w_2013[h,j,k] for j in range(len(custs)) for k in range(len(prods)))*wh[h]), name = 'warehouse_2013_%d'%h)

for i in range(len(plants)):
    for k in range(len(prods)):
        m_2013.addConstr((gp.quicksum(u_2013[i,j,k] for j in range(len(custs))) + gp.quicksum(v_2013[i, h, k] for h in range(len(wh))) <= (p_2013[i,k] + pot_2013[i,k])), name = 'costs_%d,%d'%(i,k))

for i in range(len(plants)):
    m_2013.addConstr((gp.quicksum(u_2013[i,j,k] for j in range(len(custs)) for k in range(len(prods))) + gp.quicksum(v_2013[i, h, k] for h in range(len(wh)) for k in range(len(prods))) <= rates[i]*(t_2013[i] + ot_2013[i])), name = 'time_%d'%i)

m_2013.update()

### Set Objective----------------------------------------------------------------- 
m_2013.ModelSense = GRB.MINIMIZE
m_2013.Params.MIPGap = 0.0005
###################################################################################
#End Model for 2013
###################################################################################




##################################################################################
#Model building for 2014
##################################################################################
#### Variable Generation--------------------------------------------------------
x_2014 = {} #trucks from plants to custs
y_2014 = {} #trucks from plants to warehouses
z_2014 = {} #trucks from warehouses to custs
u_2014 = {} #tons of products from plants to customers
v_2014 = {} #tons of products from plants to warehouses
w_2014 = {} #tons of products from warehouses to customers
t_2014 = {}
ot_2014 = {}
p_2014 = {}
pot_2014 = {}
for i in range(len(plants)):
    for j in range(len(custs)):
        x_2014[i,j] = m_2014.addVar(vtype = GRB.INTEGER, obj = dists_pc_arr[i][j], name="x_2014_%d,%d" %(i,j))

for i in range(len(plants)):
    for h in range(len(wh)):
        y_2014[i,h] = m_2014.addVar(vtype = GRB.INTEGER, obj = dists_pc_arr[i][h], name="y_2014_%d,%d" %(i,h))

for h in range(len(wh)):
    for j in range(len(custs)):
        z_2014[h,j] = m_2014.addVar(vtype = GRB.INTEGER, obj = dists_cc_arr[h][j], name="z_2014_%d,%d" %(h,j))

for i in range(len(plants)):
    for j in range(len(custs)):
        for k in range(len(prods)):
            u_2014[i,j,k] = m_2014.addVar(vtype = GRB.CONTINUOUS, name="u_2014_%d,%d,%d" %(i,j,k))

for i in range(len(plants)):
    for h in range(len(wh)):
        for k in range(len(prods)):
            v_2014[i,h,k] = m_2014.addVar(vtype = GRB.CONTINUOUS, name="v_2014_%d,%d,%d" %(i,h,k))

for h in range(len(wh)):
    for j in range(len(custs)):
        for k in range(len(prods)):
            w_2014[h,j,k] = m_2014.addVar(vtype = GRB.CONTINUOUS, name="w_2014_%d,%d,%d" %(h,j,k))

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
        m_2014.addConstr((gp.quicksum(u_2014[i,j,k] for i in range(len(plants))) + gp.quicksum(w_2014[h, j, k] for h in range(len(wh))) >= .25*demands_2014[j][k]), name = "demand_2014_%d,%d"%(j,k))

for h in range(len(wh)):
    for k in range(len(prods)):
        m_2014.addConstr((gp.quicksum(w_2014[h,j,k] for j in range(len(custs))) <= gp.quicksum(v_2014[i,h,k] for i in range(len(plants)))), name = 'supply_2014_%d,%d'%(h,k))

for i in range(len(plants)):
    for j in range(len(custs)):
        m_2014.addConstr((gp.quicksum(u_2014[i,j,k] for k in range(len(prods))) <= 10*x_2014[i,j]), name = 'trucks_pc_2014_%d%d'%(i,j))

for i in range(len(plants)):
    for h in range(len(wh)):
        m_2014.addConstr((gp.quicksum(v_2014[i,h,k] for k in range(len(prods))) <= 10*y_2014[i,h]), name = 'trucks_pwh_2014_%d%d'%(i,h))

for h in range(len(wh)):
    for j in range(len(custs)):
        m_2014.addConstr((gp.quicksum(w_2014[h,j,k] for k in range(len(prods))) <= 10*z_2014[h,j]), name = 'trucks_whc_2014_%d%d'%(h,j))

for i in range(len(plants)):
    for k in range(len(prods)):
        m_2014.addConstr((gp.quicksum(u_2014[i,j,k] for j in range(len(custs))) + gp.quicksum(v_2014[i, h, k] for h in range(len(wh))) <= caps[i][k]), name = 'production_caps_2014_%d,%d'%(i,k))

for h in range(len(wh)):
    m_2014.addConstr((gp.quicksum(w_2014[h,j,k] for j in range(len(custs)) for k in range(len(prods))) <=  gp.quicksum(w_2014[h,j,k] for j in range(len(custs)) for k in range(len(prods)))*wh[h]), name = 'warehouse_2014_%d'%h)

for i in range(len(plants)):
    for k in range(len(prods)):
        m_2014.addConstr((gp.quicksum(u_2014[i,j,k] for j in range(len(custs))) + gp.quicksum(v_2014[i, h, k] for h in range(len(wh))) <= (p_2014[i,k] + pot_2014[i,k])), name = 'costs_%d,%d'%(i,k))

for i in range(len(plants)):
    m_2014.addConstr((gp.quicksum(u_2014[i,j,k] for j in range(len(custs)) for k in range(len(prods))) + gp.quicksum(v_2014[i, h, k] for h in range(len(wh)) for k in range(len(prods))) <= rates[i]*(t_2014[i] + ot_2014[i])), name = 'time_%d'%i)

m_2014.update()
### Set Objective----------------------------------------------------------------- 
m_2014.ModelSense = GRB.MINIMIZE
m_2014.Params.MIPGap = 0.0005
###################################################################################
#End Model for 2014
###################################################################################





#Uncomment the desired model year to run and view the resulting solutions by uncommenting the respective variable functions. 

m_2012.optimize()
m_2012.write("m_wh_imp_2012.lp")
m_2012.write("m_wh_imp_2012.sol")
print('--------------------------------------------------------------------------------------------------------------------------------')
#for i in range(len(plants)):
#    for j in range(len(custs)):
#        print(x_2012[i,j].x)

#for i in range(len(plants)):
#    for h in range(len(wh)):
#        print(y_2012[i,h].x)

#for h in range(len(wh)):
#    for j in range(len(custs)):
#       print(z_2012[j,j].x) 



#m_2013.optimize()
#m_2013.write("m_wh_imp_2013.lp")
#m_2013.write("m_wh_imp_2013.sol")
print('--------------------------------------------------------------------------------------------------------------------------------')
#for i in range(len(plants)):
#    for j in range(len(custs)):
#        print(x_2013[i,j].x)

#for i in range(len(plants)):
#    for h in range(len(wh)):
#        print(y_2013[i,h].x)

#for h in range(len(wh)):
#    for j in range(len(custs)):
#       print(z_2013[j,j].x)        





#m_2014.optimize()
#m_2014.write("m_wh_imp_2014.lp")
#m_2014.write("m_wh_imp_2014.sol")
print('--------------------------------------------------------------------------------------------------------------------------------')
#for i in range(len(plants)):
#    for j in range(len(custs)):
#        print(x_2014[i,j].x)

#for i in range(len(plants)):
#    for h in range(len(wh)):
#        print(y_2014[i,h].x)

#for h in range(len(wh)):
#    for j in range(len(custs)):
#       print(z_2014[j,j].x)    
