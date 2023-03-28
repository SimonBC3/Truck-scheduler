from math import sqrt, pow, inf

import pyhop


def distance(c1, c2):
    x = pow(c1['X'] - c2['X'], 2)
    y = pow(c1['Y'] - c2['Y'], 2)
    return sqrt(x + y)


def select_new_city(state, currentLocation, goal):  # evaluation function
    best = inf  # big float
    for connection in state.roads.keys():
        if connection not in state.path and connection in state.roads[currentLocation]:
            currentCost = state.cost + \
                distance(state.coordinates[connection],
                         state.coordinates[goal])
            if currentCost < best:
                best_city = connection
                best = currentCost
    return best_city

def select_new_city_to_walk(state, currentLocation, goal):
    best = inf  # big float
    for connection in state.walkways.keys():
        if connection not in state.walkpath and connection in state.walkways[currentLocation]:
            currentCost = state.cost + \
                distance(state.coordinates[connection],
                         state.coordinates[goal])
            if currentCost < best:
                best_city = connection
                best = currentCost
    return best_city

def travel_op(state, truck, driver, selectedCity):
    currentTruckLocation = state.trucks[truck]['location']
    if state.drivers[driver]['location'] == 'in_truck' and selectedCity in state.roads[currentTruckLocation]:
        state.trucks[truck]['location'] = selectedCity
        state.path.append(selectedCity)
        state.cost += distance(
            state.coordinates[currentTruckLocation], state.coordinates[selectedCity])
        return state
    else:
        return False


def walk_op(state, driver, selectedCity):
    currentDrivertLocation = state.drivers[driver]['location']
    if currentDrivertLocation != 'in_truck' and selectedCity in state.walkways[currentDrivertLocation]:
        state.drivers[driver]['location'] = selectedCity
        state.walkpath.append(selectedCity)
        return state
    return False


def load_truck_op(state, truck, driver):
    if state.drivers[driver]['location'] == state.trucks[truck]['location']:
        state.drivers[driver]['location'] = 'in_truck'
        return state
    return False


def unload_truck_op(state, driver, truck, goal):
    print('UNLOADED---------------------------------------  ')
    if goal.drivers[driver]['location'] == state.trucks[truck]['location'] and state.drivers[driver]['location'] == 'in_truck':
        state.drivers[driver]['location'] = state.trucks[truck]['location']
        return state
    else:
        return False


pyhop.declare_operators(travel_op, walk_op, load_truck_op, unload_truck_op)
print()
pyhop.print_operators()


def travel_m(state, goal, truck, driver):
    truckCurrentLocation = state.trucks[truck]['location']
    truckGoalLocation = goal.trucks[truck]['location']
    if truckCurrentLocation != truckGoalLocation:
        selectedCity = select_new_city(
            state, truckCurrentLocation, truckGoalLocation)
        return [('travel_op', truck, driver, selectedCity), ('travel_to_city', goal, truck, driver)]
    return False


def walk_to_truck(state, truck, driver):
    driverCurrentLocation = state.drivers[driver]['location']
    truckCurrentLocation = state.trucks[truck]['location']
    if driverCurrentLocation != truckCurrentLocation:
        selectedCity = select_new_city_to_walk(
            state, driverCurrentLocation, truckCurrentLocation)
        return [('walk_op', driver, selectedCity), ('travel_to_truck', truck, driver)]
    return False


def already_there(state, goal, truck, driver):
    if state.trucks[truck]['location'] == goal.trucks[truck]['location'] and state.drivers[driver]['location'] == 'in_truck':
        return []
    return False


def already_on_truck(state, truck, driver):
    if state.drivers[driver]['location'] == state.trucks[truck]['location'] and state.drivers[driver]['location']:
        return []
    return False


pyhop.declare_methods('travel_to_truck', walk_to_truck, already_on_truck)

pyhop.declare_methods('travel_to_city', travel_m, already_there)


