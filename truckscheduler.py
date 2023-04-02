from math import sqrt, pow, inf

import pyhop
import argparse

TRUCK_VALID_POSITIONS = ["Huelva", "Cadiz", "Sevilla",
                         "Cordoba", "Malaga", "Jaen", "Granada", "Almeria"]
ALL_CITIES = ["Huelva", "Cadiz", "Sevilla",
              "Cordoba", "Malaga", "Jaen", "Granada", "Almeria", "JerezDeLaFrontera", "Osuna", "Guadix", "Alcaudete"]


def choose_by_connection(state):
    for driver in state.drivers:
        for truck in state.trucks:
            if state.trucks[truck]['location'] in state.sideways[state.drivers[driver]['location']]:
                return {'driver': driver, 'truck': truck}
    return {}


def choose_by_distance(state):
    bestDistance = 0.0
    bestDriver = ''
    bestTruck = ''
    for driver in state.drivers:
        for truck in state.trucks:
            driverLocation = state.drivers[driver]['location']
            truckLocation = state.trucks[truck]['location']
            currentDistance = distance(
                state.coordinates[driverLocation], state.coordinates[truckLocation])
            if bestDistance == 0:
                bestDistance = currentDistance
                bestDriver = driver
                bestTruck = truck
            else:
                if currentDistance < bestDistance:
                    bestDistance = currentDistance
                    bestDriver = driver
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
    if state.walkpath == []:
        state.walkpath.append(currentDrivertLocation)
    if currentDrivertLocation != 'in_truck' and selectedCity in state.sideways[currentDrivertLocation]:
        state.drivers[driver]['location'] = selectedCity
        state.walkpath.append(selectedCity)
        return state
    return False


def get_on_bus_op(state, driver):
    for bus in state.buses:
        if state.buses[bus]['location'] == state.drivers[driver]['location']:
            state.buspath.append(state.drivers[driver]['location'])
            state.drivers[driver]['location'] = 'on_bus'
            return bus
    return False


def travel_by_bus_op(state, bus, selectedCity):
    currentBusLocation = state.buses[bus]['location']
    if selectedCity in state.sideways[currentBusLocation]:
        state.buses[bus]['location'] = selectedCity
        state.buspath.append(selectedCity)
        return state
    return False


def get_off_bus_op(state, truck, driver, bus):
    currentBusLocation = state.buses[bus]['location']
    if state.drivers[driver]['location'] == 'on_bus' and currentBusLocation == state.trucks[truck]['location']:
        state.drivers[driver]['location'] = currentBusLocation
        return state


def travel_op(state, truck, driver, selectedCity):
    currentTruckLocation = state.trucks[truck]['location']
    if state.path == []:
        state.path.append(currentTruckLocation)
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


def walk_to_truck(state, goal, truck, driver):
    driverCurrentLocation = state.drivers[driver]['location']
    truckCurrentLocation = state.trucks[truck]['location']
    if driverCurrentLocation != truckCurrentLocation:
        selectedCity = select_new_city_sideway(
            state, driverCurrentLocation, truckCurrentLocation)
        return [('walk_op', driver, selectedCity), ('travel_to_truck_on_foot', goal, truck, driver)]
    return [('start_delivery', goal, truck, driver)]


def already_on_truck(state, goal, truck, driver):
    if state.drivers[driver]['location'] == state.trucks[truck]['location'] and state.drivers[driver]['location']:
        return []
    return False


def travel_by_bus(state, goal, truck, driver, bus):
    if bus == '':
        bus = get_on_bus_op(state, driver)
        print('---selectedbus----' + bus)
        return [('travel_to_truck_by_bus', goal, truck, driver, bus)]

    busLocation = state.buses[bus]['location']
    truckLocation = state.trucks[truck]['location']

    if busLocation != truckLocation:
        selectedCity = select_new_city_sideway(
            state, busLocation, truckLocation)
        return [('travel_by_bus_op', bus, selectedCity), ('travel_to_truck_by_bus', goal, truck, driver, bus)]
    else:
        return [('get_off_bus_op', truck, driver, bus), ('start_delivery', goal, truck, driver)]


def travel_by_truck(state, goal, truck, driver):
    return [('get_on_truck_op', truck, driver), ('all_gathered', goal, truck, driver),
            ('finish_delivery', goal, truck, driver), ('travel_to_city', goal, truck, driver), ('get_off_truck_op', driver, truck, goal)]


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
            return [('travel_to_package', goal, truck, driver, package), ('all_gathered', goal, truck, driver)]
    return []


