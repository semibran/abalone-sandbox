from tkinter import Toplevel, StringVar
from tkinter.ttk import Frame, Label, OptionMenu, Button
from core.app_config import AppConfig, ControlMode
from core.board_layout import BoardLayout
import colors.themes as themes

GAME_MODE_MAP = {
    "Human vs. Computer": (ControlMode.HUMAN, ControlMode.CPU),
    "Human vs. Human": (ControlMode.HUMAN, ControlMode.HUMAN),
    "Computer vs. Computer": (ControlMode.CPU, ControlMode.CPU),
}

STARTING_LAYOUT_MAP = {
    "Standard": BoardLayout.STANDARD,
    "German Daisy": BoardLayout.GERMAN_DAISY,
    "Belgian Daisy": BoardLayout.BELGIAN_DAISY,
}

THEME_MAP = {
    "Default": themes.THEME_DEFAULT,
    "Monochrome": themes.THEME_MONOCHROME,
}

class SettingsWindow:

    @staticmethod
    def open(current_config, on_close):
        window = Toplevel()
        window.title("Settings")

        frame = Frame(window, padding=8)
        frame.pack()
        frame_rows = []

        starting_layout = StringVar(frame)
        starting_layouts = [*STARTING_LAYOUT_MAP.keys()]
        frame_rows.append((
            Label(frame, text="Starting Layout"),
            OptionMenu(frame, starting_layout,
                next((k for k, v in STARTING_LAYOUT_MAP.items() if v == current_config.starting_layout), starting_layouts[0]),
                *starting_layouts),
        ))

        game_mode = StringVar(frame)
        game_modes = [*GAME_MODE_MAP.keys()]
        frame_rows.append((
            Label(frame, text="Game Mode"),
            OptionMenu(frame, game_mode,
                next((k for k, v in GAME_MODE_MAP.items() if v == current_config.control_modes), game_modes[0]),
                *game_modes),
        ))

        theme = StringVar(frame)
        themes = [*THEME_MAP.keys()]
        frame_rows.append((
            Label(frame, text="Theme"),
            OptionMenu(frame, theme,
                next((k for k, v in THEME_MAP.items() if v == current_config.theme), themes[0]),
                *themes),
        ))

        for i, (key_widget, value_widget) in enumerate(frame_rows):
            key_widget.grid(column=0, row=i, sticky='e', ipadx=4)
            value_widget.grid(column=1, row=i, sticky='w', ipadx=4, ipady=4)

        Button(frame, text="Confirm", command=lambda: (
            on_close and on_close(AppConfig(
                starting_layout=next((v for k, v in STARTING_LAYOUT_MAP.items() if k == starting_layout.get()), None),
                control_modes=next((v for k, v in GAME_MODE_MAP.items() if k == game_mode.get()), None),
                theme=next((v for k, v in THEME_MAP.items() if k == theme.get()), None),
            )),
            window.destroy(),
        )).grid(columnspan=2, column=0, row=i + 1, pady=8)
