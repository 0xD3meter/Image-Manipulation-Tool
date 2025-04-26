#!/usr/bin/env python3

import argparse
import os
import sys
from datetime import datetime
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ExifTags

# Supported image formats
SUPPORTED_FORMATS = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"]

def is_valid_image(file_path):
    """Check if file exists and is a supported image format"""
    if not os.path.isfile(file_path):
        return False
    
    ext = os.path.splitext(file_path)[1].lower()
    return ext in SUPPORTED_FORMATS

def create_output_path(input_path, output_path=None, suffix=None, format=None):
    """Create an output path for the processed image"""
    if output_path and os.path.isdir(output_path):
        # If output_path is a directory, use the original filename
        base_name = os.path.basename(input_path)
        file_name, ext = os.path.splitext(base_name)
        if format:
            ext = f".{format.lower()}"
        if suffix:
            file_name = f"{file_name}_{suffix}"
        return os.path.join(output_path, f"{file_name}{ext}")
    
    if output_path:
        # If output_path is a specific file path
        if format:
            # Override the extension if format is specified
            output_path = os.path.splitext(output_path)[0] + f".{format.lower()}"
        return output_path
    
    # If no output_path is provided, create one from the input_path
    file_name, ext = os.path.splitext(input_path)
    if format:
        ext = f".{format.lower()}"
    if suffix:
        file_name = f"{file_name}_{suffix}"
    return f"{file_name}{ext}"

def resize_image(image, width=None, height=None, scale=None, maintain_aspect=True):
    """Resize an image based on width, height, or scale factor"""
    original_width, original_height = image.size
    
    if scale:
        width = int(original_width * scale)
        height = int(original_height * scale)
    elif width and height:
        if maintain_aspect:
            # Calculate which dimension to adjust based on aspect ratio
            aspect = original_width / original_height
            if width / height > aspect:
                width = int(height * aspect)
            else:
                height = int(width / aspect)
    elif width:
        if maintain_aspect:
            height = int(width * original_height / original_width)
    elif height:
        if maintain_aspect:
            width = int(height * original_width / original_height)
    else:
        # No resize parameters specified
        return image
    
    return image.resize((width, height), Image.LANCZOS)

def crop_image(image, left, top, right, bottom):
    """Crop an image to the specified coordinates"""
    width, height = image.size
    
    # Convert percentages to pixel values if needed
    if 0 <= left <= 1:
        left = int(width * left)
    if 0 <= top <= 1:
        top = int(height * top)
    if 0 <= right <= 1:
        right = int(width * right)
    if 0 <= bottom <= 1:
        bottom = int(height * bottom)
    
    # Ensure coordinates are valid
    left = max(0, min(left, width - 1))
    top = max(0, min(top, height - 1))
    right = max(left + 1, min(right, width))
    bottom = max(top + 1, min(bottom, height))
    
    return image.crop((left, top, right, bottom))

def rotate_image(image, angle, expand=True):
    """Rotate an image by the specified angle in degrees"""
    return image.rotate(angle, expand=expand, resample=Image.BICUBIC)

def apply_filter(image, filter_name):
    """Apply a filter to an image"""
    filters = {
        "blur": ImageFilter.BLUR,
        "contour": ImageFilter.CONTOUR,
        "detail": ImageFilter.DETAIL,
        "edge_enhance": ImageFilter.EDGE_ENHANCE,
        "edge_enhance_more": ImageFilter.EDGE_ENHANCE_MORE,
        "emboss": ImageFilter.EMBOSS,
        "find_edges": ImageFilter.FIND_EDGES,
        "sharpen": ImageFilter.SHARPEN,
        "smooth": ImageFilter.SMOOTH,
        "smooth_more": ImageFilter.SMOOTH_MORE,
        "gaussian_blur": ImageFilter.GaussianBlur(2),
        "box_blur": ImageFilter.BoxBlur(2),
        "grayscale": "grayscale",
        "sepia": "sepia",
        "invert": "invert",
        "mirror": "mirror",
        "flip": "flip",
        "auto_contrast": "auto_contrast"
    }
    
    if filter_name not in filters:
        print(f"Unknown filter: {filter_name}")
        return image
    
    filter_effect = filters[filter_name]
    
    if filter_effect == "grayscale":
        return ImageOps.grayscale(image)
    elif filter_effect == "sepia":
        # Apply sepia effect
        return apply_sepia(image)
    elif filter_effect == "invert":
        # Only invert RGB channels for color images
        if image.mode == "RGB" or image.mode == "RGBA":
            r, g, b = image.split()[:3]
            rgb_image = Image.merge("RGB", (r, g, b))
            inverted = ImageOps.invert(rgb_image)
            
            # If original had alpha channel, restore it
            if image.mode == "RGBA":
                r, g, b = inverted.split()
                a = image.split()[3]
                return Image.merge("RGBA", (r, g, b, a))
            return inverted
        return ImageOps.invert(image)
    elif filter_effect == "mirror":
        return ImageOps.mirror(image)
    elif filter_effect == "flip":
        return ImageOps.flip(image)
    elif filter_effect == "auto_contrast":
        return ImageOps.autocontrast(image)
    else:
        return image.filter(filter_effect)

