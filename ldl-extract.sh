#! /bin/bash

# Navigate to the Drupal 7 directory
cd /var/www/drupal7
# Fetch all PIDs for a specific collection and save them to a file
drush -u 1 islandora_datastream_crud_fetch_pids --namespace=COLLECTION_NAME --pid_file=/tmp/COLLECTION_NAME.txt

# Download the MODS datastream for all PIDs
drush -u 1 idcrudfd --pid_file=/tmp/COLLECTION_NAME.txt --datastreams_directory=/tmp/COLLECTION_NAME --dsid=MODS

# Download the RELS-EXT datastream for all PIDs
drush -u 1 idcrudfd --pid_file=/tmp/COLLECTION_NAME.txt --datastreams_directory=/tmp/COLLECTION_NAME --dsid=RELS-EXT

# Download the OBJ datastream (binary files) for all PIDs
drush -u 1 idcrudfd --pid_file=/tmp/COLLECTION_NAME.txt --datastreams_directory=/tmp/COLLECTION_NAME --dsid=OBJ

# Change to the directory where the datastreams were downloaded
cd /tmp/COLLECTION_NAME || exit

# Compress the collection into a zip file
zip COLLECTION_NAME.zip *

# Transfer the zip file from the remote server to your local machine
scp dgi-ingest:/tmp/COLLECTION_NAME/COLLECTION_NAME.zip ~/Downloads

# Copy the zip file to an external media storage location
cp ~/Downloads/COLLECTION_NAME.zip /media/wwc/0A2C-888E/COLLECTION_NAME/

# Navigate to the directory where the data will be unzipped
cd /media/wwc/0A2C-888E/COLLECTION_NAME || exit

# Create a 'Data' directory to store unzipped content
mkdir -p Data
cd Data || exit

# Unzip the downloaded collection
unzip ../COLLECTION_NAME.zip

# Convert all JP2 images in the directory to PNG format
for f in *.jp2; do
  opj_decompress -i "$f" -OutFor PNG -o "${f%.*}.png"
done
