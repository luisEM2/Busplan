import pygame
from pygame.locals import *
import xlrd

pygame.init()
pygame.font.init()
info = pygame.display.Info()
WIDTH = info.current_w
HEIGHT = info.current_h

DEFAULT_CHANGE = 2
FONT = pygame.font.Font(None, 32)
COLOR_INACTIVE = (150, 150, 150)
COLOR_ACTIVE = (100, 100, 100)
FILEPATH_OLD = r"excel\busplan_alt.xlsx"
FILEPATH_NEW = r"excel\busplan_neu.xlsx"
ITERATIONS = 3
dict_names_old = {}
with xlrd.open_workbook(FILEPATH_OLD) as file:
    for sheet in file.sheets():
        try:
            dict_names_old[sheet.cell_value(0, 1)]
        except KeyError:
            dict_names_old.update({sheet.cell_value(0, 1): sheet.cell_value(0, 2)})

dict_names_new = {}
with xlrd.open_workbook(FILEPATH_NEW) as file:
    for sheet in file.sheets():
        try:
            dict_names_new[sheet.cell_value(0, 1)]
        except KeyError:
            dict_names_new.update({sheet.cell_value(0, 1): sheet.cell_value(0, 2)})
