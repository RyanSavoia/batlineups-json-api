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
        
        # Just get everything after "MLB Lineups"
        data = await page.evaluate('''
            () => {
                const content = document.body.innerText;
                const startIndex = content.indexOf('MLB Lineups');
                if (startIndex !== -1) {
                    return content.substring(startIndex);
                }
                return "MLB Lineups not found in content";
            }
        ''')
        
        await browser.close()
        return {"content": data}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
