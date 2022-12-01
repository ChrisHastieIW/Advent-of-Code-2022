
# Import modules
import numpy
import pandas

# Determine input file location
input_file = "01\input.txt"

# Ingest file into series
df_calories = pandas.read_csv(input_file, header=None, names=["calories"], skip_blank_lines=False)

# Investigate dataframe
print(df_calories)
df_calories.head(15)

# Determine elf ID
df_calories["new_elf"] = df_calories["calories"].isnull()
df_calories["elf_id_calc"] = df_calories["new_elf"].cumsum()
df_calories["elf_id"] = numpy.where(df_calories["new_elf"], df_calories["elf_id_calc"], df_calories["elf_id_calc"] + 1)

# New dataframe without extra fields
df_elves = df_calories[["elf_id", "calories"]]

# Investigate elves
print(df_elves)
df_elves.head(15)

# Aggregate by elf
df_elf_totals = df_elves.groupby("elf_id").sum("calories")

# Investigate elf totals
print(df_elf_totals)
df_elf_totals.head(15)

# Detemine elf with the most
df_elf_max = df_elf_totals[df_elf_totals["calories"] == df_elf_totals["calories"].max()]

# Investigate max elf for answer to first part
print(df_elf_max)

# Sort and filter to top three
df_elf_top_three = df_elf_totals.sort_values(by=["calories"], ascending=False)[:3]

# Aggregate for total calories
df_elf_top_three["calories"].sum()