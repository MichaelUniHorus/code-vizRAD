"""Generate demo GIF for README."""

from __future__ import annotations

import asyncio
import subprocess
from pathlib import Path

from playwright.async_api import async_playwright

OUTPUT_DIR = Path(__file__).parent.parent / "examples" / "demo_output"
OUTPUT_DIR.mkdir(exist_ok=True)


async def capture_screenshots() -> list[Path]:
    """Capture screenshots of code-viz visualization."""
    sample_project = Path(__file__).parent.parent / "examples" / "sample_project"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1400, "height": 900})
        page = await context.new_page()

        # Generate visualization
        subprocess.run(
            [
                "code-viz",
                "analyze",
                str(sample_project),
                "--no-open",
                "--output",
                str(OUTPUT_DIR),
            ],
            check=True,
        )

        html_path = OUTPUT_DIR / "code-viz.html"

        # Load page
        await page.goto(f"file://{html_path.resolve()}")
        await page.wait_for_timeout(2000)  # Wait for graph to settle

        screenshots = []

        # Capture sequence
        actions = [
            ("initial", 2000),
            ("hover_main", 500),
            ("search_utils", 1000),
            ("zoom_in", 1000),
            ("reset", 1000),
        ]

        for action, wait_time in actions:
            if action == "initial":
                pass  # Already loaded
            elif action == "hover_main":
                await page.hover("circle:nth-child(1)")
            elif action == "search_utils":
                await page.fill("#searchInput", "utils")
                await page.wait_for_timeout(500)
            elif action == "zoom_in":
                await page.mouse.wheel(0, -200)
                await page.wait_for_timeout(500)
            elif action == "reset":
                await page.evaluate("document.getElementById('resetBtn').click()")
                await page.wait_for_timeout(500)

            await page.wait_for_timeout(wait_time)

            screenshot_path = OUTPUT_DIR / f"demo_{action}.png"
            await page.screenshot(path=screenshot_path)
            screenshots.append(screenshot_path)
            print(f"Captured: {screenshot_path.name}")

        await browser.close()

    return screenshots


def create_gif(screenshots: list[Path]) -> Path:
    """Create GIF from screenshots using ffmpeg."""
    gif_path = OUTPUT_DIR / "demo.gif"

    # Try ffmpeg
    try:
        cmd = [
            "ffmpeg",
            "-framerate",
            "2",
            "-i",
            str(OUTPUT_DIR / "demo_%d.png"),
            "-vf",
            "scale=800:-1",
            "-y",
            str(gif_path),
        ]
        subprocess.run(cmd, check=True)
        print(f"Created GIF: {gif_path}")
        return gif_path
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ffmpeg not found, skipping GIF creation")
        print(f"Screenshots saved in: {OUTPUT_DIR}")
        return None


async def main() -> None:
    """Main entry point."""
    print("Starting demo capture...")
    screenshots = await capture_screenshots()

    if screenshots:
        create_gif(screenshots)

    print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
