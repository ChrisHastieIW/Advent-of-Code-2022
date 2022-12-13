
######################
## Imports

import numpy
import pandas
import json

######################
## Functions
  
def clean_input_string(input_string: str) :
  if input_string.isnumeric() :
    return int(input_string)
  else :
    return json.loads(input_string)

def parse_input_to_list(input_file: str) :
  
  # Ingest file into list
  with open(input_file, 'r') as f:
    input_list = f.read().splitlines()

  packets_list = [clean_input_string(input_string) for input_string in input_list if len(input_string) > 0]
  return packets_list

def parse_input(input_file: str) :
  
  # Ingest file into list
  with open(input_file, 'r') as f:
    input_list = f.read().splitlines()

  packet_pairs = []
  current_packet_pair_id = 0
  current_packet_pair_dict = {}
  counter = 0
  for input_string in input_list :
    if len(input_string) == 0 :
      counter = 0
      packet_pairs.append(current_packet_pair_dict)
    elif counter == 0 :
      counter += 1
      current_packet_pair_id += 1
      current_packet_pair_dict = {"id" : current_packet_pair_id, "left" : clean_input_string(input_string)}
    else :
      current_packet_pair_dict["right"] = clean_input_string(input_string)
  packet_pairs.append(current_packet_pair_dict)

  df_packet_pairs = pandas.DataFrame(data=packet_pairs)

  return df_packet_pairs

def compare_packets(left, right, pair_id: int = 0, depth: int = 0, logging: str = "") : 
  if depth == 0 :
    logging +=f"== Pair {pair_id} =="
  indent = " "*depth
  logging +=f"\n{indent}- Compare {left} vs {right}"
  if type(left) != list \
    and type(right) != list :
      if left < right :
        logging +=f"\n{indent} - Left side is smaller, so inputs are in the right order"
        validation = True
      elif left == right :
        validation = None
      elif left > right :
        logging +=f"\n{indent} - Right side is smaller, so inputs are not in the right order"
        validation = False
  else :
    if type(left) == int \
      and type(right) == list :
      left = [left]
      logging +=f"\n{indent} - Mixed types; convert left to {left} and retry comparison"
      validation, logging = compare_packets(left, right, pair_id, depth + 1, logging)
    elif type(left) == list \
      and type(right) == int :
      right = [right]
      logging +=f"\n{indent} - Mixed types; convert right to {right} and retry comparison"
      validation, logging = compare_packets(left, right, pair_id, depth + 1, logging)
    elif len(left) == 0 \
      and len(right) == 0:
      validation = None
    elif len(left) == 0 :
      logging +=f"\n{indent}- Left side ran out of items, so inputs are in the right order"
      validation = True
    elif len(right) == 0:
      logging +=f"\n{indent}- Right side ran out of items, so inputs are not in the right order"
      validation = False
    else :
      for x in range(max(len(left), len(right))) :
        if x >= len(left) :
          logging +=f"\n{indent}- Left side ran out of items, so inputs are in the right order"
          validation = True
        elif x >= len(right) :
          logging +=f"\n{indent}- Right side ran out of items, so inputs are not in the right order"
          validation = False
        else :
          validation, logging = compare_packets(left[x], right[x], pair_id, depth + 1, logging)
        if validation is not None :
          break
  if depth == 0 :
    if validation is None :
      logging +=f"\n{indent}- Left side ran out of items, so inputs are in the right order"
      validation = True
    # print(logging)
    return {"validation": validation, "logging": logging}
  else :
    return validation, logging

######################
## Part 1

def part_1(input_file: str, output_file: str = "") :

  df_packet_pairs = parse_input(input_file)
  df_packet_pairs["validation"] = df_packet_pairs.apply(lambda x: compare_packets(x["left"], x["right"], x["id"])["validation"], axis=1)
  df_packet_pairs["logging"] = df_packet_pairs.apply(lambda x: compare_packets(x["left"], x["right"], x["id"])["logging"], axis=1)
  
  if len(output_file) > 0 :
    df_packet_pairs["logging"].to_csv(output_file, header=None, index=None, doublequote=False)

  result = df_packet_pairs[df_packet_pairs["validation"] == True]["id"].sum()

  return result

part_1(input_file="13/sample_input.txt")
part_1(input_file="13/input.txt", output_file = "13/output.txt")

######################
## Part 2

def part_2(input_file: str) :

  packets_list = parse_input_to_list(input_file)

  decoder_start_value = [[2]]
  decoder_end_value = [[6]]
  packets_list += [decoder_start_value, decoder_end_value]

  for i in range(len(packets_list) - 1) :
    for x in range(len(packets_list) - 1) :
      left = packets_list[x]
      right = packets_list[x+1]
      if compare_packets(left, right)["validation"] == False :
        packets_list[x] = right
        packets_list[x+1] = left

  decoder_start = packets_list.index(decoder_start_value) + 1
  decoder_end = packets_list.index(decoder_end_value) + 1

  result = decoder_start * decoder_end

  return result

part_2(input_file="13/sample_input.txt")
part_2(input_file="13/input.txt")