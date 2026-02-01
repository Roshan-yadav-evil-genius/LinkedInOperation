from playwright.async_api import async_playwright
import asyncio
import os
import shutil

async def main():
    async with async_playwright() as playwright:
        user_data_dir = os.path.join(os.getcwd(), "data", "browser_data")

        context = await playwright.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            viewport={"width": 1920, "height": 1080}
        )

        blocked_resources = {"image", "font", "media", "stylesheet", "texttrack", "manifest"}

        async def handle_route(route):
            if route.request.resource_type in blocked_resources:
                await route.abort()
            else:
                await route.continue_()

        # await context.route("**/*", handle_route)

        responses_dir = os.path.join(os.getcwd(), "data", "network_responses")
        if os.path.exists(responses_dir):
            shutil.rmtree(responses_dir)
        os.makedirs(responses_dir, exist_ok=True)

        page = await context.new_page()
        await page.goto("https://www.linkedin.com/in/robhochstein/")

        # ⬇️ WAIT until you manually close the browser
        await context.wait_for_event("close",timeout=0)

if __name__ == "__main__":
    asyncio.run(main())
