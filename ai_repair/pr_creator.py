"""
Commits a fixed scraper to a new branch and opens a GitHub PR.
"""
import subprocess
from pathlib import Path


class PRCreator:
    def __init__(self, base_branch: str = "main"):
        self.base_branch = base_branch

    def _run(self, *args: str) -> str:
        result = subprocess.run(list(args), capture_output=True, text=True, check=True)
        return result.stdout.strip()

    def create(self, scraper_name: str, fixed_code: str, error_summary: str) -> str:
        """
        Writes fixed_code to the scraper file, creates a branch, commits, pushes,
        and opens a PR. Returns the PR URL.
        """
        branch = f"fix/auto-repair-{scraper_name.lower()}-scraper"
        scraper_path = Path(f"Extract/{scraper_name}Scraper.py")

        # Make sure we start from a clean base
        self._run("git", "checkout", self.base_branch)
        self._run("git", "pull", "origin", self.base_branch)

        # Create or reset the fix branch
        existing = self._run("git", "branch", "--list", branch)
        if existing:
            self._run("git", "branch", "-D", branch)
        self._run("git", "checkout", "-b", branch)

        scraper_path.write_text(fixed_code, encoding="utf-8")
        self._run("git", "add", str(scraper_path))
        self._run(
            "git", "commit", "-m",
            f"fix: auto-repair {scraper_name}Scraper broken selectors\n\n"
            f"Co-Authored-By: Claude Opus <noreply@anthropic.com>",
        )
        self._run("git", "push", "-u", "origin", branch)

        body = (
            f"## Auto-repair: {scraper_name}Scraper\n\n"
            f"The scraper was detected as broken by the AI repair module.\n\n"
            f"### Error summary\n```\n{error_summary[:800]}\n```\n\n"
            f"### What changed\n"
            f"Claude inspected the current HTML structure of the website and rewrote "
            f"`set_breakpoint` and `parse_page` to match.\n\n"
            f"**Please review the diff before merging** — AI-generated code may need "
            f"minor adjustments.\n\n"
            f"🤖 Generated with [Claude Code](https://claude.ai/claude-code)"
        )

        pr_url = self._run(
            "gh", "pr", "create",
            "--title", f"fix: auto-repair {scraper_name}Scraper",
            "--body", body,
            "--base", self.base_branch,
            "--head", branch,
        )

        # Return to base branch
        self._run("git", "checkout", self.base_branch)
        return pr_url
