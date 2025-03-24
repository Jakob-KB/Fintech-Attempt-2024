# TradeManager.py
from dataclasses import dataclass, asdict
from datetime import datetime
import json


@dataclass
class TradeLogEntry:
    day: int
    instrument: str
    intended_position: int
    adjusted_position: int
    action: str  # e.g., "open_long", "open_short", "close", "reverse"
    impact_flag: bool = False  # Flag if significant adjustment occurred
    reason: str = ""
    timestamp: str = datetime.now().isoformat()

    def to_dict(self):
        return asdict(self)


class TradeLogger:
    def __init__(self):
        # Logs organized by day then instrument
        self.logs = {}  # Structure: { "day_0": { "Instrument": [TradeLogEntry, ...], ... }, ... }

    def log_trade(self, trade: TradeLogEntry):
        day_key = f"day_{trade.day}"
        if day_key not in self.logs:
            self.logs[day_key] = {}
        if trade.instrument not in self.logs[day_key]:
            self.logs[day_key][trade.instrument] = []
        self.logs[day_key][trade.instrument].append(trade)

    def save_logs(self, filename="trade_logs.json"):
        json_logs = {
            day: {
                instr: [entry.to_dict() for entry in entries]
                for instr, entries in instruments.items()
            } for day, instruments in self.logs.items()
        }
        with open(filename, 'w') as f:
            json.dump(json_logs, f, indent=4)


class TradeManager:
    def __init__(self, position_limits, current_positions):
        self.position_limits = position_limits
        # Make a copy of current_positions so you don't accidentally modify the original
        self.current_positions = current_positions.copy()
        self.logger = TradeLogger()

    def validate_and_log(self, day, instrument, intended_position):
        current = self.current_positions.get(instrument, 0)
        limit = self.position_limits[instrument]
        adjusted = intended_position
        reason = ""
        action = "open"

        # Check against position limits
        if abs(intended_position) > limit:
            adjusted = limit if intended_position > 0 else -limit
            reason = f"Intended position {intended_position} exceeds limit {limit}"

        # Detect reversal (existing position and intended have opposite signs)
        if current != 0 and (current * intended_position < 0):
            reason += "; reversal detected: closing existing position then opening new one"
            action = "reverse"

        # Determine if adjustment is significant (e.g. more than 5% change)
        impact_flag = abs(adjusted - intended_position) / (abs(intended_position) + 1e-6) > 0.05

        entry = TradeLogEntry(
            day=day,
            instrument=instrument,
            intended_position=intended_position,
            adjusted_position=adjusted,
            action=action,
            impact_flag=impact_flag,
            reason=reason
        )
        # Log the trade decision
        self.logger.log_trade(entry)
        # Update the stored position
        self.current_positions[instrument] = adjusted
        return adjusted

    def save_trade_logs(self, filename="trade_logs.json"):
        self.logger.save_logs(filename)
