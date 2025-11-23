"""
Zhipu MCP Debug Test

Debug Web Search via Zhipu MCP
"""

import asyncio
import os
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger
from dotenv import load_dotenv
import httpx

# Load environment variables
load_dotenv()


async def test_1_check_env():
    """Test 1: Check environment variables"""
    print("\n" + "=" * 70)
    print("Test 1: Check Environment Variables")
    print("=" * 70)

    api_key = os.getenv("ZHIPU_MCP_API_KEY")

    if not api_key:
        print("  ZHIPU_MCP_API_KEY not found")
        print("  Please add to .env file:")
        print("ZHIPU_MCP_API_KEY=your_api_key_here")
        return False
    else:
        # Mask API key for display
        masked_key = api_key[:10] + "..." + api_key[-10:] if len(api_key) > 20 else "***"
        print(f"  ZHIPU_MCP_API_KEY found: {masked_key}")
        return True


async def test_2_simple_request():
    """Test 2: Simple HTTP request"""
    print("\n" + "=" * 70)
    print("Test 2: HTTP GET Request")
    print("=" * 70)

    api_key = os.getenv("ZHIPU_MCP_API_KEY")
    if not api_key:
        print("  API Key not found")
        return

    # Construct URL
    base_url = f"https://open.bigmodel.cn/api/mcp/web_search/sse?Authorization={api_key}"

    print(f"URL: {base_url[:60]}...{base_url[-20:]}")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print("\nSending GET request...")
            response = await client.get(
                base_url,
                headers={
                    "Accept": "text/event-stream",
                    "User-Agent": "MCP Client/1.0"
                }
            )

            print(f"Status code: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")

            if response.status_code == 200:
                content = response.text[:500]
                print(f"First 500 chars:\n{content}")
            else:
                print(f"Error status: {response.status_code}")
                print(f"Error message: {response.text[:500]}")

    except Exception as e:
        print(f"Request error: {e}")
        import traceback
        traceback.print_exc()


async def test_3_sse_with_query():
    """Test 3: SSE with query"""
    print("\n" + "=" * 70)
    print("Test 3: SSE Stream with Query")
    print("=" * 70)

    api_key = os.getenv("ZHIPU_MCP_API_KEY")
    if not api_key:
        print("  API Key not found")
        return

    # Construct URL with query
    from urllib.parse import urlencode

    base_url = f"https://open.bigmodel.cn/api/mcp/web_search/sse?Authorization={api_key}"
    search_params = {
        "query": "AI technology trends",
        "count": 3
    }
    search_url = f"{base_url}&{urlencode(search_params)}"

    print(f"Search query: {search_params['query']}")
    print(f"URL: {search_url[:60]}...{search_url[-30:]}")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            print("\nStarting SSE stream...")

            async with client.stream(
                'GET',
                search_url,
                headers={
                    "Accept": "text/event-stream",
                    "User-Agent": "MCP Client/1.0"
                }
            ) as response:
                print(f"Status code: {response.status_code}")
                print(f"Content-Type: {response.headers.get('content-type')}")

                if response.status_code != 200:
                    error_text = await response.aread()
                    print(f"Error response: {error_text.decode()[:500]}")
                    return

                print("\nSSE Events:")
                print("-" * 70)

                line_count = 0
                event_count = 0

                async for line in response.aiter_lines():
                    line_count += 1

                    if not line:
                        continue

                    print(f"[{line_count}] {line}")

                    if line.startswith('data: '):
                        event_count += 1
                        data_str = line[6:].strip()

                        if data_str not in ['[DONE]', '']:
                            try:
                                import json
                                event_data = json.loads(data_str)
                                print(f"    Event {event_count} data:")
                                print(f"    Content: {json.dumps(event_data, ensure_ascii=False, indent=2)[:300]}")
                            except json.JSONDecodeError as e:
                                print(f"    JSON decode error: {e}")
                                print(f"    Raw data: {data_str[:200]}")

                print("-" * 70)
                print(f"SSE stream completed: {line_count} lines, {event_count} events")

    except httpx.TimeoutException:
        print("Request timeout")
    except Exception as e:
        print(f"Stream error: {e}")
        import traceback
        traceback.print_exc()


async def test_4_use_mcp_client():
    """Test 4: Use MCP Client"""
    print("\n" + "=" * 70)
    print("Test 4: MCP Client")
    print("=" * 70)

    api_key = os.getenv("ZHIPU_MCP_API_KEY")
    if not api_key:
        print("  API Key not found")
        return

    try:
        from src.mcp.zhipu_web_search import ZhipuWebSearchClient

        client = ZhipuWebSearchClient(api_key=api_key)

        print(f"Client created")
        print(f"Client name: {client.name}")
        print(f"URL: {client.config.url[:60]}...")

        print("\nCalling web_search tool...")
        result = await client.call_tool(
            "web_search",
            {"query": "AI technology trends", "max_results": 3}
        )

        print(f"\nSearch result:")
        print(f"Status: {result.get('status')}")
        print(f"Message: {result.get('message', 'N/A')}")
        print(f"Results count: {len(result.get('results', []))}")

        for i, item in enumerate(result.get('results', [])[:3], 1):
            print(f"\nResult {i}:")
            print(f"  Title: {item.get('title', 'N/A')}")
            print(f"  URL: {item.get('url', 'N/A')}")
            print(f"  Snippet: {item.get('snippet', 'N/A')[:100]}")

    except Exception as e:
        print(f"Client error: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Main test function"""
    print("\n" + "Starting Zhipu MCP Debug Tests" + "\n")

    # Enable DEBUG logging
    logger.remove()
    logger.add(sys.stderr, level="DEBUG")

    try:
        # Test 1: Check environment
        has_key = await test_1_check_env()

        if not has_key:
            print("\nPlease set ZHIPU_MCP_API_KEY in .env file")
            return

        # Test 2: Simple request
        await test_2_simple_request()

        # Test 3: SSE with query
        await test_3_sse_with_query()

        # Test 4: MCP client
        await test_4_use_mcp_client()

        print("\n" + "=" * 70)
        print("All tests completed")
        print("=" * 70)

    except Exception as e:
        logger.error(f"Test error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
