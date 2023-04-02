from math import sqrt, pow, inf

import pyhop


def chooseByConnection(state):
    for driver in state.drivers:
        for truck in state.trucks:
           if state.trucks[truck]['location'] in state.sideways[state.drivers[driver]['location']]:
                return {'driver': driver, 'truck': truck}
    return {}

def chooseByDistance(state):
    bestDistance, bestDriver, bestTruck = inf
    for driver in state.drivers:
        for truck in state.trucks:
            currentDistance = distance(state.drivers[driver]['location'], state.trucks[truck]['location'])
            if currentDistance < bestDistance:
                bestDistance = currentDistance
                bestDistance = driver
                bestTruck = truck
    return {'driver': bestDriver, 'truck': bestTruck}

def distance(c1, c2):
    x = pow(c1['X'] - c2['X'], 2)
    y = pow(c1['Y'] - c2['Y'], 2)
    return sqrt(x + y)

def select_new_city(state, currentLocation, goal):  # evaluation function
    best = inf  # big float
    for connection in state.roads.keys():
        if connection in state.roads[currentLocation]:
            currentCost = state.cost + \
                distance(state.coordinates[connection],
                         state.coordinates[goal])
            if currentCost < best:
                best_city = connection
                best = currentCost
    return best_city


def select_new_city_sideway(state, currentLocation, goal):
    best = inf  # big float
    for connection in state.sideways.keys():
        if connection not in state.walkpath and connection in state.sideways[currentLocation]:
            currentCost = state.cost + \
                distance(state.coordinates[connection],
                         state.coordinates[goal])
            if currentCost < best:
                best_city = connection
                best = currentCost
    return best_city

def walk_op(state, driver, selectedCity):
    currentDrivertLocation = state.drivers[driver]['location']
    if currentDrivertLocation != 'in_truck' and selectedCity in state.sideways[currentDrivertLocation]:
        state.drivers[driver]['location'] = selectedCity
        state.walkpath.append(selectedCity)
        return state
    return False

def get_on_bus_op(state, driver):
    currentBus = ''
    for bus in state.buses:
        busLocation = state.buses[bus]['location']
        if busLocation == state.drivers[driver]['location']:
            state.buses[driver]['location'] = busLocation
            return bus
    return False

def travel_by_bus_op(state, bus, selectedCity):
    currentBusLocation = state.buses[bus]['location']
    if selectedCity in state.sideways[currentBusLocation]:
        state.buses[bus]['location']
        state.buspath.append(selectedCity)
        return state
    return False

def get_off_bus_op(state, bus, truck, driver):
    currentBusLocation = state.buses[bus]['location']
    if state.drivers[driver]['location'] == 'on_bus' and currentBusLocation == state.trucks[truck]['location']:
        state.drivers[driver]['location'] = currentBusLocation
        return state

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

def get_on_truck_op(state, truck, driver):
    if state.drivers[driver]['location'] == state.trucks[truck]['location']:
        state.drivers[driver]['location'] = 'in_truck'
        return state
    return False


def get_off_truck_op(state, driver, truck, goal):
    if goal.drivers[driver]['location'] == state.trucks[truck]['location'] and state.drivers[driver]['location'] == 'in_truck':
        state.drivers[driver]['location'] = state.trucks[truck]['location']
        return state
    else:
        return False


def gather_package_op(state, truck, package):
    if state.trucks[truck]['location'] == state.packages[package]['location']:
        state.packages[package]['location'] = 'in_truck'
        return state


def drop_package_op(state, goal, truck, package):
    truckLocation = state.trucks[truck]['location']
    if truckLocation == goal.packages[package]['location'] and state.packages[package]['location'] == 'in_truck':
        state.packages[package]['location'] = truckLocation
        return state


pyhop.declare_operators(travel_op, walk_op, get_on_truck_op,
                        get_off_truck_op, gather_package_op, drop_package_op, get_on_bus_op, travel_by_bus_op, get_off_bus_op)
print()
pyhop.print_operators()

def walk_to_truck(state, goal, truck, driver):
    driverCurrentLocation = state.drivers[driver]['location']
    truckCurrentLocation = state.trucks[truck]['location']
    if driverCurrentLocation != truckCurrentLocation:
        selectedCity = select_new_city_sideway(
            state, driverCurrentLocation, truckCurrentLocation)
        return [('walk_op', driver, selectedCity), ('travel_to_truck_on_foot', goal, truck, driver)]
    return travel_by_truck(state, goal, truck, driver)

def already_on_truck(state, goal, truck, driver):
    if state.drivers[driver]['location'] == state.trucks[truck]['location'] and state.drivers[driver]['location']:
        return []
    return False

def travel_by_bus(state, goal, truck, driver, bus):
    if bus == '':
        bus = get_on_bus_op(state, driver)
        print('---selectedbus----' + bus)
        return [('travel_by_bus', goal, truck, driver, bus)]
    
    busLocation = state.buses[bus]['location']
    truckLocation = state.trucks[truck]['location']

    if busLocation != truckLocation:
        selectedCity = select_new_city_sideway(state, busLocation, truckLocation)
        return [('travel_by_bus_op', bus, selectedCity )]
    else: 
        return [('get_off_bus_op', truck, driver, bus), travel_by_truck(state, goal, truck, driver)]

def travel_m(state, goal, truck, driver):
    truckCurrentLocation = state.trucks[truck]['location']
    truckGoalLocation = goal.trucks[truck]['location']
    if truckCurrentLocation != truckGoalLocation:
        selectedCity = select_new_city(
            state, truckCurrentLocation, truckGoalLocation)
        return [('travel_op', truck, driver, selectedCity), ('travel_to_city', goal, truck, driver)]
    return False

