import sys
sys.path.insert(0, "/challenge/deps")
from PIL import Image
from PIL.PngImagePlugin import PngInfo
import yaml

with open("input.yml", "r") as file:
    config = yaml.safe_load(file)
meta_data_attributes = config["Meta Data Attributes (attribute1, attribute2, ...)"].split(",")
meta_data_values = config["Meta Data Values (Value1,Value2, ... [At least as many as Meta Data Attributes])"].split(",")
flag_attr = config["Attribute With The Flag"]
image_name = config["Image Name"]
new_name = "/challenge/" + image_name
# Open an existing PNG file
image = Image.open("/challenge/input/CP_wallpaper.jpg")

# Create a new PngInfo object to hold metadata
metadata = PngInfo()

# Add new metadata
for i in range(len(meta_data_attributes)):
    attr = meta_data_attributes[i]
    val = meta_data_values[i]
    if(meta_data_attributes[i].strip() == flag_attr.strip()):
        #with open("/flag", "r") as f:
            val = "Bello"#f.readline()
    metadata.add_text(attr, val)

# Save the image with the new metadata
image.save(new_name, "JPEG", pnginfo=metadata)

# Verify the metadata
modified_image = Image.open(new_name)
print(modified_image.info)