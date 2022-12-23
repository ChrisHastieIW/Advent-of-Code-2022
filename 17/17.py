
######################
## Imports

import numpy
import pandas

######################
## Functions

def parse_input(input_file: str) :
  
  # Ingest file into list
  with open(input_file, 'r') as f:
    jet_pattern = f.read()

  return jet_pattern

def retrieve_list_rock_types() :
  
  # Define empty list to populate
  list_rock_types = []
  
  '''
  Rock Type 1

  @@@@
  '''
  array_rock_type_1 = numpy.empty((1, 4), dtype="<U16")
  array_rock_type_1[:] = "@"
  list_rock_types.append(array_rock_type_1)
  
  '''
  Rock Type 2

  .@.
  @@@
  .@.
  '''
  array_rock_type_2 = numpy.empty((3, 3), dtype="<U16")
  array_rock_type_2[:] = "."
  array_rock_type_2[:, 1] = "@"
  array_rock_type_2[1, :] = "@"
  list_rock_types.append(array_rock_type_2)
  
  '''
  Rock Type 3

  ..@
  ..@
  @@@
  '''
  array_rock_type_3 = numpy.empty((3, 3), dtype="<U16")
  array_rock_type_3[:] = "."
  array_rock_type_3[:, 2] = "@"
  array_rock_type_3[2, :] = "@"
  list_rock_types.append(array_rock_type_3)
  
  '''
  Rock Type 4

  @
  @
  @
  @
  '''
  array_rock_type_4 = numpy.empty((4, 1), dtype="<U16")
  array_rock_type_4[:] = "@"
  list_rock_types.append(array_rock_type_4)
  
  '''
  Rock Type 5

  @@
  @@
  '''
  array_rock_type_5 = numpy.empty((2, 2), dtype="<U16")
  array_rock_type_5[:] = "@"
  list_rock_types.append(array_rock_type_5)

  return list_rock_types

def print_array_plot(array_plot: numpy.array) :
  print(array_plot)
  print("\n")
  for row in array_plot :
    print("".join(row))

def retrieve_initial_array_plot(initial_height: int = 1, chamber_width: int = 9) :

  array_plot = numpy.empty((initial_height, chamber_width), dtype="<U16")
  array_plot[:] = "."
  array_plot[:, 0] = "|"
  array_plot[:, -1] = "|"
  array_plot[-1, :] = "-"
  array_plot[-1, 0] = "+"
  array_plot[-1, -1] = "+"

  return array_plot

def extend_array_plot(array_plot: numpy.array, extension_height: int = 3, chamber_width: int = 9) :

  array_extension = numpy.empty((extension_height, chamber_width), dtype="<U16")
  array_extension[:] = "."
  array_extension[:, 0] = "|"
  array_extension[:, -1] = "|"

  extended_array_plot = numpy.concatenate((array_extension, array_plot))

  return extended_array_plot
  
def retrieve_array_rock_plot(array_rock_type: numpy.array, chamber_width: int = 9) :

  (rock_height, rock_width) = numpy.shape(array_rock_type)

  array_rock_plot_left = numpy.empty((rock_height, 3), dtype="<U16")
  array_rock_plot_left[:] = "."
  array_rock_plot_left[:, 0] = "|"
  
  array_rock_plot_right = numpy.empty((rock_height, chamber_width - rock_width - 3), dtype="<U16")
  array_rock_plot_right[:] = "."
  array_rock_plot_right[:, -1] = "|"

  array_rock_plot = numpy.concatenate((array_rock_plot_left, array_rock_type, array_rock_plot_right), axis=1)

  return array_rock_plot
  
def plot_rock_in_array(array_plot: numpy.array, array_rock_type: numpy.array, extension_height: int = 3) :

  chamber_width = numpy.shape(array_plot)[1]
  extended_array_plot = extend_array_plot(array_plot=array_plot, extension_height=extension_height, chamber_width=chamber_width)

  array_rock_plot = retrieve_array_rock_plot(array_rock_type=array_rock_type, chamber_width=chamber_width)

  array_plot_with_rock = numpy.concatenate((array_rock_plot, extended_array_plot))

  return array_plot_with_rock

def plot_rock_movement(array_plot: numpy.array, movement_tuple: tuple, available_values: list) :
  
  current_positions = [tuple(x) for x in numpy.argwhere(array_plot == "@").tolist()]
  new_positions = [tuple(numpy.add(position_tuple, movement_tuple)) for position_tuple in current_positions]
    
  values_to_check = [array_plot[position] for position in new_positions]

  # If values of movement's target positions are all available values
  if set(values_to_check).issubset(available_values) :
    movement_success = True
    array_plot[numpy.where(array_plot == "@")] = "."
    for new_position in new_positions :
      array_plot[new_position] = "@"
  else :
    movement_success = False

  return array_plot, movement_success
  
