import os
import random
import shutil

# Paths
dataset_path = "/Users/pabloelgueta/Documents/trading-card-assistant/datasets/pokemon"
train_images_path = os.path.join(dataset_path, "images", "train")
train_labels_path = os.path.join(dataset_path, "labels", "train")
val_images_path = os.path.join(dataset_path, "images", "val")
val_labels_path = os.path.join(dataset_path, "labels", "val")

os.makedirs(val_images_path, exist_ok=True)
os.makedirs(val_labels_path, exist_ok=True)

# Parameters
val_split = 0.2  # 20% for validation
random.seed(42)  # For reproducibility

# Get all image files
image_files = [
    f for f in os.listdir(train_images_path) if f.endswith((".jpg", ".jpeg", ".png"))
]

# Shuffle and split
random.shuffle(image_files)
split_idx = int(len(image_files) * val_split)
val_files = image_files[:split_idx]


# Move files
def move_files(files, src_dir, dst_dir):
    for file in files:
        shutil.move(os.path.join(src_dir, file), os.path.join(dst_dir, file))


move_files(val_files, train_images_path, val_images_path)


# Move corresponding label files
def move_label_files(files, src_dir, dst_dir):
    for file in files:
        label_file = (
            file.replace(".jpg", ".txt")
            .replace(".jpeg", ".txt")
            .replace(".png", ".txt")
        )
        if os.path.exists(os.path.join(src_dir, label_file)):
            shutil.move(
                os.path.join(src_dir, label_file), os.path.join(dst_dir, label_file)
            )


move_label_files(val_files, train_labels_path, val_labels_path)

print("Dataset split completed.")
