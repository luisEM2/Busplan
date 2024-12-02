from initialize import *
from functions import get_bus_with_color


class Hoverable:
    hoverable_items = []
    font = pygame.font.SysFont('Comic Sans MS', 20)

    def __init__(self, pos, information="None", size=(5, 5)):
        self.information = information

        self.actual_pos_x = pos[0] * WIDTH
        self.actual_pos_y = pos[1] * HEIGHT
        self.size = size

        self.width = self.size[0]
        self.height = self.size[1]

        self.rect = pygame.Rect(self.actual_pos_x - (self.width / 2), self.actual_pos_y - (self.height / 2), self.width,
                                self.height)

        Hoverable.hoverable_items.append(self)

    def is_hovered(self, screen, mouse_x, mouse_y):
        if self.rect.collidepoint((mouse_x, mouse_y)):
            list_text = [self.font.render(single_info, True, (0, 0, 0)) for single_info in self.information]
            width = max([text.get_width() for text in list_text]) + 10
            height = sum([text.get_height() for text in list_text]) + 10
            txt_surface = pygame.Surface((width, height))
            txt_surface.fill((129, 191, 230))
            position = [5, 5]
            for text in list_text:
                txt_surface.blit(text, tuple(position))
                position[1] += text.get_height()

            top_left_pos_x = self.actual_pos_x - width if self.actual_pos_x - width > 0 else 0
            top_left_pos_y = self.actual_pos_y - height if self.actual_pos_y - height > 0 else 0
            screen.blit(txt_surface, (top_left_pos_x, top_left_pos_y))


# this class is only there to draw the stations, check the collision,
# maybe display the name of the station below the station when the user hovers over the station
class Stations(Hoverable):
    list_stations_new = []
    list_stations_old = []

    def __init__(self, name, pos_x, pos_y, bus_routes, new):
        if new:
            if not (name in [station.name for station in Stations.list_stations_new]):
                self.name = name
                self.pos_x = pos_x
                self.pos_y = pos_y
                self.connections = bus_routes
                Stations.list_stations_new.append(self)

                information = [f"NAME : {self.name}", f"BUSSE: {self.connections}"]
                Hoverable.__init__(self, pos=(pos_x, pos_y), size=(10, 10), information=information)
        else:
            if not (name in [station.name for station in Stations.list_stations_old]):
                self.name = name
                self.pos_x = pos_x
                self.pos_y = pos_y
                self.connections = bus_routes
                Stations.list_stations_old.append(self)

                information = [f"NAME : {self.name}", f"BUSSE: {self.connections}"]
                Hoverable.__init__(self, pos=(pos_x, pos_y), size=(10, 10), information=information)

    def draw(self, screen):
        self.rect = pygame.Rect(self.actual_pos_x - (self.width / 2), self.actual_pos_y - (self.height / 2), self.width,
                                self.height)
        pygame.draw.rect(screen, (115, 41, 7), self.rect, 0)

    @staticmethod
    def get_station_by_name(name, new):
        if new:
            for station in Stations.list_stations_new:
                if station.name == name:
                    return station
        else:
            for station in Stations.list_stations_old:
                if station.name == name:
                    return station

    def __repr__(self):
        return self.name


