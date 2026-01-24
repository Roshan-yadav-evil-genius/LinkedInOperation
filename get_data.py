from playwright.async_api import async_playwright
import asyncio
import os
import re
import shutil
from urllib.parse import urlparse
from datetime import datetime

async def main():
    async with async_playwright() as playwright:
        # Create a persistent browser context with user data directory
        user_data_dir = os.path.join(os.getcwd(),"data", "browser_data")
        context = await playwright.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            viewport={"width": 1920, "height": 1080}
        )
        
        # Block unnecessary resources to speed up page loading
        # blocked_resources = {"image", "font", "media", "stylesheet", "texttrack", "manifest"}
        blocked_resources = {"image", "font", "media", "stylesheet", "texttrack","manifest"}
        
        async def handle_route(route):
            if route.request.resource_type in blocked_resources:
                await route.abort()
            else:
                await route.continue_()
        
        await context.route("**/*", handle_route)
        
        # Delete and recreate directory for saving responses
        responses_dir = os.path.join(os.getcwd(), "data", "network_responses")
        if os.path.exists(responses_dir):
            shutil.rmtree(responses_dir)
        os.makedirs(responses_dir, exist_ok=True)
        

        async def on_response(response):
            status = response.status
            
            # Check if response is JSON
            content_type = response.headers.get("content-type", "")
            is_json = "json" in content_type.lower()
            
            # Check if URL matches target pattern (voyagerFeedDashProfileUpdates queryId)
            parsed_url = urlparse(response.url)
            is_graphql = "/voyager/api/graphql" in parsed_url.path
            has_target_query = "queryId=voyagerFeedDashProfileUpdates" in response.url or "voyagerFeedDashProfileUpdates" in response.url
            url_contains_target = is_graphql and has_target_query
            
            # Save only JSON responses with voyagerMessagingDashConversationNudges in URL
            if 200 <= status < 300 and is_json and url_contains_target:
                try:
                    print(f"  📄 JSON RESPONSE URL: {response.url}")
                    
                    # Get response body as text (for JSON)
                    response_text = await response.text()
                    
                    # Create a safe filename from URL
                    parsed_url = urlparse(response.url)
                    path_parts = [part for part in parsed_url.path.split("/") if part]
                    filename = "_".join(path_parts[-3:]) if path_parts else "index"
                    filename = re.sub(r'[^\w\-_\.]', '_', filename)
                    
                    # Add query params if present
                    if parsed_url.query:
                        query_safe = re.sub(r'[^\w\-_\.]', '_', parsed_url.query[:50])
                        filename = f"{filename}_{query_safe}"
                    
                    # Add timestamp and domain
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                    domain = parsed_url.netloc.replace(".", "_")
                    resource_type = response.request.resource_type
                    
                    full_filename = f"{timestamp}_{domain}_{resource_type}_{filename}.json"
                    filepath = os.path.join(responses_dir, full_filename)
                    
                    # Save response body to file
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(response_text)
                    
                    print(f"  Saved: {filepath}")
                except Exception as e:
                    print(f"  Error saving response: {e}")
        
        def on_request_failed(request):
            print(f"✗ FAILED {request.method} {request.url} - {request.failure}")
        
        # context.on("request", on_request)
        context.on("response", on_response)
        # context.on("requestfailed", on_request_failed)
        
        page = await context.new_page()
        # await page.goto("https://www.linkedin.com/in/robhochstein/recent-activity/reactions/")
        # await page.goto("https://www.linkedin.com/in/robhochstein/recent-activity/comments/")
        # await page.goto("https://www.linkedin.com/in/robhochstein/recent-activity/all/")
        await page.goto("https://www.linkedin.com/in/robhochstein/")
        await page.wait_for_timeout(60000)
        await context.close()

if __name__ == "__main__":
    asyncio.run(main())