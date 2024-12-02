import sys
import pygame.font

from pygame_classes import *
from classes import *
import time as time2


def timer(func):
    def wrapper(*args, **kwargs):
        start = time2.time()
        print(f"starting {func.__name__}")
        rv = func(*args, **kwargs)
        print(f"{func.__name__} took {time2.time()-start} seconds")
        return rv
    return wrapper


def check_for_less_changes(current_route: StationForBus, new):
    lane = Lane.get_lane_by_number(int(current_route.number / 100), new)
    print("lane is", lane.busses[0], current_route)
    best_routes = []
    for name in set(lane.list_names):
        for route in current_route.route:
            if int(route.number / 100) != lane.id:
                if route.name == name:
                    highest_time = 1000000
                    best_route = None
                    for bus in lane.busses:
                        for station in bus.times:
                            if station.name == name:
                                if highest_time > station.time >= \
                                        [r.time + r.change + station.change + DEFAULT_CHANGE for r in current_route.route if
                                         r.name == name][0]:
                                    highest_time = station.time
                                    best_route = station
                    if best_route:
                        best_routes.append(best_route)

    best_routes_copy = best_routes.copy()
    if best_routes:
        print("best routes not empty", best_routes)
        own_bus = lane.get_bus_by_station(current_route)
        if not own_bus:
            print("no bus", lane.busses[0], current_route)
        else:
            for route in best_routes:
                own_bus_in_route = [route2 for route2 in current_route.route if int(route2.number / 100) == int(
                    current_route.number / 100) and route.name == route2.name]
                try:
                    if own_bus_in_route:
                        best_routes_copy.remove(route)
                    if int(route.number/100) == int(current_route.number/100) and route.name == current_route.name:
                        best_routes_copy.remove(route)
                except ValueError:
                    pass
    else:
        print("best routes empty")
    best_routes = list(set(best_routes_copy))
    own_bus = lane.get_bus_by_station(current_route)

    print("best routes are:")
    print(best_routes)

    for route in best_routes:
        route.distance_to_start = route.time - current_route.route[0].time
        new_route = StationForBus(route, *[ITERATIONS for _ in range(5)], new, ITERATIONS)
        routes = []
        while True:
            route2 = own_bus.get_next(new_route, new_route.time, new)
            if not route2:
                break
            if route2.time == current_route.time and route2.number == current_route.number:
                print("got less connections", route2)
                route2.route = routes + route2.route
                return route2

            if route2.time > current_route.time:
                print("wrong connection", route2)
                break
            new_route = StationForBus(route2, *[ITERATIONS for _ in range(5)], new, ITERATIONS)
            routes.append(route2)


