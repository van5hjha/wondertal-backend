import os
import json
import time
import logging
import requests
import random
import re

from django.conf import settings
from config.models import SiteConfiguration
from django.core.files.base import ContentFile
from catalog.models import BookTemplate, PageTemplate
from .models import BookRequest, BookResult, BookPage, PreviewRequest, PreviewResult, ChildFace

logger = logging.getLogger(__name__)

class ComfyUIClient:
    def __init__(self, base_url=None):
        if not base_url:
            base_url = SiteConfiguration.get_solo().comfyui_url
        self.base_url = base_url.rstrip('/')

    def image_exists(self, filename, folder_type="input"):
        """Checks if an image exists on ComfyUI via HEAD or streamed GET on /view"""
        url = f"{self.base_url}/view"
        params = {"filename": filename, "type": folder_type}
        try:
            response = requests.head(url, params=params)
            if response.status_code == 405:
                # Fallback to streaming GET if HEAD is not allowed
                response = requests.get(url, params=params, stream=True)
                response.close()
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Error checking if image exists: {e}")
            return False

    def upload_image(self, file_field, overwrite=True):
        """
        Uploads an image (from a Django FileField/ImageField) to ComfyUI.
        Skips upload if the file already exists on ComfyUI with the exact same name.
        """
        filename = os.path.basename(file_field.name)
        if self.image_exists(filename, folder_type="input"):
            logger.info(f"Image {filename} already exists on ComfyUI, skipping upload.")
            return filename

        url = f"{self.base_url}/upload/image"
        
        # Read file bytes directly from storage
        file_field.open('rb')
        try:
            files = {'image': (filename, file_field.read(), 'image/png')}
            data = {'overwrite': 'true'} if overwrite else {}
            response = requests.post(url, files=files, data=data)
        finally:
            file_field.close()

        response.raise_for_status()
        return response.json()['name']

    def run_workflow(self, prompt_workflow):
        """
        Sends the API prompt to ComfyUI, polls for completion, and returns the output image bytes and filename.
        """
        # 1. Send prompt
        prompt_url = f"{self.base_url}/prompt"
        response = requests.post(prompt_url, json={"prompt": prompt_workflow})
        response.raise_for_status()
        prompt_id = response.json()["prompt_id"]
        logger.info(f"ComfyUI prompt dispatched. Prompt ID: {prompt_id}")

        # 2. Poll for completion
        history_url = f"{self.base_url}/history/{prompt_id}"
        
        # Max polling time: 10 minutes (300 iterations * 2 seconds)
        for _ in range(300):
            time.sleep(2)
            try:
                hist_resp = requests.get(history_url)
                hist_resp.raise_for_status()
                hist_data = hist_resp.json()
            except Exception as e:
                logger.warning(f"Error querying history for prompt {prompt_id}: {e}")
                continue
            
            if prompt_id in hist_data:
                # Execution complete!
                outputs = hist_data[prompt_id].get("outputs", {})
                image_info = None
                
                # Check for SaveImage output (usually node 16 in our workflow)
                if "16" in outputs and outputs["16"].get("images"):
                    image_info = outputs["16"]["images"][0]
                else:
                    # Fallback: search for any node with images output
                    for node_id, node_output in outputs.items():
                        if "images" in node_output and node_output["images"]:
                            image_info = node_output["images"][0]
                            break
                
                if image_info:
                    filename = image_info["filename"]
                    subfolder = image_info.get("subfolder", "")
                    img_type = image_info.get("type", "output")
                    
                    # Fetch the generated image bytes
                    view_url = f"{self.base_url}/view"
                    view_params = {"filename": filename, "subfolder": subfolder, "type": img_type}
                    view_resp = requests.get(view_url, params=view_params)
                    view_resp.raise_for_status()
                    
                    return view_resp.content, filename
                else:
                    raise Exception("ComfyUI generation complete but no output images were found.")
        
        raise Exception(f"ComfyUI prompt execution timed out for prompt_id: {prompt_id}")



