import asyncio
from jinja2 import Template
import os
import pandas as pd
from playwright.async_api import async_playwright
from PIL import Image
import shutil
from util import git_util
import uuid

from process.process_adapter import ProcessAdapter
from util import dict_util, html_util

class AnorProcessAdapter(ProcessAdapter):

    def __init__(self) -> None:
        pass

    def get_display_name(self) -> str:
        return f"Anor"

    async def process(self, data: pd.DataFrame, configuration: dict) -> str:
        """
        Processes the given data and returns the path to the process directory.
        """
        print(f"Writing to Anor: {data}")

        process_dir: str = configuration["meta"]["process_path"]
        print(f"Process directory: {process_dir}")

        os.makedirs(os.path.join(process_dir, "csv"), exist_ok=True)
        data.to_csv(os.path.join(process_dir, "csv", "data.csv"), index=False)

        # Clone or pull the repository
        repositories_path = os.path.join(os.getcwd(), "repositories")
        os.makedirs(repositories_path, exist_ok=True)
        repo_url = os.environ.get("ANOR_REPOSITORY_URL")
        if not repo_url:
            raise ValueError("ANOR_REPOSITORY_URL environment variable is not set")
        repo_path: str | None = git_util.clone_or_pull_repository(repo_url, repositories_path)

        # Prepare data
        datas: list[dict] = self.prepare_datas(data, configuration, repositories_path)

        # Render templates
        self.render_templates(process_dir, datas)

        # Render images
        await self.render_images(process_dir, configuration)

        # Push the repository
        # This will copy the PNG files AND convert them to JPG files for the TCG Arena.
        if repo_path and configuration.get("meta", {}).get("commit_to_repo"):
            png_source_dir: str = os.path.join(process_dir, "png")
            if os.path.exists(png_source_dir):
                png_dest_dir: str = os.path.join(repo_path, "export", "png")
                jpg_dest_dir: str = os.path.join(repo_path, "export", "jpg")
                os.makedirs(png_dest_dir, exist_ok=True)
                os.makedirs(jpg_dest_dir, exist_ok=True)
                for file_name in os.listdir(png_source_dir):
                    if file_name.endswith(".png"):
                        png_source_path: str = os.path.join(png_source_dir, file_name)
                        png_dest_path: str = os.path.join(png_dest_dir, file_name)
                        shutil.copy2(png_source_path, png_dest_path)

                        # remove ".png" at the end
                        jpg_file_name: str = file_name.removesuffix(".png") + ".jpg"
                        jpg_dest_path: str = os.path.join(jpg_dest_dir, jpg_file_name)
                        with Image.open(png_source_path) as img:
                            rgb_img = img.convert("RGB")
                            rgb_img.save(jpg_dest_path, quality=100)

            git_util.commit_and_push_repository(repo_url, repo_path)

        return process_dir

    def prepare_datas(self, data: pd.DataFrame, configuration: dict, repositories_path: str) -> list[dict]:
        datas: list[dict] = []

        def get_or_none(row: pd.Series, column: str) -> str | None:
            if pd.isna(row[column]):
                return None
            return row[column]

        for index, row in data.iterrows():
            # CSV: Kosten Aqua,Charakter Pipeline,Element,Kartenart,⭕️,Kartentext,Kartentyp,Design Skelett,Kosten Ignis,ID,Erstellungsdatum,⚔️,Flavourtext,Erstellt von,Kosten Ungeprägt,Idee Brackground,🛡️,Slot zugewiesen,Status,Kosten Aeris,Einzigartig,Set Release,Kartentext-Planung,Kosten Terra,Kosten Magica,Letzte Änderung,Rarität,Name,PageID,Row_Hash

            try:
                # Prepare data
                data: dict = dict_util.combine(
                    configuration,
                    {
                        "entity": {
                            "id": get_or_none(row, "ID"),
                            "layout": get_or_none(row, "kind"),
                            "kind": get_or_none(row, "kind"),
                            "type": get_or_none(row, "type"),
                            "title": {
                                "primary": get_or_none(row, "title_primary"),
                                "secondary": get_or_none(row, "title_secondary"),
                            },
                            "description": html_util.clean_html_text(get_or_none(row, "description")),
                            "artwork": {
                                "path": f"{repositories_path}/anor/artworks/{get_or_none(row, "ID")}.png",
                            },
                            "flavour": get_or_none(row, "flavour"),
                            "cost": {
                                "terra": get_or_none(row, "cost_terra"),
                                "aqua": get_or_none(row, "cost_aqua"),
                                "aeris": get_or_none(row, "cost_aeris"),
                                "ignis": get_or_none(row, "cost_ignis"),
                                "magica": get_or_none(row, "cost_magica"),
                                "unshaped": get_or_none(row, "cost_unshaped"),
                            },
                            "elemental": {
                                "element": get_or_none(row, "elemental_element"),
                                "amount": get_or_none(row, "elemental_amount"),
                            },
                            "stats": {
                                "offensive": {
                                    "strength": get_or_none(row, "stats_offensive_strength"),
                                    "toughness": get_or_none(row, "stats_offensive_toughness"),
                                },
                                "defensive": {
                                    "strength": get_or_none(row, "stats_defensive_strength"),
                                    "toughness": get_or_none(row, "stats_defensive_toughness") ,
                                },
                                "barriers": get_or_none(row, "stats_barriers"),
                            },
                            "rarity": get_or_none(row, "rarity"),
                        },
                    },
                )

                data["meta"] = {
                    "style": {
                        "path": f"{repositories_path}/anor/templates/style.jinja",
                    },
                    "template": {
                        "path": f"{repositories_path}/anor/templates/{data['entity']['layout']}.jinja",
                    },
                    "artworks": {
                        "path": f"{repositories_path}/anor/artworks/",
                    },
                    "fonts": {
                        "path": f"{repositories_path}/anor/fonts/",
                    },
                    "layout": {
                        "path": f"{repositories_path}/anor/layout/",
                    },
                    "templates": {
                        "path": f"{repositories_path}/anor/templates/",
                    },
                }
                datas.append(data)
            except Exception as e:
                print(f"Error preparing data: {e}")
                print(f"Row: {row}")
                raise e

        return datas

    def render_templates(self, process_dir: str, datas: list[dict]) -> None:
        for data in datas:
            # Render CSS
            style: str = self.render_template(
                data["meta"]["style"]["path"],
                os.path.join(process_dir, "html", "style.css"),
                data,
            )

            try:
                # Render HTML
                self.render_template(
                    data["meta"]["template"]["path"],
                    os.path.join(process_dir, "html", f"{data['entity']['id']}.html"),
                    dict_util.combine(
                        data,
                        {
                            "meta": {
                                "style": style,
                            },
                        },
                    ),
                )
            except ValueError as e:
                print(f"Error rendering template for ID {data['entity']['id']}: {e}")
                continue

    def render_template(self, template_path: str, output_path: str | None, data: dict) -> str:
        """
        Renderes a Jinja2 template to HTML and saves it to the process directory.
        """
        print(f"Rendering template from {template_path} to {output_path}...")

        template_content: str
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                template_content = f.read()
        except FileNotFoundError:
            raise ValueError(f"Template not found at {template_path}")

        template = Template(template_content)

        html = template.render(**data)

        if output_path is not None:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html)

        return html

    async def render_images(self, process_dir: str, configuration: dict) -> None:
        print(f"Rendering images: {process_dir}")
        
        # 1. Setup Paths
        html_input_path = os.path.join(process_dir, "html")
        image_output_path = os.path.join(process_dir, "png")
        
        # Ensure output directory exists
        os.makedirs(image_output_path, exist_ok=True)

        # 2. Extract Dimensions from Configuration
        # We use the "bleed" dimensions in pixels as per your previous logic
        width_px = configuration["card"]["width"]["bleed"]["px"]
        height_px = configuration["card"]["height"]["bleed"]["px"]

        # 3. Identify Files
        # Get all HTML files in the directory
        try:
            html_files = [f for f in os.listdir(html_input_path) if f.endswith(".html")]
        except FileNotFoundError:
            print(f"Error: HTML directory not found at {html_input_path}")
            return

        # 4. Playwright Execution
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            
            # Create a context with the correct viewport preset
            # This saves setting it on every single page
            context = await browser.new_context(
                viewport={'width': width_px, 'height': height_px}
            )

            # Semaphore limits concurrent tabs to avoid memory crashes
            # 10 is usually a safe number for Playwright
            semaphore = asyncio.Semaphore(10)

            async def render_card(filename: str):
                async with semaphore:
                    page = await context.new_page()
                    name = os.path.splitext(filename)[0]
                    
                    try:
                        file_url = f"file://{os.path.join(os.path.abspath(html_input_path), filename)}"
                        print(f"Rendering: {name}...")
                        
                        await page.goto(file_url)
                        await page.wait_for_load_state("networkidle")
                        
                        output_file = os.path.join(image_output_path, f"{name}.png")
                        await page.screenshot(path=output_file)
                        
                    except Exception as e:
                        print(f"Error rendering card {name}: {e}")
                    finally:
                        await page.close()

            # Create tasks for all files and run them concurrently
            tasks = [render_card(f) for f in html_files]
            await asyncio.gather(*tasks)

            await browser.close()
            
        print("Done rendering cards.")