def confirm_rock_placement(array_plot: numpy.array, rock_counter: int) :
  
  # Confirm @ placements to solid #
  array_plot[array_plot == "@"] = rock_counter

  # Trim unrequired top space
  chamber_width = numpy.shape(array_plot)[1]
  tallest_row = numpy.where(array_plot[:, 1:chamber_width-1] != ".")[0].min() 
  array_plot = array_plot[tallest_row:, :]

  return array_plot

def plot_single_rock_journey(array_plot: numpy.array, jet_pattern: str, array_rock_type: numpy.array, available_values: list, rock_counter: int, current_jet_index: int = -1) :
  
  array_plot_in_progress = plot_rock_in_array(array_plot, array_rock_type)

  # print("---------")
  # print('''Dropping shape:''')
  # print_array_plot(array_rock_type)
  # print("---------")

  # print_array_plot(array_plot_in_progress)
  vertical_movement_success = True
  while vertical_movement_success == True :
    current_jet_index = (current_jet_index + 1) % len(jet_pattern)
    current_jet_pattern = jet_pattern[current_jet_index]
    # print(f"current_jet_pattern: {current_jet_pattern}")
    if current_jet_pattern == "<" :
      horizontal_movement_tuple = (0, -1)
    else :
      horizontal_movement_tuple = (0, 1)
    
    array_plot_in_progress, horizontal_movement_success = plot_rock_movement(array_plot=array_plot_in_progress, movement_tuple=horizontal_movement_tuple, available_values=available_values)

    vertical_movement_tuple = (1, 0)
    array_plot_in_progress, vertical_movement_success = plot_rock_movement(array_plot=array_plot_in_progress, movement_tuple=vertical_movement_tuple, available_values=available_values)

  # print_array_plot(array_plot_in_progress)
  array_plot = confirm_rock_placement(array_plot_in_progress, rock_counter=rock_counter)
  # print_array_plot(array_plot)
      
  return array_plot, current_jet_index

def plot_rocks(array_plot: numpy.array, jet_pattern: str, list_rock_types: list, rock_count: int = 10,   current_jet_index: int = -1, current_rock_type_index: int = -1) :
  
  available_values = ["@", "."]
  # blocking_values = ["#", "|", "-", "+"]

  rock_counter = 0
  while rock_counter < rock_count:
    rock_counter+=1
    current_rock_type_index = (current_rock_type_index + 1) % len(list_rock_types)
    current_array_rock_type = list_rock_types[current_rock_type_index]
    array_plot, current_jet_index = plot_single_rock_journey(array_plot=array_plot, jet_pattern=jet_pattern, array_rock_type=current_array_rock_type, available_values=available_values, current_jet_index=current_jet_index, rock_counter=rock_counter)

  return array_plot, current_rock_type_index, current_jet_index

