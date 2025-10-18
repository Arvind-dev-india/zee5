"""
Test script to debug ZEE5 API calls
"""
import asyncio
import httpx
from app.core.cache import cache
from app.core.token_generator import TokenGenerator
from app.utils.helpers import generate_user_agent

async def test_api():
    await cache.connect()

    # Get platform token
    platform_token = await cache.get('platform_token')
    if platform_token:
        platform_token = platform_token.decode() if isinstance(platform_token, bytes) else platform_token
        print(f"✓ Platform token: {platform_token[:80]}...")
    else:
        print("✗ No platform token found")
        await cache.close()
        return

    # Generate tokens
    token_generator = TokenGenerator()
    guest_token = token_generator.generate_guest_token()
    dd_token = token_generator.generate_dd_token()
    user_agent = generate_user_agent()

    print(f"✓ Guest token: {guest_token}")
    print(f"✓ DD token: {dd_token[:80]}...")
    print(f"✓ User agent: {user_agent[:80]}...")

    # Test API call
    channel_id = "0-9-zeetamil"
    url = (
        f"https://spapi.zee5.com/singlePlayback/getDetails/secure"
        f"?channel_id={channel_id}&device_id={guest_token}"
        f"&platform_name=desktop_web&translation=en&user_language=en,hi"
        f"&country=IN&state=&app_version=4.24.0&user_type=guest"
        f"&check_parental_control=false"
    )

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "origin": "https://www.zee5.com",
        "referer": "https://www.zee5.com/",
        "user-agent": user_agent
    }

    payload = {
        "x-access-token": platform_token,
        "X-Z5-Guest-Token": guest_token,
        "x-dd-token": dd_token
    }

    print(f"\n📡 Testing API call to:")
    print(f"   URL: {url[:100]}...")
    print(f"\n   Headers:")
    for key, value in headers.items():
        print(f"     {key}: {value[:80] if len(value) > 80 else value}")
    print(f"\n   Payload keys: {list(payload.keys())}")

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(url, headers=headers, json=payload)
            print(f"\n📥 Response:")
            print(f"   Status: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")

            if response.status_code == 200:
                data = response.json()
                if 'keyOsDetails' in data and 'video_token' in data['keyOsDetails']:
                    m3u8_url = data['keyOsDetails']['video_token']
                    print(f"   ✓ Got M3U8 URL: {m3u8_url[:100]}...")
                else:
                    print(f"   ✗ No video_token in response")
                    print(f"   Response keys: {list(data.keys())}")
            else:
                print(f"   ✗ Error response:")
                print(f"   {response.text[:500]}")

        except Exception as e:
            print(f"   ✗ Exception: {e}")

    await cache.close()

if __name__ == "__main__":
    asyncio.run(test_api())
