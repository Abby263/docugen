"""
Design Coordinator Agent - PPT Global Design Coordinator

Generates unified color scheme, theme style, and design patterns after outline generation and before page generation
"""

from typing import Dict, Any
from pydantic import BaseModel, Field
import logging
import json

logger = logging.getLogger(__name__)


class DesignSpec(BaseModel):
    """PPT Global Design Specification"""

    # Color Scheme
    primary_color: str = Field(description="Primary color (hex)")
    secondary_color: str = Field(description="Secondary color (hex)")
    accent_color: str = Field(description="Accent color (hex)")
    background_color: str = Field(description="Background color (hex)")
    text_color: str = Field(description="Text color (hex)")
    text_secondary_color: str = Field(description="Secondary text color (hex)")

    # Font Scheme
    title_font_size: str = Field(description="Title font size")
    content_font_size: str = Field(description="Content font size")
    font_family: str = Field(description="Font family")

    # Layout Style
    layout_style: str = Field(description="Layout style: modern/business/minimal/creative")
    spacing: str = Field(description="Spacing style: compact/normal/spacious")
    border_radius: str = Field(description="Border radius: 0px/0.5rem/1rem")

    # Visual Elements
    use_shadows: bool = Field(description="Whether to use shadows")
    use_gradients: bool = Field(description="Whether to use gradients")
    animation_style: str = Field(description="Animation style: none/subtle/dynamic")

    # Chart Colors
    chart_colors: list[str] = Field(description="Chart color array")