def process_svg_subtitle(page_template, child_name, raw_image_url):
    if not page_template.svg_template:
        return None
    try:
        page_template.svg_template.open('r')
        svg_content = page_template.svg_template.read()
        if isinstance(svg_content, bytes):
            svg_content = svg_content.decode('utf-8')
    finally:
        page_template.svg_template.close()
        
    # Replace Vivaan
    child_name = child_name or "Child"
    svg_content = svg_content.replace("vivaan", child_name.lower())
    svg_content = svg_content.replace("Vivaan", child_name.capitalize())
    svg_content = svg_content.replace("VIVAAN", child_name.upper())
    
    image_tag = f'\n  <image href="{raw_image_url}" x="0" y="0" width="100%" height="100%" preserveAspectRatio="xMidYMid slice" />\n'
    
    match = re.search(r'<svg[^>]*>', svg_content, re.IGNORECASE)
    if match:
        insert_pos = match.end()
        svg_content = svg_content[:insert_pos] + image_tag + svg_content[insert_pos:]
        
    return svg_content.encode('utf-8')

def convert_ui_to_api(ui_workflow_dict):
    """
    Converts ComfyUI UI JSON format (with nodes and links lists) to API format (node_id -> inputs).
    """
    nodes = ui_workflow_dict.get("nodes", [])
    links = ui_workflow_dict.get("links", [])
    
    # Map link_id -> (origin_node_id, origin_slot_index)
    link_map = {}
    for link in links:
        if len(link) >= 3:
            link_id, origin_node_id, origin_slot_index = link[0], link[1], link[2]
            link_map[link_id] = [str(origin_node_id), origin_slot_index]

    WIDGET_MAPPING = {
        "VAELoader": ["vae_name"],
        "PulidFluxInsightFaceLoader": ["provider"],
        "PulidFluxModelLoader": ["pulid_file"],
        "PulidFluxEvaClipLoader": [],
        "UNETLoader": ["unet_name", "weight_dtype"],
        "DualCLIPLoader": ["clip_name1", "clip_name2", "type", "weight_dtype"],
        "LoraLoader": ["lora_name", "strength_model", "strength_clip"],
        "CLIPTextEncode": ["text"],
        "KSampler": ["seed", "control_after_generate", "steps", "cfg", "sampler_name", "scheduler", "denoise"],
        "ApplyPulidFlux": ["weight", "start_at", "end_at"],
        "GrowMask": ["expand", "tapered_corners"],
        "ImageCompositeMasked": ["x", "y", "resize_source"],
        "LoadImage": ["image", "upload"],
        "SaveImage": ["filename_prefix"],
        "ImageToMask": ["channel"],
        "ImageBatch": [],
        "SetLatentNoiseMask": [],
        "VAEEncode": [],
        "VAEDecode": []
    }

    api_prompt = {}
    for node in nodes:
        node_id_str = str(node["id"])
        node_type = node["type"]
        
        api_prompt[node_id_str] = {
            "class_type": node_type,
            "inputs": {}
        }
        
        # Populate widget inputs
        widget_names = WIDGET_MAPPING.get(node_type, [])
        widget_values = node.get("widgets_values", [])
        for i, name in enumerate(widget_names):
            if i < len(widget_values):
                api_prompt[node_id_str]["inputs"][name] = widget_values[i]
                
        # Populate link inputs (which override/complement widgets)
        inputs_list = node.get("inputs", [])
        for inp in inputs_list:
            inp_name = inp.get("name")
            link_id = inp.get("link")
            if link_id is not None and link_id in link_map:
                api_prompt[node_id_str]["inputs"][inp_name] = link_map[link_id]
                
    return api_prompt


