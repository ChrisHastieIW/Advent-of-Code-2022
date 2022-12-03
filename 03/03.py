
# Import modules
import numpy
import pandas

# Function to retrieve item priority
def retrieve_item_priority(char: str) :
  if char == char.lower() :
    return ord(char) - ord("a") + 1
  elif char == char.upper() :
    return ord(char) - ord("A") + 27

## Testing
retrieve_item_priority("b")
retrieve_item_priority("B")

# Determine input file location
input_file = "03\input.txt"

# Ingest file into dataframe
df_rucksacks = pandas.read_csv(input_file, header=None, names=["contents"])

# Investigate dataframe
print(df_rucksacks)
df_rucksacks.head(15)

# Split contents into compartments and determine overlap
df_rucksacks["item_count"] = df_rucksacks["contents"].str.len()

df_rucksacks["compartment_1"] = df_rucksacks.apply(lambda x: x["contents"][0:int(x["item_count"]/2)], 1)
df_rucksacks["compartment_2"] = df_rucksacks.apply(lambda x: x["contents"][int(x["item_count"]/2):int(x["item_count"])], 1)

df_rucksacks["common_item"] = df_rucksacks.apply(lambda x: ''.join(set(x["compartment_1"]).intersection(x["compartment_2"])), 1)

df_rucksacks["common_item_priority"] = df_rucksacks.apply(lambda x: retrieve_item_priority(x["common_item"]), 1)

# Investigate dataframe
print(df_rucksacks)
df_rucksacks.head(15)

# Total priority
df_rucksacks["common_item_priority"].sum()

#####################
## Part 2

df_rucksacks["new_group"] = numpy.where(df_rucksacks.index % 3 == 0, 1, 0)

df_rucksacks["group"] = df_rucksacks["new_group"].cumsum()

df_grouped_rucksacks = df_rucksacks.groupby("group")["contents"].apply(list).reset_index(name="contents_list")

df_grouped_rucksacks["common_item"] = df_grouped_rucksacks.apply(lambda x: ''.join(set.intersection(*map(set,x["contents_list"]))), 1)

df_grouped_rucksacks["common_item_priority"] = df_grouped_rucksacks.apply(lambda x: retrieve_item_priority(x["common_item"]), 1)

# Investigate dataframe
print(df_grouped_rucksacks)
df_grouped_rucksacks.head(15)

# Total priority
df_grouped_rucksacks["common_item_priority"].sum()