class DesignCoordinator:
    """PPT Global Design Coordinator"""

    def __init__(self, llm_client):
        """
        Initialize design coordinator

        Args:
            llm_client: LLM client
        """
        self.llm_client = llm_client

    async def generate_design_spec(
        self,
        topic: str,
        outline: Dict[str, Any],
        style: str
    ) -> DesignSpec:
        """
        Generate PPT global design specification

        Args:
            topic: PPT topic
            outline: PPT outline
            style: User-specified style (ted/business/academic/creative/simple)

        Returns:
            DesignSpec: Design specification object
        """
        prompt = self._build_design_prompt(topic, outline, style)

        logger.info(f"[DesignCoordinator] Generating design specification: {topic}")

        response = await self.llm_client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.9  # Increase creativity, let LLM freely choose colors
        )

        # Parse LLM returned JSON
        content = response.get("content", "").strip()

        # Clean possible markdown code block markers
        if content.startswith('```json'):
            content = content[7:]
        elif content.startswith('```'):
            content = content[3:]
        if content.endswith('```'):
            content = content[:-3]
        content = content.strip()

        try:
            design_dict = json.loads(content)
            design_spec = DesignSpec(**design_dict)
            logger.info(f"[DesignCoordinator] Design specification generated successfully: {design_spec.layout_style} style")
            return design_spec
        except Exception as e:
            logger.error(f"[DesignCoordinator] Failed to parse design specification: {e}")
            # Return default design specification
            return self._get_default_design(style)

    def _build_design_prompt(
        self,
        topic: str,
        outline: Dict[str, Any],
        style: str
    ) -> str:
        """Build design generation prompt"""

        # Extract outline key information
        pages = outline.get('pages', [])
        page_topics = [p.get('topic', '') for p in pages[:5]]  # First 5 page topics

        style_guides = {
            'ted': 'TED presentation style, minimalism, each page has only large title + core points, minimal text, suitable for live presentations. Color scheme flexibly chosen based on theme, bold and impactful',
            'business': 'Business presentation style, detailed content, includes detailed data, charts, bullet points, suitable for professional presentations. Color scheme flexibly chosen based on theme content',
            'academic': 'Academic rigorous style, color scheme should be chosen based on theme content, can use dark colors or other suitable colors',
            'creative': 'Creative and lively style, encourages bold and interesting color schemes',
            'simple': 'Minimalist style, use simple color scheme, but can choose appropriate colors based on theme'
        }

        style_hint = style_guides.get(style, 'Freely choose appropriate color scheme based on theme content')

        return f"""You are a creative PPT visual designer. Please design a unique and attractive visual scheme based on the PPT topic content.

# PPT Topic Analysis
**Topic**: {topic}
**Main Content**: {', '.join(page_topics)}
**Style**: {style} - {style_hint}

# Design Task
**Please creatively design color scheme and visual style based on the characteristics of the topic content!**

## Color Design Key Points
1. **Style Priority**:
   - **If the style is {style}, please prioritize following the requirements of that style**
   - ted style: Bold and impactful color scheme, choose the most attractive color combinations based on theme
   - business style: Professional but flexible, choose appropriate color scheme based on theme, not limited to blue
   - creative style: Bold use of contrasting colors and vibrant colors

2. **Theme Relevance** (while following style requirements):
   - Gaming theme? Consider vibrant, energetic colors (purple, orange, cyan, magenta, etc.)
   - Pet theme? Consider warm, cute colors (pink, light orange, sky blue, grass green, etc.)
   - Technology theme? Consider futuristic colors (dark blue, cyan, purple, etc.)
   - Nature/Environmental theme? Consider green tones, earth tones
   - Food theme? Consider warm colors (red, orange, yellow)
   - Finance/Professional theme? Consider stable colors (dark blue, dark green, gray)

3. **Color Matching**: Primary, secondary, and accent colors should form interesting contrast and harmony
4. **Readability**: Ensure sufficient contrast between text and background

## Visual Element Design
- **layout_style**: Choose based on theme (modern/playful/elegant/tech/artistic/minimal, etc.)
- **use_gradients**: Gaming and technology themes are suitable for gradients
- **border_radius**: Cute themes use large radius, professional themes use small radius
- **animation_style**: Lively themes use dynamic, serious themes use subtle or none

# Creative Examples

**TED Presentation Style Example (for ted style)**:
{{
    "primary_color": "#dc2626",  // Bold primary color - choose based on theme
    "secondary_color": "#1f2937",  // Dark color - contrast
    "accent_color": "#fbbf24",  // Accent color - attract attention
    "background_color": "#ffffff",
    "title_font_size": "4rem",  // TED style uses extra-large titles
    "content_font_size": "1.5rem",  // Body text also large
    "use_shadows": false,  // Minimal, no shadows
    "use_gradients": false,  // Minimal, no gradients
    "animation_style": "none",  // Minimal, no animation
    "chart_colors": ["#dc2626", "#1f2937", "#fbbf24", "#6b7280", "#f97316"]
}}

**Gaming Theme Example**:
{{
    "primary_color": "#8b5cf6",  // Purple - gaming feel
    "secondary_color": "#ec4899",  // Magenta - energy
    "accent_color": "#f59e0b",  // Orange - emphasis
    "chart_colors": ["#8b5cf6", "#ec4899", "#06b6d4", "#10b981", "#f59e0b"]
}}

**Pet Theme Example**:
{{
    "primary_color": "#f472b6",  // Pink - cute
    "secondary_color": "#fb923c",  // Light orange - warm
    "accent_color": "#60a5fa",  // Sky blue - fresh
    "chart_colors": ["#f472b6", "#fb923c", "#a78bfa", "#34d399", "#fbbf24"]
}}

**Technology/AI Theme Example**:
{{
    "primary_color": "#06b6d4",  // Cyan - tech feel
    "secondary_color": "#8b5cf6",  // Purple - futuristic
    "accent_color": "#10b981",  // Green - intelligent
    "chart_colors": ["#06b6d4", "#8b5cf6", "#10b981", "#f59e0b", "#ec4899"]
}}

# Output Requirements
**Output ONLY JSON! No explanations!**

JSON Structure:
{{
    "primary_color": "#xxxxxx",
    "secondary_color": "#xxxxxx",
    "accent_color": "#xxxxxx",
    "background_color": "#ffffff",
    "text_color": "#1f2937",
    "text_secondary_color": "#6b7280",
    "title_font_size": "2.5rem",
    "content_font_size": "1rem",
    "font_family": "'Segoe UI', 'Microsoft YaHei', sans-serif",
    "layout_style": "Choose based on theme",
    "spacing": "normal",
    "border_radius": "1rem",
    "use_shadows": true,
    "use_gradients": true,
    "animation_style": "subtle",
    "chart_colors": ["color1", "color2", "color3", "color4", "color5"]
}}

**Important Notes**:
- Current style is "{style}", please strictly follow the requirements of that style
- ted style requires extra-large font (title_font_size: 4rem), minimal design, bold color scheme
- business style requires detailed content, moderate font, professional color scheme
- Don't always use blue! Choose the most suitable color based on theme "{topic}"
- Be creative, let the color scheme resonate with the theme content
- chart_colors should include 5 harmonious colors

Output JSON immediately:
"""

    def _get_default_design(self, style: str) -> DesignSpec:
        """Get default design specification"""

        default_designs = {
            'ted': DesignSpec(
                primary_color="#dc2626",
                secondary_color="#1f2937",
                accent_color="#fbbf24",
                background_color="#ffffff",
                text_color="#1f2937",
                text_secondary_color="#6b7280",
                title_font_size="4rem",  # TED style extra-large title
                content_font_size="1.5rem",  # TED style large body text
                font_family="'Segoe UI', 'Microsoft YaHei', sans-serif",
                layout_style="minimal",  # Minimal layout
                spacing="spacious",  # Spacious spacing
                border_radius="0px",  # No border radius, minimal
                use_shadows=False,  # No shadows
                use_gradients=False,  # No gradients
                animation_style="none",  # No animation
                chart_colors=["#dc2626", "#1f2937", "#fbbf24", "#6b7280", "#f97316"]
            ),
            'business': DesignSpec(
                primary_color="#2563eb",
                secondary_color="#1d4ed8",
                accent_color="#3b82f6",
                background_color="#ffffff",
                text_color="#1f2937",
                text_secondary_color="#6b7280",
                title_font_size="2.5rem",
                content_font_size="1rem",
                font_family="'Segoe UI', 'Microsoft YaHei', sans-serif",
                layout_style="business",
                spacing="normal",
                border_radius="0.5rem",
                use_shadows=True,
                use_gradients=True,
                animation_style="subtle",
                chart_colors=["#2563eb", "#3b82f6", "#60a5fa", "#93c5fd", "#dbeafe"]
            ),
            'simple': DesignSpec(
                primary_color="#1f2937",
                secondary_color="#374151",
                accent_color="#4b5563",
                background_color="#ffffff",
                text_color="#1f2937",
                text_secondary_color="#6b7280",
                title_font_size="2.5rem",
                content_font_size="1rem",
                font_family="'Segoe UI', 'Microsoft YaHei', sans-serif",
                layout_style="minimal",
                spacing="spacious",
                border_radius="0px",
                use_shadows=False,
                use_gradients=False,
                animation_style="none",
                chart_colors=["#1f2937", "#374151", "#4b5563", "#6b7280", "#9ca3af"]
            )
        }

        return default_designs.get(style, default_designs['business'])

    def design_spec_to_dict(self, design_spec: DesignSpec) -> Dict[str, Any]:
        """Convert DesignSpec to dictionary for passing to PageAgent"""
        return design_spec.model_dump()
