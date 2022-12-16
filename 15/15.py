
######################
## Imports

import numpy
import pandas

######################
## Functions

def parse_input(input_file: str) :
  
  # Ingest file into dataframe
  df_input = pandas.read_csv(input_file, header=None, names=["sensor_input", "closest_beacon_input"], sep=":")

  # Parse input strings to coords
  df_input["sensor_coords"] = df_input.apply(lambda x: tuple([int(y.split("=")[-1]) for y in x["sensor_input"].split(", ")]), axis=1)
  df_input["closest_beacon_coords"] = df_input.apply(lambda x: tuple([int(y.split("=")[-1]) for y in x["closest_beacon_input"].split(", ")]), axis=1)
  df_input["sensor_coord_x"] = df_input["sensor_coords"].str[0]
  df_input["sensor_coord_y"] = df_input["sensor_coords"].str[1]

  return df_input

def calculate_manhattan_distance(tuple_coords_1: tuple, tuple_coords_2: tuple) :
  manhattan_distance = sum(tuple(numpy.absolute(tuple(numpy.subtract(tuple_coords_1, tuple_coords_2)))))
  return manhattan_distance

def retrieve_coords_within_manhattan_distance(tuple_sensor_coords: tuple, manhattan_distance: int, list_coords: list) :
  coords_within_distance = [tuple_coord for tuple_coord in list_coords if (calculate_manhattan_distance(tuple_sensor_coords, tuple_coord) <= manhattan_distance) and (tuple_coord != tuple_sensor_coords)]

  return coords_within_distance

def enhance_input(df_input: pandas.DataFrame) :

  df_input_enhanced = df_input.copy()
  df_input_enhanced["manhattan_distance"] = df_input_enhanced.apply(lambda x: calculate_manhattan_distance(x["sensor_coords"], x["closest_beacon_coords"]), axis=1)

  list_sensor_coords = df_input_enhanced["sensor_coords"].unique().tolist()
  list_beacon_coords = df_input_enhanced["closest_beacon_coords"].unique().tolist()
  
  df_input_enhanced["sensors_in_range"] = df_input_enhanced.apply(lambda x: retrieve_coords_within_manhattan_distance(x["sensor_coords"], x["manhattan_distance"], list_sensor_coords), axis=1)
  df_input_enhanced["beacons_in_range"] = df_input_enhanced.apply(lambda x: retrieve_coords_within_manhattan_distance(x["sensor_coords"], x["manhattan_distance"], list_beacon_coords), axis=1)

  return df_input_enhanced

def determine_viewed_spaces_x_range_on_specific_y_coord(tuple_origin_x_coord: int, manhattan_distance: int, manhattan_distance_to_specific_y_coord: int, x_coord_boundary_min: int = None, x_coord_boundary_max: int = None) :
  if manhattan_distance_to_specific_y_coord <= manhattan_distance :
    min_x = tuple_origin_x_coord - (manhattan_distance - manhattan_distance_to_specific_y_coord)
    max_x = tuple_origin_x_coord + (manhattan_distance - manhattan_distance_to_specific_y_coord)
    
    if x_coord_boundary_min is not None and x_coord_boundary_max is not None :
      min_x = max(min_x, x_coord_boundary_min)
      max_x = min(max_x, x_coord_boundary_max)

    result = [min_x, max_x]
  else :
    result = None

  return result

def combine_ranges(list_ranges: list) :
  list_output = []
  if len(list_ranges) > 0 :
    current_min = list_ranges[0][0]
    current_max = list_ranges[0][1]
    for x in range(1, len(list_ranges)):
      if list_ranges[x][0] <= current_max + 1 :
        current_max = max(current_max, list_ranges[x][1])
      else :
        list_output.append([current_min, current_max])
        current_min = list_ranges[x][0]
        current_max = list_ranges[x][1]
    list_output.append([current_min, current_max])
  return list_output

def determine_identified_spaces_for_specific_y_coord(df_input_enhanced: pandas.DataFrame, specific_y_coord: int, x_coord_boundary_min: int = None, x_coord_boundary_max: int = None) :

  list_sensors_in_range_on_y_coord = df_input_enhanced[df_input_enhanced["sensor_coord_y"] == specific_y_coord]["sensor_coords"].unique().tolist()
  list_beacons_in_range_on_y_coord = df_input_enhanced[df_input_enhanced["closest_beacon_coords"].str[1] == specific_y_coord]["closest_beacon_coords"].unique().tolist()

  list_identified_spaces_within_boundary = list_sensors_in_range_on_y_coord + list_beacons_in_range_on_y_coord
  if x_coord_boundary_min is not None and x_coord_boundary_max  is not None :
    list_identified_spaces_within_boundary = [x for x in list_identified_spaces_within_boundary if x_coord_boundary_min <= x[0] <= x_coord_boundary_max]

  return list_identified_spaces_within_boundary