#@timer
def calculate_route(start, end, start_time, new):
    dict_names = dict_names_new if new else dict_names_old
    debug = False
    start_station = Stations.get_station_by_name(start, new)
    end_station = Stations.get_station_by_name(end, new)
    if not (start_station or end_station):
        return
    best_connections = []

    @timer
    def calculate(connection, new, start, end):
        connection_stations = StationForBus.get_station_by_name_and_lane(start, [k for k in dict_names.keys() if
                                                                                 dict_names[k] == connection][0], new)
        lowest_time = 1000000
        next_stations = []
        for station in connection_stations:
            if lowest_time + 40 >= station.time >= start_time:  # +40 für gleiche station zu unterschiedlichen zeiten in der route
                if station.time < lowest_time:
                    lowest_time = station.time
                try:
                    if next_stations[-1].time >= station.time + 30:
                        next_stations.pop(-1)
                except IndexError:
                    pass
                next_stations.append(station)

        for station in next_stations:
            best_connection = calculate_route_only(start, end, station.time, new)
            if best_connection:
                best_connections.append(StationForBus(best_connection, *[ITERATIONS for _ in range(5)], new, ITERATIONS))

    for connection in start_station.connections:
        calculate(connection, new, start, end)

    def get_lowest(l):
        lowest_time = 1000000
        best = None
        for station in l:
            if station.distance_to_start < lowest_time:
                lowest_time = station.distance_to_start
                best = station
        return best

    best_three = []
    best = get_lowest(best_connections)
    best_three.append(best_connections.pop(best_connections.index(best)))
    if best_connections:
        best = get_lowest(best_connections)  # compiler trollt oder so
        best = get_lowest(best_connections)
        best_three.append(best_connections.pop(best_connections.index(best)))
        if best_connections:
            best = get_lowest(best_connections)
            best_three.append(best_connections.pop(best_connections.index(best)))

    pop_list = []
    for connection in best_three:
        for connection2 in best_three:
            if not connection2 == connection:
                if connection.time == connection2.time:
                    if connection.distance_to_start < connection2.distance_to_start:
                        pop_list.append(best_three.index(connection2))
                    else:
                        pop_list.append(best_three.index(connection))

    pop_list = set(pop_list)
    for element in pop_list:
        try:
            best_three.pop(element)
        except IndexError:
            pass

    def add_missing_station(connection):
        if connection.route:
            last_lane = int(connection.route[0].number / 100)
        else:
            last_lane = int(connection.number / 100)
        for route in connection.route:
            if int(route.number / 100) != last_lane:
                last_lane = int(route.number / 100)
                insert_element = None
                highest_time = 0
                for station in StationForBus.list_stations_new if new else StationForBus.list_stations_old:
                    if int(station.number / 100) == last_lane:
                        if station.name == connection.route[connection.route.index(route) - 1].name:
                            if highest_time < station.time <= route.time:
                                highest_time = station.time
                                insert_element = station

                insert_element.route = route.route[:-1]
                connection.route.insert(connection.route.index(route), insert_element)

        return connection

    pos_y = 2
    for connection in best_three:
        connection = add_missing_station(connection)
        for route in connection.route:
            connection.route[connection.route.index(route)] = add_missing_station(route)

        first_route = True
        for route in connection.route:
            if first_route:
                first_route = False
                continue
            if route.route[-1].time != connection.route[connection.route.index(route) - 1].time and \
                    route.route[-1].number != connection.route[connection.route.index(route) - 1].number:
                route.route.append(connection.route[connection.route.index(route) - 1])

        if debug:
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n")
            print("calculation ready", connection, connection.route)

        first_route = True
        # self missing in calculation
        name_list = []
        for name in connection.route:
            in_list = 5000
            for j in name_list:
                if j[0].name == name.name:
                    in_list = name_list.index(j)
            if in_list != 5000:
                name_list[in_list].append(name)
            else:
                name_list.append([name])

        for names in name_list:
            if len(names) > 2:
                for station in connection.route:
                    if station == names[1]:
                        remove_index = connection.route.index(station)
                        while connection.route[remove_index] != names[-1]:
                            connection.route.pop(remove_index)

        try:
            for route in (connection.route + [connection]):
                if first_route:
                    first_route = False
                    continue
                else:
                    if int(route.number/100) != int(connection.route[(connection.route+[connection]).index(route) - 1].number/100):
                        # route changes in func and thats bad
                        new_connection = check_for_less_changes(StationForBus(route, *[ITERATIONS for _ in range(5)], new, ITERATIONS), new)
                        if new_connection:
                            if debug:
                                print("rerouting")
                                print(new_connection, "\n", new_connection.route)
                                print("route", route)
                            first_route = True
                            for route3 in connection.route + [connection]:
                                for route4 in new_connection.route:
                                    if route3.name == route4.name and route3.number != route4.number:
                                        connection_copy = StationForBus(connection, *[ITERATIONS for _ in range(5)], new, ITERATIONS)
                                        if first_route:
                                            first_route = False
                                            continue
                                        start_index = connection.route.index(route3)
                                        connection.route.remove(route3)
                                        while True:
                                            if connection.route[start_index].time == new_connection.time and \
                                                    connection.route[start_index].number == new_connection.number:
                                                connection.route.pop(start_index)
                                                break
                                            else:
                                                connection.route.pop(start_index)
                                        for route4 in new_connection.route:
                                            connection.route.insert(start_index, route4)
                                            start_index += 1
                                        raise ZeroDivisionError
        except ValueError:
            connection = connection_copy
        except ZeroDivisionError:
            if debug:
                print("new route")
                print(connection)
                print(connection.route)
        Options(connection, (WIDTH / 16, HEIGHT / 8 * pos_y), (WIDTH / 6, HEIGHT / 8), new)
        pos_y += 1


