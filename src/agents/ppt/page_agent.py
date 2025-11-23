"""
PageAgent - PPT

PageAgentPPTHTML
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class PageSpec(BaseModel):
    """ - """
    slide_number: int = Field(description="")
    page_type: str = Field(description=": title/content/section/conclusion")
    topic: str = Field(description="")
    key_points: list[str] = Field(description="")
    has_chart: bool = Field(default=False, description="")


class GlobalContext(BaseModel):
    """ - PageAgent"""
    ppt_title: str = Field(description="PPT")
    style: str = Field(description=": ted/business/academic/creative/simple")
    colors: Dict[str, str] = Field(description="")
    total_slides: int = Field(description="")
    speech_scene: Optional[str] = Field(default=None, description="")


class PageAgent:
    """PPT"""

    def __init__(self, llm_client, css_guide: str):
        """
        PageAgent

        Args:
            llm_client: LLM
            css_guide: CSS
        """
        self.llm_client = llm_client
        self.css_guide = css_guide

    async def generate_page_html(
        self,
        page_spec: PageSpec,
        global_context: GlobalContext,
        content_data: str
    ) -> Dict[str, str]:
        """
        HTML

        Args:
            page_spec: 
            global_context: 
            content_data: 

        Returns:
            
            - html_content: HTMLdiv
            - speech_notes: 
        """
        prompt = self._build_prompt(page_spec, global_context, content_data)

        logger.info(f"[PageAgent] {page_spec.slide_number}: {page_spec.topic}")

        response = await self.llm_client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.9  #
        )

        # Clean LLM output: remove descriptive text and code block markers
        html = response.get("content", "").strip()

        # 1. Find the position of the first HTML tag
        import re

        # Find the first HTML tag starting with <
        first_tag_match = re.search(r'<[a-zA-Z!]', html)
        if first_tag_match:
            # Remove all descriptive text before HTML
            html = html[first_tag_match.start():]

        # 2. Remove markdown code block markers
        if html.startswith('```html'):
            html = html[7:]
        if html.startswith('```'):
            html = html[3:]
        if html.endswith('```'):
            html = html[:-3]

        # 3. Clean possible leading text again
        html = html.strip()
        first_tag_match = re.search(r'<[a-zA-Z!]', html)
        if first_tag_match and first_tag_match.start() > 0:
            html = html[first_tag_match.start():]

        result = {"html_content": html.strip()}

        # 
        if global_context.speech_scene:
            speech_notes = await self._generate_speech_notes(
                page_spec, global_context, content_data, html
            )
            result["speech_notes"] = speech_notes

        return result

    def _build_prompt(
        self,
        page_spec: PageSpec,
        global_context: GlobalContext,
        content_data: str
    ) -> str:
        """TODO: Add docstring."""

        # page_type
        layout_hints = {
            'title': '',
            'section': '',
            'content': '//',
            'conclusion': ''
        }

        # Add special layout hints based on style
        style_hint = ""
        if global_context.style == 'ted':
            style_hint = """
****TED Presentation Style Requirements (IMPORTANT!)****
This is a TED-style PPT and must follow these principles:

1. **Minimal Content**:
   - Each page has only 1 large title + 1-3 core points
   - Title must use extra-large font size (text-6xl or text-7xl, font-size: 3-5rem)
   - Core points use large font size (text-2xl or text-3xl, font-size: 1.5-2rem)
   - **Do NOT** use long paragraphs, detailed lists, or dense text

2. **Visual Impact**:
   - Lots of white space, centered content
   - Use bold colors from the global color scheme
   - Simple background, highlight core information

3. **Layout Proportions**:
   - Title area: 30-40% (extra-large title)
   - Core points area: 30-40% (1-3 sentences)
   - Other areas: white space
   - Minimal footer (only page number)

4. **Forbidden Elements**:
   - ❌ No multi-level lists
   - ❌ No detailed data tables
   - ❌ No long paragraph explanations
   - ❌ No complex layouts

**TED Style Example**:
```html
<div style="height: 60%; display: flex; align-items: center; justify-content: center;">
    <h1 style="font-size: 4rem; font-weight: bold; text-align: center;">
        Core Point Title
    </h1>
</div>
<div style="height: 30%; display: flex; align-items: center; justify-content: center;">
    <p style="font-size: 1.8rem; text-align: center; max-width: 70%;">
        One sentence explaining the core point
    </p>
</div>
```
"""
        elif global_context.style == 'business':
            style_hint = """
****Business Presentation Style Requirements****
This is a business presentation style PPT that can include detailed content:

1. **Detailed Content**: Can include multiple points, data, charts
2. **Clear Structure**: Use lists, cards to organize content
3. **Professional Layout**: Title, content area, charts properly distributed
4. **Moderate Font Sizes**: Title text-4xl (2.5rem), body text-base (1rem)
"""

        chart_hint = ""
        if page_spec.has_chart:
            chart_hint = """
****Chart Generation Requirements****
**Use Chart.js to create charts**

1. **Canvas Element Requirements**
   <canvas id="chart_{page_spec.slide_number}_{{random_number}}"></canvas>

