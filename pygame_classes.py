import pygame.font

from classes import *


class PygameObject:
    objects = []

    TEXT_COLOR = (0, 0, 0)
    BACKGROUND_COLOR = (153, 153, 153)
    BORDER_COLOR = (0, 0, 0)
    BORDER_SIZE = 0
    BORDER_DISTANCE = 5

    FONT = pygame.font.Font(None, 32)

    def __init__(self, pos, size, text="NO_TEXT",
                 background_color=BACKGROUND_COLOR, border_color=BORDER_COLOR,
                 border_size=BORDER_SIZE, border_distance=BORDER_DISTANCE):
        self.centered = True
        self.pos = pos
        self.pos_x = pos[0]
        self.pos_y = pos[1]
        self.size = size
        self.width = size[0]
        self.height = size[1]

        self.background_color = background_color
        self.border_color = border_color
        self.border_size = border_size
        self.border_distance = border_distance

        self.update_text(text)

        PygameObject.objects.append(self)

    def update_text(self, new_text):
        self.text = new_text
        text = FONT.render(self.text, True, self.TEXT_COLOR)
        self.txt_surface = pygame.Surface(self.size)
        self.txt_surface.fill(self.background_color)

        position = (5, 5)
        if self.centered:
            position = text.get_rect(center=(self.width / 2, self.height / 2))

        self.txt_surface.blit(text, position)

        self.rect = pygame.Rect(self.pos_x - self.border_distance, self.pos_y - self.border_distance,
                                self.width + self.border_distance * 2, self.height + self.border_distance * 2)

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x + self.border_distance, self.rect.y + self.border_distance))
        # Blit the rect.
        pygame.draw.rect(screen, self.border_color, self.rect, self.border_size)

    def __repr__(self):
        return str(", ".join([self.text, self.pos, self.size]))


class InputBox(PygameObject):
    list_input_boxes = []

    BACKGROUND_COLOR_INACTIVE = (117, 117, 117)
    BACKGROUND_COLOR_ACTIVE = (10, 87, 105)

    BORDER_COLOR = (0, 3, 92)
    BORDER_SIZE = 3
    BORDER_DISTANCE = 3

    MAX_CHARACTERS = 30
    DEFAULT_TEXT = 'SEARCH ...'

    def __init__(self, pos, size, max_characters=MAX_CHARACTERS, text=DEFAULT_TEXT):
        PygameObject.__init__(self, pos=pos, size=size, text=text,
                              background_color=self.BACKGROUND_COLOR_INACTIVE, border_color=self.BORDER_COLOR,
                              border_size=self.BORDER_SIZE, border_distance=self.BORDER_DISTANCE)
        self.max_charachters = max_characters
        self.active = False

        InputBox.list_input_boxes.append(self)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.background_color = self.BACKGROUND_COLOR_ACTIVE if self.active else self.BACKGROUND_COLOR_INACTIVE
            new_text = "" if self.active and self.text == self.DEFAULT_TEXT else self.text
            self.update_text(new_text)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                text = self.text
                self.text = ''
                return text
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif len(self.text) < self.max_charachters:
                self.text += event.unicode
            self.update_text(self.text)


class Label(PygameObject):
    labels = []

    BACKGROUND_COLOR = (138, 85, 62)
    BORDER_COLOR = (0, 0, 0)
    BORDER_SIZE = 3
    BORDER_DISTANCE = 3

    def __init__(self, pos, size, text, text_infront="", click_empty=False):
        PygameObject.__init__(self, pos=pos, size=size, text=str(text_infront + text),
                              background_color=self.BACKGROUND_COLOR, border_color=self.BORDER_COLOR,
                              border_size=self.BORDER_SIZE, border_distance=self.BORDER_DISTANCE)
        self.text_infront = text_infront
        self.centered = False
        self.click_empty = click_empty

        self.update_text(self.text)

        Label.labels.append(self)

    def change_text(self, new_text):
        self.update_text(self.text_infront + new_text)

    def check_collision(self, screen: pygame.Surface, mouse_x, mouse_y):
        if self.click_empty and self.rect.collidepoint((mouse_x, mouse_y)):
            self.update_text(self.text_infront + "")


class Button(PygameObject):
    buttons = []

    BACKGROUND_COLOR = (112, 75, 153)
    BORDER_COLOR = (32, 32, 32)
    BORDER_SIZE = 3
    BORDER_DISTANCE = 3

    def __init__(self, pos, size, text):  # , command=None, *args, **kwargs
        PygameObject.__init__(self, pos=pos, size=size, text=text,
                              background_color=self.BACKGROUND_COLOR, border_color=self.BORDER_COLOR,
                              border_size=self.BORDER_SIZE, border_distance=self.BORDER_DISTANCE)

        # self.command = command
        # self.args = args
        # self.kwargs = kwargs

        self.buttons.append(self)
        self.enabled = True

    def check_collision(self, mouse_x, mouse_y):  # screen: pygame.Surface,  , *args, **kwargs
        if self.enabled:
            return self.rect.collidepoint((mouse_x, mouse_y))
        # if self.command and self.rect.collidepoint((mouse_x, mouse_y)):
        #     return self.command(screen, *args, **kwargs)


