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
                const lines = content.split('\\n');
                const games = [];
                
                // Look for team matchups with the @ symbol
                for (let i = 0; i < lines.length; i++) {
                    // Match pattern like "  SEA  @  CHC  "
                    if (lines[i].includes(' @ ') && lines[i].match(/[A-Z]{2,3}\\s+@\\s+[A-Z]{2,3}/)) {
                        const game = {
                            matchup: lines[i].trim(),
                            pitchers: {},
                            lineups: {
                                away: [],
                                home: []
                            }
                        };
                        
                        // Look for pitchers in next few lines
                        for (let j = i+1; j < i+5 && j < lines.length; j++) {
                            const line = lines[j].trim();
                            // Away pitcher: "(R) George Kirby"
                            if (line.match(/^\\([RL]\\)\\s+/)) {
                                game.pitchers.away = line;
                            }
                            // Home pitcher: "Matthew Boyd (L)"
                            else if (line.match(/\\s+\\([RL]\\)$/)) {
                                game.pitchers.home = line;
                            }
                        }
                        
                        // Look for lineups
                        let isAwayLineup = true;
                        for (let j = i+1; j < i+40 && j < lines.length; j++) {
                            const line = lines[j].trim();
                            
                            // Check for lineup markers
                            if (line === 'Official Lineup' || line === 'Projected Lineup') {
                                continue;
                            }
                            
                            // Stop at weather or betting lines
                            if (line.includes('°') || line.includes('MLRun')) {
                                break;
                            }
                            
                            // Away lineup: "1   J.P. Crawford (L) SS"
                            if (line.match(/^\\d+\\s+.+\\([LRS]\\)\\s+\\w+$/)) {
                                game.lineups.away.push(line);
                            }
                            // Home lineup: "LF (S) Ian Happ   1"
                            else if (line.match(/^\\w+\\s+\\([LRS]\\).+\\d+$/)) {
                                game.lineups.home.push(line);
                            }
                        }
                        
                        games.push(game);
                    }
                }
                
                return games;
            }
        ''')
        
        await browser.close()
        return data

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