class StationForBus:
    person_image = pygame.image.load("bilder/boy.png")
    default_number = 1000000000
    list_stations_new = []
    list_stations_old = []
    __list_lane_stations_new = []
    __list_lane_stations_old = []

    def __init__(self, number, time, connections, pos, change, name, new, false_init=False):
        if false_init:
            self.false_init(number, time, new)
        else:
            self.time = time
            self.number = number
            self.name = name
            self.new = new
            self.x = pos[0]
            self.y = pos[1]
            self.change = change
            if type(connections) == float:
                self.connections = [int(connections)]
            else:
                self.connections = [int(i) for i in connections.split(" ")]
            self.distance_to_start = self.default_number
            self.route = []
            if new:
                StationForBus.list_stations_new.append(self)
            else:
                StationForBus.list_stations_old.append(self)

    def false_init(self, station, iterations, new):
        self.time = station.time
        self.number = station.number
        self.name = station.name
        self.new = new
        self.x = station.x
        self.y = station.y
        self.change = station.change
        self.distance_to_start = station.distance_to_start
        self.connections = station.connections
        if iterations:
            self.route = [StationForBus(route, iterations - 1, *[1 for _ in range(4)], new, 1) for route in
                          station.route if route != station]
        else:
            self.route = []
        return self

    def draw_person(self, screen, minutes):
        count = 0
        route = self.route + [self]
        if route[0].time <= minutes <= route[-1].time:
            for station in route:
                if station.time >= minutes:
                    break
                count += 1
            if minutes == route[count].time:
                screen.blit(self.person_image, (route[count].x * WIDTH, route[count].y * HEIGHT))
            else:
                current = minutes - route[count - 1].time
                future = route[count].time - route[count - 1].time
                current_portion = current / future
                screen.blit(self.person_image, (
                    (route[count - 1].x * (1 - current_portion) + route[count].x * current_portion) * WIDTH,
                    (route[count - 1].y * (1 - current_portion) + route[count].y * current_portion) * HEIGHT))

    @staticmethod
    def create_lane_stations():
        help_list = [[]]
        counter = 0
        current_lane = int(StationForBus.list_stations_new[0].number/100)
        for station in StationForBus.list_stations_new:
            if int(station.number/100) == current_lane:
                help_list[counter].append(station)
            else:
                current_lane = int(station.number/100)
                counter += 1
                help_list.append([])
                help_list[counter].append(station)

        for lane in help_list:
            StationForBus.__list_lane_stations_new.append(tuple(lane))

        StationForBus.__list_lane_stations_new = tuple(StationForBus.__list_lane_stations_new)

        help_list = [[]]
        counter = 0
        current_lane = int(StationForBus.list_stations_old[0].number / 100)
        for station in StationForBus.list_stations_old:
            if int(station.number / 100) == current_lane:
                help_list[counter].append(station)
            else:
                current_lane = int(station.number / 100)
                counter += 1
                help_list.append([])
                help_list[counter].append(station)

        for lane in help_list:
            StationForBus.__list_lane_stations_old.append(tuple(lane))

        StationForBus.__list_lane_stations_old = tuple(StationForBus.__list_lane_stations_old)

    @classmethod
    def get_lane_stations(cls, lane, new):
        if new:
            return StationForBus.__list_lane_stations_new[int(lane - 1)]
        else:
            return StationForBus.__list_lane_stations_old[int(lane - 1)]

    @staticmethod
    def get_station_by_name_and_lane(name: str, number: int, new):
        l = []
        l2 = StationForBus.list_stations_new if new else StationForBus.list_stations_old
        for station in l2:
            if station.name == name:
                if int(station.number / 100) == number:
                    l.append(station)
        return l

    def __repr__(self):
        return f"{self.name}; num: {self.number}; dis:{self.distance_to_start}; time:{self.time}; " \
               f"lane: {dict_names_new[int(self.number / 100)] if self.new else dict_names_old[int(self.number / 100)]}"


