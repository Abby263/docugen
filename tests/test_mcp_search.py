"""
MCP Search Test

Test Web Search via MCP
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

# Load environment variables
load_dotenv()


async def test_mcp_manager():
    """Test MCP Manager"""
    from src.mcp.mcp_manager import get_mcp_manager

    logger.info("=" * 60)
    logger.info("Test 1: MCP Manager")
    logger.info("=" * 60)

    manager = get_mcp_manager()

    # List all clients
    all_clients = manager.list_clients()
    logger.info(f"All MCP clients: {all_clients}")

    # List enabled clients
    enabled_clients = manager.list_enabled_clients()
    logger.info(f"Enabled MCP clients: {enabled_clients}")

    # Check if any clients are enabled
    has_enabled = manager.has_enabled_clients()
    logger.info(f"Has enabled clients: {has_enabled}")

    return manager


async def test_zhipu_search(manager):
    """Test Web Search"""
    logger.info("\n" + "=" * 60)
    logger.info("Test 2: Web Search")
    logger.info("=" * 60)

    if not manager.has_enabled_clients():
        logger.warning("No MCP clients enabled")
        logger.info("Please set ZHIPU_MCP_API_KEY in .env file")
        return

    # Test search query
    query = "2025103 AIGC"
    logger.info(f"Search query: {query}")

    result = await manager.search(query, max_results=5)

    logger.info(f"\nSearch status: {result.get('status')}")
    logger.info(f"Search source: {result.get('source')}")
    logger.info(f"Results count: {len(result.get('results', []))}")

    # Display results
    results = result.get("results", [])
    for i, item in enumerate(results, 1):
        logger.info(f"\n--- Result {i} ---")
        logger.info(f"Title: {item.get('title', 'N/A')}")
        logger.info(f"URL: {item.get('url', 'N/A')}")
        logger.info(f"Snippet: {item.get('snippet', 'N/A')[:100]}...")


async def test_web_searcher():
    """Test Web Searcher"""
    logger.info("\n" + "=" * 60)
    logger.info("Test 3: Web Searcher")
    logger.info("=" * 60)

    from src.tools.web_searcher import WebSearcher

    # Create searcher with MCP preference
    searcher = WebSearcher(prefer_mcp=True)

    # Test search query
    query = "AI technology trends"
    logger.info(f"Search query: {query}")

    results = await searcher.search(query, max_results=3)

    logger.info(f"\nFound {len(results)} results")

    # Display results
    for i, result in enumerate(results, 1):
        logger.info(f"\n--- Result {i} ---")
        logger.info(f"Title: {result.get('title', 'N/A')}")
        logger.info(f"URL: {result.get('url', 'N/A')}")
        logger.info(f"Source: {result.get('source', 'N/A')}")
        logger.info(f"Snippet: {result.get('snippet', 'N/A')[:100]}...")


async def test_prompt_instruction():
    """Test prompt instruction generation"""
    logger.info("\n" + "=" * 60)
    logger.info("Test 4: Prompt Instruction")
    logger.info("=" * 60)

    from src.mcp.mcp_manager import get_mcp_manager

    manager = get_mcp_manager()

    if not manager.has_enabled_clients():
        logger.warning("No MCP clients enabled")
        return

    # Test prompt instruction
    query = "2025103 AIGC"
    instruction = manager.get_search_prompt_instruction(query)

    logger.info(f"Query: {query}")
    logger.info(f"Instruction: {instruction}")


async def main():
    """Main test function"""
    logger.info("Starting MCP Search Tests\n")

    try:
        # Test 1: MCP Manager
        manager = await test_mcp_manager()

        # Test 2: Zhipu Search
        await test_zhipu_search(manager)

        # Test 3: Web Searcher
        await test_web_searcher()

        # Test 4: Prompt Instruction
        await test_prompt_instruction()

        logger.info("\n" + "=" * 60)
        logger.info("All tests completed!")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Test error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
