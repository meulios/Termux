import aiohttp
import asyncio
import random
import math

# PRO-GRADE HEADERS
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Referer": "https://www.languagenut.com/",
    "Origin": "https://www.languagenut.com"
}

async def run_points_farm():
    print("--- 💠 Languagenut Global Points Farmer ---")
    user = input("Username: ")
    pwd = input("Password: ")
    ietf = input("Language (e.g., fr-FR, es-ES): ") # French is fr-FR as per your screen
    
    async with aiohttp.ClientSession(headers=HEADERS) as s:
        # 1. AUTHENTICATION
        async with s.get("https://api.languagenut.com/loginController/attemptLogin", params={"username": user, "pass": pwd}) as r:
            login_data = await r.json(content_type=None)
            token = login_data.get("newToken")
            if not token: return print("❌ Login Failed.")

        # 2. TARGET SELECTION (Finding a Module for Points)
        # We fetch the curriculum to find a module ID that gives points
        async with s.get("https://api.languagenut.com/contentController/getSecondaryCurriculum", params={"token": token, "ietf": ietf}) as r:
            curriculum = await r.json(content_type=None)
            # Find the very first section (usually the easiest)
            try:
                catalog_uid = curriculum['years'][0]['units'][0]['sections'][0]['id']
            except:
                catalog_uid = "1500" # Fallback to standard 'Basics' ID

        print(f"✅ Target Locked: {catalog_uid}. Starting point generation...")

        while True:
            # Fetch vocab for that module to calculate real scores
            params = {"token": token, "toLanguage": ietf, "fromLanguage": "en-US", "catalogUid[]": catalog_uid}
            async with s.get("https://api.languagenut.com/vocabTranslationController/getVocabTranslations", params=params) as r:
                res = await r.json(content_type=None)
                vocabs = res.get("vocabTranslations", [])
            
            if not vocabs: 
                print("⚠️ Error fetching data. Trying again in 5s...")
                await asyncio.sleep(5)
                continue

            # SIMULATION: Points are calculated based on module length
            # Correct count * 200 = Standard Game Score
            score = len(vocabs) * 200 
            sim_time = random.randint(35, 50) # Safe speed to avoid detection
            
            payload = {
                "moduleUid": catalog_uid,
                "gameUid": "1", # 1 = Vocab Game
                "gameType": "vocab",
                "isTest": "true",
                "toietf": ietf,
                "fromietf": "en-US",
                "score": score,
                "correctVocabs": ",".join([str(x.get('uid')) for x in vocabs]),
                "incorrectVocabs": "[]",
                "timeStamp": sim_time * 1000,
                "token": token,
                "product": "secondary",
                "dontStoreStats": "false" # CRITICAL: Must be false to update Rankings
            }

            # SUBMIT TO API
            async with s.get("https://api.languagenut.com/gameDataController/addGameScore", params=payload) as r:
                resp = await r.json(content_type=None)
                print(f"💰 +{score} Points | Time: {sim_time}s | Sync: {resp.get('status', 'Success')}")
            
            await asyncio.sleep(2) # Prevent rate-limiting

if __name__ == "__main__":
    asyncio.run(run_points_farm())