class Bus(Hoverable):
    def __init__(self, list_times, cyclic, rgb, lane, last, icon_choose, new):
        """
        :param list_times: all the times of one bus driving around in the format
                           (Number of Bus stop for certain lane, time in minutes, connections_raw, (x, y), change, name)
        :param cyclic: bool weather start station = end station
        :param rgb: color of the bus
        :param lane: the lane of the bus e.g. 60
        :param last: the highest Bus stop number
        """
        self.new = new
        self.x = 0
        self.y = 0
        self.displayed = True
        self.times = tuple([StationForBus(*i, new) for i in list_times])
        self.image = get_bus_with_color(rgb, icon_choose)
        self.cyclic = cyclic
        self.lane = lane
        self.last = last

        information = [f"NAME  : {str(self.lane)}"]  # , f"CYCLIC: {str(self.displayed)}"
        Hoverable.__init__(self, pos=(0, 0), size=self.image.get_size(), information=information)

    # find the route the person has to take, e.g enter bus lane 60 and then change to bus lane 61
    def find_route(self, start_station: Stations, end_station: Stations, departure_time, new):
        departures_start = [i for i in self.times if i.x == start_station.pos_x]
        set_numbers = {i.number for i in departures_start}
        list_by_numbers = []
        first_stations = []
        list_calculating = []
        for number in set_numbers:
            list_by_numbers.append([i for i in departures_start if i.number == number])
        for departures in list_by_numbers:
            lowest_time = 1000000
            for station in departures:
                if lowest_time > station.time >= departure_time:
                    lowest_time = station.time
                    first_station = station
            first_stations.append(first_station)
        for first_station in first_stations:
            first_station.distance_to_start = first_station.time - departure_time
            first_station.route.append(first_station)
            next_station = self.get_next(first_station, first_station.time, new)
            if next_station:
                list_calculating.append(next_station)
        return list_calculating

    def get_next(self, station: StationForBus, departure_time, new):  # departureTime ist die zeit wo man am bussteig ankommt
        departures_start = [i for i in self.times if i.number == station.number]
        lowest_time = 1000000
        for station2 in departures_start:
            if lowest_time > station2.time >= departure_time:
                lowest_time = station2.time
                first_station = station2
        first_station.distance_to_start = first_station.time - departure_time + station.distance_to_start
        next_station = [i for i in self.times if i.number == first_station.number + 1]
        if self.cyclic:
            if new:
                ns = StationForBus.list_stations_new[StationForBus.list_stations_new.index(first_station) + 1]
                if int(ns.number / 100) == int(first_station.number / 100):
                    next_station = [ns]
            else:
                # firststation in from new list
                ns = StationForBus.list_stations_old[StationForBus.list_stations_old.index(first_station) + 1]
                if int(ns.number / 100) == int(first_station.number / 100):
                    next_station = [ns]
        if next_station:
            lowest_time = 1000000
            for departure in next_station:
                if lowest_time > departure.time >= departure_time:
                    lowest_time = departure.time
                    next_station = departure
            if type(next_station) == list:
                if next_station:
                    next_station = next_station[0]
                else:
                    return False
            if next_station:
                if next_station.distance_to_start == StationForBus.default_number:
                    next_station.distance_to_start = first_station.distance_to_start + next_station.time - first_station.time
                    next_station.route = station.route.copy()
                    next_station.route.append(next_station)
                else:
                    if next_station.distance_to_start < first_station.distance_to_start + next_station.time - first_station.time:
                        return False
                    else:
                        next_station.distance_to_start = first_station.distance_to_start + next_station.time - first_station.time
                        next_station.route = station.route.copy()
                        next_station.route.append(next_station)
                return next_station
            else:
                return False
        else:
            return False

    # for the animation the code should run through every minute and draw the bus on his current position
    def draw_bus(self, screen, minutes):
        count = 0
        try:
            while self.times[count].time <= minutes:
                count += 1
            count -= 1
            if minutes == self.times[count].time:
                self.x = self.times[count].x
                self.y = self.times[count].y
                self.draw(screen)
            else:
                current = minutes - self.times[count].time
                future = self.times[count + 1].time - self.times[count].time
                current_portion = current / future
                self.x = self.times[count].x * (1 - current_portion) + self.times[count + 1].x * current_portion
                self.y = self.times[count].y * (1 - current_portion) + self.times[count + 1].y * current_portion
                if self.cyclic:
                    self.draw(screen)
                else:
                    if self.times[count].number + 1 == self.times[count + 1].number:
                        self.draw(screen)
            self.actual_pos_x, self.actual_pos_y = self.x * WIDTH, self.y * HEIGHT
        except IndexError:
            pass

    def draw(self, screen):
        self.rect = pygame.Rect(self.actual_pos_x - (self.width / 2), self.actual_pos_y - (self.height / 2), self.width,
                                self.height)
        screen.blit(self.image, (self.actual_pos_x - (self.width / 2), self.actual_pos_y - (self.height / 2)))

    def get_bus_by_station(self, station) -> bool:
        for station2 in self.times:
            if station.time == station2.time:
                return True
        return False

    def __repr__(self):
        return f"Bus lane Nr.{dict_names_new[int(self.times[0].number / 100)] if self.new else dict_names_old[int(self.times[0].number / 100)]}"