# this func takes the longest
#@timer
def calculate_route_only(start: str, end: str, start_time: int, new: bool):
    dict_names = dict_names_new if new else dict_names_old
    # setup
    print(start, end, start_time)
    debug = False
    if new:
        for station in StationForBus.list_stations_new:
            station.route = []
            station.distance_to_start = StationForBus.default_number
    else:
        for station in StationForBus.list_stations_old:
            station.route = []
            station.distance_to_start = StationForBus.default_number

    start_station = Stations.get_station_by_name(start, new)
    end_station = Stations.get_station_by_name(end, new)
    list_routes = []

    # start of execution
    for route in start_station.connections:
        lane = Lane.get_lane_by_name(route, new)
        for bus in lane.busses:
            next_stations = bus.find_route(start_station, end_station, start_time, new)
            if next_stations:
                for station in next_stations:
                    is_in_list = False
                    for i in list_routes:
                        if i.number == station.number:
                            if i.time < station.time:
                                is_in_list = True
                            else:
                                list_routes.pop(list_routes.index(i))
                                list_routes.append(station)
                                is_in_list = True
                    if not is_in_list:
                        list_routes.append(station)
    # if debug:
    #   print([(r) for r in list_routes])
    popped_list = []
    end_time = 0
    while True:
        best = None
        lowest = 1000000
        for route in list_routes:
            if route.time < lowest:
                lowest = route.time
                best = route

        if not best:
            return False

        for connection in best.connections:
            if connection == dict_names[int(best.number / 100)]:  # own lane
                next_station = Lane.get_lane_by_name(connection, new).get_next(best, best.time, new)
                is_in = [False for _ in next_station]
                for station in next_station:
                    for route in list_routes:
                        if station.number == route.number:
                            if station.distance_to_start < route.distance_to_start:
                                if debug:
                                    print("popped", route, [dict_names[int(r.number / 100)] for r in route.route])
                                popped_list.append(list_routes.pop(list_routes.index(route)))
                            else:
                                is_in[next_station.index(station)] = True
                for i in range(len(next_station)):
                    if not is_in[i]:
                        if debug:
                            print(next_station[i], [dict_names[int(r.number / 100)] for r in next_station[i].route])
                        list_routes.append(next_station[i])
            else:
                connection_id = [k for k, v in dict_names.items() if v == connection][0]
                lowest = 1000000
                best_transit = None
                # get next station for specific connection

                station_list = StationForBus.get_lane_stations(connection_id, new)
                for station2 in station_list:
                    if station2.name == best.name:
                        if lowest > station2.time >= station2.change + best.change + DEFAULT_CHANGE + best.distance_to_start + start_time:
                            lowest = station2.time
                            best_transit = station2
                if best_transit:
                    best_transit.distance_to_start = best_transit.time - start_time
                    best_transit.route = best.route
                    next_station = Lane.get_lane_by_name(connection, new).get_next(best_transit, best_transit.time, new)

                    is_in = [False for _ in next_station]
                    for station in next_station:
                        for route in list_routes:
                            if station.number == route.number:
                                if station.distance_to_start < route.distance_to_start:
                                    if debug:
                                        print("popped", route, [dict_names[int(r.number / 100)] for r in route.route])
                                    popped_list.append(list_routes.pop(list_routes.index(route)))
                                else:
                                    is_in[next_station.index(station)] = True

                    for i in range(len(next_station)):
                        if not is_in[i]:
                            if next_station[i] not in list_routes:
                                if debug:
                                    print(next_station[i],
                                          [dict_names[int(r.number / 100)] for r in next_station[i].route])
                                # get a check if bus will come with less change
                                list_routes.append(next_station[i])

        popped_list.append(list_routes.pop(list_routes.index(best)))

        def get_least_change(best, list_routes):
            for route in list_routes:
                if route.number == best.number:
                    if route[0].time == best[0].time:
                        if len(route.route) < len(best.route):
                            return route, False
            return best, True

        if best.name == end:
            best, is_best = get_least_change(best, list_routes)
            while not is_best:
                best, is_best = get_least_change(best, list_routes)

            return best


