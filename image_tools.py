# image_tools.py

from PIL import Image, ExifTags
import piexif
import os

resize_templates = {
    "Passport": (400, 600),
    "Instagram Post": (1080, 1080),
    "Instagram Reel": (1080, 1920),
    "Facebook Cover": (820, 312),
    "Twitter Post": (1024, 512),
    "YouTube Thumbnail": (1280, 720),
    "A4 Document (300 DPI)": (2480, 3508),
}

def get_exif_info(img):
    try:
        exif_data = img._getexif()
        if not exif_data:
            return None
        exif = {}
        for tag_id, value in exif_data.items():
            tag = ExifTags.TAGS.get(tag_id, tag_id)
            exif[tag] = value
        return exif
    except Exception:
        return None

def print_image_info(img, path):
    print("\n" + "="*40)
    print(f"Image loaded: {path}")
    print(f"Format: {img.format}")
    print(f"Size (WxH): {img.size[0]} x {img.size[1]}")
    print(f"Mode: {img.mode}")
    
    exif = get_exif_info(img)
    if exif:
        print("\nEXIF metadata summary:")
        for key in ['Make', 'Model', 'DateTime', 'Orientation', 'Software', 'GPSInfo']:
            if key in exif:
                print(f"  {key}: {exif[key]}")
    else:
        print("\nNo EXIF metadata found.")
    print("="*40 + "\n")

def load_image(path):
    try:
        img = Image.open(path)
        print_image_info(img, path)
        return img
    except Exception as e:
        print(f"Error loading image: {e}")
        return None

def resize_image(img, width, height):
    return img.resize((width, height), Image.LANCZOS)

def convert_format(img, output_path, output_format):
    save_kwargs = {}
    if output_format.upper() == 'JPEG':
        save_kwargs['quality'] = 95
        if img.mode != 'RGB':
            img = img.convert('RGB')
    img.save(output_path, output_format, **save_kwargs)
    print(f"Saved image as {output_format} at {output_path}")

def remove_exif(img, output_path):
    try:
        img.save(output_path, exif=b'')
        print(f"Saved image without EXIF metadata at {output_path}")
    except Exception as e:
        print(f"Failed to remove EXIF metadata: {e}")

def choose_resize_template():
    print("\nAvailable resize templates:")
    for i, (name, (w, h)) in enumerate(resize_templates.items(), start=1):
        print(f"  {i}. {name} ({w}x{h})")
    choice = input("\nChoose a template number or press Enter to cancel: ").strip()
    if choice.isdigit():
        idx = int(choice)
        if 1 <= idx <= len(resize_templates):
            template_name = list(resize_templates.keys())[idx - 1]
            return resize_templates[template_name]
    return None

def save_image_prompt(img):
    out_path = input("Enter output file path (including extension): ").strip()
    if out_path.lower().endswith(('.jpg', '.jpeg')):
        img_to_save = img.convert('RGB')
        img_to_save.save(out_path, quality=95)
    else:
        img.save(out_path)
    print(f"Image saved at {out_path}")

def interactive_cli():
    print("="*50)
    print("      Welcome to Image Tools CLI")
    print("="*50)
    input_path = input("Enter path to image file: ").strip()
    if not os.path.isfile(input_path):
        print("\n[Error] File does not exist. Exiting.\n")
        return
    
    img = load_image(input_path)
    if img is None:
        return
    
    while True:
        print("\n" + "-"*50)
        print("Choose an operation:")
        print("  1. Resize image")
        print("  2. Convert image format")
        print("  3. Remove EXIF metadata")
        print("  4. Upscale image (increase dimensions)")
        print("  5. Exit")
        print("-"*50)
        choice = input("Enter choice (1-5): ").strip()
        
        if choice == '1':
            try:
                use_template = input("\nUse predefined resize template? (y/n): ").strip().lower()
                if use_template == 'y':
                    size = choose_resize_template()
                    if size:
                        w, h = size
                    else:
                        print("\n[Cancelled] No valid template selected.")
                        continue
                else:
                    w = int(input("Enter new width: "))
                    h = int(input("Enter new height: "))
                img = resize_image(img, w, h)
                print(f"\nImage resized to {w}x{h}")
                save_now = input("Save resized image now? (y/n): ").strip().lower()
                if save_now == 'y':
                    save_image_prompt(img)
            except Exception as e:
                print(f"\n[Error] Resizing failed: {e}")
        
        elif choice == '2':
            try:
                fmt = input("\nEnter output format (JPEG, PNG, BMP, etc.): ").strip().upper()
                out_path = input("Enter output file path (including extension): ").strip()
                convert_format(img, out_path, fmt)
            except Exception as e:
                print(f"\n[Error] Format conversion failed: {e}")
        
        elif choice == '3':
            try:
                out_path = input("\nEnter output file path for metadata removed image: ").strip()
                remove_exif(img, out_path)
            except Exception as e:
                print(f"\n[Error] Removing EXIF metadata failed: {e}")

        elif choice == '4':
            try:
                scale_percent = float(input("\nEnter upscale percentage (e.g., 150 for 1.5x): ").strip())
                if scale_percent <= 0:
                    print("[Error] Percentage must be positive.")
                    continue
                w = int(img.width * (scale_percent / 100))
                h = int(img.height * (scale_percent / 100))
                img = resize_image(img, w, h)
                print(f"\nImage upscaled to {w}x{h}")
                save_now = input("Save upscaled image now? (y/n): ").strip().lower()
                if save_now == 'y':
                    save_image_prompt(img)
            except Exception as e:
                print(f"\n[Error] Upscaling failed: {e}")

        elif choice == '5':
            print("\nExiting. Thanks for using Image Tools CLI!\n")
            break
        
        else:
            print("\n[Warning] Invalid choice. Please enter a number from 1 to 5.")

if __name__ == "__main__":
    interactive_cli()
