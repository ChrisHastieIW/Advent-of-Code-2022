
######################
## Imports

import numpy
import pandas

######################
## Functions

def parse_input(input_file: str) :
  
  # Ingest file into dataframe
  df_input = pandas.read_csv(input_file, names=["x", "y", "z"])

  return df_input

def generate_array_plot(df_input: pandas.DataFrame) :

  # Have to adjust for additional empty space as
  # input has entries in the 0th place
  array_plot = numpy.zeros((df_input["x"].max() + 3, df_input["y"].max() + 3, df_input["z"].max() + 3), dtype=int)

  for index, row in df_input.iterrows() :
    array_plot[(row["x"]+1, row["y"]+1, row["z"]+1)] = 1

  return array_plot

def determine_surface_area(df_input: pandas.DataFrame, array_plot: numpy.array) :
  total = 0
  for index, row in df_input.iterrows():
    # Have to adjust for additional empty space as
    # input has entries in the 0th place, thus adding 1 to coords
    position_tuple = tuple((row["x"]+1, row["y"]+1, row["z"]+1))

    position_x1 = tuple(numpy.add(position_tuple, tuple((1, 0, 0))))
    position_x2 = tuple(numpy.add(position_tuple, tuple((-1, 0, 0))))
    position_y1 = tuple(numpy.add(position_tuple, tuple((0, 1, 0))))
    position_y2 = tuple(numpy.add(position_tuple, tuple((0, -1, 0))))
    position_z1 = tuple(numpy.add(position_tuple, tuple((0, 0, 1))))
    position_z2 = tuple(numpy.add(position_tuple, tuple((0, 0, -1))))

    total += int(array_plot[position_x1] == 0)
    total += int(array_plot[position_x2] == 0)
    total += int(array_plot[position_y1] == 0)
    total += int(array_plot[position_y2] == 0)
    total += int(array_plot[position_z1] == 0)
    total += int(array_plot[position_z2] == 0)
  return total

