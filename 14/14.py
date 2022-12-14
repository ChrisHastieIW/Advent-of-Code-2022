
######################
## Imports

import numpy
import pandas

######################
## Functions

def parse_input(input_file: str) :
  
  # Ingest file into list
  with open(input_file, 'r') as f:
    list_input = f.read().splitlines()

  list_cleaned = [x.split(" -> ") for x in list_input]
  list_structures = [[(int(x.split(",")[1]), int(x.split(",")[0])) for x in sub_list] for sub_list in list_cleaned]

  return list_structures

def create_array_plot(list_structures: list, floor_present: bool = False) :
  min_height = 0
  min_width = min([min(x, key=lambda tup: tup[1]) for x in list_structures], key=lambda tup: tup[1])[1] - 1
  max_height = max([max(x, key=lambda tup: tup[0]) for x in list_structures], key=lambda tup: tup[0])[0] + 3
  max_width = max([max(x, key=lambda tup: tup[1]) for x in list_structures], key=lambda tup: tup[1])[1] + 2

  array_plot = numpy.empty([max_height, max_width+max_height], dtype=str)
  array_plot[:, :] = "."

  if floor_present :
    array_plot[max_height-1:max_height, :] = "~"
  else :
    array_plot[max_height-1:max_height, :] = "-"
    array_plot[:, min_width:min_width+1] = "|"
    array_plot[:, max_width-1:max_width] = "|"

  return array_plot

def plot_structures(array_plot: numpy.array, list_structures: list) :
  for list_structure in list_structures :
    for x in range(len(list_structure) - 1) :
      starting_height = min(list_structure[x][0], list_structure[x+1][0])
      ending_height = max(list_structure[x][0], list_structure[x+1][0]) + 1
      starting_width = min(list_structure[x][1], list_structure[x+1][1])
      ending_width = max(list_structure[x][1], list_structure[x+1][1]) + 1
      array_plot[starting_height:ending_height, starting_width:ending_width] = "#"
  return array_plot

def drop_grain_of_sand(array_plot: numpy.array, tuple_starting_location: tuple) :
  tuple_current_location = tuple_starting_location
  sand_finished = False
  sand_at_rest = False
  while sand_at_rest == False and sand_finished == False :
    if array_plot[tuple(numpy.add(tuple_current_location, (1, 0)))] == "." :
      tuple_current_location = tuple(numpy.add(tuple_current_location, (1, 0)))
    elif array_plot[tuple(numpy.add(tuple_current_location, (1, -1)))] == "." :
      tuple_current_location = tuple(numpy.add(tuple_current_location, (1, -1)))
    elif array_plot[tuple(numpy.add(tuple_current_location, (1, 1)))] == "." :
      tuple_current_location = tuple(numpy.add(tuple_current_location, (1, 1)))
    elif array_plot[tuple(numpy.add(tuple_current_location, (1, -1)))] in ("|", "-") \
      or array_plot[tuple(numpy.add(tuple_current_location, (1, 1)))] in ("|", "-") :
      sand_finished = True
    else :
      array_plot[tuple_current_location] = "o"
      sand_at_rest = True
      if tuple_current_location == tuple_starting_location :
        sand_finished = True

  return array_plot, sand_finished

def drop_sand(array_plot: numpy.array, tuple_starting_location: tuple) :
  sand_finished = False
  while sand_finished == False :
    array_plot, sand_finished = drop_grain_of_sand(array_plot=array_plot, tuple_starting_location=tuple_starting_location)

  return array_plot

def main(input_file: str, output_file: str = "", floor_present: bool = False) :

  tuple_starting_location = (0, 500)
  list_structures = parse_input(input_file)

  array_plot = create_array_plot(list_structures=list_structures, floor_present=floor_present)
  array_plot = plot_structures(array_plot=array_plot, list_structures=list_structures)
  array_plot = drop_sand(array_plot=array_plot, tuple_starting_location=tuple_starting_location)

  # Write plot into text
  if len(output_file) > 0 :
    populated_widths = numpy.where((array_plot == "o") | (array_plot == "#") | (array_plot == "|"))[1]
    min_width = populated_widths.min()
    max_width = populated_widths.max() + 1
    array_populated = array_plot[:, min_width:max_width]
    numpy.savetxt(output_file, array_populated, delimiter="", fmt="%s")

  result = (array_plot=="o").sum()
  return result

######################
## Part 1

main(input_file="14/sample_input.txt", output_file="14/part_1_sample_visualised.txt")
main(input_file="14/input.txt", output_file="14/part_1_visualised.txt")

######################
## Part 2

main(input_file="14/sample_input.txt", output_file="14/part_1_sample_visualised.txt", floor_present=True)
main(input_file="14/input.txt", output_file="14/part_1_visualised.txt", floor_present=True)
