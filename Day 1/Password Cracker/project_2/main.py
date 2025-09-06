import os 

files = os.listdir('.')

zip_files = [file for file in files if file.endswith('.zip')]
print(zip_files)