class ScrollableTimeBox(PygameObject):
    list_scrollable_time_boxes = []

    BACKGROUND_COLOR = (156, 156, 156)
    BORDER_COLOR = (69, 3, 59)
    BORDER_SIZE = 3
    BORDER_DISTANCE = 3

    def __init__(self, pos, size, time_in_min):
        PygameObject.__init__(self, pos=pos, size=size, text="-",
                              background_color=self.BACKGROUND_COLOR, border_color=self.BORDER_COLOR,
                              border_size=self.BORDER_SIZE, border_distance=self.BORDER_DISTANCE)

        self.time_in_min = time_in_min
        self.generate_and_update_text()

        ScrollableTimeBox.list_scrollable_time_boxes.append(self)

    def generate_and_update_text(self):
        hours = "0" * (2 - len(str(self.time_in_min // 60))) + str(self.time_in_min // 60)
        mins = "0" * (2 - len(str(self.time_in_min % 60))) + str(self.time_in_min % 60)
        new_text = f"{hours} : {mins}"
        self.update_text(new_text)

    def handle_event(self, event):
        if event.type == pygame.MOUSEWHEEL:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                if (pygame.mouse.get_pos()[0] - self.pos_x - (self.width / 2)) >= 0:
                    self.time_in_min = (self.time_in_min + (event.y * 1)) % (24 * 60)
                else:
                    self.time_in_min = (self.time_in_min + (event.y * 60)) % (24 * 60)
                self.generate_and_update_text()
                return self.time_in_min


class SwitchButton(PygameObject):
    switch_buttons = []
    OLD = "alter Busplan"
    NEW = "neuer Busplan"

    TEXT_COLOR = (0, 0, 0)
    BACKGROUND_COLOR = (171, 161, 161)
    BORDER_COLOR = (0, 0, 0)
    BORDER_SIZE = 3
    BORDER_DISTANCE = 3

    def __init__(self, pos, size, list_states, list_colors=False):
        self.list_states = list_states
        self.active_state = list_states[0]
        self.list_colors = list_colors

        background_color = list_colors[0] if list_colors else self.BACKGROUND_COLOR

        PygameObject.__init__(self, pos=pos, size=size, text=str(self.active_state),
                              background_color=background_color, border_color=self.BORDER_COLOR,
                              border_size=self.BORDER_SIZE, border_distance=self.BORDER_DISTANCE)
        self.list_states = list_states
        SwitchButton.switch_buttons.append(self)

    def check_collision(self, screen: pygame.Surface, mouse_x, mouse_y):
        if self.rect.collidepoint((mouse_x, mouse_y)):
            pos_active_state = self.list_states.index(self.active_state)
            new_pos_active_state = (pos_active_state + 1) % len(self.list_states)
            self.active_state = self.list_states[new_pos_active_state]
            if self.list_colors:
                self.background_color = self.list_colors[new_pos_active_state]
            self.update_text(str(self.active_state))
            return True


class Options(PygameObject):
    FONT = pygame.font.Font(None, int(HEIGHT / 24))
    options = []
    bus_image = pygame.transform.scale(pygame.image.load("bilder/bus2.svg"), (HEIGHT / 32, HEIGHT / 32))
    train_image = pygame.transform.scale(pygame.image.load("bilder/rail2.svg"), (HEIGHT / 32, HEIGHT / 32))
    BORDER_SIZE = 5
    DISTANCE_IN_CELL = HEIGHT / 128

    def __init__(self, route, pos, size, new):
        dict_names = dict_names_new if new else dict_names_old
        self.route = route
        _ = [dict_names[int(r.number / 100)] for r in (route.route + [route])]
        self.changes = []
        for i in _:
            if i not in self.changes:
                self.changes.append(i)
        PygameObject.__init__(self, pos=pos, size=size, text="-",
                              background_color=self.BACKGROUND_COLOR, border_color=self.BORDER_COLOR,
                              border_size=self.BORDER_SIZE, border_distance=self.BORDER_DISTANCE)
        Options.options.append(self)

    def update_text(self, _):
        def draw_lane(lane, x, y, last):
            if last:
                text = self.FONT.render(str(lane.name), True, self.TEXT_COLOR)
            else:
                text = self.FONT.render(str(lane.name) + " >", True, self.TEXT_COLOR)
            if x + text.get_width() + self.bus_image.get_width() + self.DISTANCE_IN_CELL > self.width:
                x = self.DISTANCE_IN_CELL
                y += self.DISTANCE_IN_CELL + self.bus_image.get_height()
            if lane.is_bus:
                self.txt_surface.blit(self.bus_image, (x, y))  # (HEIGHT / 64, HEIGHT / 64))
            else:
                self.txt_surface.blit(self.train_image, (x, y))
            x += self.bus_image.get_width() + self.DISTANCE_IN_CELL
            self.txt_surface.blit(text, (x, y))
            x += text.get_width() + self.DISTANCE_IN_CELL
            return x, y

        self.txt_surface = pygame.Surface(self.size)
        self.txt_surface.fill(self.background_color)
        lanes = [Lane.get_lane_by_name(i, self.route.new) for i in self.changes]
        # anders machen wegen transit
        x, y = self.DISTANCE_IN_CELL, self.DISTANCE_IN_CELL
        for lane in lanes:
            x, y = draw_lane(lane, x, y, lane == lanes[-1])

        self.txt_surface.blit(self.FONT.render(
            f"{int(self.route.distance_to_start)} minuten, "
            f"{'0' * (2 - len(str(int(self.route.route[0].time / 60)))) + str(int(self.route.route[0].time / 60))}:"
            f"{'0' * (2 - len(str(int(self.route.route[0].time % 60)))) + str(int(self.route.route[0].time % 60))}h",
            True, self.TEXT_COLOR),
            (self.DISTANCE_IN_CELL, 3 * self.DISTANCE_IN_CELL + self.bus_image.get_height() * 2))

        self.rect = pygame.Rect(self.pos_x - self.border_distance, self.pos_y - self.border_distance,
                                self.width + self.border_distance * 2, self.height + self.border_distance * 2)

    def check_collision(self, mouse_x, mouse_y):
        if self.rect.collidepoint((mouse_x, mouse_y)):
            return True

    def __repr__(self):
        return f"options of {self.route}"