def determine_repeating_segment_in_array(array_plot_full_loop: numpy.array) :

  found_repeating_segment = False
  
  array_repeating_segments_search = numpy.zeros_like(array_plot_full_loop, dtype=int)
  
  array_repeating_segments_search[~numpy.isin(array_plot_full_loop, [".", "|", "-", "+"])] = 1
  
  array_as_ints = array_plot_full_loop.copy()
  array_as_ints[numpy.isin(array_plot_full_loop, [".", "|", "-", "+"])] = 0
  array_as_ints = array_as_ints.astype(int)
  
  max_population_count = numpy.count_nonzero(array_repeating_segments_search, axis=1).max()

  potential_segment_boundaries_search_filter = numpy.count_nonzero(array_repeating_segments_search, axis=1) >= max_population_count - 1
  array_potential_segment_boundaries_search = array_repeating_segments_search[potential_segment_boundaries_search_filter]

  unique, counts = numpy.unique(array_potential_segment_boundaries_search, axis=0, return_counts=True)
  
  potential_segment_boundaries_search = []
  for x in range(len(unique)) :
    potential_segment_boundaries_search.append({
        "unique": unique[x]
      , "count": counts[x]
    })
  df_potential_segment_boundaries_search = pandas.DataFrame(data=potential_segment_boundaries_search).sort_values(by="count", ascending=True)
  df_potential_segment_boundaries_search = df_potential_segment_boundaries_search[df_potential_segment_boundaries_search["count"] > 3]

  for index, row in df_potential_segment_boundaries_search.iterrows():
    potential_segment_boundary = row["unique"]

    array_potential_segment_boundaries = array_plot_full_loop[numpy.all(array_repeating_segments_search == potential_segment_boundary, axis=1)]

    array_potential_segment_boundaries[numpy.isin(array_potential_segment_boundaries, [".", "|", "-", "+"])] = "0"

    list_potential_segment_boundaries_max_rock_numbers = numpy.max(array_potential_segment_boundaries.astype(int), axis=1)

    list_potential_segment_boundary_distances = []
    for x in range(len(list_potential_segment_boundaries_max_rock_numbers) - 1):
      list_potential_segment_boundary_distances.append(list_potential_segment_boundaries_max_rock_numbers[x] - list_potential_segment_boundaries_max_rock_numbers[x+1])

    # If a repeating boundary is found
    if len(set(list_potential_segment_boundary_distances)) == 1 \
      and len(list_potential_segment_boundary_distances) > 2: 
      found_repeating_segment = True
      segment_starting_rock_number = list_potential_segment_boundaries_max_rock_numbers[-1]
      
      segment_rock_count = list_potential_segment_boundary_distances[0]
      segment_boundary_row_indices = sorted(numpy.where((array_repeating_segments_search == potential_segment_boundary).all(axis=1))[0])
      segment_last_index = segment_boundary_row_indices[-1]
      segment_penultimate_index = segment_boundary_row_indices[-2]
      segment_starting_height = numpy.shape(array_repeating_segments_search)[0] - segment_last_index - 1 # Remove the floor
      segment_height = segment_last_index - segment_penultimate_index
      break

  if found_repeating_segment == True :
    segment_details = {
        "potential_segment_boundary": potential_segment_boundary
      , "segment_starting_rock_number": segment_starting_rock_number
      , "segment_rock_count": segment_rock_count
      # , "segment_boundary_row_indices": segment_boundary_row_indices
      # , "segment_last_index": segment_last_index
      # , "segment_penultimate_index": segment_penultimate_index
      , "segment_starting_height": segment_starting_height
      , "segment_height": segment_height
    }
  else :
    segment_details = None
  # numpy.shape(array_plot_full_loop[segment_penultimate_index:segment_last_index+1, :])
  # print_array_plot(array_plot_full_loop[segment_penultimate_index:segment_last_index+1, :])
  
  return found_repeating_segment, segment_details

def determine_height_of_rock_tower_old(array_plot: numpy.array, jet_pattern: str, list_rock_types: list, rock_count: int = 10) :
  
  array_plot, current_rock_type_index, current_jet_index = plot_rocks(array_plot=array_plot, jet_pattern=jet_pattern, list_rock_types=list_rock_types, rock_count=rock_count)
  # print_array_plot(array_plot)
  height = numpy.shape(array_plot)[0] - 1 # Deduct 1 to remove the floor
  
  return height

