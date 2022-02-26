from dataclasses import dataclass
from enum import Enum, auto

class BoardLayout(Enum):
    STANDARD = "layouts/standard.json"
    GERMAN_DAISY = auto()
    BELGIAN_DAISY = auto()

class ControlMode(Enum):
    Human = auto()
    Cpu = auto()

@dataclass
class AppConfig:
    starting_layout: BoardLayout = BoardLayout.STANDARD
    colours_inverted: bool = False
    control_modes: tuple[ControlMode, ControlMode] = (ControlMode.Human, ControlMode.Cpu)
    move_limits: tuple[int, int] = (50, 50)
    time_limits: tuple[int, int] = (5, 5)
