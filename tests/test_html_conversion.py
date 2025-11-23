"""
HTML Conversion Tests
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agents.html import (
    DocumentHTMLAgent,
    FictionHTMLAgent,
    PPTHTMLAgent,
    get_template_registry
)


def test_document_agent():
    """Test document HTML agent conversion."""
    agent = DocumentHTMLAgent()
    content = """
# 

## 



## 


"""

    html = agent.convert_to_html(
        content=content,
        metadata={'title': '', 'author': ''},
        template='academic',
        theme='light'
    )

    assert '<h1' in html
    assert '' in html
    print(" ")


def test_fiction_agent():
    """Test fiction HTML agent"""
    agent = FictionHTMLAgent()
    content = """
# Test Novel

## Chapter 1

The story begins...

## Chapter 2

The story continues...
"""

    html = agent.convert_to_html(
        content=content,
        metadata={'title': 'Test Novel', 'author': 'Test Author'},
        template='novel',
        theme='sepia'
    )

    assert '<h1' in html or '<h2' in html
    assert 'Test Novel' in html
    print("Fiction agent test passed")


def test_ppt_agent():
    """Test PPT HTML agent"""
    agent = PPTHTMLAgent(framework='reveal')
    content = """
# Test PPT

---

## Slide 1

- Point 1
- Point 2

---

## Slide 2

More content...
"""

    html = agent.convert_to_html(
        content=content,
        metadata={'title': 'Test PPT'},
        template='default',
        theme='white'
    )

    assert 'reveal' in html.lower()
    assert 'Test PPT' in html
    print("PPT agent test passed")


def test_template_registry():
    """Test template registry"""
    registry = get_template_registry()

    # List document templates
    doc_templates = registry.list_templates('document')
    assert len(doc_templates) > 0

    # Get recommended template
    recommended = registry.recommend_template('document', 'research')
    assert recommended in ['academic', 'technical']

    print("Template registry test passed")


def test_chapter_extraction():
    """Test chapter extraction"""
    agent = DocumentHTMLAgent()
    content = """
# Test Document

## Chapter 1

Chapter 1 content

### 1.1 Subsection

Subsection 1.1 content

## Chapter 2

Chapter 2 content
"""

    parsed = agent.parse_content(content)
    assert len(parsed['sections']) > 0
    assert parsed['title'] == 'Test Document'
    print("Chapter extraction test passed")


def test_ppt_smart_split():
    """PPT"""
    agent = PPTHTMLAgent(framework='reveal')
    content = """
# 



## 



## 


"""

    parsed = agent.parse_content(content)
    slides = parsed['slides']

    # 
    assert len(slides) >= 2
    assert slides[0]['layout'] == 'title'
    print(" PPT")


if __name__ == "__main__":
    print("=" * 60)
    print("HTML Conversion Tests")
    print("=" * 60)

    test_document_agent()
    test_fiction_agent()
    test_ppt_agent()
    test_template_registry()
    test_chapter_extraction()
    test_ppt_smart_split()

    print("\n" + "=" * 60)
    print("All tests passed")
    print("=" * 60)
