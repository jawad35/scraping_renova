import asyncio
from playwright.async_api import async_playwright
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

async def main():
    url = 'https://www.build.com/trimlite-21681388730pllrh1d6916/s1866883?uid=4412605&searchId=Nk1r8tdzEI'

    async with async_playwright() as p:
        # Launch the browser
        browser = await p.chromium.launch(headless=False)  # Set to False to see the browser action
        # Create a new browser context with custom headers
        context = await browser.new_context(
            extra_http_headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
            }
        )
        # Open a new page
        page = await context.new_page()

        try:
            # Go to the URL with an increased timeout
            await page.goto(url, timeout=60000)  # Timeout set to 60 seconds (60000 milliseconds)

            # Wait for the page to load completely
            await page.wait_for_load_state('networkidle')

            # Find all buttons with the class "HzuYA"
            buttons = await page.query_selector_all('.HzuYA')

            # Iterate through each button and click synchronously
            for button in buttons:
                try:
                    # Wait for the button to be stable before clicking
                    await button.wait_for_element_state('stable')
                    await button.click()
                    print(f"Button clicked successfully.")
                except PlaywrightTimeoutError:
                    print(f"Timeout occurred while clicking the button.")

                # Wait for the page to settle after each click
                await page.wait_for_load_state('networkidle')

            # After clicking all buttons, capture the final URL
            final_url = page.url
            print(f"Final URL after all clicks: {final_url}")

        except PlaywrightTimeoutError:
            print("Timeout occurred while waiting for page to load.")

        finally:
            # Close the browser
            await browser.close()

# Run the main function
asyncio.run(main())
