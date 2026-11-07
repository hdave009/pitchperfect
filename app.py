import matplotlib

matplotlib.use("Agg")  # Headless backend safety lock

import pygame
import sys
from audio_listener import AudioListener
from melody_generator import MelodyGenerator
from database import init_db, get_all_users, create_user, save_score, get_user_history
from helpers import draw_staff, draw_sharp_symbol
from visualization import create_trend_chart_surface

import os


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller bundle."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


# Initialize Pygame & Database
pygame.init()
init_db()

WIDTH, HEIGHT = 900, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PitchPerfect - Sheet Music Sight Reader")
clock = pygame.time.Clock()

# Fonts
FONT_TITLE = pygame.font.SysFont(None, 56)
FONT_LARGE = pygame.font.SysFont(None, 70)
FONT_MEDIUM = pygame.font.SysFont(None, 28)
FONT_SMALL = pygame.font.SysFont(None, 20)

# Colors
BG_COLOR = (35, 35, 40)
WHITE = (240, 240, 240)
GRAY = (120, 120, 130)
STAFF_COLOR = (200, 200, 210)
RED = (220, 80, 80)
GREEN = (80, 200, 120)
BLUE = (70, 130, 180)
NOTE_BLACK = (230, 230, 240)

# Use it when loading images:
try:
    clef_path = resource_path("treble_clef.png")
    clef_image = pygame.image.load(clef_path).convert_alpha()
    clef_image = pygame.transform.smoothscale(clef_image, (50, 130))
except Exception:
    clef_image = None

melody_generator = MelodyGenerator(root_note="G", octave=4, scale_type="major")
NOTE_DECK = []

NOTE_OFFSETS = {
    "C4": 6,
    "C#4": 6,
    "D4": 5,
    "D#4": 5,
    "E4": 4,
    "F4": 3,
    "F#4": 3,
    "G4": 2,
    "G#4": 2,
    "A4": 1,
    "A#4": 1,
    "B4": 0,
    "C5": -1,
    "C#5": -1,
    "D5": -2,
    "D#5": -2,
    "E5": -3,
    "F5": -4,
    "F#5": -4,
    "G5": -5,
    "G#5": -5,
    "A5": -6,
}


def draw_note_on_staff(surface, note_name, staff_lines, line_spacing, center_x):
    if note_name not in NOTE_OFFSETS:
        return
    offset_index = NOTE_OFFSETS[note_name]
    middle_line_y = staff_lines[2]
    note_y = middle_line_y + (offset_index * (line_spacing / 2))
    is_on_line = offset_index % 2 == 0
    radius = 8 if not is_on_line else 9

    if "#" in note_name:
        draw_sharp_symbol(surface, NOTE_BLACK, center_x - 18, int(note_y))

    pygame.draw.circle(surface, NOTE_BLACK, (center_x, int(note_y)), radius)

    if note_name in ["C4", "C#4", "Cb4"]:
        pygame.draw.line(
            surface, STAFF_COLOR, (center_x - 16, note_y), (center_x + 16, note_y), 2
        )
    elif note_name in ["A5", "A#5", "Ab5"]:
        pygame.draw.line(
            surface, STAFF_COLOR, (center_x - 16, note_y), (center_x + 16, note_y), 2
        )