def travel_by_truck(state, goal, truck):
    for driver in state.drivers:
        if state.drivers[driver]['location'] != goal.drivers[driver]['location']:
            return [('travel_to_truck', truck, driver), ('load_truck_op', truck, driver), ('travel_to_city', goal, truck, driver), ('unload_truck_op', driver, truck, goal)]
    return False


def travel_by_truck_t0(state, goal):
    return travel_by_truck(state, goal, 't0')


pyhop.declare_methods('travel', travel_by_truck_t0)
print()
pyhop.print_methods()

# INITIAL STATE

state1 = pyhop.State('state1')
state1.coordinates = {'Huelva': {'X': 25, 'Y': 275}, 'Cadiz': {'X': 200, 'Y': 50}, 'Sevilla': {'X': 250, 'Y': 325},
                      'Cordoba': {'X': 475, 'Y': 450}, 'Malaga': {'X': 550, 'Y': 100}, 'Jaen': {'X': 750, 'Y': 425},
                      'Granada': {'X': 800, 'Y': 250}, 'Almeria': {'X': 1000, 'Y': 150}, 'JerezDeLaFrontera': {'X': 225, 'Y': 300},
                      'Osuna': {'X': 300, 'Y': 300}, 'Alcaudete': {'X': 675, 'Y': 400}, 'Guadix': {'X': 900, 'Y': 350}}
state1.roads = {'Huelva': {'Sevilla'}, 'Sevilla': {'Cadiz', 'Huelva', 'Cordoba', 'Malaga'},
                'Cadiz': {'Sevilla', 'Malaga'}, 'Cordoba': {'Sevilla', 'Malaga', 'Jaen'},
                'Malaga': {'Cadiz', 'Huelva', 'Cordoba', 'Sevilla', 'Granada', 'Almeria'},
                'Jaen': {'Cordoba', 'Granada'}, 'Granada': {'Jaen', 'Malaga', 'Almeria'},
                'Almeria': {'Granada', 'Malaga'}}

state1.walkways = {'Huelva': {'JerezDeLaFrontera'}, 'Sevilla': {'JerezDeLaFrontera', 'Osuna'},
                   'Cadiz': {'JerezDeLaFrontera', 'Osuna'}, 'Cordoba': {'Alcaudete'},
                   'Malaga': {'Osuna', 'Alcaudete'},
                   'Jaen': {'Alcaudete', 'Guadix'}, 'Granada': {'Gaudix', 'Alcaudete'},
                   'Almeria': {'Guadix'}, 'JerezDeLaFrontera': {'Cadiz', 'Osuna', 'Huelva', 'Sevilla'},
                   'Osuna': {'JerezDeLaFrontera', 'Cadiz', 'Sevilla', 'Alcaudete', 'Malaga'},
                   'Alcaudete': {'Malaga', 'Osuna', 'Cordoba', 'Jaen', 'Granada'},
                   'Guadix': {'Granada', 'Jaen', 'Almeria'}}

#state1.paths = {}

# state1.buses = {'b0': {'location': 'Huelva', 'price': 3}, 'b1': {'location': 'Sevilla', 'price': 3},
#                'b2': {'location': 'Almeria'}, 'price': 3}

# state1.location_car = 'Huelva'

state1.packages = {'p1': {'location': 'Sevilla'}}

state1.drivers = {'d1': {'location': 'Jaen'}}
state1.trucks = {'t0': {'location': 'Cordoba'}}

state1.path = ['Cordoba']
state1.walkpath = ['Jaen']
state1.cost = 0

# GOAL
goal1 = pyhop.Goal('goal1')
goal1.packages = {'p1': {'location': 'Jaen'}}
goal1.drivers = {'d1': {'location': 'Sevilla'}}
goal1.trucks = {'t0': {'location': 'Sevilla'}}


# print('- If verbose=3, Pyhop also prints the intermediate states:')

result = pyhop.pyhop(state1, [('travel', goal1)], verbose=3)
