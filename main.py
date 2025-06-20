from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from playwright.async_api import async_playwright
import asyncio

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://www.thebettinginsider.com"],  # Your website domain
    allow_credentials=True,
    allow_methods=["GET"],  # Only allow GET requests
    allow_headers=["*"],
)

@app.get("/")
async def get_lineup_data():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        page = await browser.new_page()
        await page.goto("https://swishanalytics.com/optimus/mlb/lineups", timeout=60000)
        await page.wait_for_timeout(5000)  # Let page fully load
        
        # Get the page content as text
        data = await page.evaluate('''
            () => {
                const content = document.body.innerText;
                
                // Return debug info to see what we're getting
                return {
                    contentLength: content.length,
                    first500Chars: content.substring(0, 500),
                    hasAtSymbol: content.includes('@'),
                    lineCount: content.split('\\n').length,
                    // Try to find any line with @
                    atLines: content.split('\\n').filter(line => line.includes('@')).slice(0, 5)
                };
            }
        ''')
        
        await browser.close()
        return data

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