def all_delivered(state, goal, truck, driver):
    for package in state.packages:
        if (state.packages[package]['location'] == 'in_truck'):
            return [('deliver_package', goal, truck, driver, package), ('finish_delivery', goal, truck, driver)]
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


def choose_truck_and_driver(state, goal):
    answer = choose_by_connection(state)
    if answer != {}:
        # walkToTruck
        return [('travel_to_truck_on_foot', goal, answer['truck'], answer['driver'])]

    answer = choose_by_distance(state)
    if answer != {}:
        # takeBusToTruck
        return [('travel_to_truck_by_bus', goal, answer['truck'], answer['driver'], '')]
    return False


def main(args):

    # Operators declaration
    pyhop.declare_operators(travel_op, walk_op, get_on_truck_op,
                            get_off_truck_op, gather_package_op, drop_package_op, get_on_bus_op, travel_by_bus_op, get_off_bus_op)
    # Method declaration
    pyhop.declare_methods('travel_to_truck_on_foot',
                          walk_to_truck, already_on_truck)
    pyhop.declare_methods('travel_to_truck_by_bus', travel_by_bus)
    pyhop.declare_methods('start_delivery', travel_by_truck)
    pyhop.declare_methods('all_gathered', all_gathered)
    pyhop.declare_methods('travel_to_package', travel_to_package_m)
    pyhop.declare_methods('finish_delivery', all_delivered)
    pyhop.declare_methods('deliver_package', deliver_package_m)
    pyhop.declare_methods('travel_to_city', travel_m, already_there)
    pyhop.declare_methods('choose_truck_and_driver', choose_truck_and_driver)

    # Initial State
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

    state1.buses = {'b0': {'location': 'Huelva', 'price': 10}, 'b1': {'location': 'Cadiz', 'price': 10},
                    'b2': {'location': 'Sevilla', 'price': 10}, 'b3': {'location': 'Cordoba', 'price': 10},
                    'b4': {'location': 'Malaga', 'price': 10}, 'b5': {'location': 'Jaen', 'price': 10},
                    'b5': {'location': 'Granada', 'price': 10}, 'b6': {'location': 'Almeria', 'price': 10}}

    state1.packages = {f'p{i+1}': {'location': loc}
                       for i, loc in enumerate(args.ppos)}

    state1.drivers = {f'd{i+1}': {'location': loc}
                      for i, loc in enumerate(args.dpos)}

    state1.trucks = {f't{i+1}': {'location': loc}
                     for i, loc in enumerate(args.tpos)}

    state1.path = []
    state1.walkpath = []
    state1.buspath = []
    state1.cost = 0

    # Goal
    goal1 = pyhop.Goal('goal1')
    goal1.packages = {f'p{i+1}': {'location': loc}
                      for i, loc in enumerate(args.delivery)}

    goal1.drivers = {f'd{i+1}': {'location': args.destination}
                     for i in range(0, len(args.dpos))}
    goal1.trucks = {f't{i+1}': {'location': args.destination}
                    for i in range(0, len(args.dpos))}

    pyhop.pyhop(state1, [('choose_truck_and_driver', goal1)], verbose=args.verbose)


def check_args(args):
    if (len(args.delivery) == len(args.ppos)):
        return True
    else:
        raise Exception(f"Check that the number of specified arguments match.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dpos", required=True,
                        help="Drivers' initial positions",
                        nargs="+",
                        choices=ALL_CITIES)
    parser.add_argument("--tpos", required=True,
                        help="Trucks' initial positions",
                        nargs="+",
                        choices=TRUCK_VALID_POSITIONS)
    parser.add_argument("--destination", required=True,
                        help="Drivers' and trucks' final destinations. Trucks and drivers share the same destination.",
                        choices=TRUCK_VALID_POSITIONS)
    parser.add_argument("--ppos", required=True,
                        help="Packages' initial positions",
                        nargs="+",
                        choices=TRUCK_VALID_POSITIONS)
    parser.add_argument("--delivery", required=True,
                        help="Packages' final destination",
                        nargs="+",
                        choices=TRUCK_VALID_POSITIONS)
    parser.add_argument("--verbose",
                        help="""
                            Verbosity in the execution. if verbose = 0 (the default), pyhop returns the solution but prints nothing;
                            - if verbose = 1, it prints the initial parameters and the answer;
                            - if verbose = 2, it also prints a message on each recursive call;
                            - if verbose = 3, it also prints info about what it's computing.")
                            """,
                        choices=[0, 1, 2, 3],
                        type=int,
                        default=0)

    args = parser.parse_args()
    if check_args(args):
        main(args)
