import sys
from pygame_classes import InputBox, Button, ScrollableTimeBox, Label, SwitchButton
from classes import *


def calculate_route(start, end, start_time):
    start_station = Stations.get_station_by_name(start)
    end_station = Stations.get_station_by_name(end)
    if not (start_station or end_station):
        return
    best_connections = []
    for connection in start_station.connections:
        connection_stations = StationForBus.get_station_by_name_and_lane(start, [k for k in dict_names.keys() if
                                                                                 dict_names[k] == connection][0])
        lowest_time = 1000000
        next_stations = []
        for station in connection_stations:
            if lowest_time + 30 >= station.time >= start_time:  # +30 für gleiche station an unterschiedlichen punkten in der route
                if station.time < lowest_time:
                    lowest_time = station.time
                try:
                    if next_stations[-1].time >= station.time + 30:
                        next_stations.pop(-1)
                except IndexError:
                    pass
                next_stations.append(station)

        for station in next_stations:
            best_connection = calculate_route_only(start, end, station.time)
            if best_connection:
                best_connections.append(StationForBus(best_connection, *[1 for _ in range(6)]))

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
        best = get_lowest(best_connections)
        best_three.append(best_connections.pop(best_connections.index(best)))
        if best_connections:
            best = get_lowest(best_connections)
            best_three.append(best_connections.pop(best_connections.index(best)))

    # TODO: Show options on screen w/ size and pos
    for connection in best_three:
        Options(connection)


# route gets empty
def calculate_route_only(start: str, end: str, start_time: int):
    print(start, end, start_time)
    debug = False
    for station in StationForBus.list_stations:
        station.route = []
        station.distance_to_start = StationForBus.default_number

    start_station = Stations.get_station_by_name(start)
    end_station = Stations.get_station_by_name(end)
    list_routes = []
    for route in start_station.connections:
        lane = Lane.get_lane_by_name(route)
        for bus in lane.busses:
            next_stations = bus.find_route(start_station, end_station, start_time)
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
            if connection == dict_names[int(best.number / 100)]:
                next_station = Lane.get_lane_by_name(connection).get_next(best, best.time)
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
                for station2 in StationForBus.list_stations:
                    if int(station2.number / 100) == connection_id:
                        if station2.name == best.name:
                            if lowest > station2.time >= station2.change + best.change + 1 + best.distance_to_start + start_time:
                                lowest = station2.time
                                best_transit = station2
                if best_transit:
                    best_transit.distance_to_start = best_transit.time - start_time
                    best_transit.route = best.route
                    next_station = Lane.get_lane_by_name(connection).get_next(best_transit, best_transit.time)

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
                                list_routes.append(next_station[i])

        popped_list.append(list_routes.pop(list_routes.index(best)))
        # print([(route, route.route) for route in list_routes])

        if best.name == end:
            return best


fps = 60
fpsClock = pygame.time.Clock()

time = 60 * 12
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

button_legnede = Button(pos=(1650, 800), size=(250, 30),
                        text="Legende Busse")  # Button Calulate  , command=calculate_route, args=("START_STATION", "END_STATION", time
button_calculate = Button(pos=(1600, 1000), size=(300, 50),
                          text="CACULATE")  # Button Calulate  , command=calculate_route, args=("START_STATION", "END_STATION", time

time_box = ScrollableTimeBox(pos=(570, 30), size=(100, 40), time_in_min=time)
simulation_button = SwitchButton(pos=(690, 30), size=(90, 40), list_states=["START", "STOP"],
                                 list_colors=[(13, 140, 40), (163, 5, 5)])

active_busplan = SwitchButton(pos=(1700, 110), size=(180, 40), list_states=["alterBusplan", "neuerBusplan"],
                              list_colors=[(178, 227, 175), (29, 112, 24)])

# create lanes
with xlrd.open_workbook(FILEPATH) as file:
    for sheet in file.sheets():
        Lane(sheet)

# create stations
for lane in Lane.list_lanes:
    for i in range(len(lane.list_names)):
        Stations(lane.list_names[i], *lane.list_coordinates[i], lane.list_connections[i])

# Game loop.
while True:
    start = label_depature.text
    end = label_destination.text

    mouse_x, mouse_y = pygame.mouse.get_pos()
    screen.blit(background, (0, 0))
    if simulation_button.active_state == "STOP":
        # TODO: Increase TIME
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
            for item in SwitchButton.switch_buttons + Label.labels:
                item.check_collision(screen, mouse_x, mouse_y)

            if button_calculate.check_collision(mouse_x=mouse_x, mouse_y=mouse_y):
                s = start[len(label_depature.text_infront):]
                e = end[len(label_destination.text_infront):]
                calculate_route(start=s, end=e, start_time=int(time))

            last_overview = show_overview
            show_overview = button_legnede.check_collision(mouse_x=mouse_x, mouse_y=mouse_y) and (not last_overview)

        searched_text = search_box.handle_event(event=event)
        for station in Stations.list_stations:
            if (mouse_pressed and station.rect.collidepoint((mouse_x, mouse_y))) or (
                    searched_text and searched_text.lower() in station.name.lower()):
                if start == label_depature.text_infront:
                    label_depature.change_text(station.name)
                elif end == label_destination.text_infront:
                    label_destination.change_text(station.name)

                searched_text = search_box.handle_event(event)

    button_calculate.args = (start, end)

    # Draw.
    for object in PygameObject.objects:
        object.draw(screen)

    for station in Stations.list_stations:
        station.draw(screen)

    for lane in Lane.list_lanes:
        for bus in lane.busses:
            bus.draw_bus(screen, time)

    for hoverable_item in Hoverable.hoverable_items:
        hoverable_item.is_hovered(screen, mouse_x, mouse_y)

    if show_overview and active_busplan.text == "alterBusplan":
        screen.blit(overview_image_alt, (1120, 550))
    if show_overview and active_busplan.text == "neuerBusplan":
        screen.blit(overview_image_neu, (1120, 550))

    pygame.display.flip()
    fpsClock.tick(fps)
