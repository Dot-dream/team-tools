import re
import logging
from typing import Optional, Pattern, Callable
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class EventRule:
    name: str
    pattern: Pattern
    callback: Optional[Callable] = None


class EventDetector:
    def __init__(self, rules: Optional[list[EventRule]] = None):
        self.rules: list[EventRule] = rules or []
        self._add_builtin_rules()

    def _add_builtin_rules(self):
        builtins = [
            ("error", r"(?i)\b(error|fail|fatal|exception)\b"),
            ("success", r"(?i)\b(success|ok|done|complete)\b"),
            ("timeout", r"(?i)\b(timeout|timed?\s*out)\b"),
            ("reboot", r"(?i)\b(reboot|reset|restarting)\b"),
            ("crash", r"(?i)\b(panic|coredump|segfault|assert(ion)?\s*fail)"),
        ]
        for name, pattern_str in builtins:
            try:
                p = re.compile(pattern_str)
                self.rules.append(EventRule(name=name, pattern=p))
            except re.error:
                pass

    def add_rule(self, name: str, pattern: str) -> bool:
        try:
            p = re.compile(pattern)
            self.rules.append(EventRule(name=name, pattern=p))
            return True
        except re.error:
            return False

    def detect(self, text: str) -> list[EventRule]:
        matched = []
        for rule in self.rules:
            if rule.pattern.search(text):
                matched.append(rule)
        return matched

    def detect_names(self, text: str) -> list[str]:
        return [r.name for r in self.detect(text)]
