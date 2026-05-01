from datetime import datetime
from fastapi import APIRouter, Request, Response, Form
from fastapi.responses import HTMLResponse
from jinja2 import Template
import json
import logging
import os
from playwright.async_api import async_playwright
import shutil
import traceback
import uuid

from web import web_server

log = logging.getLogger(__name__)

router = APIRouter()

SAMPLE_CONTEXT = {
    "entity": {
        "id": 486,
        "layout": "Charakter",
        "kind": "Charakter",
        "type": "Abenteurer",
        "title": {
            "primary": "Sarius",
            "secondary": "Kundschafter der Hofkanzlei",
        },
        "description": "Wenn <self>ich</self> das <zone>Feld</zone> <key>betrete</key>, <key>Ziehe</key> eine <key>Karte</key> und wähle 2x:\n<ul>\n<li>Sieh Dir 2 <key>Schildkarte</key> Deiner Wahl an.</li>\n<li>Sieh Dir 1 <zone>Handkarten</zone> Deiner Wahl an.</li>\n</ul>",
        "flavour": "Diesmal war der Schrei des Ausgucks eine Erlösung.",
        "cost": {
            "terra": 0,
            "aqua": 3,
            "aeris": 0,
            "ignis": 0,
            "magica": 0,
            "unshaped": 2,
        },
        "elemental": {
            "element": "Aqua",
            "amount": 1,
        },
        "stats": {
            "offensive": {
                "strength": 4,
                "toughness": 3,
            },
            "defensive": {
                "strength": 2,
                "toughness": 5,
            },
        },
        "rarity": "Rare",
    },
    "release": {
        "label": {
            "display": "dev"
        }
    },
    "card": {
        "width": {
            "bleed": {"mm": 69.5, "px": 820},
            "no_bleed": {"mm": 63.5, "px": 750}
        },
        "height": {
            "bleed": {"mm": 94.9, "px": 1120},
            "no_bleed": {"mm": 88.9, "px": 1050}
        },
        "bleed": {
            "mm": 3,
            "px": 35,
        },
        "border_radius": {
            "mm": 3,
            "px": 35,
        },
    },
    "meta": {
        # These will be updated to absolute paths if possible
        "layout": {"path": "/static/images/layout"}, # Placeholder
        "style": "" 
    }
}

@router.get("/layout_constructor")
async def constructor_page(request: Request):
    # Load templates from the repository
    repositories_path = os.path.join(os.getcwd(), "repositories")
    templates_path = os.path.join(repositories_path, "anor", "templates")
    
    files = {
        "Charakter.jinja": "",
        "Ereignis.jinja": "",
        "Manifestation.jinja": "",
        "style.jinja": ""
    }

    for file_name in files.keys():
        file_path = os.path.join(templates_path, file_name)
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                files[file_name] = f.read()

    # Create default data.json from SAMPLE_CONTEXT
    import json
    default_data = json.dumps(SAMPLE_CONTEXT, indent=4, ensure_ascii=False)

    return web_server.templates.TemplateResponse(
        request,
        "layout_constructor.jinja",
        {
            "title": "Layout Constructor",
            "author": "Aetherlab",
            "files": files,
            "default_data": default_data,
            "now": datetime.now(),
        }
    )

@router.post("/layout_constructor/preview")
async def preview_card(request: Request):
    try:
        payload = await request.json()
        files = payload.get("files", {})
        data_json = files.get("data.json", "{}")
        
        import json
        context = json.loads(data_json)
        
        # Determine layout
        active_layout_override = payload.get("activeLayout")
        if active_layout_override and active_layout_override.endswith(".jinja") and active_layout_override != "style.jinja":
            layout_filename = active_layout_override
        else:
            layout_name = context.get("entity", {}).get("layout", "Charakter")
            layout_filename = f"{layout_name}.jinja"
        
        jinja_code = files.get(layout_filename)
        if not jinja_code:
            # Fallback to Charakter if specific layout not found in payload
            jinja_code = files.get("Charakter.jinja", "")

        style_code = files.get("style.jinja", "")
        
        # Prepare paths for the context
        repositories_path = os.path.join(os.getcwd(), "repositories")
        anor_repo_path = os.path.join(repositories_path, "anor")
        
        if "meta" not in context:
            context["meta"] = {}
        
        context["meta"]["layout"] = {"path": os.path.join(anor_repo_path, "layout")}
        context["meta"]["templates"] = {"path": os.path.join(anor_repo_path, "templates")}
        context["meta"]["fonts"] = {"path": os.path.join(anor_repo_path, "fonts")}
        context["meta"]["artworks"] = {"path": os.path.join(anor_repo_path, "artworks")}
        
        # Resolve artwork path based on ID if not explicitly provided
        if "entity" not in context: context["entity"] = {}
        entity = context["entity"]
        if "artwork" not in entity or not entity["artwork"].get("path"):
            card_id = entity.get("id", "0")
            artwork_path = os.path.join(anor_repo_path, "artworks", f"{card_id}.png")
            # If the file doesn't exist, we might want to fall back to a placeholder or 0.png
            if not os.path.exists(artwork_path):
                artwork_path = os.path.join(anor_repo_path, "artworks", "0.png")
            
            context["entity"]["artwork"] = {"path": artwork_path}

        # Render Style
        style_template = Template(style_code)
        context["meta"]["style"] = style_template.render(**context)

        # Render Main Layout
        template = Template(jinja_code)
        html_content = template.render(**context)

        # Inject Cut Line if requested
        if payload.get("showCutLine"):
            bleed_px = context.get("card", {}).get("bleed", {}).get("px", 35)
            border_radius_px = context.get("card", {}).get("border_radius", {}).get("px", 35)
            cut_line_html = f"""
            <div id="cut-line-overlay" style="position: absolute; top: {bleed_px}px; left: {bleed_px}px; right: {bleed_px}px; bottom: {bleed_px}px; 
                        border: 2px dashed rgba(255, 0, 0, 0.8); border-radius: {border_radius_px}px; 
                        pointer-events: none; z-index: 99999; box-shadow: 0 0 0 5000px rgba(0,0,0,0.3);">
            </div>
            """
            if "</body>" in html_content:
                html_content = html_content.replace("</body>", f"{cut_line_html}</body>")
            else:
                html_content += cut_line_html

        # Render HTML to Image using Playwright
        task_id = str(uuid.uuid4())
        temp_dir = os.path.join(os.getcwd(), "process", "temp", task_id)
        os.makedirs(temp_dir, exist_ok=True)
        html_file = os.path.join(temp_dir, "preview.html")
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        png_file = os.path.join(temp_dir, "preview.png")
        
        # Get dimensions from card data or use defaults
        card_config = context.get("card", {})
        width = card_config.get("width", {}).get("bleed", {}).get("px", 820)
        height = card_config.get("height", {}).get("bleed", {}).get("px", 1120)

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            context_browser = await browser.new_context(viewport={"width": width, "height": height})
            page = await context_browser.new_page()
            
            await page.goto(f"file://{html_file}")
            await page.wait_for_load_state("networkidle")
            await page.screenshot(path=png_file)
            await browser.close()

        with open(png_file, "rb") as f:
            image_data = f.read()

        # Clean up
        shutil.rmtree(temp_dir)

        return Response(content=image_data, media_type="image/png")

    except Exception as e:
        import traceback
        log.error(f"Error in preview_card: {e}\n{traceback.format_exc()}")
        return Response(content=f"Error: {str(e)}", status_code=500)
