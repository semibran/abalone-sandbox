from enum import Enum, auto
from dataclasses import dataclass, field
from core.board_layout import BoardLayout
import colors.themes as themes

class ControlMode(Enum):
    HUMAN = auto()
    CPU = auto()

@dataclass
class AppConfig:
    starting_layout: BoardLayout = BoardLayout.STANDARD
    colours_inverted: bool = False
    control_modes: tuple[ControlMode, ControlMode] = (ControlMode.HUMAN, ControlMode.CPU)
    move_limits: tuple[int, int] = (50, 50)
    time_limits: tuple[int, int] = (5, 5)
    theme: dict = field(default_factory=lambda: themes.THEME_DEFAULT)
