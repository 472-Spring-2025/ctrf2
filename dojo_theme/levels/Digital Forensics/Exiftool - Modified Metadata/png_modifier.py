from PIL import Image
from PIL.PngImagePlugin import PngInfo
import yaml

with open("input.yml", "r") as file:
    config = yaml.safe_load(file)
meta_data_attributes = config["meta-data-attributes"].split(",")
meta_data_values = config["meta-data-values"].split(",")
flag_attr = config["attribute-with-flag"]
image_name = config["image-name"]
new_name = "input/" + image_name
# Open an existing PNG file
image = Image.open("input/ABPRUNING.png")

# Create a new PngInfo object to hold metadata
metadata = PngInfo()

# Add new metadata
for i in range(len(meta_data_attributes)):
    attr = meta_data_attributes[i]
    val = meta_data_values[i]
    if(meta_data_attributes[i].strip() == flag_attr.strip()):
        with open("/flag", "r") as f:
            val = f.readline()
    metadata.add_text(attr, val)

# Save the image with the new metadata
image.save(new_name, "PNG", pnginfo=metadata)

# Verify the metadata
modified_image = Image.open(new_name)
print(modified_image.info)