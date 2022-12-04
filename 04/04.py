
# Import modules
import numpy
import pandas

# Function to build range from string
def build_range_from_string(string_list: str) :
  range_boundaries = [int(x) for x in string_list.split('-')]
  range_object = range(range_boundaries[0], range_boundaries[1] + 1)
  range_list = list(range_object)
  return range_list

## Testing
build_range_from_string("4-8")
build_range_from_string("502-607")

# Determine input file location
input_file = "04\input.txt"

# Ingest file into dataframe
df_areas = pandas.read_csv(input_file, header=None, names=["elf_1_input","elf_2_input"], sep=",")

# Investigate dataframe
print(df_areas)
df_areas.head(15)

# Convert inputs to lists
df_areas["elf_1_area_list"] = df_areas.apply(lambda x: build_range_from_string(x["elf_1_input"]), 1)
df_areas["elf_2_area_list"] = df_areas.apply(lambda x: build_range_from_string(x["elf_2_input"]), 1)

# Determine overlaps
df_areas["overlap"] = df_areas.apply(lambda x: sorted(list(set(x["elf_1_area_list"]).intersection(x["elf_2_area_list"]))), 1)

df_areas["elf_1_fully_contained"] = df_areas.apply(lambda x: x["elf_1_area_list"] == x["overlap"], 1)
df_areas["elf_2_fully_contained"] = df_areas.apply(lambda x: x["elf_2_area_list"] == x["overlap"], 1)
df_areas["fully_contained_flag"] = df_areas.apply(lambda x: x["elf_1_fully_contained"] or x["elf_2_fully_contained"], 1)

# Investigate dataframe
print(df_areas)
df_areas.head(10)

df_areas["fully_contained_flag"].astype(int).sum()

###########
## Part 2

df_areas["overlap_exists"] = df_areas.apply(lambda x: len(x["overlap"]) > 0, 1)

df_areas["overlap_exists"].astype(int).sum()
