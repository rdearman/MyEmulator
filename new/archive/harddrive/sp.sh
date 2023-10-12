#!/bin/bash

input_file="full.txt"
output_directory="sp"

# Create the output directory if it doesn't exist
mkdir -p "$output_directory"

# Read each line from the input file and create separate output files
line_number=1
while read -r line; do
    output_file="$output_directory/$line_number.txt"
    echo -e "$line\n$(tail -n 1 $input_file)" > "$output_file"
    ((line_number++))
done < "$input_file"
