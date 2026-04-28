from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
import aiohttp
import io
from typing import List
from backend.app.models import SlideContent


class PPTXGenerator:
    def __init__(self):
        self.prs = Presentation()

    def apply_style(self, style: str):
        """Apply different styles to presentation"""
        if style == "corporate":
            # Corporate style - blue tones
            self.title_slide_layout = self.prs.slide_layouts[0]
            self.content_slide_layout = self.prs.slide_layouts[1]
        elif style == "creative":
            # Creative style - colorful
            self.title_slide_layout = self.prs.slide_layouts[0]
            self.content_slide_layout = self.prs.slide_layouts[5]
        else:  # minimal
            self.title_slide_layout = self.prs.slide_layouts[0]
            self.content_slide_layout = self.prs.slide_layouts[1]

    async def create_presentation(
            self,
            slides: List[SlideContent],
            style: str,
            include_images: bool = True
    ) -> bytes:
        """Create PPTX file from slides content"""

        self.apply_style(style)

        for i, slide_content in enumerate(slides):
            if i == 0:
                # Title slide
                slide = self.prs.slides.add_slide(self.title_slide_layout)
                title = slide.shapes.title
                subtitle = slide.placeholders[1] if len(slide.placeholders) > 1 else None

                title.text = slide_content.title
                if subtitle:
                    subtitle.text = slide_content.content[:100]
            else:
                # Content slide
                slide_layout = self.content_slide_layout
                slide = self.prs.slides.add_slide(slide_layout)

                # Add title
                if slide.shapes.title:
                    slide.shapes.title.text = slide_content.title

                # Add content
                content_shape = None
                for shape in slide.placeholders:
                    if shape.placeholder_format.type == 1:  # Body placeholder
                        content_shape = shape
                        break

                if content_shape:
                    text_frame = content_shape.text_frame
                    text_frame.clear()

                    # Split by newlines for bullet points
                    for line in slide_content.content.split('\n'):
                        p = text_frame.add_paragraph()
                        p.text = line.strip()
                        p.font.size = Pt(18)
                        p.space_after = Pt(12)

                # Add image if available and requested
                if include_images and slide_content.image_url:
                    await self._add_image_to_slide(slide, slide_content.image_url)

        # Save to bytes
        output = io.BytesIO()
        self.prs.save(output)
        output.seek(0)
        return output.getvalue()

    async def _add_image_to_slide(self, slide, image_url: str):
        """Download and add image to slide"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        image_stream = io.BytesIO(image_data)

                        # Add image to top-right corner
                        left = Inches(7)
                        top = Inches(1.5)
                        width = Inches(3)
                        slide.shapes.add_picture(image_stream, left, top, width=width)
        except Exception as e:
            print(f"Failed to add image: {e}")