#!/usr/bin/env python
"""Fiction generation test script"""

import asyncio
import sys
from pathlib import Path

# Add src to Python path
sys.path.append(str(Path(__file__).parent / "src"))

from src.deep_search_agent import DeepSearchAgent


async def main():
    """Main test function"""

    # Test query for fiction generation
    query = 'Write a locked room mystery short story; the story should be told from the murderer\'s perspective, but only reveal "I am the murderer" at the end'

    print("=== Fiction Generation Test ===\n")
    print(f"Query: {query}\n")

    # Create agent
    agent = DeepSearchAgent()
    print("Initializing DeepSearch Agent\n")

    # Start search and generation
    print("Starting generation...")
    result = await agent.search(query)

    print(f"\nStatus: {result['status']}")

    # Display project info
    if result.get('project_id'):
        print(f"Project ID: {result['project_id']}")
    if result.get('project_dir'):
        print(f"Project directory: {result['project_dir']}")

    # Display messages
    if result.get('messages'):
        print("\nMessages:")
        for msg in result['messages']:
            if msg.get('agent'):
                content = msg.get('content', '')
                print(f"   {msg.get('agent')}: {content[:80]}...")

    # Display final report
    if result.get('final_report') and result['final_report'].get('result'):
        final_result = result['final_report']['result']
        if final_result.get('report'):
            report_data = final_result['report']
            report_content = report_data.get('content', '')
            print(f"\n=== Final Report ===")
            print(f"{report_content[:800]}...")
            print(f"\nFull report: {result['project_dir']}/reports/FINAL_REPORT.md")

            # Display metadata
            metadata = report_data.get('metadata', {})
            print(f"\n=== Metadata ===")
            print(f"Type: {metadata.get('type', 'unknown')}")
            print(f"Genre: {metadata.get('genre', 'unknown')}")
            print(f"Total chapters: {metadata.get('total_chapters', 0)}")
            print(f"Successful chapters: {metadata.get('successful_chapters', 0)}")
            print(f"Word count: {report_data.get('word_count', 0)}")

    print("\nTest completed")


if __name__ == "__main__":
    asyncio.run(main())
