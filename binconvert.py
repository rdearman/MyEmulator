#!/usr/bin/python
#!/usr/bin/env python


import argparse

def text_to_binary(input_file, output_file):
    # Open the text file for reading
    with open(input_file, "r") as text_f:
        # Read lines from the text file
        lines = text_f.readlines()

    # Initialize an empty list to store binary data
    binary_data = []

    # Iterate through the lines and convert them to binary
    for line in lines:
        # Remove leading and trailing whitespace
        line = line.strip()

        # Check if the line is not empty
        if line:
            # Convert the binary string to an integer
            binary_integer = int(line, 2)

            # Append the binary integer to the list
            binary_data.append(binary_integer)

    # Open the binary file for writing in binary mode
    with open(output_file, "wb") as binary_f:
        # Write the binary data as bytes to the binary file
        for binary_integer in binary_data:
            binary_f.write(binary_integer.to_bytes(2, byteorder="big"))

    print(f"Text file '{input_file}' has been converted to binary file '{output_file}'.")

if __name__ == "__main__":
    # Create a command-line argument parser
    parser = argparse.ArgumentParser(description="Convert a text file to a binary file.")

    # Add arguments for input and output file names
    parser.add_argument("-i", "--input", help="Input text file name", required=True)
    parser.add_argument("-o", "--output", help="Output binary file name", required=True)

    # Parse the command-line arguments
    args = parser.parse_args()

    # Call the conversion function with the provided file names
    text_to_binary(args.input, args.output)

