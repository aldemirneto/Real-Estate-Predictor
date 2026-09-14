"""
Sends a broken scraper + current site HTML to Claude and returns the fixed source code.
"""
import re
from pathlib import Path

import anthropic

MODEL = "claude-opus-4-8"
MAX_HTML_CHARS = 12_000


class ScraperRepairer:
    def __init__(self):
        self.client = anthropic.Anthropic()

    def repair(self, scraper_name: str, error: str, html_sample: str) -> str:
        """
        Asks Claude to fix the scraper. Returns the complete fixed Python file as a string.
        Raises ValueError if Claude's response does not contain valid Python code.
        """
        scraper_path = Path(f"Extract/{scraper_name}Scraper.py")
        current_code = scraper_path.read_text(encoding="utf-8")
        base_scraper = Path("Extract/BaseScraper.py").read_text(encoding="utf-8")

        prompt = f"""You are a Python web scraping expert.

The scraper below has stopped working. Your job is to fix it so it correctly
extracts real estate listings from the current HTML of the website.

## BaseScraper (do not modify — for reference only)
```python
{base_scraper}
```

## Broken scraper: Extract/{scraper_name}Scraper.py
```python
{current_code}
```

## Error encountered when running the scraper
```
{error[:2000]}
```

## Current HTML from the website (first {MAX_HTML_CHARS} chars)
```html
{html_sample[:MAX_HTML_CHARS]}
```

## Requirements
- Fix `set_breakpoint` and `parse_page` to work with the current HTML structure.
- Keep the same output dict keys: preco, area, quartos, vagas, banheiros, bairro, tipo, Status, link, Imobiliaria.
- preco must be a Python float or None.
- Do NOT change the class name or the Imobiliaria value.
- Do NOT modify BaseScraper.
- Return ONLY the complete fixed Python file with no explanation, no markdown fences.
"""

        message = self.client.messages.create(
            model=MODEL,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )

        raw = message.content[0].text.strip()

        # Strip markdown fences if Claude added them despite instructions
        raw = re.sub(r"^```python\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        if "def parse_page" not in raw:
            raise ValueError(f"Claude response does not look like valid Python:\n{raw[:500]}")

        return raw
