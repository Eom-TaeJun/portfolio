import h5py

# Define the file path
file_path = r"C:\Users\TJ\Desktop\VNP46A3.A2012245.h30v05.001.2021118161919.h5"

# Open the HDF5 file
with h5py.File(file_path, 'r') as hdf:
    # Print all groups
    print("Keys: %s" % hdf.keys())
    
    # Access the 'HDFEOS' group
    hdfeos_group = hdf['HDFEOS']
    print("\nKeys in 'HDFEOS': %s" % hdfeos_group.keys())
    
    # Access the 'HDFEOS INFORMATION' group
    hdfeos_info_group = hdf['HDFEOS INFORMATION']
    print("\nKeys in 'HDFEOS INFORMATION': %s" % hdfeos_info_group.keys())
    
    # Example: Iterating through datasets in the 'HDFEOS' group
    for name, item in hdfeos_group.items():
        if isinstance(item, h5py.Dataset):
            print(f"Dataset: {name}, Shape: {item.shape}")
        elif isinstance(item, h5py.Group):
            print(f"Group: {name}")
            # Recursively print datasets within the group
            for sub_name, sub_item in item.items():
                if isinstance(sub_item, h5py.Dataset):
                    print(f"  Dataset: {sub_name}, Shape: {sub_item.shape}")
                elif isinstance(sub_item, h5py.Group):
                    print(f"  Sub-group: {sub_name}")
                    
    # Example: Accessing a specific dataset and printing its shape
    dataset_name = 'HDFEOS/SWATHS/VNP_Grid_DNB/Data Fields/OutlierPixelQA'  # Replace with actual dataset path
    if dataset_name in hdf:
        dataset = hdf[dataset_name]
        print(f"\nShape of dataset '{dataset_name}': {dataset.shape}")
    else:
        print(f"\nDataset '{dataset_name}' not found.")