fps = 60
fpsClock = pygame.time.Clock()

time = 60 * 12 + 20
simulation = True
show_overview = False

screen = pygame.display.set_mode((WIDTH, HEIGHT))
background = pygame.image.load(r"bilder\background_map.png")
overview_image_neu = pygame.image.load(r"bilder\overview_connections_neu.png")
overview_image_alt = pygame.image.load(r"bilder\overview_connections_alt.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# create Classes
search_box = InputBox(pos=(1400, 950), size=(500, 32), max_characters=30)

label_depature = Label(pos=(1400, 850), size=(450, 30), text="", text_infront="START : ",
                       click_empty=True)  # Label Depature
label_destination = Label(pos=(1400, 900), size=(450, 30), text="", text_infront="END     : ",
                          click_empty=True)  # Label Depature
label_calculation_time = Label(pos=(1460, 45), size=(80, 30), text="TIME", text_infront="")  # Label TimeSave

result_alter_busplan = Label(pos=(1550, 20), size=(300, 30), text="", text_infront="alterBusplan: ")  # Label Depature
result_neuer_busplan = Label(pos=(1550, 65), size=(300, 30), text="", text_infront="neuerBusplan: ")  # Label Depature

button_legende = Button(pos=(1650, 800), size=(250, 30),
                        text="Legende Busse")  # Button Calulate  , command=calculate_route, args=("START_STATION", "END_STATION", time
button_calculate = Button(pos=(1600, 1000), size=(300, 50),
                          text="CACULATE")  # Button Calulate  , command=calculate_route, args=("START_STATION", "END_STATION", time

time_box = ScrollableTimeBox(pos=(570, 30), size=(100, 40), time_in_min=time)
simulation_button = SwitchButton(pos=(690, 30), size=(90, 40), list_states=["START", "STOP"],
                                 list_colors=[(13, 140, 40), (163, 5, 5)])

active_busplan = SwitchButton(pos=(1700, 110), size=(180, 40), list_states=[SwitchButton.NEW, SwitchButton.OLD],
                              list_colors=[(178, 227, 175), (29, 112, 24)])

# create lanes
with xlrd.open_workbook(FILEPATH_OLD) as file:
    for sheet in file.sheets():
        Lane(sheet, False)

with xlrd.open_workbook(FILEPATH_NEW) as file:
    for sheet in file.sheets():
        Lane(sheet, True)

# create stations
for lane in Lane.list_lanes_old:
    for i in range(len(lane.list_names)):
        Stations(lane.list_names[i], *lane.list_coordinates[i], lane.list_connections[i], False)

for lane in Lane.list_lanes_new:
    for i in range(len(lane.list_names)):
        Stations(lane.list_names[i], *lane.list_coordinates[i], lane.list_connections[i], True)

StationForBus.list_stations_new = tuple(StationForBus.list_stations_new)
StationForBus.list_stations_old = tuple(StationForBus.list_stations_old)
StationForBus.create_lane_stations()

active_route = None
# Game loop.
while True:
    start = label_depature.text
    end = label_destination.text

    mouse_x, mouse_y = pygame.mouse.get_pos()
    screen.blit(background, (0, 0))
    if simulation_button.active_state == "STOP":
        time = (time + (1 / 10)) % float(60 * 24)
        time_box.time_in_min = int(time)
        time_box.generate_and_update_text()

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        output_time = time_box.handle_event(event)
        if output_time:
            time = output_time

        mouse_pressed = event.type == pygame.MOUSEBUTTONDOWN
        if mouse_pressed:
            for item in Label.labels:
                item.check_collision(screen, mouse_x, mouse_y)

            for item in SwitchButton.switch_buttons:
                if item.check_collision(screen, mouse_x, mouse_y):
                    label_depature.update_text(label_depature.text_infront + "")
                    label_destination.update_text(label_destination.text_infront + "")

            if button_calculate.check_collision(mouse_x=mouse_x, mouse_y=mouse_y):
                active_route = None
                for obj in PygameObject.objects:
                    if obj in Options.options:
                        PygameObject.objects.remove(obj)
                Options.options.clear()
                button_calculate.enabled = False
                s = start[len(label_depature.text_infront):]
                e = end[len(label_destination.text_infront):]
                if active_busplan.active_state == active_busplan.NEW:
                    calculate_route(start=s, end=e, start_time=int(time), new=True)
                else:
                    calculate_route(start=s, end=e, start_time=int(time), new=False)

            for obj in Options.options:
                if obj.check_collision(mouse_x, mouse_y):
                    button_calculate.enabled = True
                    active_route = obj.route
                    simulation_button.active_state = "STOP"
                    time = obj.route.route[0].time
                    for obj in Options.options:
                        try:
                            PygameObject.objects.remove(obj)
                        except ValueError:
                            pass
                    break

            last_overview = show_overview
            show_overview = button_legende.check_collision(mouse_x=mouse_x, mouse_y=mouse_y) and (not last_overview)

        searched_text = search_box.handle_event(event=event)
        if active_busplan.active_state == active_busplan.NEW:
            for station in Stations.list_stations_new:
                if (mouse_pressed and station.rect.collidepoint((mouse_x, mouse_y))) or (
                        searched_text and searched_text.lower() in station.name.lower()):
                    if start == label_depature.text_infront:
                        label_depature.change_text(station.name)
                    elif end == label_destination.text_infront:
                        label_destination.change_text(station.name)

                    searched_text = search_box.handle_event(event)
        else:
            for station in Stations.list_stations_old:
                if (mouse_pressed and station.rect.collidepoint((mouse_x, mouse_y))) or (
                        searched_text and searched_text.lower() in station.name.lower()):
                    if start == label_depature.text_infront:
                        label_depature.change_text(station.name)
                    elif end == label_destination.text_infront:
                        label_destination.change_text(station.name)

                    searched_text = search_box.handle_event(event)

    button_calculate.args = (start, end)

    if active_route:
        active_route.draw_person(screen, time)
    # Draw.
    for obj in PygameObject.objects:
        obj.draw(screen)

    if active_busplan.active_state == SwitchButton.NEW:
        for station in Stations.list_stations_new:
            station.draw(screen)

        for lane in Lane.list_lanes_new:
            for bus in lane.busses:
                bus.draw_bus(screen, time)
    else:
        for station in Stations.list_stations_old:
            station.draw(screen)

        for lane in Lane.list_lanes_old:
            for bus in lane.busses:
                bus.draw_bus(screen, time)

    for hoverable_item in Hoverable.hoverable_items:
        hoverable_item.is_hovered(screen, mouse_x, mouse_y)

    if show_overview and active_busplan.text == SwitchButton.OLD:
        screen.blit(overview_image_alt, (1120, 550))
    if show_overview and active_busplan.text == SwitchButton.NEW:
        screen.blit(overview_image_neu, (1120, 550))

    pygame.display.flip()
    fpsClock.tick(fps)
