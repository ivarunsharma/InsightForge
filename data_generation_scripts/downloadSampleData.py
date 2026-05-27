import kagglehub
import os

# data/ subfolder next to this script
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# Download directly into the data directory
path = kagglehub.dataset_download(
    "vivek468/superstore-dataset-final",
    output_dir=DATA_DIR
)

print("Downloaded to:", path)