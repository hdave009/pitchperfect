import pygame


def draw_staff(surface, staff_color, start_x, start_y, width):
    """Draws the 5 horizontal lines of a standard musical staff pixel by pixel."""
    line_spacing = 16
    staff_lines = []
    for i in range(5):
        y = start_y + (i * line_spacing)
        staff_lines.append(y)
        pygame.draw.line(surface, staff_color, (start_x, y), (start_x + width, y), 2)
    return staff_lines, line_spacing


def draw_sharp_symbol(surface, color, x, y):
    """Draws a clean, vector-based sharp sign (♯) using Pygame lines."""
    pygame.draw.line(surface, color, (x, y - 9), (x, y + 9), 2)
    pygame.draw.line(surface, color, (x + 6, y - 9), (x + 6, y + 9), 2)
    pygame.draw.line(surface, color, (x - 3, y - 2), (x + 9, y - 5), 2)
    pygame.draw.line(surface, color, (x - 3, y + 4), (x + 9, y + 1), 2)
