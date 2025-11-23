"""
Multi-Slide PPT Generator - HTML PPT Generator for Multiple Pages

Independent HTML architecture for each page, supporting parallel generation and flexible navigation
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger
from jinja2 import Environment, FileSystemLoader, Template


class MultiSlidePPTGenerator:
    """Multi-page HTML PPT Generator"""

    def __init__(self, llm_manager=None, prompt_manager=None, template_dir: Optional[Path] = None):
        """
        Initialize PPT Generator

        Args:
            llm_manager: LLM Manager (for generating page content)
            prompt_manager: Prompt Manager
            template_dir: Template directory path
        """
        self.llm_manager = llm_manager
        self.prompt_manager = prompt_manager
        self.template_dir = template_dir or self._get_default_template_dir()
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True
        )

        # PPT Configuration
        self.slide_size = {"width": 1280, "height": 720}
        self.aspect_ratio = "16:9"

        logger.info(f"[MultiSlidePPTGenerator] Initialization complete, template directory: {self.template_dir}")

    def _get_default_template_dir(self) -> Path:
        """Get default template directory"""
        return Path(__file__).parent / 'templates'

    async def generate_ppt(
        self,
        slides_data: List[Dict[str, Any]],
        ppt_config: Dict[str, Any],
        output_dir: Path
    ) -> Dict[str, Any]:
        """
        Generate complete multi-page PPT

        Args:
            slides_data: List of slide data
            ppt_config: PPT configuration
            output_dir: Output directory

        Returns:
            Generation results
        """
        try:
            logger.info(f"[MultiSlidePPTGenerator] Starting PPT generation, total {len(slides_data)} pages")

            # 1. Create output directory structure
            ppt_dir = self._create_directory_structure(output_dir)

            # 2. Generate slide metadata
            metadata = self._create_slides_metadata(slides_data, ppt_config)

            # 3. Generate all slides in parallel
            slide_files = await self._generate_all_slides(
                slides_data, metadata, ppt_dir
            )

            # 4. Generate navigation pages
            self._generate_navigation_pages(metadata, ppt_dir)

            # 5. Save metadata
            self._save_metadata(metadata, ppt_dir)

            # 6. Copy common assets
            self._copy_common_assets(ppt_dir)

            logger.info(f"[MultiSlidePPTGenerator] PPT generation complete: {ppt_dir}")

            return {
                "status": "success",
                "ppt_dir": str(ppt_dir),
                "total_slides": len(slides_data),
                "slide_files": slide_files,
                "index_page": str(ppt_dir / "index.html"),
                "presenter_page": str(ppt_dir / "presenter.html")
            }

        except Exception as e:
            logger.error(f"[MultiSlidePPTGenerator] PPT generation failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    def _create_directory_structure(self, output_dir: Path) -> Path:
        """Create PPT directory structure"""
        ppt_dir = output_dir / "ppt"
        ppt_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (ppt_dir / "slides").mkdir(exist_ok=True)
        (ppt_dir / "assets" / "styles").mkdir(parents=True, exist_ok=True)
        (ppt_dir / "assets" / "scripts").mkdir(parents=True, exist_ok=True)
        (ppt_dir / "assets" / "images").mkdir(parents=True, exist_ok=True)
        (ppt_dir / "data").mkdir(exist_ok=True)

        logger.info(f"[MultiSlidePPTGenerator] Directory structure created: {ppt_dir}")
        return ppt_dir

    def _create_slides_metadata(
        self,
        slides_data: List[Dict[str, Any]],
        ppt_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create slide metadata"""
        total_slides = len(slides_data)

        slides_meta = []
        for i, slide_data in enumerate(slides_data):
            slide_number = i + 1
            slide_type = slide_data.get('type', 'content')

            # Generate filename
            file_name = f"slide_{slide_number:02d}_{slide_type}.html"

            # Determine previous and next pages
            prev_file = f"slide_{slide_number-1:02d}_{slides_data[i-1].get('type', 'content')}.html" if i > 0 else None
            next_file = f"slide_{slide_number+1:02d}_{slides_data[i+1].get('type', 'content')}.html" if i < total_slides - 1 else None

            slides_meta.append({
                "slide_id": f"slide_{slide_number:02d}",
                "slide_number": slide_number,
                "file_name": file_name,
                "type": slide_type,
                "title": slide_data.get('title', f'Slide {slide_number}'),
                "template": slide_data.get('template', slide_type),
                "prev": prev_file,
                "next": next_file
            })

        metadata = {
            "ppt_title": ppt_config.get('title', 'Untitled Presentation'),
            "total_slides": total_slides,
            "generation_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "theme": ppt_config.get('theme', 'business'),
            "color_scheme": ppt_config.get('color_scheme', {
                "primary": "#2E8B57",
                "secondary": "#FF8C00",
                "accent": "#E6E6FA"
            }),
            "slides": slides_meta
        }

        return metadata

    async def _generate_all_slides(
        self,
        slides_data: List[Dict[str, Any]],
        metadata: Dict[str, Any],
        ppt_dir: Path
    ) -> List[str]:
        """Generate all slides in parallel"""
        tasks = []

        for i, slide_data in enumerate(slides_data):
            slide_meta = metadata['slides'][i]
            task = self._generate_single_slide(
                slide_data, slide_meta, metadata, ppt_dir
            )
            tasks.append(task)

        # Execute in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Check results
        slide_files = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"[MultiSlidePPTGenerator] Slide {i+1} generation failed: {result}")
            else:
                slide_files.append(result)

        logger.info(f"[MultiSlidePPTGenerator] Successfully generated {len(slide_files)}/{len(slides_data)} pages")
        return slide_files

    async def _generate_single_slide(
        self,
        slide_data: Dict[str, Any],
        slide_meta: Dict[str, Any],
        ppt_metadata: Dict[str, Any],
        ppt_dir: Path
    ) -> str:
        """Generate a single slide page"""
        try:
            slide_number = slide_meta['slide_number']
            slide_type = slide_meta['type']

            logger.info(f"[MultiSlidePPTGenerator] Generating slide {slide_number}: {slide_meta['title']}")

            # Check if LLM-generated HTML content already exists (V3 mode)
            if 'html_content' in slide_data:
                # V3 mode: Use HTML directly generated by PageAgent
                html_content = slide_data['html_content']
                logger.info(f"[MultiSlidePPTGenerator] Using PageAgent generated HTML (V3 mode)")
            else:
                # V2 compatibility mode: Use Jinja2 template rendering
                # 1. Select template
                template_name = self._get_template_name(slide_type)
                template = self.jinja_env.get_template(template_name)

                # 2. Prepare rendering data
                render_data = {
                    # Slide content
                    "content": slide_data.get('content', {}),

                    # Page metadata
                    "slide_number": slide_number,
                    "total_slides": ppt_metadata['total_slides'],
                    "slide_title": slide_meta['title'],
                    "slide_type": slide_type,

                    # Navigation information
                    "prev_slide": slide_meta['prev'],
                    "next_slide": slide_meta['next'],

                    # Theme configuration
                    "theme": ppt_metadata['theme'],
                    "colors": ppt_metadata['color_scheme'],

                    # PPT information
                    "ppt_title": ppt_metadata['ppt_title'],

                    # AIGC metadata
                    "aigc_metadata": self._generate_aigc_metadata()
                }

                # 3. Render HTML
                html_content = template.render(**render_data)
                logger.info(f"[MultiSlidePPTGenerator] Using Jinja2 template rendering HTML (V2 compatibility mode)")

            # 4. Wrap HTML as complete page (add navigation and basic structure)
            html_content = self._wrap_slide_html(
                html_content,
                slide_meta,
                ppt_metadata
            )

            # 5. Save file
            output_file = ppt_dir / "slides" / slide_meta['file_name']
            output_file.write_text(html_content, encoding='utf-8')

            logger.info(f"[MultiSlidePPTGenerator] Slide {slide_number} saved: {output_file.name}")
            return str(output_file)

        except Exception as e:
            logger.error(f"[MultiSlidePPTGenerator] Slide {slide_number} generation failed: {e}")
            raise

    def _wrap_slide_html(
        self,
        content_html: str,
        slide_meta: Dict[str, Any],
        ppt_metadata: Dict[str, Any]
    ) -> str:
        """
        Process slide HTML

        V3 architecture: No longer inject navigation components, keep LLM-generated HTML pure
        Navigation is handled uniformly by presenter.html container page
        """
        slide_number = slide_meta['slide_number']

        # Check if it's already a complete HTML document
        is_complete_html = '<!DOCTYPE' in content_html or '<html' in content_html

        if is_complete_html:
            # LLM-generated is complete HTML, return directly without modification
            logger.info(f"[MultiSlidePPTGenerator] Slide {slide_number}: Using LLM-generated complete HTML, keeping it pure")
            return content_html
        else:
            # Extract variables needed for navigation
            total_slides = ppt_metadata.get('total_slides', 1)
            prev_slide = slide_meta.get('prev', None)
            next_slide = slide_meta.get('next', None)
            
            # Prepare navigation button HTML (avoid backslash in f-string)
            quote = "'"
            if prev_slide:
                prev_button = f'<button class="nav-btn" onclick="window.location.href={quote}{prev_slide}{quote}"><i class="fas fa-arrow-left"></i> Previous</button>'
            else:
                prev_button = '<button class="nav-btn" disabled><i class="fas fa-arrow-left"></i> Previous</button>'
            
            if next_slide:
                next_button = f'<button class="nav-btn" onclick="window.location.href={quote}{next_slide}{quote}">Next <i class="fas fa-arrow-right"></i></button>'
            else:
                next_button = '<button class="nav-btn" disabled>Next <i class="fas fa-arrow-right"></i></button>'
            
            # Prepare keyboard navigation script
            prev_slide_safe = prev_slide or ''
            next_slide_safe = next_slide or ''
            
            # Not complete HTML, needs full wrapping
            return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{slide_meta['title']} - {ppt_metadata['ppt_title']}</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet"/>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body, html {{
            width: 100%;
            height: 100%;
            overflow: hidden;
            font-family: -apple-system, BlinkMacSystemFont, "Seguro UI", sans-serif;
        }}
        .slide-controls {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            display: flex;
            gap: 10px;
            z-index: 1000;
        }}
        .nav-btn {{
            padding: 10px 20px;
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid #ddd;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s;
        }}
        .nav-btn:hover {{
            background: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .nav-btn:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
        }}
        .slide-number {{
            position: fixed;
            bottom: 20px;
            left: 20px;
            padding: 8px 16px;
            background: rgba(255, 255, 255, 0.9);
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            z-index: 1000;
        }}
    </style>