# check for cyclic function as numbers are changed
class Lane:
    list_lanes_new = []
    list_lanes_old = []

    # method to only add a new bus to a lane if the lane already exists
    def __add_bus(self, sheet: xlrd.sheet.Sheet, new):
        departures = []
        column = 0
        while True:
            row = 1
            departure = True
            try:
                sheet.cell_value(row, 6 + column * 2)
            except IndexError:
                break
            while departure:
                try:
                    departure = (sheet.cell_value(row, 6 + column * 2), sheet.cell_value(row, 7 + column * 2))
                    if not departure[0]:
                        break
                    #                   number                      time                                connections_raw
                    departures.append(
                        (sheet.cell_value(row, 1), departure[0] * 60 + departure[1], sheet.cell_value(row, 2),
                         (sheet.cell_value(row, 3), sheet.cell_value(row, 4)), sheet.cell_value(row, 5),
                         sheet.cell_value(row, 0)))
                    #                               (x,                     y)                      change                      name
                    row += 1
                except IndexError:
                    departure = False

            column += 1
        self.busses.append(Bus(departures, self.cyclic, (int(sheet.cell_value(0, 4)), int(sheet.cell_value(0, 5)),
                                                         int(sheet.cell_value(0, 6))), self.name, self.last,
                               sheet.cell_value(0, 3), new))

    def __init__(self, sheet: xlrd.sheet.Sheet, new):
        """
        :param sheet: whole excel sheet with all its contents
        :attr list_names: all the names of the stops ( e.g. Alte Frankfurter Str
        :attr buses: for every bus that will drive around, there is a Bus object with
                     the numbers(e.g.101) of the stops and the correspondent times, init will only add the first bus
        :attr list_connections: list of other bus lanes you can enter from each station, in the same order as the rest
                                in the format of (conn, conn, ...) without the own lane
        :attr id: id of the bus lane
        :attr name: the name of the bus lane, e.g. 60
        :attr cyclic: bool weather the first station is also the last station
        """
        number = int(sheet.cell_value(1, 1) / 100)
        list_lanes = Lane.list_lanes_new if new else Lane.list_lanes_old
        for lane in list_lanes:
            if lane.id == number:
                lane.__add_bus(sheet, new)
                break
        else:
            self.list_names = []
            self.list_coordinates = []
            self.busses = []
            self.list_connections = []
            self.id = number
            self.new = new
            self.name = dict_names_new[self.id] if new else dict_names_old[self.id]
            self.is_bus = sheet.cell_value(0, 3) == "B"
            row = 1
            while True:
                try:
                    name = sheet.cell_value(row, 0)
                except IndexError:
                    break
                if not name:
                    break
                self.list_names.append(name)
                connections = sheet.cell_value(row, 2)
                if connections:
                    if type(connections) == float:
                        self.list_connections.append([int(connections)])
                    else:
                        connections = [int(i) for i in connections.split(" ")]
                        self.list_connections.append(connections)
                    self.list_coordinates.append((sheet.cell_value(row, 3), sheet.cell_value(row, 4)))
                    row += 1
            self.cyclic = self.list_names[0] == self.list_names[-1]
            self.last = 0
            row = 1
            while True:
                try:
                    number = sheet.cell_value(row, 1)
                    if type(number) != float:
                        break
                    if number > self.last:
                        self.last = number
                    row += 1
                except IndexError:
                    break
            self.__add_bus(sheet, new)
            list_lanes.append(self)

    # changed
    def get_next(self, station: StationForBus, departure_time, new):
        l = []
        is_in_list = False
        for bus in self.busses:
            x = bus.get_next(station, departure_time, new)
            if x:
                for i in l.copy():
                    if i.number == x.number:
                        if i.time < x.time:
                            is_in_list = True
                        else:
                            l.pop(l.index(i))
                            l.append(x)
                            is_in_list = True
                if not is_in_list:
                    l.append(x)
        return l

    @staticmethod
    def get_lane_by_name(name, new):
        if new:
            for lane in Lane.list_lanes_new:
                if lane.name == name:
                    return lane
        else:
            for lane in Lane.list_lanes_old:
                if lane.name == name:
                    return lane

    @staticmethod
    def get_lane_by_number(number, new):
        if new:
            for lane in Lane.list_lanes_new:
                if lane.id == number:
                    return lane
        else:
            for lane in Lane.list_lanes_old:
                if lane.id == number:
                    return lane

    def get_bus_by_station(self, station) -> Bus:
        for bus in self.busses:
            if bus.get_bus_by_station(station):
                return bus
