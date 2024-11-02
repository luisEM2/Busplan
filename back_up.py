
# old Stations
'''
# this class is only there to draw the stations, check the collision,
# maybe display the name of the station below the station when the user hovers over the station
class Stations(Hoverable):
    list_stations = []

    def __init__(self, name, pos_x, pos_y, bus_routes):
        if not (name in [station.name for station in Stations.list_stations]):
            self.name = name
            self.bus_routes = bus_routes
            Stations.list_stations.append(self)

            information = [f"NAME : {self.name}", f"BUSSE: {self.bus_routes}"]
            Hoverable.__init__(self, pos=(pos_x*WIDTH, pos_y*HEIGHT), size=(10, 10), information=information)
    
    @staticmethod
    def get_station_by_name(name):
        for station in Stations.list_stations:
            if station.name == name:
                return station
    
    def __repr__(self):
        return self.name
'''

# old Lane
'''
# calculates the best route and contains all of the information of the excel sheets
class Lane:
    list_lanes = []

    # method to only add a new bus to a lane if the lane already exists
    def __add_bus(self, sheet: xlrd.sheet.Sheet):
        departures = []
        column = 0
        while True:
            row = 1
            departure = True
            try:
                sheet.cell_value(row, 5 + column * 2)
            except IndexError:
                break
            while departure:
                try:
                    departure = (sheet.cell_value(row, 5 + column * 2), sheet.cell_value(row, 6 + column * 2))
                    if not departure[0]:
                        break
                    departures.append((sheet.cell_value(row, 1), departure[0] * 60 + departure[1],
                                       (sheet.cell_value(row, 3), sheet.cell_value(row, 4))))
                    row += 1
                except IndexError:
                    departure = False

            column += 1
        self.busses.append(Bus(departures, self.cyclic, (int(sheet.cell_value(0, 4)), int(sheet.cell_value(0, 5)), int(sheet.cell_value(0, 6))), self.name))

    def __init__(self, sheet: xlrd.sheet.Sheet):
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
        for lane in Lane.list_lanes:
            if lane.id == number:
                lane.__add_bus(sheet)
                break
        else:
            self.list_names = []
            self.list_coordinates = []
            self.busses = []
            self.list_connections = []
            self.id = number
            self.name = dict_names[self.id]
            """numbers = []
            times = []
            """
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
                    """departure = 1
                    count = 0  # listen werden nicht voll gespeichert
                    while departure:
                        try:
                            departure = (sheet.cell_value(row, 5 + count * 2), sheet.cell_value(row, 6 + count * 2))  # (x,y)
                            count += 1
                            numbers.append(sheet.cell_value(row, 1))
                            times.append(departure[0] * 60 + departure[1])
                        except IndexError:
                            break

            self.busses.append(Bus(list(zip(numbers, times, self.list_coordinates*row))))"""
            self.cyclic = self.list_names[0] == self.list_names[-1]
            self.__add_bus(sheet)
            Lane.list_lanes.append(self)

    @staticmethod
    def get_lane_by_name(name):
        for lane in Lane.list_lanes:
            if lane.name == name:
                return lane


    # find the route the person has to take, e.g enter bus lane 60 and then change to bus lane 61
    def find_route(self, end_station:Stations, time):
        return "route"
'''


# old Bus
'''
# makes the bus animation and to calculate the time of a trip in one bus from station a to b within one lane
class Bus(Hoverable):
    def __init__(self, list_times, cyclic, rgb, name):
        """
        :param list_times: all the times of one bus driving around in the format
                           (Number of Bus stop for certain lane, time in minutes, (x, y))
        """
        self.name = str(name)
        self.displayed = True
        self.times = list_times
        self.cyclic = cyclic

        information = [f"NAME  : {str(self.name)}"] # , f"CYCLIC: {str(self.displayed)}"
        Hoverable.__init__(self, pos=(0, 0), image=get_bus_with_color(rgb), information=information)

    # calculate time from station a to b within one lane
    def get_trip(self, start_number, start_time, finish_number, cyclic):
        return self.times[0]  # index of the finish place or just the time then self.times[0][1]

    # for the animation the code should run through every minute and draw the bus on his current position
    def draw_bus(self, screen, minutes):
        count = 0
        try:
            while self.times[count][1] <= minutes:
                count += 1
            count -= 1
            if minutes == self.times[count][1]:
                self.pos_x = (self.times[count][2][0])*WIDTH
                self.pos_y = (self.times[count][2][1])*HEIGHT
            else:
                current = minutes - self.times[count][1]  # 1
                future = self.times[count + 1][1] - self.times[count][1]  # 3
                current_portion = current / future
                self.pos_x = (self.times[count][2][0] * (1 - current_portion) + self.times[count + 1][2][0] * current_portion)*WIDTH
                self.pos_y = (self.times[count][2][1] * (1 - current_portion) + self.times[count + 1][2][1] * current_portion)*HEIGHT
                if self.cyclic:
                    self.draw(screen)
                else:
                    if self.times[count][0] + 1 == self.times[count + 1][0]:
                        self.draw(screen)
        except IndexError:
            pass

    def __repr__(self):
        return f"Bus lane Nr.{dict_names[int(self.times[0][0]) / 100]}"
'''
   


# if __name__ == "__main__":
#     import pygame 
#     i = get_bus_with_color((25, 255, 25))


#     fps = 60
#     fpsClock = pygame.time.Clock()

#     screen = pygame.display.set_mode((1000, 1000))

#     # Game loop.
#     while True:
#         screen.fill((50, 50, 50))
#         screen.blit(i, [10, 10])

#         pygame.display.flip()
#         fpsClock.tick(fps)


# def initialize_classes():
#     pass

# def get_user_input():
#     # pygame Window where User enters input
#     # 2 options: clicking on dots OR typing busstation in
#     # 1_input: depature
#     # 2_input: destination
#     # 3_input: time
#     pass

# def get_surface_text_entry(written_text, ):
#     color_background_of_text_entry = (100, 100, 100)
#     color_text_of_text_entry = (0, 0, 0)
#     text_entry = surface
#     text_entry.fill()
#     txt_surface = font.render(text, True, color)

#     return text_entry