def main():
    global NOTE_DECK
    listener = AudioListener(device_index=1)
    listener.start()

    game_state = "PROFILE_SELECT"
    current_user = None
    input_name = ""

    current_card_index = 0
    total_notes_attempted = 0
    score_saved = False
    cached_chart_surf = None
    last_processed_note = None

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if game_state == "PROFILE_SELECT":
                    if event.key == pygame.K_n:
                        game_state = "NEW_PROFILE"
                        input_name = ""
                    elif event.key == pygame.K_RETURN:
                        users = get_all_users()
                        if users:
                            current_user = users[0]
                            NOTE_DECK = melody_generator.generate_progression(length=8)
                            game_state = "PLAYING"
                            current_card_index = 0
                            total_notes_attempted = 0
                            last_processed_note = None
                            score_saved = False
                            cached_chart_surf = None

                elif game_state == "NEW_PROFILE":
                    if event.key == pygame.K_RETURN:
                        if input_name.strip():
                            user_id = create_user(input_name.strip())
                            current_user = (user_id, input_name.strip())
                            NOTE_DECK = melody_generator.generate_progression(length=8)
                            game_state = "PLAYING"
                            current_card_index = 0
                            total_notes_attempted = 0
                            last_processed_note = None
                            score_saved = False
                            cached_chart_surf = None
                    elif event.key == pygame.K_BACKSPACE:
                        input_name = input_name[:-1]
                    elif event.key == pygame.K_ESCAPE:
                        game_state = "PROFILE_SELECT"
                    else:
                        if len(input_name) < 15 and event.unicode.isprintable():
                            input_name += event.unicode

                elif game_state == "COMPLETE":
                    if event.key == pygame.K_RETURN:
                        NOTE_DECK = melody_generator.generate_progression(length=8)
                        current_card_index = 0
                        total_notes_attempted = 0
                        last_processed_note = None
                        score_saved = False
                        cached_chart_surf = None
                        game_state = "PLAYING"
                    elif event.key == pygame.K_ESCAPE:
                        game_state = "PROFILE_SELECT"

        # Audio polling & gameplay logic
        target_note = None
        if (
            game_state == "PLAYING"
            and NOTE_DECK
            and current_card_index < len(NOTE_DECK)
        ):
            target_note = NOTE_DECK[current_card_index]

        heard_note, heard_freq, confidence = listener.get_current_note()

        if game_state == "PLAYING" and target_note:
            if heard_note:
                if heard_note != last_processed_note:
                    total_notes_attempted += 1
                    last_processed_note = heard_note

                    if heard_note == target_note:
                        current_card_index += 1
                        last_processed_note = None
                        if current_card_index >= len(NOTE_DECK):
                            game_state = "COMPLETE"
            else:
                last_processed_note = None

        # Drawing UI
        screen.fill(BG_COLOR)

        if game_state == "PROFILE_SELECT":
            title_surf = FONT_TITLE.render("PitchPerfect", True, WHITE)
            sub_surf = FONT_MEDIUM.render("Select Profile to Start", True, BLUE)
            users = get_all_users()

            screen.blit(
                title_surf, (WIDTH // 2 - title_surf.get_width() // 2, HEIGHT // 3 - 50)
            )
            screen.blit(
                sub_surf, (WIDTH // 2 - sub_surf.get_width() // 2, HEIGHT // 3 + 20)
            )

            if users:
                user_text = FONT_MEDIUM.render(
                    f"Current Player: {users[0][1]}", True, WHITE
                )
                prompt_surf = FONT_MEDIUM.render(
                    "Press [ENTER] to Play or [N] for New Profile", True, GRAY
                )
                screen.blit(
                    user_text, (WIDTH // 2 - user_text.get_width() // 2, HEIGHT // 2)
                )
                screen.blit(
                    prompt_surf,
                    (WIDTH // 2 - prompt_surf.get_width() // 2, HEIGHT // 2 + 50),
                )
            else:
                prompt_surf = FONT_MEDIUM.render(
                    "Press [N] to Create Your First Profile", True, WHITE
                )
                screen.blit(
                    prompt_surf,
                    (WIDTH // 2 - prompt_surf.get_width() // 2, HEIGHT // 2),
                )

        elif game_state == "NEW_PROFILE":
            title_surf = FONT_TITLE.render("New Profile", True, WHITE)
            prompt_surf = FONT_MEDIUM.render(
                "Enter your name, then press [ENTER]:", True, GRAY
            )
            name_surf = FONT_LARGE.render(input_name + "_", True, GREEN)

            screen.blit(
                title_surf, (WIDTH // 2 - title_surf.get_width() // 2, HEIGHT // 3 - 40)
            )
            screen.blit(
                prompt_surf,
                (WIDTH // 2 - prompt_surf.get_width() // 2, HEIGHT // 3 + 40),
            )
            screen.blit(
                name_surf, (WIDTH // 2 - name_surf.get_width() // 2, HEIGHT // 2)
            )

        elif game_state == "PLAYING":
            player_name = current_user[1] if current_user else "Player"
            player_surf = FONT_SMALL.render(f"Player: {player_name}", True, BLUE)
            card_display_num = min(current_card_index + 1, len(NOTE_DECK))
            progress_surf = FONT_SMALL.render(
                f"Note {card_display_num} of {len(NOTE_DECK)}", True, GRAY
            )
            screen.blit(player_surf, (50, 30))
            screen.blit(progress_surf, (750, 30))

            instr_surf = FONT_MEDIUM.render(
                "Read the staff and play the note:", True, WHITE
            )
            screen.blit(instr_surf, (WIDTH // 2 - instr_surf.get_width() // 2, 80))

            board_rect = pygame.Rect(150, 140, 600, 220)
            pygame.draw.rect(screen, (45, 45, 55), board_rect, border_radius=12)
            pygame.draw.rect(screen, BLUE, board_rect, width=2, border_radius=12)

            if clef_image:
                screen.blit(clef_image, (175, 185))
            else:
                fallback_surf = FONT_MEDIUM.render("𝄞", True, WHITE)
                screen.blit(fallback_surf, (180, 220))

            staff_lines, line_spacing = draw_staff(
                screen, STAFF_COLOR, start_x=240, start_y=200, width=460
            )

            if target_note:
                draw_note_on_staff(
                    screen, target_note, staff_lines, line_spacing, center_x=470
                )

            status_text = "Listening for your piano..."
            status_color = GRAY

            if heard_note:
                status_text = f"Heard: {heard_note} ({heard_freq:.1f} Hz)"
                if heard_note == target_note:
                    status_color = GREEN
                    status_text = f"Correct! ({heard_note})"
                else:
                    status_color = RED

            feedback_surf = FONT_MEDIUM.render(status_text, True, status_color)
            screen.blit(
                feedback_surf,
                (WIDTH // 2 - feedback_surf.get_width() // 2, HEIGHT - 120),
            )

        elif game_state == "COMPLETE":
            accuracy = len(NOTE_DECK) / max(total_notes_attempted, len(NOTE_DECK)) * 100

            if current_user and not score_saved:
                save_score(current_user[0], accuracy, len(NOTE_DECK))
                score_saved = True
                history = get_user_history(current_user[0])
                cached_chart_surf = create_trend_chart_surface(
                    history, width=520, height=180
                )

            win_surf = FONT_TITLE.render("Melody Complete!", True, GREEN)
            acc_surf = FONT_MEDIUM.render(f"Accuracy: {accuracy:.1f}%", True, WHITE)

            screen.blit(win_surf, (WIDTH // 2 - win_surf.get_width() // 2, 30))
            screen.blit(acc_surf, (WIDTH // 2 - acc_surf.get_width() // 2, 95))

            if cached_chart_surf:
                screen.blit(
                    cached_chart_surf,
                    (WIDTH // 2 - cached_chart_surf.get_width() // 2, 140),
                )

            restart_surf = FONT_MEDIUM.render(
                "Press [ENTER] to Play Again or [ESC] for Menu", True, WHITE
            )
            screen.blit(
                restart_surf, (WIDTH // 2 - restart_surf.get_width() // 2, HEIGHT - 60)
            )

        pygame.display.flip()
        clock.tick(60)

    listener.stop()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
