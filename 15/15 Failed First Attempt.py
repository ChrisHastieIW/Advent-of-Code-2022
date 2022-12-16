
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
  df_input["sensor_coords"] = df_input.apply(lambda x: [int(y.split("=")[-1]) for y in x["sensor_input"].split(", ")], axis=1)
  df_input["sensor_coords_x"] = df_input["sensor_coords"].str[0]
  df_input["sensor_coords_y"] = df_input["sensor_coords"].str[1]
  df_input["closest_beacon_coords"] = df_input.apply(lambda x: [int(y.split("=")[-1]) for y in x["closest_beacon_input"].split(", ")], axis=1)
  df_input["closest_beacon_coords_x"] = df_input["closest_beacon_coords"].str[0]
  df_input["closest_beacon_coords_y"] = df_input["closest_beacon_coords"].str[1]
  
  # Convert coords to numpy locations
  df_input["sensor_location_height"] = df_input["sensor_coords_y"] 
  df_input["sensor_location_width"] = df_input["sensor_coords_x"] 
  df_input["sensor_location"] = df_input.apply(lambda x: (x["sensor_location_height"], x["sensor_location_width"]), axis=1)
  df_input["closest_beacon_location_height"] = df_input["closest_beacon_coords_y"] 
  df_input["closest_beacon_location_width"] = df_input["closest_beacon_coords_x"] 
  df_input["closest_beacon_location"] = df_input.apply(lambda x: (x["closest_beacon_location_height"], x["closest_beacon_location_width"]), axis=1)

  df_input["manhattan_distance"] = df_input.apply(lambda x: sum(tuple(numpy.absolute(tuple(numpy.subtract(x["sensor_location"], x["closest_beacon_location"]))))), axis=1)

  return df_input

def clean_input(df_input: pandas.DataFrame) :

  df_locations = df_input.copy()[["sensor_coords", "sensor_location", "closest_beacon_location", "manhattan_distance"]]

  return df_locations

def determine_dict_array_dimensions(df_input: pandas.DataFrame) :
  max_location_distance = df_input["manhattan_distance"].max()
  min_height = min(df_input["sensor_location_height"].min(), df_input["closest_beacon_location_height"].min()) - max_location_distance
  min_width = min(df_input["sensor_location_width"].min(), df_input["closest_beacon_location_width"].min()) - max_location_distance
  
  height_offset = abs(min(0, min_height))
  width_offset = abs(min(0, min_width))

  max_height = max(df_input["sensor_location_height"].max(), df_input["closest_beacon_location_height"].max()) + max_location_distance + height_offset + 2
  max_width = max(df_input["sensor_location_width"].max(), df_input["closest_beacon_location_width"].max()) + max_location_distance + width_offset + 2

  dict_array_dimensions = {
      "height_offset" : height_offset
    , "width_offset" : width_offset
    , "max_height" : max_height
    , "max_width" : max_width
  }

  return dict_array_dimensions

def populate_array_locations_in_dataframe(df_locations: pandas.DataFrame, dict_array_dimensions: dict) :

  df_locations["sensor_array_location"] = df_locations.apply(lambda x: tuple(numpy.add(x["sensor_location"], tuple((dict_array_dimensions["height_offset"], dict_array_dimensions["width_offset"])))), axis=1)
  df_locations["closest_beacon_array_location"] = df_locations.apply(lambda x: tuple(numpy.add(x["closest_beacon_location"], tuple((dict_array_dimensions["height_offset"], dict_array_dimensions["width_offset"])))), axis=1)

  return df_locations

def create_array_plot(dict_array_dimensions: dict) :

  array_plot = numpy.empty([dict_array_dimensions["max_height"], dict_array_dimensions["max_width"]], dtype=str)
  array_plot[:, :] = "."

  return array_plot

def plot_input_locations(array_plot: numpy.array, df_locations: pandas.DataFrame) :

  for index, row in df_locations.iterrows():
    array_plot[row["sensor_array_location"]] = "S"
    array_plot[row["closest_beacon_array_location"]] = "B"
  return array_plot

def plot_known_empty_locations(array_plot: numpy.array, df_locations: pandas.DataFrame) :

  for index, row in df_locations.iterrows():
    for x in range(-row["manhattan_distance"], row["manhattan_distance"] + 1) :
      for y in range(abs(x) - row["manhattan_distance"], row["manhattan_distance"] + 1 -abs(x)) :
        known_empty_location = tuple(numpy.add(row["sensor_array_location"], tuple((x, y))))
        if array_plot[known_empty_location] == "." :
          array_plot[known_empty_location] = "#"
  return array_plot

def output_array_plot(array_plot: numpy.array, output_file: str) :
  # Write plot into text
  # populated_widths = numpy.where((array_plot == "o") | (array_plot == "#") | (array_plot == "|"))[1]
  # min_width = populated_widths.min()
  # max_width = populated_widths.max() + 1
  # array_populated = array_plot[:, min_width:max_width]
  numpy.savetxt(output_file, array_plot, delimiter="", fmt="%s")

def main(input_file: str, y_position_to_check: int, output_file: str = "") :

  df_input = parse_input(input_file)
  df_locations = clean_input(df_input=df_input)
  dict_array_dimensions = determine_dict_array_dimensions(df_input=df_input)
  df_locations = populate_array_locations_in_dataframe(df_locations=df_locations, dict_array_dimensions=dict_array_dimensions)
  array_plot = create_array_plot(dict_array_dimensions)
  array_plot = plot_input_locations(array_plot=array_plot, df_locations=df_locations)
  array_plot = plot_known_empty_locations(array_plot=array_plot, df_locations=df_locations)

  # Write plot into text
  if len(output_file) > 0 :
    output_array_plot(array_plot=array_plot, output_file=output_file)

  result = (array_plot[y_position_to_check+dict_array_dimensions["height_offset"], :]=="#").sum()
  return result

######################
## Part 1

main(input_file="15/sample_input.txt", y_position_to_check=10, output_file="15/part_1_sample_visualised.txt")

# Fails as it attempts to allocate a 222 Tib array to memory
main(input_file="15/input.txt", y_position_to_check=2000000, output_file="15/part_1_visualised.txt")