</head>
<body>
    {content_html}

    <div class="slide-number">
        {slide_number} / {total_slides}
    </div>

    <div class="slide-controls">
        <button class="nav-btn" onclick="window.location.href='../index.html'">
            <i class="fas fa-home"></i> Home
        </button>
        {prev_button}
        {next_button}
    </div>

    <script>
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {{
            if (e.key === 'ArrowLeft' && '{prev_slide_safe}') {{
                window.location.href = '{prev_slide_safe}';
            }} else if (e.key === 'ArrowRight' && '{next_slide_safe}') {{
                window.location.href = '{next_slide_safe}';
            }} else if (e.key === 'Home') {{
                window.location.href = '../index.html';
            }}
        }});
    </script>
</body>
</html>
"""

    def _get_template_name(self, slide_type: str) -> str:
        """Get template filename"""
        template_map = {
            'cover': 'slide_cover.html',
            'toc': 'slide_toc.html',
            'content': 'slide_content.html',
            'chart': 'slide_chart.html',
            'comparison': 'slide_comparison.html',
            'summary': 'slide_summary.html'
        }
        return template_map.get(slide_type, 'slide_content.html')

    def _generate_navigation_pages(
        self,
        metadata: Dict[str, Any],
        ppt_dir: Path
    ):
        """Generate navigation pages"""
        # 1. Generate index.html (thumbnail navigation)
        self._generate_index_page(metadata, ppt_dir)

        # 2. Generate presenter.html (presentation mode)
        self._generate_presenter_page(metadata, ppt_dir)

    def _generate_index_page(self, metadata: Dict[str, Any], ppt_dir: Path):
        """Generate navigation entry page"""
        try:
            template = self.jinja_env.get_template('index.html')
            html = template.render(metadata=metadata)

            output_file = ppt_dir / "index.html"
            output_file.write_text(html, encoding='utf-8')

            logger.info(f"[MultiSlidePPTGenerator] Navigation page generated: index.html")
        except Exception as e:
            logger.warning(f"[MultiSlidePPTGenerator] Navigation page generation failed: {e}")

    def _generate_presenter_page(self, metadata: Dict[str, Any], ppt_dir: Path):
        """Generate presentation mode page"""
        try:
            template = self.jinja_env.get_template('presenter.html')
            html = template.render(metadata=metadata)

            output_file = ppt_dir / "presenter.html"
            output_file.write_text(html, encoding='utf-8')

            logger.info(f"[MultiSlidePPTGenerator] Presenter page generated: presenter.html")
        except Exception as e:
            logger.warning(f"[MultiSlidePPTGenerator] Presenter page generation failed: {e}")

    def _save_metadata(self, metadata: Dict[str, Any], ppt_dir: Path):
        """Save metadata to JSON file"""
        metadata_file = ppt_dir / "data" / "slides_metadata.json"
        metadata_file.write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
        logger.info(f"[MultiSlidePPTGenerator] Metadata saved: {metadata_file}")

    def _copy_common_assets(self, ppt_dir: Path):
        """Copy common asset files"""
        # TODO: Copy common CSS, JS and other resources
        # Currently using CDN, no local resources needed
        logger.info("[MultiSlidePPTGenerator] Common assets processing complete")

    def _generate_aigc_metadata(self) -> str:
        """Generate AIGC metadata"""
        import uuid
        project_id = str(uuid.uuid4())[:32]

        metadata = {
            "AIGC": {
                "Label": "1",
                "ContentProducer": "ai-content-generator",
                "ProduceID": project_id,
                "ContentPropagator": "ai-content-generator",
                "PropagateID": project_id
            }
        }
        return json.dumps(metadata, ensure_ascii=False)


# Helper functions

def create_slide_data(
    slide_type: str,
    title: str,
    content: Dict[str, Any],
    template: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create slide data structure

    Args:
        slide_type: Slide type (cover, toc, content, chart, etc.)
        title: Slide title
        content: Slide content
        template: Optional custom template name

    Returns:
        Slide data dictionary
    """
    return {
        "type": slide_type,
        "title": title,
        "content": content,
        "template": template or slide_type
    }