def process_preview_request(preview_request, page_number=None):
    """
    Processes all pages of a PreviewRequest that are marked as is_preview=True,
    or a single page if page_number is specified.
    """
    logger.info(f"Starting PreviewRequest processing for request {preview_request.id} (page_number: {page_number})")
    preview_request.status = 'generating'
    preview_request.save()

    try:
        # Get face filenames
        faces = list(preview_request.faces.all().order_by('id'))
        if not faces:
            raise Exception("No child faces provided for this preview request.")
        
        client = ComfyUIClient()
        face_filenames = []
        for face in faces:
            logger.info(f"Uploading face {face.id} to ComfyUI...")
            face_name = client.upload_image(face.image)
            face_filenames.append(face_name)

        # Pad face filenames to have exactly 3 images for the workflow
        if len(face_filenames) == 1:
            face_filenames = [face_filenames[0]] * 3
        elif len(face_filenames) == 2:
            face_filenames = [face_filenames[0], face_filenames[0], face_filenames[1]]

        # Load the base workflow JSON
        workflow_path = os.path.join(settings.BASE_DIR, 'books', 'templates', 'inpainting_workflow.json')
        with open(workflow_path, 'r') as f:
            ui_workflow = json.load(f)

        # Process each preview page
        pages = preview_request.book_template.pages.filter(is_preview=True)
        if page_number is not None:
            pages = pages.filter(page_number=page_number)
        pages = pages.order_by('page_number')

        if not pages.exists():
            if page_number is not None:
                raise Exception(f"Page {page_number} is not a preview page or not found for BookTemplate: {preview_request.book_template.title}")
            else:
                raise Exception(f"No preview pages found for BookTemplate: {preview_request.book_template.title}")

        for page in pages:
            logger.info(f"Processing preview page {page.page_number} for BookTemplate '{preview_request.book_template.title}'")
            
            # Construct API prompt from UI workflow
            api_prompt = convert_ui_to_api(ui_workflow)
            
            # Set the reference photos
            api_prompt["5"]["inputs"]["image"] = face_filenames[0]
            api_prompt["23"]["inputs"]["image"] = face_filenames[1]
            api_prompt["26"]["inputs"]["image"] = face_filenames[2]
            
            # Upload or retrieve the scene and mask images
            scene_image_name = ""
            mask_image_name = ""
            if page.image:
                scene_image_name = client.upload_image(page.image)
            if page.mask_image:
                mask_image_name = client.upload_image(page.mask_image)
            
            # Set the scene and mask image names
            api_prompt["8"]["inputs"]["image"] = scene_image_name
            api_prompt["28"]["inputs"]["image"] = mask_image_name
            
            # Set a random seed to avoid ComfyUI caching issues
            if "13" in api_prompt and "inputs" in api_prompt["13"]:
                api_prompt["13"]["inputs"]["seed"] = random.randint(1, 1125899906842624)
            
            # Run the workflow
            logger.info(f"Dispatching workflow for page {page.page_number} to ComfyUI...")
            img_bytes, filename = client.run_workflow(api_prompt)
            
            # Store in PreviewResult
            preview_result, created = PreviewResult.objects.get_or_create(
                preview_request=preview_request,
                page_number=page.page_number,
                defaults={"page_template": page}
            )
            preview_result.page_template = page
            preview_result.raw_image.save(filename, ContentFile(img_bytes), save=True)
            
            if page.svg_template:
                child_name = preview_request.child_name or "Child"
                svg_bytes = process_svg_subtitle(page, child_name, preview_result.raw_image.url)
                if svg_bytes:
                    svg_filename = f"page_{page.page_number}_{filename.split('.')[0]}.svg"
                    preview_result.generated_svg.save(svg_filename, ContentFile(svg_bytes), save=True)
            
            logger.info(f"Page {page.page_number} processed and saved successfully.")

        preview_request.status = 'completed'
        preview_request.save()
        logger.info(f"PreviewRequest {preview_request.id} processed successfully.")

    except Exception as e:
        logger.error(f"Error processing PreviewRequest {preview_request.id}: {e}", exc_info=True)
        preview_request.status = 'failed'
        preview_request.save()
        raise e


