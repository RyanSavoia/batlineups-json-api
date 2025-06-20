async def scrape_swish_lineups():
    """Scrape today's MLB lineups from Swish Analytics"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        page = await browser.new_page()
        
        try:
            await page.goto("https://swishanalytics.com/optimus/mlb/lineups", timeout=60000)
            await page.wait_for_timeout(5000)  # Let page fully load
            
            # Get all tables and process them
            lineups = await page.evaluate('''
                () => {
                    const games = [];
                    const tables = document.querySelectorAll('table');
                    
                    // Process each table as a game
                    tables.forEach((table, index) => {
                        const rows = Array.from(table.querySelectorAll('tbody tr'));
                        
                        if (rows.length > 0) {
                            // Extract game info from the table
                            const game = {
                                tableIndex: index,
                                teams: {},
                                starters: {},
                                lineups: {
                                    away: [],
                                    home: []
                                }
                            };
                            
                            // Get headers tofrom fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from playwright.async_api import async_playwright
import asyncio
import re
from typing import Dict, List, Optional
from datetime import datetime

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://www.thebettinginsider.com", "http://localhost:3000"],  # Add localhost for testing
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

async def scrape_swish_lineups():
    """Scrape today's MLB lineups from Swish Analytics"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        page = await browser.new_page()
        
        try:
            await page.goto("https://swishanalytics.com/optimus/mlb/lineups", timeout=60000)
            await page.wait_for_timeout(5000)  # Let page fully load
            
            # First, let's see what we're getting
            page_text = await page.evaluate('() => document.body.innerText')
            print(f"Page text length: {len(page_text)}")
            print(f"First 500 chars: {page_text[:500] if page_text else 'No text found'}")
            
            # Try a simpler approach - look for any tables
            tables_data = await page.evaluate('''
                () => {
                    const tables = document.querySelectorAll('table');
                    return {
                        tableCount: tables.length,
                        firstTableText: tables[0]?.innerText?.substring(0, 500) || 'No table found'
                    };
                }
            ''')
            print(f"Tables found: {tables_data}")
            
            # If there are tables, let's parse them similar to the umpire scraper
            if tables_data['tableCount'] > 0:
                # Try to get lineup data from tables
                lineups = await page.evaluate('''
                    () => {
                        const games = [];
                        const tables = document.querySelectorAll('table');
                        
                        // Process each table
                        tables.forEach((table, tableIndex) => {
                            const rows = Array.from(table.querySelectorAll('tbody tr'));
                            
                            // For now, let's just capture the raw data
                            const tableData = rows.map(row => {
                                const cells = Array.from(row.querySelectorAll('td'));
                                return cells.map(cell => cell.textContent.trim());
                            });
                            
                            if (tableData.length > 0) {
                                games.push({
                                    tableIndex: tableIndex,
                                    rawData: tableData.slice(0, 5) // First 5 rows for debugging
                                });
                            }
                        });
                        
                        return games;
                    }
                ''')
                
                await browser.close()
                return lineups
            else:
                # Original text-based parsing
                lineups = await page.evaluate('''
                    () => {
                        const games = [];
                        const content = document.body.innerText;
                        
                        // Split by game times to separate games
                        const gameBlocks = content.split(/(?=Friday \\d+\\/\\d+ \\d+:\\d+ [AP]M ET)/);
                        
                        gameBlocks.forEach(block => {
                            if (!block.trim() || !block.includes(' @ ')) return;
                            
                            const lines = block.split('\\n').map(line => line.trim()).filter(line => line);
                            
                            // Find teams - look for the @ symbol
                            const teamLineIndex = lines.findIndex(line => line.includes(' @ '));
                            if (teamLineIndex === -1) return;
                            
                            const teamLine = lines[teamLineIndex];
                            const teams = teamLine.split(' @ ').map(t => t.trim());
                            if (teams.length !== 2) return;
                            
                            const game = {
                                teams: {
                                    away: teams[0],
                                    home: teams[1]
                                },
                                starters: {},
                                lineups: {
                                    away: [],
                                    home: []
                                }
                            };
                            
                            // Find pitchers - they appear after team names with (R) or (L)
                            let pitcherIndex = teamLineIndex + 1;
                            if (lines[pitcherIndex] && lines[pitcherIndex].includes('(') && lines[pitcherIndex].includes(')')) {
                                // Away pitcher
                                const awayPitcherMatch = lines[pitcherIndex].match(/([^(]+)\\s*\\([RL]\\)/);
                                if (awayPitcherMatch) {
                                    game.starters.away = awayPitcherMatch[1].trim();
                                }
                                
                                // Home pitcher - check next lines
                                for (let i = pitcherIndex + 1; i < pitcherIndex + 4; i++) {
                                    if (lines[i] && lines[i].includes('(') && !lines[i].includes(',')) {
                                        const homePitcherMatch = lines[i].match(/([^(]+)\\s*\\([RL]\\)/);
                                        if (homePitcherMatch) {
                                            game.starters.home = homePitcherMatch[1].trim();
                                            break;
                                        }
                                    }
                                }
                            }
                            
                            // Find lineups - look for "Official Lineup" or "Projected Lineup"
                            let currentTeam = 'away';
                            let inLineup = false;
                            let batterOrder = 1;
                            
                            for (let i = teamLineIndex; i < lines.length; i++) {
                                const line = lines[i];
                                
                                if (line.includes('Official Lineup') || line.includes('Projected Lineup')) {
                                    inLineup = true;
                                    batterOrder = 1;
                                    continue;
                                }
                                
                                // Check if we've moved to home team lineup
                                if (inLineup && currentTeam === 'away' && 
                                    (line.match(/^[A-Z]{2,3}\\s+\\([LRS]\\)/) || 
                                     (game.lineups.away.length >= 9 && line.match(/[A-Z][a-z]/))
                                    )) {
                                    currentTeam = 'home';
                                    batterOrder = 1;
                                }
                                
                                // Parse lineup entries
                                // Away team format: "1   Player Name (L) POS"
                                // Home team format: "POS (L) Player Name   1"
                                
                                if (inLineup && line.match(/\\d/) && line.match(/\\([LRS]\\)/)) {
                                    let name, position;
                                    
                                    if (currentTeam === 'away') {
                                        // Format: "1   J.P. Crawford (L) SS"
                                        const match = line.match(/\\d+\\s+([^(]+)\\s*\\([LRS]\\)\\s*(\\w+)/);
                                        if (match) {
                                            name = match[1].trim();
                                            position = match[2];
                                        }
                                    } else {
                                        // Format: "LF (S) Ian Happ   1"
                                        const match = line.match(/(\\w+)\\s*\\([LRS]\\)\\s*([^\\d]+)\\s*\\d+/);
                                        if (match) {
                                            position = match[1];
                                            name = match[2].trim();
                                        }
                                    }
                                    
                                    if (name && position) {
                                        game.lineups[currentTeam].push({
                                            name: name,
                                            position: position,
                                            order: batterOrder++
                                        });
                                    }
                                }
                                
                                // Stop if we hit weather or betting lines
                                if (line.includes('°') || line.includes('MLRun') || line.includes('Current Lines')) {
                                    break;
                                }
                            }
                            
                            games.push(game);
                        });
                        
                        return games;
                    }
                ''')
                
                await browser.close()
                return lineups
            
        except Exception as e:
            await browser.close()
            raise e