def determine_external_surface_area(array_plot: numpy.array) :
  
  '''
  Value map:
  0 - Air with status unidentified
  1 - Lava
  2 - Air identified as external to lava droplet
  '''
  
  array_plot_external_search = array_plot.copy()

  shape_array_plot = numpy.shape(array_plot_external_search)
  
  # First iteration loop to map all easy targets
  for x in range(1, shape_array_plot[0] - 1) :
    for y in range(1, shape_array_plot[1] - 1) :
      for z in range(1, shape_array_plot[2] - 1) :
        position_tuple = tuple((x, y, z))

        # Check if the space is empty
        if array_plot_external_search[position_tuple] == 0 :

          # Check if there is access to the outside
          # and flag as an external cell if so
          if (
              (int(numpy.max(array_plot_external_search[x:, y, z]) == 0))
            | (int(numpy.max(array_plot_external_search[:x+1, y, z]) == 0))
            | (int(numpy.max(array_plot_external_search[x, y:, z]) == 0))
            | (int(numpy.max(array_plot_external_search[x, :y+1, z]) == 0))
            | (int(numpy.max(array_plot_external_search[x, y, z:]) == 0))
            | (int(numpy.max(array_plot_external_search[x, y, :z+1]) == 0))
          ) :

            array_plot_external_search[position_tuple] = 2

  # Set outer boundaries to 2
  array_plot_external_search[0, :, :] = 2
  array_plot_external_search[-1, :, :] = 2
  array_plot_external_search[:, 0, :] = 2
  array_plot_external_search[:, -1, :] = 2
  array_plot_external_search[:, :, 0] = 2
  array_plot_external_search[:, :, -1] = 2
  
  # Subsequent iteration loops to map all remaining air gaps
  iterator_stop_flag = False
  while iterator_stop_flag == False:
    total_external_spaces_start_count = numpy.count_nonzero(array_plot_external_search[array_plot_external_search==2])
    for x in range(1, shape_array_plot[0] - 1) :
      for y in range(1, shape_array_plot[1] - 1) :
        for z in range(1, shape_array_plot[2] - 1) :
          position_tuple = tuple((x, y, z))

          # Check if the space is identified as external
          if array_plot_external_search[position_tuple] == 2 :
            # Determine position of adjacent spaces
            position_x1 = tuple(numpy.add(position_tuple, tuple((1, 0, 0))))
            position_x2 = tuple(numpy.add(position_tuple, tuple((-1, 0, 0))))
            position_y1 = tuple(numpy.add(position_tuple, tuple((0, 1, 0))))
            position_y2 = tuple(numpy.add(position_tuple, tuple((0, -1, 0))))
            position_z1 = tuple(numpy.add(position_tuple, tuple((0, 0, 1))))
            position_z2 = tuple(numpy.add(position_tuple, tuple((0, 0, -1))))

            # Flag any adjacent air spaces as external
            if array_plot_external_search[position_x1] == 0 : 
              array_plot_external_search[position_x1] = 2
            if array_plot_external_search[position_x2] == 0 : 
              array_plot_external_search[position_x2] = 2
            if array_plot_external_search[position_y1] == 0 : 
              array_plot_external_search[position_y1] = 2
            if array_plot_external_search[position_y2] == 0 : 
              array_plot_external_search[position_y2] = 2
            if array_plot_external_search[position_z1] == 0 : 
              array_plot_external_search[position_z1] = 2
            if array_plot_external_search[position_z2] == 0 : 
              array_plot_external_search[position_z2] = 2
          
          # Check if the space is not yet identified
          elif array_plot_external_search[position_tuple] == 0 :
            # Determine position of adjacent spaces
            position_x1 = tuple(numpy.add(position_tuple, tuple((1, 0, 0))))
            position_x2 = tuple(numpy.add(position_tuple, tuple((-1, 0, 0))))
            position_y1 = tuple(numpy.add(position_tuple, tuple((0, 1, 0))))
            position_y2 = tuple(numpy.add(position_tuple, tuple((0, -1, 0))))
            position_z1 = tuple(numpy.add(position_tuple, tuple((0, 0, 1))))
            position_z2 = tuple(numpy.add(position_tuple, tuple((0, 0, -1))))

            # Flag the space as external if it is adjacent to external
            if array_plot_external_search[position_x1] == 2 \
              or array_plot_external_search[position_x2] == 2 \
              or array_plot_external_search[position_y1] == 2 \
              or array_plot_external_search[position_y2] == 2 \
              or array_plot_external_search[position_z1] == 2 \
              or array_plot_external_search[position_z2] == 2 :
                array_plot_external_search[position_tuple] = 2

    total_external_spaces_end_count = numpy.count_nonzero(array_plot_external_search[array_plot_external_search==2])

    if total_external_spaces_start_count == total_external_spaces_end_count :
      iterator_stop_flag = True

  total = 0

  # Now iterate over lava droplets to sum external faces
  for x in range(1, shape_array_plot[0] - 1) :
    for y in range(1, shape_array_plot[1] - 1) :
      for z in range(1, shape_array_plot[2] - 1) :
        position_tuple = tuple((x, y, z))
        
        # Final process to add up external faces
        if array_plot_external_search[position_tuple] == 1 :

          # Determine position of adjacent spaces
          position_x1 = tuple(numpy.add(position_tuple, tuple((1, 0, 0))))
          position_x2 = tuple(numpy.add(position_tuple, tuple((-1, 0, 0))))
          position_y1 = tuple(numpy.add(position_tuple, tuple((0, 1, 0))))
          position_y2 = tuple(numpy.add(position_tuple, tuple((0, -1, 0))))
          position_z1 = tuple(numpy.add(position_tuple, tuple((0, 0, 1))))
          position_z2 = tuple(numpy.add(position_tuple, tuple((0, 0, -1))))

          # Add each face to the total
          total += int(array_plot_external_search[position_x1] == 2)
          total += int(array_plot_external_search[position_x2] == 2)
          total += int(array_plot_external_search[position_y1] == 2)
          total += int(array_plot_external_search[position_y2] == 2)
          total += int(array_plot_external_search[position_z1] == 2)
          total += int(array_plot_external_search[position_z2] == 2)

  return total

def main(input_file: str) :

  df_input = parse_input(input_file)
  # print(df_input)
  array_plot = generate_array_plot(df_input=df_input)
  # print(array_plot[1:-1, 1:-1, 1:-1])

  surface_area = determine_surface_area(df_input=df_input, array_plot=array_plot)
  external_surface_area = determine_external_surface_area(array_plot=array_plot)

  return surface_area, external_surface_area

######################
## Parts 1 and 2

main(input_file="18/sample_input.txt")
main(input_file="18/input.txt")


