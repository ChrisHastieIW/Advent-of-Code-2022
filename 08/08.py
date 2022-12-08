
# Import modules
import numpy
from functools import reduce

# Determine input file location
input_file = "08\input.txt"

# Ingest input file into text
with open(input_file, 'r') as f:
  input_list = f.read().splitlines()

# Convert to numpy array
array_trees = numpy.array([[int(y) for y in list(x)] for x in input_list])

# Investigate input
print(array_trees)

###########
## Part 1

(max_x, max_y) = array_trees.shape

# Empty arrays as placeholder
array_visible_trees = numpy.empty([max_x, max_y])
array_scenic_score = numpy.empty([max_x, max_y])

def view_distance(ordered_height_list: list, focus_tree_height: int) :
  return next((index + 1 for index, item in enumerate(ordered_height_list) if item >= focus_tree_height), len(ordered_height_list))

for x in range(max_x) :
  for y in range(max_y) :
    if x in [0, max_x - 1] or y in [0, max_y - 1] :
      array_visible_trees[x, y] = 1
    else :    
      focus_tree_height = array_trees[x, y]

      ## Part 1

      west_slice = array_trees[[x], :y]
      east_slice = array_trees[[x], y+1:]
      north_slice = array_trees[:x, [y]]
      south_slice = array_trees[x+1:, [y]]

      max_tree_height = max(north_slice.max(), east_slice.max(), south_slice.max(), west_slice.max())

      north_visible_flag = (focus_tree_height > north_slice.max())
      east_visible_flag = (focus_tree_height > east_slice.max())
      south_visible_flag = (focus_tree_height > south_slice.max())
      west_visible_flag = (focus_tree_height > west_slice.max())
      visible_flag = north_visible_flag or east_visible_flag or south_visible_flag or west_visible_flag 

      array_visible_trees[x, y] = int(visible_flag)
      
      ## Part 2

      north_ordered_height_list = [x for [x] in north_slice.tolist()]
      north_ordered_height_list.reverse()
      east_ordered_height_list = east_slice.tolist()[0]
      south_ordered_height_list = [x for [x] in south_slice.tolist()]
      west_ordered_height_list = west_slice.tolist()[0]
      west_ordered_height_list.reverse()

      view_distances = []
      for ordered_height_list in [north_ordered_height_list, east_ordered_height_list, south_ordered_height_list, west_ordered_height_list] :
        view_distances.append(view_distance(ordered_height_list=ordered_height_list, focus_tree_height=focus_tree_height))
  
      scenic_score = reduce(lambda x, y: x*y, view_distances)
      array_scenic_score[x, y] = scenic_score

###########
## Part 1

print(array_visible_trees)

int(numpy.count_nonzero(array_visible_trees))

###########
## Part 2

print(array_scenic_score)

int(array_scenic_score.max())