async def get_pitcher_arsenal(pitcher_name: str):
    """Get pitcher's arsenal from Baseball Savant player page"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        page = await browser.new_page()
        
        try:
            # Format the player name for URL (lowercase, replace spaces with hyphens)
            url_name = pitcher_name.lower().replace(' ', '-')
            
            # First try direct URL with common pattern
            player_url = f"https://baseballsavant.mlb.com/savant-player/{url_name}"
            response = await page.goto(player_url, timeout=60000)
            
            # If 404, we need to search for the player ID
            if response.status == 404:
                # Go to the search page
                await page.goto("https://baseballsavant.mlb.com/", timeout=60000)
                await page.wait_for_timeout(2000)
                
                # Search for the player
                player_id = await page.evaluate(f'''
                    async () => {{
                        const searchBox = document.querySelector('input[type="text"][placeholder*="Player"]');
                        if (!searchBox) return null;
                        
                        searchBox.value = "{pitcher_name}";
                        searchBox.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        
                        // Wait for dropdown
                        await new Promise(resolve => setTimeout(resolve, 2000));
                        
                        // Click first result
                        const firstResult = document.querySelector('.player-search-results a, .ui-menu-item a');
                        if (firstResult) {{
                            const href = firstResult.href;
                            const match = href.match(/savant-player\\/.*?-(\\d+)/);
                            return match ? match[1] : null;
                        }}
                        return null;
                    }}
                ''')
                
                if player_id:
                    player_url = f"https://baseballsavant.mlb.com/savant-player/{url_name}-{player_id}?stats=statcast-r-pitching-mlb"
                else:
                    raise Exception(f"Could not find player ID for {pitcher_name}")
            else:
                # Add the stats parameter to ensure we're on the right tab
                player_url = f"{player_url}?stats=statcast-r-pitching-mlb"
            
            # Navigate to the player's pitching stats page
            await page.goto(player_url, timeout=60000)
            await page.wait_for_timeout(3000)
            
            # Extract pitch arsenal data
            arsenal = await page.evaluate('''
                () => {
                    const pitches = [];
                    
                    // Find all tables on the page
                    const tables = document.querySelectorAll('table');
                    
                    for (const table of tables) {
                        // Look for a table that has pitch arsenal data
                        const headers = Array.from(table.querySelectorAll('th')).map(th => th.textContent.trim().toLowerCase());
                        
                        // Check if this is the pitch arsenal table
                        if (headers.some(h => h.includes('pitch type') || h.includes('pitch %')) && 
                            headers.some(h => h.includes('velo') || h.includes('velocity'))) {
                            
                            const rows = table.querySelectorAll('tbody tr');
                            
                            rows.forEach(row => {
                                const cells = Array.from(row.querySelectorAll('td'));
                                if (cells.length > 0) {
                                    const pitchType = cells[0]?.textContent.trim();
                                    
                                    // Extract all available data
                                    pitches.push({
                                        pitchType: pitchType,
                                        count: cells[1]?.textContent.trim() || '',
                                        pitchPct: cells[2]?.textContent.trim() || '',
                                        velo: cells[3]?.textContent.trim() || '',
                                        maxVelo: cells[4]?.textContent.trim() || '',
                                        spin: cells[5]?.textContent.trim() || '',
                                        exitVelo: cells[6]?.textContent.trim() || '',
                                        launchAngle: cells[7]?.textContent.trim() || '',
                                        whiffPct: cells[8]?.textContent.trim() || '',
                                        kPct: cells[9]?.textContent.trim() || '',
                                        putAwayPct: cells[10]?.textContent.trim() || '',
                                        hardHitPct: cells[11]?.textContent.trim() || '',
                                        xba: cells[12]?.textContent.trim() || '',
                                        xslg: cells[13]?.textContent.trim() || '',
                                        xwoba: cells[14]?.textContent.trim() || '',
                                        chasePct: cells[15]?.textContent.trim() || '',
                                        estWoba: cells[16]?.textContent.trim() || '',
                                        runValue: cells[17]?.textContent.trim() || '',
                                        rv100: cells[18]?.textContent.trim() || ''
                                    });
                                }
                            });
                            break; // Found the right table
                        }
                    }
                    
                    // If we didn't find the arsenal in the standard way, look for summary stats
                    if (pitches.length === 0) {
                        // Try to find pitch usage summary (often in a different format)
                        const summaryElements = document.querySelectorAll('.pitch-summary, [class*="pitch-type"]');
                        summaryElements.forEach(element => {
                            const pitchInfo = element.textContent.trim();
                            if (pitchInfo) {
                                pitches.push({
                                    summary: pitchInfo
                                });
                            }
                        });
                    }
                    
                    return pitches;
                }
            ''')
            
            await browser.close()
            return arsenal
            
        except Exception as e:
            await browser.close()
            raise e

async def get_batter_vs_pitch_type(batter_name: str):
    """Get batter's performance against all pitch types from Baseball Savant player page
    
    Args:
        batter_name: The batter's name (e.g., "Mike Trout", "Shohei Ohtani", etc.)
    
    Returns:
        Dictionary with pitch types as keys and performance stats as values
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        page = await browser.new_page()
        
        try:
            # Format the player name for URL (lowercase, replace spaces with hyphens)
            url_name = batter_name.lower().replace(' ', '-')
            
            # First try direct URL with common pattern
            player_url = f"https://baseballsavant.mlb.com/savant-player/{url_name}"
            response = await page.goto(player_url, timeout=60000)
            
            # If 404, we need to search for the player ID
            if response.status == 404:
                # Go to the search page
                await page.goto("https://baseballsavant.mlb.com/", timeout=60000)
                await page.wait_for_timeout(2000)
                
                # Search for the player
                player_id = await page.evaluate(f'''
                    async () => {{
                        const searchBox = document.querySelector('input[type="text"][placeholder*="Player"]');
                        if (!searchBox) return null;
                        
                        searchBox.value = "{batter_name}";
                        searchBox.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        
                        // Wait for dropdown
                        await new Promise(resolve => setTimeout(resolve, 2000));
                        
                        // Click first result
                        const firstResult = document.querySelector('.player-search-results a, .ui-menu-item a');
                        if (firstResult) {{
                            const href = firstResult.href;
                            const match = href.match(/savant-player\\/.*?-(\\d+)/);
                            return match ? match[1] : null;
                        }}
                        return null;
                    }}
                ''')
                
                if player_id:
                    player_url = f"https://baseballsavant.mlb.com/savant-player/{url_name}-{player_id}?stats=statcast-r-hitting-mlb"
                else:
                    raise Exception(f"Could not find player ID for {batter_name}")
            else:
                # Add the stats parameter to ensure we're on the right tab
                player_url = f"{player_url}?stats=statcast-r-hitting-mlb"
            
            # Navigate to the player's hitting stats page
            await page.goto(player_url, timeout=60000)
            await page.wait_for_timeout(3000)
            
            # Scroll down to find the "Run Values by Pitch Type" section
            await page.evaluate('''
                () => {
                    // Find the run values section and scroll to it
                    const headers = Array.from(document.querySelectorAll('h3, h4, .table-header'));
                    const runValuesHeader = headers.find(h => 
                        h.textContent.toLowerCase().includes('run value') || 
                        h.textContent.toLowerCase().includes('pitch type')
                    );
                    if (runValuesHeader) {
                        runValuesHeader.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }
                }
            ''')
            
            await page.wait_for_timeout(2000)
            
            # Extract pitch type data from the Run Values table
            batter_stats = await page.evaluate('''
                () => {
                    const stats = {};
                    
                    // Find all tables on the page
                    const tables = document.querySelectorAll('table');
                    
                    for (const table of tables) {
                        // Look for a table that has pitch type data
                        const headers = Array.from(table.querySelectorAll('th')).map(th => th.textContent.trim().toLowerCase());
                        
                        // Check if this is the pitch type table by looking for key headers
                        if (headers.some(h => h.includes('pitch type') || h.includes('pitch%')) && 
                            headers.some(h => h.includes('ba') || h.includes('avg'))) {
                            
                            const rows = table.querySelectorAll('tbody tr');
                            
                            rows.forEach(row => {
                                const cells = Array.from(row.querySelectorAll('td'));
                                if (cells.length > 0) {
                                    const pitchType = cells[0]?.textContent.trim();
                                    
                                    // Map the cells based on common column positions
                                    // The exact positions may vary, but typically:
                                    // 0: Pitch Type, 1: Count/Pitches, 2: Pitch%, 3: PA, 4: BA, 5: SLG, 6: wOBA, etc.
                                    stats[pitchType] = {
                                        pitchType: pitchType,
                                        count: cells[1]?.textContent.trim() || '',
                                        pitchPct: cells[2]?.textContent.trim() || '',
                                        pa: cells[3]?.textContent.trim() || '',
                                        ab: cells[4]?.textContent.trim() || '',
                                        hits: cells[5]?.textContent.trim() || '',
                                        ba: cells[6]?.textContent.trim() || '',
                                        slg: cells[7]?.textContent.trim() || '',
                                        iso: cells[8]?.textContent.trim() || '',
                                        babip: cells[9]?.textContent.trim() || '',
                                        woba: cells[10]?.textContent.trim() || '',
                                        xwoba: cells[11]?.textContent.trim() || '',
                                        xba: cells[12]?.textContent.trim() || '',
                                        xslg: cells[13]?.textContent.trim() || '',
                                        wobacon: cells[14]?.textContent.trim() || '',
                                        xwobacon: cells[15]?.textContent.trim() || '',
                                        ev: cells[16]?.textContent.trim() || '',
                                        la: cells[17]?.textContent.trim() || '',
                                        barrels: cells[18]?.textContent.trim() || '',
                                        hardHit: cells[19]?.textContent.trim() || '',
                                        whiff: cells[20]?.textContent.trim() || '',
                                        swingPct: cells[21]?.textContent.trim() || '',
                                        runValue: cells[22]?.textContent.trim() || '',
                                        rv100: cells[23]?.textContent.trim() || ''
                                    };
                                }
                            });
                            break; // Found the right table
                        }
                    }
                    
                    // If we didn't find the table in the standard way, try alternative selectors
                    if (Object.keys(stats).length === 0) {
                        // Look for specific Baseball Savant table classes
                        const pitchTypeTable = document.querySelector('[id*="pitchType"], .pitch-type-table, [class*="run-value"]');
                        if (pitchTypeTable) {
                            const rows = pitchTypeTable.querySelectorAll('tbody tr');
                            rows.forEach(row => {
                                const cells = Array.from(row.querySelectorAll('td'));
                                if (cells.length > 0) {
                                    const pitchType = cells[0]?.textContent.trim();
                                    stats[pitchType] = {
                                        pitchType: pitchType,
                                        data: cells.map(c => c.textContent.trim())
                                    };
                                }
                            });
                        }
                    }
                    
                    return stats;
                }
            ''')
            
            await browser.close()
            return batter_stats
            
        except Exception as e:
            await browser.close()
            raise e

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "MLB Matchup Analysis API",
        "endpoints": {
            "/lineups": "Get today's MLB lineups from Swish Analytics",
            "/matchup/{away_team}/{home_team}": "Get detailed matchup analysis",
            "/pitcher/{name}": "Get pitcher arsenal data",
            "/batter/{name}/vs-pitches": "Get batter performance vs pitch types"
        }
    }