def determine_height_of_rock_tower(array_plot: numpy.array, jet_pattern: str, list_rock_types: list, rock_count: int = 10, output_file_prefix: str = "") :
  
  # Determine the number of iterations that must
  # be performed for the rock types and jet pattern
  # to both reset to the start of the list
  iterations_for_full_loop = len(list_rock_types) * len(jet_pattern)

  if rock_count < min(iterations_for_full_loop, 10000) :
    array_plot, current_rock_type_index, current_jet_index = plot_rocks(array_plot=array_plot, jet_pattern=jet_pattern, list_rock_types=list_rock_types, rock_count=rock_count)
    height = numpy.shape(array_plot)[0] - 1 # Deduct 1 to remove the floor
    if len(output_file_prefix) > 0 :
      array_output = numpy.zeros_like(array_plot, dtype=int)
      array_output[~numpy.isin(array_plot, [".", "|", "-", "+"])] = 1
      output_array_plot(array_output, f"{output_file_prefix}visualiased_output.txt")
    return height

  found_repeating_segment = False
  current_rock_type_index = -1
  current_jet_index = -1
  array_plot_full_loop = array_plot.copy()
  
  print(f"iterations_for_full_loop: {iterations_for_full_loop}")

  # Calculate plot and height for a full loop
  array_plot_full_loop, current_rock_type_index, current_jet_index = plot_rocks(array_plot=array_plot_full_loop, jet_pattern=jet_pattern, list_rock_types=list_rock_types, rock_count=iterations_for_full_loop, current_jet_index=current_jet_index, current_rock_type_index=current_rock_type_index)

  if len(output_file_prefix) > 0 :
    array_output = numpy.zeros_like(array_plot_full_loop, dtype=int)
    array_output[~numpy.isin(array_plot_full_loop, [".", "|", "-", "+"])] = 1
    output_array_plot(array_output, f"{output_file_prefix}visualiased_output.txt")

  found_repeating_segment, segment_details = determine_repeating_segment_in_array(array_plot_full_loop)
  print(f"found_repeating_segment: {found_repeating_segment}")

  if found_repeating_segment == False :
    return 0
  else :
    print("segment_details")
    print(segment_details)

  array_plot_before_repeating_segment, repeating_segment_starting_rock_type_index, repeating_segment_starting_current_jet_index = plot_rocks(array_plot=array_plot, jet_pattern=jet_pattern, list_rock_types=list_rock_types, rock_count=segment_details["segment_starting_rock_number"])

  repeating_segment_starting_rock_first_index = numpy.where(array_plot_before_repeating_segment == str(segment_details["segment_starting_rock_number"]))[0].min()
  
  array_plot_remainder_starting_state = array_plot_before_repeating_segment[:repeating_segment_starting_rock_first_index + 1, :]

  # Calculate plot and height for remainder
  rock_count_remainder = ((rock_count - segment_details["segment_starting_rock_number"]) % segment_details["segment_rock_count"])
  array_plot_remainder, current_rock_type_index, current_jet_index = plot_rocks(array_plot=array_plot_remainder_starting_state, jet_pattern=jet_pattern, list_rock_types=list_rock_types, rock_count=rock_count_remainder, current_jet_index=repeating_segment_starting_current_jet_index, current_rock_type_index=repeating_segment_starting_rock_type_index)
  
  height_remainder = numpy.shape(array_plot_remainder)[0]

  # validation
  print(f"current_rock_type_index: {repeating_segment_starting_rock_type_index}")
  print(f"current_jet_index: {repeating_segment_starting_current_jet_index}")
  print(f"rock_count_remainder: {rock_count_remainder}")
  
  if len(output_file_prefix) > 0 :
    output_array_plot(array_plot_before_repeating_segment, f"{output_file_prefix}visualiased_output_before_repeating_segment.txt")
    output_array_plot(array_plot_remainder_starting_state, f"{output_file_prefix}visualiased_output_remainder_starting_state.txt")
    output_array_plot(array_plot_remainder, f"{output_file_prefix}visualiased_output_remainder.txt")

    array_plot_segment, repeating_segment_starting_rock_type_index, repeating_segment_starting_current_jet_index = plot_rocks(array_plot=array_plot_remainder_starting_state, jet_pattern=jet_pattern, list_rock_types=list_rock_types, rock_count=segment_details["segment_rock_count"], current_jet_index=repeating_segment_starting_current_jet_index, current_rock_type_index=repeating_segment_starting_rock_type_index)
    output_array_plot(array_plot_segment, f"{output_file_prefix}visualiased_output_segment.txt")

  segment_count = int((rock_count - segment_details["segment_starting_rock_number"]) / segment_details["segment_rock_count"])
  height = segment_details["segment_starting_height"] + segment_count * (segment_details["segment_height"]) + height_remainder
    
  print(f'segment_starting_height: {segment_details["segment_starting_height"]}')
  print(f'segment_count: {segment_count}')
  print(f'segment_height: {segment_details["segment_height"]}')
  print(f'total_segments_height: {segment_count * (segment_details["segment_height"])}')
  print(f'height_remainder: {height_remainder}')
  print(f'height: {height}')

  return height

def output_array_plot(array_plot: numpy.array, output_file: str) :
  numpy.savetxt(output_file, array_plot, delimiter="", fmt="%s")

def main(input_file: str, rock_count: int, output_file_prefix: str = "") :

  jet_pattern = parse_input(input_file)
  list_rock_types = retrieve_list_rock_types()
  array_plot = retrieve_initial_array_plot()

  # old_height = determine_height_of_rock_tower_old(array_plot=array_plot, jet_pattern=jet_pattern, list_rock_types=list_rock_types, rock_count=rock_count)
  # print(f"old_height: {old_height}")
  height = determine_height_of_rock_tower(array_plot=array_plot, jet_pattern=jet_pattern, list_rock_types=list_rock_types, rock_count=rock_count, output_file_prefix=output_file_prefix)
  # print(f"new_height: {height}")

  return height

######################
## Part 1

main(input_file="17/sample_input.txt", rock_count=2022, output_file_prefix="17/sample_")
main(input_file="17/input.txt", rock_count=2022, output_file_prefix="17/")

######################
## Part 2

# Suspected repeating key: 011110110
# Suspected distance: 2681
# Answer was too low: 1540804597681
main(input_file="17/sample_input.txt", rock_count=1000000000000)
main(input_file="17/input.txt", rock_count=1000000000000, output_file_prefix="17/")
