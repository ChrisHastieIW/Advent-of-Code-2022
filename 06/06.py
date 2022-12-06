
# Determine input file location
input_file = "06\input.txt"

# Ingest input file into text
with open(input_file, 'r') as f:
  input_text = f.read()

# Investigate input text
print(input_text)

# Define function to find position
# of first distinct combination of given length

def find_marker(input_text: str, marker_length: int) :    
  for x in range(marker_length, len(input_text)) :
    substring = input_text[x-marker_length:x]
    unique_substring_length = len(set(substring))
    if unique_substring_length == marker_length :
      return x

find_marker(input_text, 4)

################
## Part 2

find_marker(input_text, 14)
