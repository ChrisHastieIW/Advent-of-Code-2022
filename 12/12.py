
######################
## Imports

import numpy
import pandas

######################
## Functions

def parse_input(input_file: str) :
  
  # Ingest file into list
  with open(input_file, 'r') as f:
    input_list = f.read().splitlines()

  # Determine height and width of array
  height = len(input_list)
  width = len(input_list[0])

  array_input = numpy.empty([height, width], dtype=str)

  for height_position in range(height) :
    for width_position in range(width) :
      array_input[height_position, width_position] = input_list[height_position][width_position]

  return array_input

def find_positions_in_array(array_input: numpy.array, input_char: str) :
  positions = []
  for height_position in range(numpy.shape(array_input)[0]) :
    for width_position in range(numpy.shape(array_input)[1]) :
      if array_input[height_position, width_position] == input_char :
        positions.append((height_position, width_position))

  return positions
 
def retrieve_array_elevations(array_input: numpy.array, start_position: tuple, end_position: tuple) :
  array_elevations = array_input.copy()
  array_elevations[start_position] = "a"
  array_elevations[end_position] = "z"
  return array_elevations

def retrieve_direction_mapping() :
  direction_mapping = {
      "^" : (-1, 0)
    , ">" : (0,1)
    , "v" : (1,0)
    , "<" : (0,-1)
  }
  return direction_mapping

def determine_path_class_value(array_elevations: numpy.array, current_position: tuple, target_position: tuple) :
  try :
    path_class_value = ord(array_elevations[target_position]) - ord(array_elevations[current_position])
    if path_class_value > 1 :
      return None
    elif path_class_value == 1 :
      return 1
    elif path_class_value == 0 :
      return 0
    else :
      return -1
  except :
    return None

def determine_possible_directions(direction_mapping: dict, array_elevations: numpy.array, array_paths: numpy.array, current_position: tuple) :
  possible_directions = []
  for direction in ["^", ">", "v", "<"] :
    direction_tuple = direction_mapping[direction]
    target_position = tuple(numpy.add(current_position, direction_tuple))
    if target_position >= (0, 0) \
      and target_position[0] <= tuple(numpy.subtract(numpy.shape(array_elevations), (1, 1)))[0] \
      and target_position[1] <= tuple(numpy.subtract(numpy.shape(array_elevations), (1, 1)))[1] :
      path_class_value = determine_path_class_value(array_elevations=array_elevations, current_position=current_position, target_position=target_position)
      reverse_path_class_value = determine_path_class_value(array_elevations=array_elevations, current_position=target_position, target_position=current_position)
      target_current_best_path = array_paths[target_position]

      if path_class_value is not None :
        possible_directions.append({
            "direction" : direction
          , "target_position" : target_position
          , "path_class_value" : path_class_value
          , "reverse_path_class_value" : reverse_path_class_value
          , "direction_tuple" : direction_tuple
          , "target_current_best_path" : target_current_best_path
        })
  return possible_directions

def retrieve_array_path(array_input: numpy.array, start_position: tuple, end_position: tuple, path: list) :
  array_path = numpy.empty_like(array_input, dtype=str)
  array_path[:, :] = "."
  for x in range(len(path) - 1) :
    relative_direction = tuple(numpy.sign(numpy.subtract(path[x + 1], path[x])))
    if relative_direction == (1,0) :
      array_path[path[x]] = "v"
    elif relative_direction == (-1,0) :
      array_path[path[x]] = "^"
    elif relative_direction == (0,1) :
      array_path[path[x]] = ">"
    elif relative_direction == (0,-1) :
      array_path[path[x]] = "<"
  array_path[start_position] = "S"
  array_path[end_position] = "E"

  return array_path

def check_routes_recursively(direction_mapping: dict, array_visited: numpy.array, array_elevations: numpy.array, array_paths: numpy.array, current_position: tuple, current_path: list, escape_count: int) :
  escape_count += 1
  if escape_count > 10000 : 
    return array_visited, array_paths
  array_visited[current_position] = 1
  if array_paths[current_position] is not None :
    current_path = array_paths[current_position]
    
  possible_directions = determine_possible_directions(direction_mapping=direction_mapping, array_elevations=array_elevations, array_paths=array_paths, current_position=current_position)
  unvisited_positions = [direction["target_position"] for direction in possible_directions if array_visited[direction["target_position"]] == 0]
  
  # Update visited options
  visited_options = [direction for direction in possible_directions if (direction["reverse_path_class_value"] is not None) & (direction["target_current_best_path"] is not None)]
  # print("visited_options")
  # print(visited_options)
  for visited_option in visited_options :
    if len(current_path) - 1 > len(visited_option["target_current_best_path"]) :
      # print("Updating current path from:")
      # print(current_path)
      current_path = visited_option["target_current_best_path"] + [current_position]
      # print("to:")
      # print(current_path)
    elif len(current_path) + 1 < len(visited_option["target_current_best_path"]) :
      array_paths[visited_option["target_position"]] = current_path.copy() + [visited_option["target_position"]]

  array_paths[current_position] = current_path

  for unvisited_position in unvisited_positions :
    unvisited_path = current_path.copy() + [unvisited_position]
    array_visited, array_paths = check_routes_recursively(direction_mapping=direction_mapping, array_visited=array_visited, array_elevations=array_elevations, array_paths=array_paths, current_position=unvisited_position, current_path=unvisited_path, escape_count=escape_count)

  return array_visited, array_paths