def apply_sepia(image):
    """Apply a sepia tone effect to an image"""
    if image.mode != "RGB" and image.mode != "RGBA":
        image = image.convert("RGB")
    
    # Split image into channels
    if image.mode == "RGBA":
        r, g, b, a = image.split()
    else:
        r, g, b = image.split()
    
    # Apply sepia matrix
    result_r = r.point(lambda i: min(255, int(i * 0.393 + g.point(lambda j: j * 0.769) + b.point(lambda k: k * 0.189))))
    result_g = r.point(lambda i: min(255, int(i * 0.349 + g.point(lambda j: j * 0.686) + b.point(lambda k: k * 0.168))))
    result_b = r.point(lambda i: min(255, int(i * 0.272 + g.point(lambda j: j * 0.534) + b.point(lambda k: k * 0.131))))
    
    # Merge channels
    if image.mode == "RGBA":
        return Image.merge("RGBA", (result_r, result_g, result_b, a))
    else:
        return Image.merge("RGB", (result_r, result_g, result_b))

def adjust_image(image, brightness=None, contrast=None, sharpness=None, color=None):
    """Adjust various aspects of an image"""
    if brightness is not None:
        image = ImageEnhance.Brightness(image).enhance(brightness)
    
    if contrast is not None:
        image = ImageEnhance.Contrast(image).enhance(contrast)
    
    if sharpness is not None:
        image = ImageEnhance.Sharpness(image).enhance(sharpness)
    
    if color is not None:
        image = ImageEnhance.Color(image).enhance(color)
    
    return image

def add_border(image, width, color):
    """Add a border to an image"""
    if image.mode == "P":
        image = image.convert("RGB")
    
    # Parse color
    if isinstance(color, str):
        if color.startswith("#"):
            if len(color) == 7:  # RGB
                r = int(color[1:3], 16)
                g = int(color[3:5], 16)
                b = int(color[5:7], 16)
                color = (r, g, b)
            elif len(color) == 9:  # RGBA
                r = int(color[1:3], 16)
                g = int(color[3:5], 16)
                b = int(color[5:7], 16)
                a = int(color[7:9], 16)
                color = (r, g, b, a)
        else:
            # Named colors (limited set)
            color_map = {
                "black": (0, 0, 0),
                "white": (255, 255, 255),
                "red": (255, 0, 0),
                "green": (0, 255, 0),
                "blue": (0, 0, 255),
                "yellow": (255, 255, 0),
                "cyan": (0, 255, 255),
                "magenta": (255, 0, 255),
                "gray": (128, 128, 128)
            }
            if color.lower() in color_map:
                color = color_map[color.lower()]
            else:
                print(f"Unknown color: {color}, using black")
                color = (0, 0, 0)
    
    return ImageOps.expand(image, border=width, fill=color)

