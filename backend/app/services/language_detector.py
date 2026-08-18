# ============================================================
# Language Detector Service — Heuristic + Pygments
# ============================================================

import re
import logging
from typing import Optional
from pygments.lexers import guess_lexer, get_lexer_by_name
from pygments.util import ClassNotFound

logger = logging.getLogger(__name__)

# Canonical language normalization mapping
LANGUAGE_MAP = {
    # Python
    "python": "python",
    "python3": "python",
    "py": "python",
    # JavaScript & TypeScript
    "javascript": "javascript",
    "js": "javascript",
    "jsx": "javascript",
    "typescript": "typescript",
    "ts": "typescript",
    "tsx": "typescript",
    # Java & Kotlin
    "java": "java",
    "kotlin": "kotlin",
    # Go
    "go": "go",
    "golang": "go",
    # Rust & C / C++
    "rust": "rust",
    "rs": "rust",
    "c": "c",
    "cpp": "cpp",
    "c++": "cpp",
    "csharp": "csharp",
    "c#": "csharp",
    # Web & Scripts
    "html": "html",
    "css": "css",
    "php": "php",
    "ruby": "ruby",
    "rb": "ruby",
    "shell": "shell",
    "bash": "shell",
    "sh": "shell",
    "sql": "sql",
    "json": "json",
    "yaml": "yaml",
}


def detect_language(code: str, hint: Optional[str] = None) -> str:
    """
    Detect the programming language of a code snippet using hints, heuristics, and Pygments.
    """
    if not code or not code.strip():
        return "text"

    # 1. Check explicit hint if provided
    if hint:
        normalized_hint = hint.strip().lower()
        if normalized_hint in LANGUAGE_MAP:
            return LANGUAGE_MAP[normalized_hint]

    clean_code = code.strip()

    # 2. Fast heuristic regex pattern matching
    # Go
    if re.search(r"^\s*package\s+[a-zA-Z0-9_]+", clean_code, re.MULTILINE) and "func " in clean_code:
        return "go"

    # Java / C#
    if re.search(r"public\s+class\s+[A-Z][a-zA-Z0-9_]*", clean_code) and (
        "System.out.println" in clean_code or "public static void main" in clean_code
    ):
        return "java"

    # TypeScript (explicit type annotations, interfaces)
    if re.search(r"interface\s+[A-Z][a-zA-Z0-9_]*\s*\{", clean_code) or re.search(
        r":\s*(string|number|boolean|Record<|Array<)[;,\s=)]", clean_code
    ):
        return "typescript"

    # Python
    if (
        re.search(r"^\s*(async\s+def|def|class)\s+[a-zA-Z0-9_]+", clean_code, re.MULTILINE)
        or re.search(r"^\s*(import\s+[a-zA-Z0-9_]+|from\s+[a-zA-Z0-9_]+\s+import)", clean_code, re.MULTILINE)
    ):
        # Ensure it's not JS 'import ... from ...'
        if not re.search(r"import\s+.*?from\s+['\"][^'\"]+['\"];?", clean_code):
            return "python"

    # JavaScript
    if re.search(r"(const|let|var)\s+[a-zA-Z0-9_]+\s*=", clean_code) or "console.log" in clean_code:
        return "javascript"

    # Rust
    if re.search(r"fn\s+[a-zA-Z0-9_]+\s*\(.*?\)\s*(->\s*.*?)?\{", clean_code) and (
        "let mut " in clean_code or "println!" in clean_code or "impl " in clean_code
    ):
        return "rust"

    # 3. Fallback to Pygments lexer guess
    try:
        lexer = guess_lexer(clean_code)
        guessed_name = lexer.aliases[0].lower() if lexer.aliases else lexer.name.lower()
        for key, val in LANGUAGE_MAP.items():
            if key in guessed_name:
                return val
        return guessed_name
    except (ClassNotFound, Exception):
        pass

    return "python"  # Default fallback
