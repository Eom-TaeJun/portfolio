import fastai
print(fastai.__version__)

from fastai.vision.all import *
from matplotlib.pyplot import imshow
from google.colab import files

# 2. Upload images to Colab

# Set the name of the folder to download images
img_folder_nm = 'my_labels'

# Set the name of the zip file to be downloaded
img_zipfile_nm = 'my_labels.zip'

!ls

# Unzip the image files
!unzip {img_zipfile_nm} -d {img_folder_nm}

!ls {img_folder_nm}

# Remove "__MACOSX" folder if files are compressed with a Mac
import shutil

# Path to the "__MACOSX" folder
macosx_dir = os.path.join(img_folder_nm, "__MACOSX")

# Check if the folder exists and then remove it
if os.path.exists(macosx_dir):
    shutil.rmtree(macosx_dir)
    print(f'Deleted the folder: {macosx_dir}')
else:
    print(f'The folder {macosx_dir} does not exist')

# 3. Prepare images

# Location of images
path = Path(img_folder_nm)

# Get list of image files
file_names = get_image_files(path)
file_names

# Show an example image
im = Image.open(file_names[0])
print(im.shape)
imshow(im)

# Find corrupt images and unlink them
corrupt_images = verify_images(file_names)
corrupt_images.map(Path.unlink)

corrupt_images

# Data block settings
image_size = 276
valid_set_share = 0.3
my_random_seed = 42

my_dblock = DataBlock(
    blocks=(ImageBlock, CategoryBlock),
    get_items=get_image_files,
    splitter=RandomSplitter(valid_pct=valid_set_share, seed=my_random_seed),
    get_y=parent_label,
    item_tfms=Resize(image_size))

# Prepare dataloaders
my_batch_size = 32

dls = my_dblock.dataloaders(path, batch_size=my_batch_size)

# Show image examples
dls.train.show_batch(max_n=10, nrows=2)

# 4.1 Train with Resnet18

learn = vision_learner(dls, resnet18, metrics=accuracy).to_fp16() # resnet 18, 34, 50, 101, 152
learn.fine_tune(3)

# 4.2 Deeper Network

# Use Resnet50 instead of Resnet18
learn = vision_learner(dls, resnet50, metrics=accuracy).to_fp16() # resnet 18, 34, 50, 101, 152
learn.fine_tune(1)

# 4.3 Image Augmentation

# Add augmentation option: batch_tfms=aug_transforms(mult=2)
my_augmented_dblock = DataBlock(
    blocks=(ImageBlock, CategoryBlock),
    get_items=get_image_files,
    splitter=RandomSplitter(valid_pct=valid_set_share, seed=my_random_seed),
    get_y=parent_label,
    item_tfms=Resize(image_size),
    batch_tfms=aug_transforms(mult=2))

my_augmented_dls = my_augmented_dblock.dataloaders(path)

# Show image examples
my_augmented_dls.train.show_batch(max_n=10, nrows=2, unique=True)

learn = vision_learner(my_augmented_dls, resnet18, metrics=accuracy).to_fp16() # resnet 18, 34, 50, 101, 152
learn.fine_tune(1)

# 4.4 Image Augmentation + Resnet50 + More Epochs

learn = vision_learner(my_augmented_dls, resnet50, metrics=accuracy).to_fp16() # resnet 18, 34, 50, 101, 152
learn.fine_tune(10)

# 5. Plot Loss

learn.recorder.plot_loss(with_valid=True)

# 6. Early Stopping

learn = vision_learner(my_augmented_dls, resnet50, metrics=accuracy).to_fp16() # resnet 18, 34, 50, 101, 152
learn.path = Path('./')

learn.fine_tune(50, cbs=[EarlyStoppingCallback(monitor='accuracy', patience=5), SaveModelCallback(monitor='accuracy')])

learn.validate()

interp = ClassificationInterpretation.from_learner(learn)
interp.plot_confusion_matrix(figsize=(7,7))

interp.plot_confusion_matrix(normalize=True, cmap='Reds', figsize=(7,7))

# 7. Save Your Model

# Export your model
learn.export()

!ls

# Download the file to your local computer
files.download('./export.pkl')

# 8. Load Your Trained Model for Predictions

# Load your saved model
learn_inf = load_learner('./export.pkl')

# 9. Load New Images for Predictions

# Set the name of the folder to download images
img_folder_nm = 'new_images_for_prediction'

# Set the name of the zip file to be downloaded
img_zipfile_nm = 'new_imgs.zip'

# Uncomment if Dropbox link is used to download file
# !wget -O {img_zipfile_nm} {dropbox_link}

# Uncomment the following lines if using Google Drive
# from google.colab import drive
# drive.mount('/content/drive')

# Uncomment if files are uploaded directly
# files.upload()

# Unzip the test image files
!unzip {img_zipfile_nm} -d {img_folder_nm}

# Grab a list of images in the folder
test_imgs_list = get_image_files(img_folder_nm)
test_imgs_list

# 10. Generate Predictions

# Predict single image
print('- file for prediction: {}'.format(test_imgs_list[0]))
print('')
print('- prediction result:')

single_pred = learn_inf.predict(test_imgs_list[0])
print(single_pred)

# Generate predictions for multiple images
new_predictions = []
new_predictions_label_only = []

for each_img in test_imgs_list:
    each_pred = learn_inf.predict(each_img)
    new_predictions.append(each_pred)
    new_predictions_label_only.append(each_pred[0])

new_predictions_label_only

# Create a table for predictions
final_table = pd.DataFrame(zip(test_imgs_list, new_predictions_label_only), columns=['file_path', 'label'])
final_table

# Export as a CSV file
final_table.to_csv('final_table.csv', index=False)

# Export as an Excel file
final_table.to_excel('final_table.xlsx', index=False)

# Export as a Stata file
final_table['file_path'] = final_table['file_path'].astype(str)
final_table.to_stata('final_table.dta', write_index=False, version=118)
