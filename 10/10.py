
######################
## Imports

import numpy
import pandas

######################
## Functions



######################
## Part 1

def part_1(input_file: str) :

  # Ingest file into dataframe
  df_input = pandas.read_csv(input_file, header=None, names=["instruction","value"], sep=" ")

  # Add instruction ID
  df_input["instruction_id"] = df_input.index
  
  # Investigate dataframe
  # print(df_input)
  # df_input.head(15)
  
  # Duplicate rows for addx
  df_input_1 = df_input.copy()
  df_input_1["instruction_sub_id"] = 1
  df_input_2 = df_input[df_input["instruction"] == "addx"].copy()
  df_input_2["instruction_sub_id"] = 2
  df_instructions = pandas.concat([df_input_1, df_input_2]).sort_index()

  # Sort and reindex
  df_instructions.sort_values(["instruction_id", "instruction_sub_id"], inplace=True)
  df_instructions.reset_index(drop=False, inplace=True)

  # Determine cycle and cycle value
  df_instructions["cycle"] = df_instructions.index + 2
  df_instructions["cycle_value"] = numpy.where(df_instructions["instruction_sub_id"] == 2, df_instructions["value"], 0)

  # X and signal strength for current value
  df_instructions["X"] =  df_instructions["cycle_value"].cumsum() + 1
  df_instructions["signal_strength"] =  numpy.where((df_instructions["cycle"]+20)%40 == 0, df_instructions["X"] * df_instructions["cycle"], 0)

  # Investigate dataframe
  # print(df_instructions)
  # df_instructions.head(21)

  print(df_instructions[df_instructions["signal_strength"] != 0])

  total_signal_strength = df_instructions["signal_strength"].sum()

  return total_signal_strength

part_1(input_file="10/sample_input.txt")
part_1(input_file="10/input.txt")

######################
## Part 2

def part_2(input_file: str) :

  # Ingest file into dataframe
  df_input = pandas.read_csv(input_file, header=None, names=["instruction","value"], sep=" ")

  # Add instruction ID
  df_input["instruction_id"] = df_input.index
  
  # Investigate dataframe
  # print(df_input)
  # df_input.head(15)
  
  # Duplicate rows for addx
  df_input_1 = df_input.copy()
  df_input_1["instruction_sub_id"] = 1
  df_input_2 = df_input[df_input["instruction"] == "addx"].copy()
  df_input_2["instruction_sub_id"] = 2
  df_instructions = pandas.concat([df_input_1, df_input_2]).sort_index()

  # Sort and reindex
  df_instructions.sort_values(["instruction_id", "instruction_sub_id"], inplace=True)
  df_instructions.reset_index(drop=False, inplace=True)

  # Determine cycle and cycle value
  df_instructions["cycle"] = df_instructions.index + 1
  df_instructions["cycle_value"] = numpy.where(df_instructions["instruction_sub_id"] == 2, df_instructions["value"], 0)
  df_instructions["cycle_range_value"] = numpy.where(df_instructions["instruction_sub_id"] == 1, df_instructions["value"], 0)

  df_instructions["X"] = df_instructions["cycle_value"].cumsum() + 1
  df_instructions["cycle_start_value"] =  df_instructions["X"] - df_instructions["cycle_value"]
  df_instructions["cycle_end_value"] =  df_instructions["X"] + df_instructions["cycle_range_value"]
  # df_instructions["current_crt_draw_range_start"] = df_instructions[["cycle_start_value", "cycle_end_value"]].min(axis=1) - 1
  # df_instructions["current_crt_draw_range_end"] = df_instructions[["cycle_start_value", "cycle_end_value"]].max(axis=1) + 1
  df_instructions["current_crt_draw_range_start"] = df_instructions["cycle_start_value"] - 1
  df_instructions["current_crt_draw_range_end"] = df_instructions["cycle_start_value"] + 1
  df_instructions["current_pixel"] = df_instructions.index % 40
  df_instructions["current_crt_row_number"] = ((df_instructions.index % 40) == 0).cumsum() - 1
  df_instructions["current_crt_pixel_highlight"] = numpy.where(
    (df_instructions["current_pixel"] >= df_instructions["current_crt_draw_range_start"])
    &
    (df_instructions["current_pixel"] <= df_instructions["current_crt_draw_range_end"])
    , 1, 0
  )
  df_instructions["current_crt_pixel_value"] = numpy.where(df_instructions["current_crt_pixel_highlight"] == 1, "#", " ")

  # Investigate dataframe
  # print(df_instructions)
  # df_instructions.info()
  # df_instructions[["instruction", "value", "cycle", "cycle_start_value", "cycle_end_value", "current_crt_draw_range_start", "current_crt_draw_range_end", "current_pixel", "current_crt_pixel_value"]].head(8)

  current_crt = numpy.empty([6, 40], dtype=str)
  current_crt.fill(" ")

  for instruction_id in range(len(df_instructions)) :
    instruction = df_instructions.iloc[instruction_id]
    current_crt[instruction["current_crt_row_number"], instruction["current_pixel"]] = instruction["current_crt_pixel_value"]

  for crt_row in current_crt :
    print("".join(crt_row))

part_2(input_file="10/sample_input.txt")
part_2(input_file="10/input.txt")
