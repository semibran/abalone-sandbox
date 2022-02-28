from tkinter import Toplevel, StringVar
from tkinter.ttk import Frame, Label, OptionMenu, Button
from core.app_config import AppConfig, ControlMode

GAME_MODES = {
    "Human vs. Computer": (ControlMode.HUMAN, ControlMode.CPU),
    "Human vs. Human": (ControlMode.HUMAN, ControlMode.HUMAN),
    "Computer vs. Computer": (ControlMode.CPU, ControlMode.CPU),
}

class SettingsWindow:

    @staticmethod
    def open(on_close):
        window = Toplevel()
        window.title("Settings")

        frame = Frame(window, padding=8)
        frame.pack()
        frame_rows = []

        game_mode = StringVar(frame)
        game_modes = [*GAME_MODES.keys()]
        frame_rows.append((
            Label(frame, text="Game Mode"),
            OptionMenu(frame, game_mode, game_modes[0], *game_modes),
        ))

        for i, (key_widget, value_widget) in enumerate(frame_rows):
            key_widget.grid(column=0, row=i, sticky='e', ipadx=4)
            value_widget.grid(column=1, row=i, sticky='w', ipadx=4)

        Button(frame, text="Confirm", command=on_close and (lambda: (
            on_close(AppConfig(
                control_modes=next((v for k, v in GAME_MODES.items() if k == game_mode.get()), None)
            )),
            window.destroy(),
        ))).grid(columnspan=2, column=0, row=i + 1, pady=8)
