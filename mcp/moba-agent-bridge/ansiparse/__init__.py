import re
import logging

ANSI_PATTERN = re.compile(
    r"\x1b\[[0-9;]*[a-zA-Z]"       
    r"|\x1b\][0-9]*;[^\x07]*\x07"  
    r"|\x1b[PX^_].*?\x1b\\"        
    r"|\x1b\[[?]?\d*[hl]"          
    r"|\x1b[=>]"                    
    r"|\x1b\([0-9A-Za-z]"           
    r"|\x1b7|\x1b8"                 
    r"|\x1b[DEHMNOVWZa-v]|"         
    r"|\r\x1b\[K"                   
    r"|\x1b\[2J|\x1b\[H"            
    r"|\x1b\[1J"                    
    r"|\x0f"                        
    r"|\x1b\(B"                     
    r"|\x1b\[0m"                    
    r"|\x1b\(0"                     
    r"|\x1b\(U"                     
    r"|\x1b\]0[^\x07\x1b]*[\x07\x1b]?"  
    r"|\x1b\[[0-9;]*[GKr]"          
    r"|\x1b\[[0-9;]*[df]"           
    r"|\x07",                       # BEL
    re.VERBOSE
)

BACKSPACE_PATTERN = re.compile(r"[^\x08]\x08")
CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def strip_ansi(text: str) -> str:
    if not text:
        return text
    text = ANSI_PATTERN.sub("", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    for _ in range(10):
        new = BACKSPACE_PATTERN.sub("", text)
        if new == text:
            break
        text = new
    text = text.replace("\b", "")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def contains_ansi(text: str) -> bool:
    return bool(ANSI_PATTERN.search(text))


def extract_lines(raw: str) -> list[str]:
    cleaned = strip_ansi(raw)
    return [l for l in cleaned.split("\n") if l.strip()]


def sanitize_control_chars(text: str, keep_newline: bool = True) -> str:
    result = []
    for ch in text:
        code = ord(ch)
        if code == 0x0a:
            result.append(ch)
        elif keep_newline and code in (0x0d,):
            continue
        elif code < 0x20 and code not in (0x0a, 0x0d, 0x09):
            result.append(f"\\x{code:02x}")
        else:
            result.append(ch)
    return "".join(result)