2. **Chart Container Height Limit (IMPORTANT!)**
   Chart container must have explicit height to avoid exceeding page boundaries:
   - Recommended fixed height: height: 350px or height: 400px
   - Or use max-height limit: max-height: 400px
   - **Do NOT** use flex: 1 or 100% height, this will cause charts to exceed page

3. **Chart.js Configuration Example**
   <script>
   document.addEventListener('DOMContentLoaded', function() {{
       const canvas = document.getElementById('chart_{{page_spec.slide_number}}_12345');
       if (!canvas) return;

       const ctx = canvas.getContext('2d');
       new Chart(ctx, {{
           type: 'bar',  // bar, line, pie, doughnut
           data: {{
               labels: ['2020', '2021', '2022', '2023', '2024'],
               datasets: [{{
                   label: 'Data Label',
                   data: [100, 120, 150, 180, 200],
                   backgroundColor: 'rgba(59, 130, 246, 0.5)',
                   borderColor: 'rgba(59, 130, 246, 1)',
                   borderWidth: 2
               }}]
           }},
           options: {{
               responsive: true,
               maintainAspectRatio: false,
               plugins: {{
                   legend: {{ display: true }}
               }},
               scales: {{
                   y: {{ beginAtZero: true }}
               }}
           }}
       }});
   }});
   </script>

****Important Notes****
- **Canvas ID**: Use chart_{{page_spec.slide_number}}_{{random_number}} to avoid ID conflicts
- **Chart Container**: Must set fixed height (e.g., height: 350px), do not use flex: 1
- **Chart Types**: bar (bar chart), line (line chart), pie (pie chart), doughnut (doughnut chart)
- **responsive**: Set to true, chart will adapt to container
- **maintainAspectRatio**: Set to false, chart height controlled by container
- **ID in script tag**: Must exactly match canvas ID
"""

        return f"""You are an HTML code generator. You can ONLY output HTML code, nothing else.

# Task
Generate complete HTML code for PPT slide {page_spec.slide_number}

# Global Information
- PPT Title: {global_context.ppt_title}
- Style: {global_context.style}
- Color Scheme: {global_context.colors}
- Total Slides: {global_context.total_slides}

# This Page Information
- Page Number: {page_spec.slide_number}/{global_context.total_slides}
- Type: {page_spec.page_type}
- Topic: {page_spec.topic}
- Key Points: {page_spec.key_points}

# Style Requirements
{style_hint}

# Layout Suggestions
{layout_hints.get(page_spec.page_type, '')}

{chart_hint}

# Content Data
{content_data[:1000]}

{self.css_guide}

# ================================
# Strict Output Requirements (CRITICAL!)
# ================================

**You must strictly follow these rules, otherwise output will be rejected:**

1. **Output ONLY HTML code! Do NOT output any explanations, descriptions, comments, or design thoughts!**
2. **Do NOT output markdown code block markers! No ```html or ```!**
3. **Do NOT output descriptive text like "Based on the content provided", "I will create", "## Design Notes", etc.!**
4. **Start directly with <!DOCTYPE html> and end with </html>!**
5. **HTML must be complete, self-contained page, 100vw × 100vh full-screen layout**
6. **Use colors from global color scheme, do not modify on your own**
7. **Must include complete <head> section, including Chart.js reference (if charts needed)**

**Forbidden Output Examples (These are all WRONG):**
❌ "# Pet Market Analysis..."
❌ "Based on the content provided, I will create..."
❌ "```html"
❌ "## Design Notes"
❌ "Here is the HTML code:"

**Correct Output Format (The ONLY correct format):**
✅ Direct output: <!DOCTYPE html><html lang="en"><head>...

**Layout Proportion Suggestions:**
- Header (title area): 10-15%, use text-4xl or text-5xl
- Content area: 70-80%, use flex-1
- Footer (page number, etc.): 5-10%, use text-sm or text-base

**Emphasis again: Output ONLY HTML code! No explanations! Start outputting HTML code immediately:**
"""

    async def _generate_speech_notes(
        self,
        page_spec: PageSpec,
        global_context: GlobalContext,
        content_data: str,
        html_content: str
    ) -> str:
        """
        

        Args:
            page_spec: 
            global_context: 
            content_data: 
            html_content: HTML

        Returns:
            
        """
        prompt = f"""PPT{page_spec.slide_number}

# 
{global_context.speech_scene}

# PPT
- PPT: {global_context.ppt_title}
- : {page_spec.slide_number}/{global_context.total_slides}
- : {page_spec.page_type}

# 
- : {page_spec.topic}
- : {page_spec.key_points}

# 
{html_content[:500]}  # HTML

# 
1. **{global_context.speech_scene}**
2. 
   - title(): 
   - section(): 
   - content(): 
   - conclusion(): 
3. 150-300
4. 
5. 
6. ****


"""

        logger.info(f"[PageAgent] {page_spec.slide_number}")

        response = await self.llm_client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7  # 
        )

        speech_notes = response.get("content", "").strip()

        return speech_notes