def process_book_request(book_request):
    """
    Processes all pages of a BookRequest to generate the final personalized book.
    """
    logger.info(f"Starting BookRequest processing for request {book_request.id}")
    book_request.status = 'generating'
    book_request.save()

    try:
        # Get face filenames
        faces = list(book_request.faces.all().order_by('id'))
        if not faces:
            raise Exception("No child faces provided for this book request.")
        
        client = ComfyUIClient()
        face_filenames = []
        for face in faces:
            logger.info(f"Uploading face {face.id} to ComfyUI...")
            face_name = client.upload_image(face.image)
            face_filenames.append(face_name)

        # Pad face filenames to have exactly 3 images
        if len(face_filenames) == 1:
            face_filenames = [face_filenames[0]] * 3
        elif len(face_filenames) == 2:
            face_filenames = [face_filenames[0], face_filenames[0], face_filenames[1]]

        # Get BookTemplate
        template = book_request.book_template or BookTemplate.objects.first()
        if not template:
            raise Exception("No BookTemplate available to process BookRequest.")

        # Create/Get BookResult
        book_result, created = BookResult.objects.get_or_create(
            book_template=template,
            user=book_request.user,
            child_name=book_request.child_name,
            defaults={
                "child_age": book_request.child_age,
                "child_gender": "neutral",
            }
        )

        # Link faces to BookResult
        for face in faces:
            face.book_result = book_result
            face.save()

        # Load workflow template
        workflow_path = os.path.join(settings.BASE_DIR, 'books', 'templates', 'inpainting_workflow.json')
        with open(workflow_path, 'r') as f:
            ui_workflow = json.load(f)

        # Process each page
        pages = template.pages.all().order_by('page_number')
        for page in pages:
            logger.info(f"Processing page {page.page_number} for BookResult '{book_result.child_name}'")
            
            # Construct API prompt from UI workflow
            api_prompt = convert_ui_to_api(ui_workflow)
            
            # Set the reference photos
            api_prompt["5"]["inputs"]["image"] = face_filenames[0]
            api_prompt["23"]["inputs"]["image"] = face_filenames[1]
            api_prompt["26"]["inputs"]["image"] = face_filenames[2]
            
            # Upload or retrieve the scene and mask images
            scene_image_name = ""
            mask_image_name = ""
            if page.image:
                scene_image_name = client.upload_image(page.image)
            if page.mask_image:
                mask_image_name = client.upload_image(page.mask_image)
            
            # Set the scene and mask image names
            api_prompt["8"]["inputs"]["image"] = scene_image_name
            api_prompt["28"]["inputs"]["image"] = mask_image_name
            
            # Set a random seed to avoid ComfyUI caching issues
            if "13" in api_prompt and "inputs" in api_prompt["13"]:
                api_prompt["13"]["inputs"]["seed"] = random.randint(1, 1125899906842624)
            
            # Run the workflow
            logger.info(f"Dispatching workflow for page {page.page_number} to ComfyUI...")
            img_bytes, filename = client.run_workflow(api_prompt)
            
            # Store in BookPage
            book_page, created = BookPage.objects.get_or_create(
                book_result=book_result,
                page_number=page.page_number,
                defaults={"page_template": page, "is_preview": page.is_preview}
            )
            book_page.page_template = page
            book_page.is_preview = page.is_preview
            book_page.raw_image.save(filename, ContentFile(img_bytes), save=True)
            
            if page.svg_template:
                child_name = book_result.child_name or "Child"
                svg_bytes = process_svg_subtitle(page, child_name, book_page.raw_image.url)
                if svg_bytes:
                    svg_filename = f"page_{page.page_number}_{filename.split('.')[0]}.svg"
                    book_page.generated_svg.save(svg_filename, ContentFile(svg_bytes), save=True)
            
            logger.info(f"Page {page.page_number} processed and saved successfully.")

        book_request.status = 'created'
        book_request.save()
        logger.info(f"BookRequest {book_request.id} processed successfully. BookResult {book_result.id} created.")

    except Exception as e:
        logger.error(f"Error processing BookRequest {book_request.id}: {e}", exc_info=True)
        book_request.status = 'failed'
        book_request.save()
        raise e
