import re
import logging
from typing import Optional, Pattern

logger = logging.getLogger(__name__)

DEFAULT_PROMPTS: list[str] = [
    r"\$\s*$",
    r"#\s*$",
    r">\s*$",
    r">>>\s*$",
    r"]\?\s*$",
    r"login:\s*$",
    r"Login:\s*$",
    r"password:\s*$",
    r"Password:\s*$",
    r"Press\s+any\s+key.*$",
    r"\[yes/no\]\?\s*$",
    r"Continue\?.*$",
    r"\.\.\.\s*$",
    r"boot\s*>\s*$",
    r"uboot>\s*$",
    r"U-Boot>\s*$",
    r"BOOT\d*>\s*$",
    r"AT>\s*$",
    r"OK\r?\n$",
    r"ERROR\r?\n$",
    r"FAIL\r?\n$",
]


class PromptDetector:
    def __init__(self, custom_prompts: Optional[list[str]] = None):
        self._patterns: list[Pattern] = []
        prompts = list(DEFAULT_PROMPTS)
        if custom_prompts:
            prompts.extend(custom_prompts)
        for p in prompts:
            try:
                self._patterns.append(re.compile(p, re.IGNORECASE | re.MULTILINE))
            except re.error as e:
                logger.warning("Invalid prompt pattern %r: %s", p, e)

    def add_pattern(self, pattern: str) -> bool:
        try:
            self._patterns.append(re.compile(pattern, re.IGNORECASE | re.MULTILINE))
            return True
        except re.error:
            return False

    def detect(self, text: str) -> Optional[str]:
        for pat in self._patterns:
            m = pat.search(text)
            if m:
                return m.group(0)
        return None

    def has_prompt(self, text: str) -> bool:
        return self.detect(text) is not None

    def find_last_prompt(self, text: str) -> Optional[str]:
        best_match = None
        best_pos = -1
        for pat in self._patterns:
            for m in pat.finditer(text):
                if m.start() > best_pos:
                    best_pos = m.start()
                    best_match = m.group(0)
        return best_match


_prompt_detector: Optional[PromptDetector] = None


def get_detector(custom_prompts: Optional[list[str]] = None) -> PromptDetector:
    global _prompt_detector
    if _prompt_detector is None or custom_prompts:
        _prompt_detector = PromptDetector(custom_prompts)
    return _prompt_detector
