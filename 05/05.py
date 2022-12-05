
# Import modules
import numpy
import pandas
from io import StringIO
import re

# Determine input file location
input_file = "05\input.txt"

# Ingest input file into text
with open(input_file, 'r') as f:
  input_text = f.read()

# Investigate input text
print(input_text)

input_text_split = input_text.split('\n\n')

stacks_text = input_text_split[0]
instructions = input_text_split[1].splitlines()

# Investigate
print(stacks_text)
print(instructions)

# Ingest file into dataframe
df_stacks = pandas.read_fwf(StringIO(stacks_text), header=None)

# Use final row as headers for dataframe
headers = [str(x) for x in df_stacks.iloc[-1].to_list()]
df_stacks.columns = headers
df_stacks.drop(df_stacks.index[-1], inplace=True)

# Investigate dataframe
print(df_stacks)
df_stacks.head(15)

# Create dataframe of stack lists
df_stack_lists = pandas.DataFrame(columns=headers)

for stack_id in headers:
  df_stack_lists[stack_id] = [[x[1] for x in list(df_stacks[df_stacks[stack_id].notna()][stack_id].to_list())]]

# Investigate dataframe
print(df_stack_lists)
df_stack_lists.head(15)

# Apply instructions
for instruction in instructions :
  instruction_list = re.findall('(\d+)', instruction)
  number_to_move = int(instruction_list[0])
  source = instruction_list[1]
  target = instruction_list[2]
  for x in range(1, number_to_move + 1) :
    moving_value = df_stack_lists[source].iloc[0].pop(0)
    df_stack_lists[target].iloc[0].insert(0, moving_value)

# Investigate dataframe
print(df_stack_lists)
df_stack_lists.head(15)

# Determine final output
final_output_list = []
for stack_id in headers:
  final_output_list.append(df_stack_lists[stack_id].iloc[0][0])

final_output = ''.join(final_output_list)
print(final_output)

###########
## Part 2

# Create dataframe of stack lists
df_stack_lists_2 = pandas.DataFrame(columns=headers)

for stack_id in headers:
  df_stack_lists_2[stack_id] = [[x[1] for x in list(df_stacks[df_stacks[stack_id].notna()][stack_id].to_list())]]

# Investigate dataframe
print(df_stack_lists_2)
df_stack_lists_2.head(15)

# Apply instructions
for instruction in instructions :
  instruction_list = re.findall('(\d+)', instruction)
  number_to_move = int(instruction_list[0])
  source = instruction_list[1]
  target = instruction_list[2]
  moving_list = []
  for x in range(1, number_to_move + 1) :
    moving_list.append(df_stack_lists_2[source].iloc[0].pop(0))
  df_stack_lists_2[target].iloc[0] = moving_list + df_stack_lists_2[target].iloc[0]

# Investigate dataframe
print(df_stack_lists_2)
df_stack_lists_2.head(15)

# Determine final output
final_output_list_2 = []
for stack_id in headers:
  final_output_list_2.append(df_stack_lists_2[stack_id].iloc[0][0])

final_output_2 = ''.join(final_output_list_2)
print(final_output_2)