def watermark_image(image, text, position="bottom-right", opacity=0.5, size=None, color="white"):
    """Add a text watermark to an image"""
    from PIL import ImageDraw, ImageFont
    
    # Create a transparent layer for the watermark
    watermark = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark)
    
    # Parse color
    if isinstance(color, str):
        if color.startswith("#"):
            if len(color) == 7:  # RGB
                r = int(color[1:3], 16)
                g = int(color[3:5], 16)
                b = int(color[5:7], 16)
                color = (r, g, b, int(255 * opacity))
            elif len(color) == 9:  # RGBA
                r = int(color[1:3], 16)
                g = int(color[3:5], 16)
                b = int(color[5:7], 16)
                a = int(color[7:9], 16)
                color = (r, g, b, int(a * opacity))
        else:
            # Named colors (limited set)
            color_map = {
                "black": (0, 0, 0),
                "white": (255, 255, 255),
                "red": (255, 0, 0),
                "green": (0, 255, 0),
                "blue": (0, 0, 255),
                "yellow": (255, 255, 0),
                "cyan": (0, 255, 255),
                "magenta": (255, 0, 255),
                "gray": (128, 128, 128)
            }
            if color.lower() in color_map:
                r, g, b = color_map[color.lower()]
                color = (r, g, b, int(255 * opacity))
            else:
                print(f"Unknown color: {color}, using white")
                color = (255, 255, 255, int(255 * opacity))
    
    # Try to determine font size
    if size is None:
        size = max(10, min(50, image.width // 20))
    
    # Try to use a default font
    try:
        font = ImageFont.truetype("arial.ttf", size)
    except IOError:
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", size)
        except IOError:
            font = ImageFont.load_default()
    
    # Calculate text size
    text_width, text_height = draw.textsize(text, font=font)
    
    # Determine position
    padding = 20
    if position == "top-left":
        position = (padding, padding)
    elif position == "top-right":
        position = (image.width - text_width - padding, padding)
    elif position == "bottom-left":
        position = (padding, image.height - text_height - padding)
    elif position == "bottom-right":
        position = (image.width - text_width - padding, image.height - text_height - padding)
    elif position == "center":
        position = ((image.width - text_width) // 2, (image.height - text_height) // 2)
    else:
        # Default to bottom-right
        position = (image.width - text_width - padding, image.height - text_height - padding)
    
    # Draw the watermark text
    draw.text(position, text, font=font, fill=color)
    
    # Combine the watermark with the original image
    if image.mode != "RGBA":
        image = image.convert("RGBA")
    
    return Image.alpha_composite(image, watermark)

def get_image_info(image_path):
    """Get information about an image"""
    try:
        with Image.open(image_path) as img:
            info = {
                "filename": os.path.basename(image_path),
                "format": img.format,
                "mode": img.mode,
                "width": img.width,
                "height": img.height,
                "size": f"{img.width} x {img.height}",
                "file_size": f"{os.path.getsize(image_path) / 1024:.2f} KB"
            }
            
            # Try to extract EXIF data if available
            try:
                exif_data = {}
                if hasattr(img, '_getexif') and img._getexif():
                    exif = {
                        ExifTags.TAGS[k]: v
                        for k, v in img._getexif().items()
                        if k in ExifTags.TAGS
                    }
                    
                    # Extract common EXIF tags
                    common_tags = ["Make", "Model", "DateTime", "ExposureTime", "FNumber", 
                                  "ISOSpeedRatings", "FocalLength", "Flash"]
                    
                    for tag in common_tags:
                        if tag in exif:
                            value = exif[tag]
                            # Format some values for better readability
                            if tag == "ExposureTime" and value:
                                if isinstance(value, tuple):
                                    if value[1] != 0:
                                        value = f"1/{value[1]/value[0]:.0f}"
                                    else:
                                        value = str(value)
                            elif tag == "FNumber" and value:
                                if isinstance(value, tuple):
                                    if value[1] != 0:
                                        value = f"f/{value[0]/value[1]:.1f}"
                                    else:
                                        value = str(value)
                            elif tag == "FocalLength" and value:
                                if isinstance(value, tuple):
                                    if value[1] != 0:
                                        value = f"{value[0]/value[1]:.1f} mm"
                                    else:
                                        value = str(value)
                            
                            exif_data[tag] = value
                    
                    if exif_data:
                        info["exif"] = exif_data
            except Exception as e:
                pass
            
            return info
    except Exception as e:
        print(f"Error getting image info: {e}")
        return None

def print_image_info(info):
    """Print image information in a formatted way"""
    if not info:
        print("No image information available")
        return
    
    print("\n" + "="*40)
    print(f"Image: {info['filename']}")
    print("="*40)
    print(f"Format: {info['format']}")
    print(f"Mode: {info['mode']}")
    print(f"Size: {info['size']} pixels")
    print(f"File size: {info['file_size']}")
    
    if "exif" in info:
        print("\nEXIF Data:")
        for key, value in info["exif"].items():
            print(f"  {key}: {value}")
    
    print("="*40 + "\n")

def process_image(input_path, output_path=None, resize=None, crop=None, rotate=None, 
                 filter=None, brightness=None, contrast=None, sharpness=None, color=None,
                 format=None, quality=None, border=None, border_color=None,
                 watermark=None, watermark_position=None, watermark_opacity=None,
                 watermark_size=None, watermark_color=None, info=False):
    """Process an image with the specified operations"""
    # Validate input file
    if not is_valid_image(input_path):
        print(f"Error: {input_path} is not a valid image file")
        return False
    
    try:
        # Open the image
        with Image.open(input_path) as img:
            # Convert to RGB or RGBA if needed
            if img.mode == "P":
                if img.format == "PNG" and "transparency" in img.info:
                    img = img.convert("RGBA")
                else:
                    img = img.convert("RGB")
            
            # Apply operations in a sensible order
            
            # 1. Rotate (often needed before other transformations)
            if rotate is not None:
                img = rotate_image(img, rotate)
            
            # 2. Crop
            if crop is not None:
                try:
                    left, top, right, bottom = map(float, crop.split(","))
                    img = crop_image(img, left, top, right, bottom)
                except Exception as e:
                    print(f"Error applying crop: {e}")
                    print("Crop format should be: left,top,right,bottom")
            
            # 3. Resize
            if resize is not None:
                try:
                    # Check if resize is a scale factor
                    if "x" not in resize and resize.replace(".", "").isdigit():
                        scale = float(resize)
                        img = resize_image(img, scale=scale)
                    else:
                        # Check if resize has both width and height
                        if "x" in resize:
                            width, height = map(int, resize.split("x"))
                            img = resize_image(img, width=width, height=height)
                        else:
                            # Resize by width, maintain aspect ratio
                            width = int(resize)
                            img = resize_image(img, width=width)
                except Exception as e:
                    print(f"Error applying resize: {e}")
                    print("Resize format should be: WIDTHxHEIGHT, WIDTH, or SCALE")
            
            # 4. Filters and adjustments
            if filter is not None:
                img = apply_filter(img, filter)
            
            if any(x is not None for x in [brightness, contrast, sharpness, color]):
                img = adjust_image(img, 
                                  brightness=float(brightness) if brightness is not None else None,
                                  contrast=float(contrast) if contrast is not None else None,
                                  sharpness=float(sharpness) if sharpness is not None else None,
                                  color=float(color) if color is not None else None)
            
            # 5. Border
            if border is not None:
                border_width = int(border)
                border_color = border_color or "black"
                img = add_border(img, border_width, border_color)
            
            # 6. Watermark (apply last as it should be on top)
            if watermark is not None:
                watermark_position = watermark_position or "bottom-right"
                watermark_opacity = float(watermark_opacity) if watermark_opacity is not None else 0.5
                watermark_size = int(watermark_size) if watermark_size is not None else None
                watermark_color = watermark_color or "white"
                img = watermark_image(img, watermark, watermark_position, watermark_opacity, 
                                     watermark_size, watermark_color)
            
            # Create output path
            if output_path is None:
                suffix = filter if filter else "edited"
                output_path = create_output_path(input_path, suffix=suffix, format=format)
            else:
                output_path = create_output_path(input_path, output_path=output_path, format=format)
            
            # Ensure the output directory exists
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Save the image
            save_options = {}
            if quality is not None:
                save_options["quality"] = int(quality)
            
            if format:
                format = format.upper()
                img.save(output_path, format=format, **save_options)
            else:
                img.save(output_path, **save_options)
            
            print(f"Image saved to {output_path}")
            
            # Display image info if requested
            if info:
                img_info = get_image_info(output_path)
                print_image_info(img_info)
            
            return True
    
    except Exception as e:
        print(f"Error processing image {input_path}: {e}")
        return False

def batch_process(input_dir, output_dir=None, recursive=False, **kwargs):
    """Process all images in a directory"""
    # Ensure input directory exists
    if not os.path.isdir(input_dir):
        print(f"Error: {input_dir} is not a valid directory")
        return False
    
    # Create output directory if needed
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except Exception as e:
            print(f"Error creating output directory {output_dir}: {e}")
            return False
    
    # Find all image files
    image_files = []
    if recursive:
        for root, _, files in os.walk(input_dir):
            for file in files:
                file_path = os.path.join(root, file)
                if is_valid_image(file_path):
                    image_files.append(file_path)
    else:
        for file in os.listdir(input_dir):
            file_path = os.path.join(input_dir, file)
            if is_valid_image(file_path):
                image_files.append(file_path)
    
    if not image_files:
        print(f"No valid image files found in {input_dir}")
        return False
    
    # Process each image
    success_count = 0
    for file_path in image_files:
        # Create relative path for output directory
        if output_dir:
            rel_path = os.path.relpath(file_path, input_dir)
            rel_dir = os.path.dirname(rel_path)
            rel_output_dir = os.path.join(output_dir, rel_dir) if rel_dir else output_dir
            
            if not os.path.exists(rel_output_dir) and rel_dir:
                os.makedirs(rel_output_dir)
        else:
            rel_output_dir = None
        
        print(f"Processing {file_path}...")
        if process_image(file_path, rel_output_dir, **kwargs):
            success_count += 1
    
    print(f"Processed {success_count} of {len(image_files)} images successfully")
    return True

def main():
    parser = argparse.ArgumentParser(description="Image manipulation tool for various operations")
    
    # Input/output arguments
    parser.add_argument("input", help="Input image file or directory")
    parser.add_argument("-o", "--output", help="Output file or directory")
    
    # Batch processing
    parser.add_argument("--batch", action="store_true", help="Process all images in input directory")
    parser.add_argument("-r", "--recursive", action="store_true", help="Recursively process subdirectories")
    
    # Basic transformations
    parser.add_argument("--resize", help="Resize image (WIDTHxHEIGHT, WIDTH, or scale factor)")
    parser.add_argument("--crop", help="Crop image (left,top,right,bottom)")
    parser.add_argument("--rotate", type=float, help="Rotate image by degrees")
    
    # Filters and adjustments
    parser.add_argument("--filter", choices=[
        "blur", "contour", "detail", "edge_enhance", "edge_enhance_more", "emboss", 
        "find_edges", "sharpen", "smooth", "smooth_more", "gaussian_blur", "box_blur", 
        "grayscale", "sepia", "invert", "mirror", "flip", "auto_contrast"
    ], help="Apply a filter to the image")
    
    parser.add_argument("--brightness", type=float, help="Adjust brightness (0.0-2.0)")
    parser.add_argument("--contrast", type=float, help="Adjust contrast (0.0-2.0)")
    parser.add_argument("--sharpness", type=float, help="Adjust sharpness (0.0-2.0)")
    parser.add_argument("--color", type=float, help="Adjust color saturation (0.0-2.0)")
    
    # Output options
    parser.add_argument("--format", choices=["jpg", "jpeg", "png", "gif", "bmp", "tiff", "webp"], 
                       help="Output format")
    parser.add_argument("--quality", type=int, choices=range(1, 101), 
                       help="Output quality for JPG/JPEG/WebP (1-100)")
    
    # Decorations
    parser.add_argument("--border", type=int, help="Add border with specified width")
    parser.add_argument("--border-color", help="Border color (name or #RRGGBB)")
    
    parser.add_argument("--watermark", help="Add text watermark")
    parser.add_argument("--watermark-position", 
                       choices=["top-left", "top-right", "bottom-left", "bottom-right", "center"], 
                       help="Watermark position")
    parser.add_argument("--watermark-opacity", type=float, help="Watermark opacity (0.0-1.0)")
    parser.add_argument("--watermark-size", type=int, help="Watermark font size")
    parser.add_argument("--watermark-color", help="Watermark color (name or #RRGGBB)")
    
    # Information
    parser.add_argument("--info", action="store_true", help="Display image information")
    
    args = parser.parse_args()
    
    # Get image info only
    if args.info and not any(getattr(args, attr) for attr in [
        "resize", "crop", "rotate", "filter", "brightness", "contrast", 
        "sharpness", "color", "format", "quality", "border", "watermark"
    ]):
        if not args.batch:
            img_info = get_image_info(args.input)
            print_image_info(img_info)
            return
    
    # Process a single image or a batch
    if args.batch or os.path.isdir(args.input):
        batch_process(
            args.input, args.output, args.recursive,
            resize=args.resize, crop=args.crop, rotate=args.rotate,
            filter=args.filter, brightness=args.brightness, contrast=args.contrast,
            sharpness=args.sharpness, color=args.color, format=args.format,
            quality=args.quality, border=args.border, border_color=args.border_color,
            watermark=args.watermark, watermark_position=args.watermark_position,
            watermark_opacity=args.watermark_opacity, watermark_size=args.watermark_size,
            watermark_color=args.watermark_color, info=args.info
        )
    else:
        process_image(
            args.input, args.output,
            resize=args.resize, crop=args.crop, rotate=args.rotate,
            filter=args.filter, brightness=args.brightness, contrast=args.contrast,
            sharpness=args.sharpness, color=args.color, format=args.format,
            quality=args.quality, border=args.border, border_color=args.border_color,
            watermark=args.watermark, watermark_position=args.watermark_position,
            watermark_opacity=args.watermark_opacity, watermark_size=args.watermark_size,
            watermark_color=args.watermark_color, info=args.info
        )

if __name__ == "__main__":
    main()
