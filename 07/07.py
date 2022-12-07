
# Import modules
import numpy
import pandas

# Determine input file location
input_file = "07\input.txt"

# Ingest input file into text
with open(input_file, 'r') as f:
  input_list = f.read().splitlines()

# Investigate input text
print(input_list)

# Convert input list into dict
current_path_list = []
current_command = ""
directory = []

# Append initial root
directory.append({"directory": "/", "path" : "/", "type" : "dir", "name" : "root", "size" : None, "path_depth" : 0})

for console_line in input_list :
  console_list = console_line.split()
  if console_list[0] == "$" :
    current_command = console_list[1]
    if current_command == "cd" :
      target_dir = console_list[2]
      if target_dir == "/" :
        current_path_list = []
      elif target_dir == ".." :
        current_path_list.pop()
      else :
        current_path_list.append(target_dir)
  else :
    object_size = None
    if console_list[0] == "dir" : 
      object_type = "dir"
    else :
      object_type = "file"
      object_size = int(console_list[0])
    object_name = console_list[1]
    if current_path_list == [] :
      object_directory = "/"
      object_path = "/" + object_name
    else :  
      object_directory = "/" + "/".join(current_path_list)
      object_path = object_directory + "/" + object_name
    object_path_depth = object_path.count("/")
    file_object = {"directory": object_directory, "path" : object_path, "type" : object_type, "name" : object_name, "size" : object_size, "path_depth" : object_path_depth}
    directory.append(file_object)
  
# Investigate
print(directory)

# Ingest data into dataframe
df_directory = pandas.DataFrame(data=directory)
df_directory.drop_duplicates()

# Investigate
print(df_directory.sort_values(by="path"))

df_directories = df_directory[df_directory["type"] == "dir"]
df_files = df_directory[df_directory["type"] == "file"]

# Investigate
print(df_directories.sort_values(by="path"))
print(df_files.sort_values(by="path"))

# Aggregate files to determine size per directory
df_agg_file_sizes = df_files.groupby(by="directory", as_index=False).sum("size")[["directory", "size"]]

print(df_agg_file_sizes.sort_values(by="directory"))

df_directory_sizes = df_directories.merge(df_agg_file_sizes.add_prefix("file_"), how="left", left_on="path", right_on="file_directory")[["directory", "path", "type", "name", "path_depth", "file_size"]]
df_directory_sizes["file_size"] = df_directory_sizes["file_size"].fillna(0)
df_directory_sizes["child_dirs_size"] = 0
df_directory_sizes["dir_size"] = df_directory_sizes.apply(lambda x : x["file_size"] + x["child_dirs_size"], 1)

max_depth = df_directory_sizes["path_depth"].max()

# Iterate through for file sizes
for x in reversed(range(max_depth)) :
  print(x)
  if x + 1 == max_depth :
    df_child_dir_sizes = df_directory_sizes[df_directory_sizes["path_depth"] == x + 1] \
      .groupby(by="directory", as_index=False)\
      .sum("file_size")\
      [["directory", "file_size"]]
  else :
    df_child_dir_sizes = df_directory_sizes[df_directory_sizes["path_depth"] == x + 1]\
      .groupby(by="directory", as_index=False)\
      .sum("dir_size")\
      [["directory", "dir_size"]]
  df_child_dir_sizes.columns = ["join_directory", "new_child_dirs_size"]
  df_tmp_directory_sizes = df_directory_sizes.merge(df_child_dir_sizes, how="left", left_on="path", right_on="join_directory")
  df_tmp_directory_sizes["child_dirs_size"] = numpy.where(df_tmp_directory_sizes["new_child_dirs_size"].notna(), df_tmp_directory_sizes["new_child_dirs_size"], df_tmp_directory_sizes["child_dirs_size"])
  df_tmp_directory_sizes["dir_size"] = df_tmp_directory_sizes.apply(lambda x : x["file_size"] + x["child_dirs_size"], 1)
  df_directory_sizes = df_tmp_directory_sizes[["directory", "path", "type", "name", "path_depth", "file_size", "child_dirs_size", "dir_size"]]

print(df_directory_sizes.sort_values(by="directory"))

###########
## Part 1

df_directory_sizes[df_directory_sizes["dir_size"] <= 100000]["dir_size"].sum()

###########
## Part 2

used_space = df_directory_sizes[df_directory_sizes["name"] == "root"]["dir_size"].max()

disk_space = 70000000
required_space = 30000000

spillover_space = used_space - (disk_space - required_space)

df_directory_sizes[df_directory_sizes["dir_size"] >= spillover_space]["dir_size"].min()
