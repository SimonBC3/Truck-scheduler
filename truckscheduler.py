from math import sqrt, pow, inf

import pyhop


def distance(c1, c2):
    x = pow(c1['X'] - c2['X'], 2)
    y = pow(c1['Y'] - c2['Y'], 2)
    return sqrt(x + y)


def select_new_city(state, x, y):  # evaluation function
    best = inf  # big float
    for c in state.roads.keys():
        if c not in state.path and c in state.connection[x]:
            currentCost = state.cost + \
                distance(state.coordinates[c], state.coordinates[y])
            if currentCost < best:
                best_city = c
                best = currentCost
    return best_city


def travel_op(state, truck, y):
    x = state.trucks[truck]['location']
    d = distance(state.coordinates[x], state.coordinates[y])
    if state.location == 'in_car' and y in state.connection[x]:
        state.trucks[truck]['location'] = y
        state.path.append(y)
        state.cost += d
        return state
    else:
        return False


def load_truck_op(state, driver, truck):
    if state[driver]['location'] == truck['location']:
        state[driver]['location'] = 'in_truck'
        return state
    return False


pyhop.declare_operators(travel_op, load_truck_op, unload_car_op)
print()
pyhop.print_operators()


def travel_m(state, goal, truck):
    truckCurrentLocation = state.trucks[truck]['location']
    truckGoalLocation = goal.trucks[truck]['location']
    if truckCurrentLocation != truckGoalLocation:
        selectedCity = select_new_city(state, truckCurrentLocation, truckGoalLocation)
        #dunno if necesary
        g = pyhop.Goal('g')
        g.final = truckGoalLocation
        return [('travel_op', truck, selectedCity), ('travel_to_city', g, truck)]
    return False


def already_there(state, goal, truck):
    if state.trucks[truck]['location'] == goal.trucks[truck]['location']:
        return []
    return False


pyhop.declare_methods('travel_to_city', travel_m, already_there)


def travel_by_truck(state, goal, truck):
    for driver in state.drivers:
        if driver['location'] != goal.drivers[d]['location']:
            return [('load_truck_op', truck, driver), ('travel_to_city', goal, truck), ('unload_truck_op', truck)]
    return False


pyhop.declare_methods('travel', travel_by_truck)
print()
pyhop.print_methods()

# INITIAL STATE

state1 = pyhop.State('state1')
state1.coordinates = {'Huelva': {'X': 25, 'Y': 275}, 'Cadiz': {'X': 200, 'Y': 50}, 'Sevilla': {'X': 250, 'Y': 325},
                      'Cordoba': {'X': 475, 'Y': 450}, 'Malaga': {'X': 550, 'Y': 100}, 'Jaen': {'X': 750, 'Y': 425},
                      'Granada': {'X': 800, 'Y': 250}, 'Almeria': {'X': 1000, 'Y': 150}}
state1.roads = {'Huelva': {'Sevilla'}, 'Sevilla': {'Cadiz', 'Huelva', 'Cordoba', 'Malaga'},
                'Cadiz': {'Sevilla', 'Malaga'}, 'Cordoba': {'Sevilla', 'Malaga', 'Jaen'},
                'Malaga': {'Cadiz', 'Huelva', 'Cordoba', 'Sevilla', 'Granada', 'Almeria'},
                'Jaen': {'Cordoba', 'Granada'}, 'Granada': {'Jaen', 'Malaga', 'Almeria'},
                'Almeria': {'Granada', 'Malaga'}}

state1.paths = {}

# state1.buses = {'b0': {'location': 'Huelva', 'price': 3}, 'b1': {'location': 'Sevilla', 'price': 3},
#                'b2': {'location': 'Almeria'}, 'price': 3}

# state1.location_car = 'Huelva'
state1.trucks = {'t0': {'location': 'Cordoba'}}

state1.packages = {'p1': {'location': 'Sevilla'}}

state1.drivers = {'d1': {'location': 'Cordoba'}}

state1.path = ['Cordoba']
state1.cost = 0

# GOAL
goal1 = pyhop.Goal('goal1')
goal1.packages = {'p1': {'location': 'Jaen'}}
goal1.drivers = {'d1': {'location': 'Cordoba'}}
goal1.trucks = {'t0': {'location': 'Cordoba'}}


# print('- If verbose=3, Pyhop also prints the intermediate states:')

result = pyhop.pyhop(state1, [('travel', goal1)], verbose=3)
