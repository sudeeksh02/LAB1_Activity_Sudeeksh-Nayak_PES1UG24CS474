from dataclasses import dataclass, field
from typing import Optional, Tuple

@dataclass
class RoundResult:
    """Encapsulates telemetry collected during a single reflex trial."""
    round_number: int
    mode_name: str
    stimulus_time_ms: int
    response_time_ms: int
    is_false_start: bool = False
    is_timeout: bool = False
    is_correct_go: bool = True
    target_pos: Optional[Tuple[int, int]] = None
    click_pos: Optional[Tuple[int, int]] = None
    distance_error_px: float = 0.0

    @property
    def latency_ms(self) -> int:
        if self.is_false_start or self.is_timeout or not self.is_correct_go:
            return 0
        return max(0, self.response_time_ms - self.stimulus_time_ms)