@app.get("/lineups")
async def get_lineups():
    """Get today's MLB lineups"""
    try:
        lineups = await scrape_swish_lineups()
        return {"status": "success", "data": lineups}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/pitcher/{pitcher_name}")
async def get_pitcher_data(pitcher_name: str):
    """Get pitcher arsenal data"""
    try:
        arsenal = await get_pitcher_arsenal(pitcher_name)
        return {"status": "success", "pitcher": pitcher_name, "arsenal": arsenal}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/batter/{batter_name}/vs-pitches")
async def get_batter_vs_pitches(batter_name: str):
    """Get batter performance against all pitch types"""
    try:
        stats = await get_batter_vs_pitch_type(batter_name)
        return {"status": "success", "batter": batter_name, "stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/matchup/{away_team}/{home_team}")
async def get_matchup_analysis(away_team: str, home_team: str):
    """Get comprehensive matchup analysis"""
    try:
        # First get lineups
        lineups = await scrape_swish_lineups()
        
        # Find the specific game
        game = None
        for g in lineups:
            if (away_team.lower() in g['teams']['away'].lower() and 
                home_team.lower() in g['teams']['home'].lower()):
                game = g
                break
        
        if not game:
            raise HTTPException(status_code=404, detail="Game not found")
        
        # Get pitcher arsenals
        away_pitcher_arsenal = await get_pitcher_arsenal(game['starters']['away'])
        home_pitcher_arsenal = await get_pitcher_arsenal(game['starters']['home'])
        
        # Get pitch types from arsenals
        away_pitch_types = [p['pitchType'] for p in away_pitcher_arsenal if p.get('pitchType')]
        home_pitch_types = [p['pitchType'] for p in home_pitcher_arsenal if p.get('pitchType')]
        
        # Analyze key batters vs pitch types
        matchup_data = {
            "game": game,
            "pitching": {
                "away": {
                    "name": game['starters']['away'],
                    "arsenal": away_pitcher_arsenal
                },
                "home": {
                    "name": game['starters']['home'],
                    "arsenal": home_pitcher_arsenal
                }
            },
            "batting_matchups": {
                "away": [],
                "home": []
            }
        }
        
        # Get batter performance vs pitch types for each team's lineup
        for team in ['away', 'home']:
            # Get the full lineup
            lineup = game['lineups'][team]
            
            for batter in lineup:
                # Get this batter's performance against all pitch types
                batter_stats = await get_batter_vs_pitch_type(batter['name'])
                
                # Get the opposing pitcher's arsenal
                opposing_pitcher_arsenal = home_pitcher_arsenal if team == 'away' else away_pitcher_arsenal
                
                # Create a focused matchup analysis
                matchup_analysis = {
                    "batter": batter,
                    "vs_all_pitch_types": batter_stats,
                    "vs_opposing_pitcher_arsenal": {}
                }
                
                # Extract only the pitch types the opposing pitcher throws
                for pitch in opposing_pitcher_arsenal:
                    pitch_type = pitch.get('pitchType')
                    if pitch_type and pitch_type in batter_stats:
                        matchup_analysis['vs_opposing_pitcher_arsenal'][pitch_type] = {
                            "pitcher_usage": pitch.get('pitchPct'),
                            "batter_stats": batter_stats[pitch_type]
                        }
                
                matchup_data['batting_matchups'][team].append(matchup_analysis)
                
                await asyncio.sleep(0.5)  # Rate limiting
        
        return {"status": "success", "data": matchup_data}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