def determine_viewed_spaces_x_ranges_for_specific_y_coord(df_input_enhanced: pandas.DataFrame, specific_y_coord: int, x_coord_boundary_min: int = None, x_coord_boundary_max: int = None) :
  df_for_specific_coord = df_input_enhanced.copy()[["sensor_coord_x", "sensor_coord_y", "manhattan_distance"]]
  
  df_for_specific_coord["manhattan_distance_to_specific_y_coord"] = df_for_specific_coord.apply(lambda x: calculate_manhattan_distance(tuple((0, x["sensor_coord_y"])), tuple((0, specific_y_coord))), axis=1)
  
  df_for_specific_coord["viewed_spaces_x_range_on_specific_y_coord"] = df_for_specific_coord.apply(lambda x: determine_viewed_spaces_x_range_on_specific_y_coord(x["sensor_coord_x"], x["manhattan_distance"], x["manhattan_distance_to_specific_y_coord"], x_coord_boundary_min, x_coord_boundary_max), axis=1)

  list_viewed_spaces_x_ranges_on_specific_y_coord = combine_ranges(list_ranges=df_for_specific_coord[df_for_specific_coord["viewed_spaces_x_range_on_specific_y_coord"].notna()]["viewed_spaces_x_range_on_specific_y_coord"].sort_values().tolist())

  return list_viewed_spaces_x_ranges_on_specific_y_coord

def determine_known_spaces_for_specific_y_coord(df_input_enhanced: pandas.DataFrame, specific_y_coord: int, x_coord_boundary_min: int = None, x_coord_boundary_max: int = None) :

  list_viewed_spaces_x_ranges_on_specific_y_coord = determine_viewed_spaces_x_ranges_for_specific_y_coord(df_input_enhanced=df_input_enhanced, specific_y_coord=specific_y_coord, x_coord_boundary_min=x_coord_boundary_min, x_coord_boundary_max=x_coord_boundary_max) 

  count_viewed_spaces_on_specific_y_coord = sum([x[1]-x[0] for x in list_viewed_spaces_x_ranges_on_specific_y_coord])

  # Adjustment to include 0th index
  if list_viewed_spaces_x_ranges_on_specific_y_coord[0][0] < 0 and list_viewed_spaces_x_ranges_on_specific_y_coord[-1][1] >= 0 :
    count_viewed_spaces_on_specific_y_coord += 1

  list_identified_spaces_in_range_on_y_coord = determine_identified_spaces_for_specific_y_coord(df_input_enhanced=df_input_enhanced, specific_y_coord=specific_y_coord, x_coord_boundary_min=x_coord_boundary_min, x_coord_boundary_max=x_coord_boundary_max) 
  
  return count_viewed_spaces_on_specific_y_coord - len(list_identified_spaces_in_range_on_y_coord)


def locate_unknown_location(df_input_enhanced: pandas.DataFrame, coord_boundary_min: int, coord_boundary_max: int) :
  
  y_min = max(df_input_enhanced["sensor_coord_y"].min(), coord_boundary_min)
  y_max = min(df_input_enhanced["sensor_coord_y"].max(), coord_boundary_max)
  x_min = max(df_input_enhanced["sensor_coord_x"].min(), coord_boundary_min)
  x_max = min(df_input_enhanced["sensor_coord_x"].max(), coord_boundary_max)

  print("---------------")
  print(f"y_min: {y_min}")
  print(f"y_max: {y_max}")
  print(f"x_min: {x_min}")
  print(f"x_max: {x_max}")

  for specific_y_coord in range(y_min, y_max+1) :
    print(f"Checking y coord {specific_y_coord} / {y_max + 1}")
    viewed_spaces_x_ranges_for_specific_y_coord = determine_viewed_spaces_x_ranges_for_specific_y_coord(df_input_enhanced=df_input_enhanced, specific_y_coord=specific_y_coord, x_coord_boundary_min=x_min, x_coord_boundary_max=x_max)
    if len(viewed_spaces_x_ranges_for_specific_y_coord) > 1 :
      print(f"Found unviewed space on row {specific_y_coord}")
      unknown_x_location = viewed_spaces_x_ranges_for_specific_y_coord[0][1] + 1
      print(f"unknown_x_location: {unknown_x_location}")

      unknown_location = tuple((unknown_x_location, specific_y_coord))
      print(f"unknown_location: {unknown_location}") 

      break
 
  return unknown_location

######################
## Part 1

def part_1(input_file: str, specific_y_coord: int) :

  df_input = parse_input(input_file)
  df_input_enhanced = enhance_input(df_input=df_input)

  result = determine_known_spaces_for_specific_y_coord(df_input_enhanced=df_input_enhanced, specific_y_coord=specific_y_coord)
  return result

part_1(input_file="15/sample_input.txt", specific_y_coord=10)
part_1(input_file="15/input.txt", specific_y_coord=2000000)

######################
## Part 2

def part_2(input_file: str, coord_boundary_min: int, coord_boundary_max: int) :

  df_input = parse_input(input_file)
  df_input_enhanced = enhance_input(df_input=df_input)

  unknown_location = locate_unknown_location(df_input_enhanced=df_input_enhanced, coord_boundary_min=coord_boundary_min, coord_boundary_max=coord_boundary_max)

  tuning_frequency = (unknown_location[0]*4000000) + unknown_location[1]
  return tuning_frequency

part_2(input_file="15/sample_input.txt", coord_boundary_min=0, coord_boundary_max=4000000)
part_2(input_file="15/input.txt", coord_boundary_min=0, coord_boundary_max=4000000)
