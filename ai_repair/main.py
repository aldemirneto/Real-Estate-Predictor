"""
Entry point for the AI repair pipeline.

Usage:
    uv run python -m ai_repair.main              # check all active scrapers
    uv run python -m ai_repair.main FriasNeto    # repair a specific scraper
"""
import sys

from Log.Logging import Logging
from ai_repair.detector import ScraperDetector
from ai_repair.pr_creator import PRCreator
from ai_repair.repairer import ScraperRepairer


def run(target: str | None = None) -> None:
    log = Logging()
    detector = ScraperDetector()
    repairer = ScraperRepairer()
    pr_creator = PRCreator()

    if target:
        log.log(f"Forcing repair check for: {target}")
        is_broken, error, html = detector.check_scraper(target)
        if not is_broken:
            log.log(f"{target} is working correctly — no repair needed.")
            return
        broken = [(target, error, html)]
    else:
        log.log("Running scraper health check...")
        broken = detector.find_broken()

    if not broken:
        log.log("All scrapers are healthy. Nothing to repair.")
        return

    log.log(f"Found {len(broken)} broken scraper(s). Starting AI repair...")

    for name, error, html in broken:
        log.log(f"Repairing {name}...")
        try:
            fixed_code = repairer.repair(name, error, html)
            log.log(f"AI fix generated for {name}. Opening PR...")
            pr_url = pr_creator.create(name, fixed_code, error)
            log.log(f"PR opened: {pr_url}")
        except Exception as e:
            log.log(f"Failed to repair {name}: {e}")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    run(target)
