
######################
## Imports

import numpy
import pandas

######################
## Functions

def retrieve_direction_mapping() :
  direction_mapping = {
      "U": (-1, 0)
    , "R": (0, 1)
    , "D": (1, 0)
    , "L": (0, -1)
  }
  direction_mapping["UR"] = tuple(numpy.add(direction_mapping["U"], direction_mapping["R"]))
  direction_mapping["DR"] = tuple(numpy.add(direction_mapping["D"], direction_mapping["R"]))
  direction_mapping["DL"] = tuple(numpy.add(direction_mapping["D"], direction_mapping["L"]))
  direction_mapping["UL"] = tuple(numpy.add(direction_mapping["U"], direction_mapping["L"]))
  return direction_mapping

def retrieve_direction_tuple(direction_mapping: dict, direction: str) :
  return direction_mapping[direction]

def determine_current_array_positions(position_head: tuple, position_tail: tuple, position_start: tuple, array_tail_visited: numpy.array) :
  array_current_positions = numpy.where(array_tail_visited == 1, "#", " ")
  array_current_positions[position_start] = "s"
  array_current_positions[position_tail] = "T"
  array_current_positions[position_head] = "H"
  return array_current_positions
  
def determine_array_rope_journey(positions: list, position_start: tuple, array_tail_visited: numpy.array) :
  array_rope_journey = numpy.where(array_tail_visited == 1, "#", " ")
  array_rope_journey[position_start] = "s"
  for x in reversed(range(1, len(positions))) :
    array_rope_journey[positions[x]] = x
  array_rope_journey[positions[0]] = "H"
  return array_rope_journey

def move_position(position: tuple, direction_tuple: tuple) :
  new_position = tuple(numpy.add(position, direction_tuple))
  return new_position

def chase_position(position_head: tuple, position_tail: tuple) :
  if position_head == position_tail :
    return position_tail
  else :
    position_difference = tuple(numpy.subtract(position_head, position_tail))
    if max(numpy.absolute(position_difference)) > 1 :
      direction_tuple = numpy.multiply(numpy.sign(position_difference), numpy.where(numpy.absolute(position_difference) > 0, 1, 0))
      position_tail = move_position(position=position_tail, direction_tuple=direction_tuple)
      return position_tail
    else :
      return position_tail

# Testing  
chase_position(position_head=(5,2), position_tail=(4, 1))
chase_position(position_head=(2,2), position_tail=(4, 1))
chase_position(position_head=(5,3), position_tail=(3, 1))
chase_position(position_head=(5,3), position_tail=(4, 1))
chase_position(position_head=(3,4), position_tail=(5, 3))

######################
## Part 1

def part_1(input_file: str, output_file: str = "") :

  # Ingest file into dataframe
  df_motions = pandas.read_csv(input_file, header=None, names=["direction","steps"], sep=" ")

  # Investigate dataframe
  # print(df_motions)
  # df_motions.head(15)

  # Add head direction tuples to dataframe
  direction_mapping = retrieve_direction_mapping()
  df_motions["head_direction_tuple"] = df_motions.apply(lambda x: retrieve_direction_tuple(direction_mapping=direction_mapping, direction=x["direction"]), 1)

  # Investigate dataframe
  # print(df_motions)
  # df_motions.head(15)

  # Dynamically build a grid that is realistically
  # far too large but then we don't need to
  # worry about it not being big enough
  max_height = 1 + df_motions[df_motions["direction"]=="U"]["steps"].sum()
  max_width = 1 + df_motions[df_motions["direction"]=="R"]["steps"].sum()

  # Starting positions in the centre
  position_start = (max_height, max_width)
  position_head = position_start
  position_tail = position_start

  # Empty array as placeholder
  array_tail_visited = numpy.zeros([max_height*2, max_width*2])
  array_tail_visited[position_tail] = 1

  # Convert motions dataframe to list of dicts
  motions_list = df_motions.to_dict("records")

  # print(determine_current_array_positions(position_head, position_tail, position_start, array_tail_visited))

  # Iterate through motions
  for motion in motions_list :
    # print(motion)
    for x in range(motion["steps"]) :
      position_head = move_position(position=position_head, direction_tuple=motion["head_direction_tuple"])
      position_tail = chase_position(position_head=position_head, position_tail=position_tail)
      array_tail_visited[position_tail] = 1
      # print(determine_current_array_positions(position_head, position_tail, position_start, array_tail_visited))

  # print(determine_current_array_positions(position_head, position_tail, position_start, array_tail_visited))

  # Write array positions into text
  if len(output_file) > 0 :
    current_array_positions = determine_current_array_positions(position_head, position_tail, position_start, array_tail_visited)
    numpy.savetxt(output_file, current_array_positions, delimiter=" ", fmt="%s")

  return int(numpy.count_nonzero(array_tail_visited))

part_1(input_file="09/sample_input.txt", output_file="09/part_1_sample_visualised.txt")
part_1(input_file="09/input.txt")

######################
## Part 2

def part_2(input_file: str, output_file: str = "") :

  # Ingest file into dataframe
  df_motions = pandas.read_csv(input_file, header=None, names=["direction","steps"], sep=" ")

  # Investigate dataframe
  # print(df_motions)
  # df_motions.head(15)

  # Add head direction tuples to dataframe
  direction_mapping = retrieve_direction_mapping()
  df_motions["head_direction_tuple"] = df_motions.apply(lambda x: retrieve_direction_tuple(direction_mapping=direction_mapping, direction=x["direction"]), 1)

  # Investigate dataframe
  # print(df_motions)
  # df_motions.head(15)

  # Dynamically build a grid that is realistically
  # far too large but then we don't need to
  # worry about it not being big enough
  max_height = 1 + df_motions[df_motions["direction"]=="U"]["steps"].sum()
  max_width = 1 + df_motions[df_motions["direction"]=="R"]["steps"].sum()

  # Starting positions in the centre
  position_start = (max_height, max_width)
  tail_length = 9
  positions = [position_start for x in range(tail_length + 1)]
  position_end_of_tail = positions[-1]

  # Empty array as placeholder
  array_tail_visited = numpy.zeros([max_height*2, max_width*2])
  array_tail_visited[position_end_of_tail] = 1

  # Convert motions dataframe to list of dicts
  motions_list = df_motions.to_dict("records")

  # print(determine_array_rope_journey(positions, position_start, array_tail_visited))

  # Iterate through motions
  for motion in motions_list :
    # print(motion)
    for x in range(motion["steps"]) :
      # Move head first
      positions[0] = move_position(position=positions[0], direction_tuple=motion["head_direction_tuple"])

      # Move body
      for tail_part in range(1, len(positions)) :
        positions[tail_part] = chase_position(position_head=positions[tail_part - 1], position_tail=positions[tail_part])

      # Note position of end of tail
      array_tail_visited[positions[-1]] = 1
      # print(determine_array_rope_journey(positions, position_start, array_tail_visited))

  # print(determine_array_rope_journey(positions, position_start, array_tail_visited))

  # Write array positions into text
  if len(output_file) > 0 :
    array_rope_journey = determine_array_rope_journey(positions, position_start, array_tail_visited)
    numpy.savetxt(output_file, array_rope_journey, delimiter=" ", fmt="%s")

  return int(numpy.count_nonzero(array_tail_visited))

part_2(input_file="09/larger_sample_input.txt", output_file="09/part_2_sample_visualised.txt")
part_2(input_file="09/input.txt")
