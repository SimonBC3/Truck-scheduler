from math import sqrt, pow, inf

import pyhop


def distance(c1, c2):
    x = pow(c1['X'] - c2['X'], 2)
    y = pow(c1['Y'] - c2['Y'], 2)
    return sqrt(x + y)


def select_new_city(state, x, y):  # evaluation function
    best = inf  # big float
    for c in state.connection.keys():
        if c not in state.path and c in state.connection[x]:
            g = state.cost
            h = distance(state.coordinates[c], state.coordinates[y])
            if g + h < best:
                best_city = c
                best = g + h
    return best_city


def travel_op(state, car, y):  # we receive the car as parameter
    x = state.cars[car]['location']
    d = distance(state.coordinates[x], state.coordinates[y])
    if state.location == 'in_car' and y in state.connection[x] and state.cars[car]['fuel'] >= d:
        state.cars[car]['location'] = y
        state.path.append(y)
        state.cost += d
        state.cars[car]['fuel'] -= d
        return state
    else:
        return False


def load_car_op(state, car):
    if state.location == state.cars[car]['location']:
        state.location = 'in_car'
        return state
    else:
        return False


def unload_car_op(state, car):
    if state.location == 'in_car':
        state.location = state.cars[car]['location']
        return state
    else:
        return False


pyhop.declare_operators(travel_op, load_car_op, unload_car_op)
print()
pyhop.print_operators()


def travel_m(state, goal, car):
    x = state.cars[car]['location']
    y = goal.final
    if x != y:
        z = select_new_city(state, x, y)
        g = pyhop.Goal('g')
        g.final = y
        return [('travel_op', car, z), ('travel_to_city', g, car)]
    return False


def already_there(state, goal, car):
    x = state.cars[car]['location']
    y = goal.final
    if x == y:
        return []
    return False


pyhop.declare_methods('travel_to_city', travel_m, already_there)


def travel_by_car(state, goal, car):
    x = state.location
    y = goal.final
    if x != y:
        return [('load_car_op', car), ('travel_to_city', goal, car), ('unload_car_op', car)]
    return False


def travel_by_car_c0(state, goal):
    return travel_by_car(state, goal, 'c0')


def travel_by_car_c1(state, goal):
    return travel_by_car(state, goal, 'c1')


def travel_by_car_c2(state, goal):
    return travel_by_car(state, goal, 'c2')


pyhop.declare_methods('travel', travel_by_car_c0, travel_by_car_c1, travel_by_car_c2)
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

state1.buses = {'b0': {'location': 'Huelva', 'price': 3}, 'b1': {'location': 'Huelva', 'price': 3},
               'b2': {'location': 'Huelva'}, 'price': 3}
state1.location = 'Huelva'
# state1.location_car = 'Huelva'
state1.trucks = {'t0': {'location': 'Huelva'}, 't1': {'location': 'Huelva'},
               't2': {'location': 'Huelva'}}

state1.package = {'p1': {'Huelva'}, 'p2': {'Huelva'}, 'p3': {'Huelva'}}

state1.drivers = {'d1':{'location': 'Cordoba'}, 'd2':{'location': 'Cadiz'}}

state1.path = ['Huelva']
state1.cost = 0

# GOAL
goal1 = pyhop.Goal('goal1')
goal1.final = 'Almeria'

# print('- If verbose=3, Pyhop also prints the intermediate states:')

result = pyhop.pyhop(state1, [('travel', goal1)], verbose=3)
