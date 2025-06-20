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
        
        # Get the page content and parse it
        data = await page.evaluate('''
            () => {
                const content = document.body.innerText;
                const lines = content.split('\\n');
                const games = [];
                
                for (let i = 0; i < lines.length; i++) {
                    // Look for the team matchup lines
                    if (lines[i].match(/^\\s+[A-Z]{2,3}\\s+@\\s+[A-Z]{2,3}\\s+$/)) {
                        const teams = lines[i].split('@').map(t => t.trim());
                        const game = {
                            away_team: teams[0],
                            home_team: teams[1],
                            away_pitcher: '',
                            home_pitcher: '',
                            away_lineup: [],
                            home_lineup: []
                        };
                        
                        // Get pitchers (next 4 lines)
                        if (i + 4 < lines.length) {
                            game.away_pitcher = lines[i + 1].trim();
                            game.home_pitcher = lines[i + 3].trim();
                        }
                        
                        // Find lineups
                        let inAwayLineup = false;
                        let inHomeLineup = false;
                        
                        for (let j = i + 4; j < Math.min(i + 50, lines.length); j++) {
                            const line = lines[j].trim();
                            
                            if (line === 'Official Lineup' || line === 'Projected Lineup') {
                                if (!inAwayLineup) {
                                    inAwayLineup = true;
                                } else {
                                    inAwayLineup = false;
                                    inHomeLineup = true;
                                }
                                continue;
                            }
                            
                            // Stop at weather line
                            if (line.includes('°')) break;
                            
                            // Away lineup: "1   J.P. Crawford (L) SS"
                            if (inAwayLineup && line.match(/^\\d+\\s+/)) {
                                game.away_lineup.push(line);
                            }
                            // Home lineup: "LF (S) Ian Happ   1"
                            else if (inHomeLineup && line.match(/\\s+\\d+$/)) {
                                game.home_lineup.push(line);
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
