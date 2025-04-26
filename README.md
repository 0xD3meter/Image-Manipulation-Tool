# 🖼️ Image Manipulation Tool

A versatile command-line tool for image processing and manipulation with support for various operations, filters, and batch processing.

## ✨ Features

- 🔄 Resize images while maintaining aspect ratio
- ✂️ Crop images to specific dimensions
- 🔄 Rotate images with angle control
- 🎨 Apply various filters and effects
- ⚙️ Adjust brightness, contrast, sharpness, and color
- 🔍 Convert between image formats
- 💾 Control output quality
- 📏 Add custom borders
- ©️ Add text watermarks with position control
- 📊 Display image information and EXIF data
- 📁 Process multiple images in batch mode

## 📋 Requirements

- Python 3.6 or higher
- Pillow library (PIL fork)

## 🚀 Installation

1. Clone this repository:
```bash
git clone https://github.com/0xD3meter/image-manipulation-tool.git
cd image-manipulation-tool
```

2. Install requirements:
```bash
pip install -r requirements.txt
```

3. Make the script executable (Unix/Linux/macOS):
```bash
chmod +x main.py
```

## 🔍 Usage

```bash
python main.py <input_image_or_directory> [options]
```

## ⚙️ Options

### Input/Output Options:
- `input`: Input image file or directory (required)
- `-o, --output`: Output file or directory
- `--batch`: Process all images in input directory
- `-r, --recursive`: Recursively process subdirectories

### Transformation Options:
- `--resize`: Resize image (WIDTHxHEIGHT, WIDTH, or scale factor)
- `--crop`: Crop image (left,top,right,bottom)
- `--rotate`: Rotate image by degrees

### Filter and Adjustment Options:
- `--filter`: Apply a filter (blur, sharpen, grayscale, sepia, etc.)
- `--brightness`: Adjust brightness (0.0-2.0)
- `--contrast`: Adjust contrast (0.0-2.0)
- `--sharpness`: Adjust sharpness (0.0-2.0)
- `--color`: Adjust color saturation (0.0-2.0)

### Output Format Options:
- `--format`: Output format (jpg, png, webp, etc.)
- `--quality`: Output quality for JPG/JPEG/WebP (1-100)

### Decoration Options:
- `--border`: Add border with specified width
- `--border-color`: Border color (name or #RRGGBB)
- `--watermark`: Add text watermark
- `--watermark-position`: Watermark position
- `--watermark-opacity`: Watermark opacity (0.0-1.0)
- `--watermark-size`: Watermark font size
- `--watermark-color`: Watermark color (name or #RRGGBB)

### Information Options:
- `--info`: Display image information

## 📝 Examples

### Basic Operations:

#### Resize an image:
  ```bash
  python main.py image.jpg --resize 800x600
  ```
#### Resize to specific width (keep aspect ratio):
  ```bash
  python main.py image.jpg --resize 800
  ```

#### Resize to 50% of original size:
  ```bash
  python main.py image.jpg --resize 0.5
  ```
#### Crop an image:
  ```bash
  python main.py image.jpg --crop 100,50,700,550
  ```
  
#### Rotate an image:
  ```bash
  python main.py image.jpg --rotate 90
  ```
  
### Filters and Adjustments:

#### Apply a filter:
  ```bash
  python main.py image.jpg --filter grayscale
  ```
  
#### Adjust brightness and contrast:
  ```bash
  python main.py image.jpg --brightness 1.2 --contrast 1.1
  ```
  
#### Convert to another format:
  ```bash
  python main.py image.jpg --format png
  ```