def travel_to_package_m(state, goal, truck, driver, package):
    truckCurrentLocation = state.trucks[truck]['location']
    packageLocation = state.packages[package]['location']
    if truckCurrentLocation != packageLocation:
        selectedCity = select_new_city(
            state, truckCurrentLocation, packageLocation)
        return [('travel_op', truck, driver, selectedCity), ('travel_to_package', state, truck, driver, package)]
    else:
        return [('gather_package_op', truck, package)]


def already_there(state, goal, truck, driver):
    if state.trucks[truck]['location'] == goal.trucks[truck]['location'] and state.drivers[driver]['location'] == 'in_truck':
        return []
    return False


def all_gathered(state, goal, truck, driver):
    for package in state.packages:
        currentPackageLocation = state.packages[package]['location']
        if (currentPackageLocation != 'in_truck' and (currentPackageLocation != goal.packages[package]['location'])):
            return [('travel_to_package', goal, truck, driver, package), ('retrieve_packages', goal, truck, driver)]
    return []


def all_delivered(state, goal, truck, driver):
    for package in state.packages:
        if (state.packages[package]['location'] == 'in_truck'):
            return [('deliver_package', goal, truck, driver, package), ('finish_delivery', goal, truck, driver)]
        else:
            return []


def deliver_package_m(state, goal, truck, driver, package):
    truckLocation = state.trucks[truck]['location']
    packageGoalLocation = goal.packages[package]['location']
    if (truckLocation != packageGoalLocation):
        selectedCity = select_new_city(
            state, truckLocation, packageGoalLocation)
        return [('travel_op', truck, driver, selectedCity), ('deliver_package', goal, truck, driver, package)]
    else:
        return [('drop_package_op', goal, truck, package)]


pyhop.declare_methods('travel_to_truck_on_foot', walk_to_truck, already_on_truck)
pyhop.declare_methods('travel_to_truck_by_bus', travel_by_bus)
pyhop.declare_methods('retrieve_packages', all_gathered)
pyhop.declare_methods('travel_to_package', travel_to_package_m)
pyhop.declare_methods('finish_delivery', all_delivered)
pyhop.declare_methods('deliver_package', deliver_package_m)
pyhop.declare_methods('travel_to_city', travel_m, already_there)


def travel_by_truck(state, goal, truck, driver):
    return [('get_on_truck_op', truck, driver), ('retrieve_packages', goal, truck, driver),
            ('finish_delivery', goal, truck, driver), ('travel_to_city', goal, truck, driver), ('get_off_truck_op', driver, truck, goal)]

def chooseVariables(state, goal):
    answer = chooseByConnection(state)
    if answer != {}:
        #walkToTruck
        return [('travel_to_truck_on_foot', goal, answer['truck'], answer['driver'])]
    
    answer = chooseByDistance(state)
    if answer != {}:
        #takeBusToTruck
        return [('travel_to_truck_by_bus', goal, answer['truck'], answer['driver'], '')]
    return False


pyhop.declare_methods('travel', chooseVariables)
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

state1.sideways = {'Huelva': {'JerezDeLaFrontera'}, 'Sevilla': {'JerezDeLaFrontera', 'Osuna'},
                   'Cadiz': {'JerezDeLaFrontera', 'Osuna'}, 'Cordoba': {'Alcaudete'},
                   'Malaga': {'Osuna', 'Alcaudete'},
                   'Jaen': {'Alcaudete', 'Guadix'}, 'Granada': {'Gaudix', 'Alcaudete'},
                   'Almeria': {'Guadix'}, 'JerezDeLaFrontera': {'Cadiz', 'Osuna', 'Huelva', 'Sevilla'},
                   'Osuna': {'JerezDeLaFrontera', 'Cadiz', 'Sevilla', 'Alcaudete', 'Malaga'},
                   'Alcaudete': {'Malaga', 'Osuna', 'Cordoba', 'Jaen', 'Granada'},
                   'Guadix': {'Granada', 'Jaen', 'Almeria'}}


state1.buses = {'b0': {'location': 'Huelva', 'price': 3}, 'b1': {'location': 'Cadiz', 'price': 3},
                'b2': {'location': 'Sevilla', 'price': 3}, 'b3': {'location': 'Cordoba', 'price': 3},
                'b4': {'location': 'Malaga', 'price': 3}, 'b5': {'location': 'Jaen', 'price': 3},
                'b5': {'location': 'Granada', 'price': 3}, 'b6': {'location': 'Almeria', 'price': 3}}

state1.packages = {'p1': {'location': 'Sevilla'}}

state1.drivers = {'d1': {'location': 'Sevilla'}, 'd2': {'location': 'Alcaudete'}}
state1.trucks = {'t0': {'location': 'Almeria'}, 't1': {'location': 'Cordoba'}}

state1.path = ['Cordoba']
state1.walkpath = ['Jaen']
state1.cost = 0

# GOAL
goal1 = pyhop.Goal('goal1')
goal1.packages = {'p1': {'location': 'Jaen'}}
goal1.drivers = {'d1': {'location': 'Sevilla'}, 'd2': {'location': 'Sevilla'}}
goal1.trucks = {'t0': {'location': 'Sevilla'}, 't1': {'location': 'Sevilla'}}


# print('- If verbose=3, Pyhop also prints the intermediate states:')

result = pyhop.pyhop(state1, [('travel', goal1)], verbose=3)