def update_array_paths(direction_mapping: dict, array_elevations: numpy.array, start_position: tuple, array_paths: numpy.array) :

  positions_to_check = []

  array_visited = numpy.zeros_like(array_paths, dtype=int)

  current_position = start_position
  current_path = [current_position]
  
  positions_to_check.append(current_position)

  x = 0
  while len(positions_to_check) > 0 and x < 50000 :
    current_position = positions_to_check.pop(-1)
    array_visited[current_position] = 1
    if array_paths[current_position] is not None :
      current_path = array_paths[current_position].copy()

    possible_directions = determine_possible_directions(direction_mapping=direction_mapping, array_elevations=array_elevations, array_paths=array_paths, current_position=current_position)
    
    # Update current path using visited directions
    visited_directions = [direction for direction in possible_directions if (direction["reverse_path_class_value"] is not None) & (direction["target_current_best_path"] is not None)]

    for visited_direction in visited_directions :
      if len(current_path) - 1 > len(visited_direction["target_current_best_path"]) :
        current_path = visited_direction["target_current_best_path"] + [current_position]
    array_paths[current_position] = current_path.copy()

    # Update best path for possible directions
    for possible_direction in possible_directions :
      if possible_direction["target_current_best_path"] is None \
        or len(current_path) + 1 < len(possible_direction["target_current_best_path"]) :
        array_paths[possible_direction["target_position"]] = current_path.copy() + [possible_direction["target_position"]]

    # Update unvisited directions and add to positions to check
    unvisited_directions = [direction for direction in possible_directions if array_visited[direction["target_position"]] == 0]
    for unvisited_direction in unvisited_directions :
      positions_to_check.append(unvisited_direction["target_position"])

  return array_paths

######################
## Part 1

def part_1(input_file: str, output_file: str = "") :

  array_input = parse_input(input_file)
  direction_mapping = retrieve_direction_mapping()

  start_position = find_positions_in_array(array_input=array_input, input_char="S")[0]
  end_position = find_positions_in_array(array_input=array_input, input_char="E")[0]

  array_elevations = retrieve_array_elevations(array_input=array_input, start_position=start_position, end_position=end_position)
  array_paths = numpy.empty_like(array_input, dtype=list)

  array_size = array_paths.size
  for x in range(array_size) :
    print(f"Running {x + 1} / {array_size}")
    previous_array_paths = array_paths.copy()
    array_paths = update_array_paths(direction_mapping=direction_mapping, array_elevations=array_elevations, start_position=start_position, array_paths=array_paths)
    if numpy.array_equal(previous_array_paths, array_paths) :
      break

  current_path = array_paths[end_position]

  # print("-------")
  # print(array_paths)
  # print(current_path)
  # Write array positions into text
  if len(output_file) > 0 :
    array_path = retrieve_array_path(array_input=array_input, start_position=start_position, end_position=end_position, path=current_path)
    numpy.savetxt(output_file, array_path, delimiter="", fmt="%s")
    
  # print("------")
  # print(x)
  # print(current_path)
  path_length = len(current_path) - 1
  return path_length

part_1(input_file="12/sample_input.txt", output_file = "12/sample_output_visualised.txt")
part_1(input_file="12/input.txt", output_file = "12/output_visualised.txt")

######################
## Part 2

def part_2(input_file: str) :

  array_input = parse_input(input_file)
  direction_mapping = retrieve_direction_mapping()

  start_position = find_positions_in_array(array_input=array_input, input_char="S")[0]
  end_position = find_positions_in_array(array_input=array_input, input_char="E")[0]

  array_elevations = retrieve_array_elevations(array_input=array_input, start_position=start_position, end_position=end_position)
  
  possible_starting_locations = []
  array_shape = numpy.shape(array_elevations)
  for x in range(array_shape[0]) :
    for y in range(array_shape[1]) :
      if array_elevations[(x, y)] == "a" :
        possible_starting_locations.append((x, y))
  
  possible_starting_location_objects = []

  for possible_starting_location in possible_starting_locations :
    array_paths = numpy.empty_like(array_input, dtype=list)

    array_size = array_paths.size
    for x in range(array_size) :
      previous_array_paths = array_paths.copy()
      array_paths = update_array_paths(direction_mapping=direction_mapping, array_elevations=array_elevations, start_position=possible_starting_location, array_paths=array_paths.copy())
      if numpy.array_equal(previous_array_paths, array_paths) :
        break

    if array_paths[end_position] is not None :
      current_path = array_paths[end_position].copy()

      path_length = len(current_path) - 1
      possible_starting_location_objects.append({
          "possible_starting_location" : possible_starting_location
        , "path_length" : path_length
      })

  return pandas.DataFrame(data=possible_starting_location_objects).sort_values(by="path_length", ascending=True)

part_2(input_file="12/sample_input.txt")
part_2(input_file="12/input.txt")