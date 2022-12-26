
######################
## Imports

import numpy
import pandas

######################
## Functions

def parse_input(input_file: str) :
  
  # Ingest file into dataframe
  df_input = pandas.read_csv(input_file, header=None, names=["value_input", "tunnels_input"], sep=";")

  # Parse input fields
  df_input["id"] = df_input.apply(lambda x: x["value_input"].split(" ")[1], axis=1)
  df_input["flow_rate"] = df_input.apply(lambda x: int(x["value_input"].split("=")[-1]), axis=1)
  df_input["adjacent_valves"] = df_input.apply(lambda x: [y.split(" ")[-1] for y in x["tunnels_input"].split(", ")], axis=1)

  return df_input
  
def calculate_flow(total_minutes: int, flow_rate: int, minute_activated: int) :

  if minute_activated is None :
    return None
  else :
    return flow_rate * (total_minutes - minute_activated)

def build_df_valves(df_input: pandas.DataFrame) :
  
  df_valves = df_input.copy()[["id", "flow_rate", "adjacent_valves"]]
  df_valves["status"] = False
  df_valves["minute_activated"] = None
  df_valves["flow"] = None

  return df_valves

def find_shortest_route(df_valves: pandas.DataFrame, current_valve_id: str, destination_valve_id: str, current_route: list = []) :

  current_route = current_route.copy()
  route_invalid = False

  current_route.append(current_valve_id)
  if current_valve_id == destination_valve_id :
    return current_route, route_invalid

  current_valve_data = df_valves[df_valves["id"] == current_valve_id].iloc[0]
  
  if destination_valve_id in current_valve_data["adjacent_valves"] :
    current_route.append(destination_valve_id)
  else :
    possible_routes = []
    for adjacent_valve_id in current_valve_data["adjacent_valves"] :
      if adjacent_valve_id not in current_route :
        possible_route, possible_route_invalid = find_shortest_route(df_valves=df_valves, current_valve_id=adjacent_valve_id, destination_valve_id=destination_valve_id, current_route=current_route.copy())
        if possible_route_invalid == False:
          possible_routes.append(possible_route)
    if len(possible_routes) > 0 :
      current_route = min(possible_routes, key=len)
    else :
      route_invalid = True

  return current_route, route_invalid

# Stolen from stackoverflow
# https://stackoverflow.com/questions/53699012/performant-cartesian-product-cross-join-with-pandas
def cartesian_product(*arrays):
    la = len(arrays)
    dtype = numpy.result_type(*arrays)
    arr = numpy.empty([len(a) for a in arrays] + [la], dtype=dtype)
    for i, a in enumerate(numpy.ix_(*arrays)):
        arr[...,i] = a
    return arr.reshape(-1, la)
def cartesian_product_multi(*dfs):
  idx = cartesian_product(*[numpy.ogrid[:len(df)] for df in dfs])
  return pandas.DataFrame(
    numpy.column_stack([df.values[idx[:,i]] for i,df in enumerate(dfs)])
    )
      
def determine_df_shortest_routes(df_valves: pandas.DataFrame) :

  df_shortest_routes = df_valves.copy()[["id", "adjacent_valves"]]

  # Using more performant cross join from stackoverflow
  df_shortest_routes = cartesian_product_multi(*[df_shortest_routes, df_shortest_routes])
  df_shortest_routes.columns = ["id", "adjacent_valves", "target_id", "target_adjacent_valves"]

  # My original cross join
  # df_shortest_routes = df_shortest_routes.merge(df_shortest_routes.add_prefix("target_"), how="cross")[["id", "adjacent_valves", "target_id"]]
  
  df_shortest_routes["shortest_route"] = df_shortest_routes.apply(lambda x: find_shortest_route(df_valves=df_valves.copy(), current_valve_id=x["id"], destination_valve_id=x["target_id"])[0], axis=1)
  df_shortest_routes["minutes_to_activate"] = df_shortest_routes.apply(lambda x: len(x["shortest_route"]), axis=1)

  df_shortest_routes = df_shortest_routes[["id", "target_id", "minutes_to_activate"]]
  df_shortest_routes.columns=["origin_id", "target_id", "minutes_to_activate"]
  
  return df_shortest_routes

def determine_remaining_potential_flow(remaining_minutes: int, valve_flow_rate: int, minutes_to_activate: int, valve_status: bool, agent_available: bool = True) :

  if valve_status == True or agent_available == False:
    remaining_potential_flow = 0
  else :
    remaining_potential_flow = valve_flow_rate * (remaining_minutes - minutes_to_activate)
  return remaining_potential_flow

def determine_remaining_potential_flows(df_valves: pandas.DataFrame, df_shortest_routes: pandas.DataFrame, remaining_minutes: int, current_valve_id: str, identifier: str = "", agent_available: bool = True) :

  df_shortest_routes_filtered = df_shortest_routes[df_shortest_routes["origin_id"] == current_valve_id]

  current_valve_id_identifier = "current_valve_id"+identifier
  df_valves[current_valve_id_identifier] = current_valve_id

  df_valves = df_valves[["id", "flow_rate", "adjacent_valves", "status", "minute_activated", "flow", current_valve_id_identifier]]

  df_valves = df_valves.merge(df_shortest_routes_filtered.add_suffix(identifier), how="inner", left_on="id", right_on="target_id"+identifier)[["id", "flow_rate", "adjacent_valves", "status", "minute_activated", "flow", current_valve_id_identifier, "minutes_to_activate"+identifier]]

  df_valves["remaining_potential_value"+identifier] = df_valves.apply(lambda x: determine_remaining_potential_flow(remaining_minutes=remaining_minutes, valve_flow_rate=x["flow_rate"], minutes_to_activate=x["minutes_to_activate"+identifier], valve_status=x["status"], agent_available=agent_available), axis=1)
  
  return df_valves

def retrieve_df_agents(agent_count: int = 1) :
  
  list_agents = []

  for x in range(agent_count):
    list_agents.append({
          "id": str(x+1)
        , "current_valve_id": "AA"
        , "minutes_until_active" : 0
      })

  df_agents = pandas.DataFrame(data=list_agents)

  df_agents.set_index("id", inplace=True, drop=False)

  return df_agents

def determine_best_valve_order(df_valves: pandas.DataFrame, df_shortest_routes: pandas.DataFrame, total_minutes: int = 30, current_valve_id: str = "AA", remaining_minutes: int = 30) :

  current_df_valves = df_valves.copy()
  current_df_valves["flow"] = current_df_valves.apply(lambda x: calculate_flow(total_minutes=total_minutes, flow_rate=x["flow_rate"], minute_activated=x["minute_activated"]), axis=1)

  current_df_valves = determine_remaining_potential_flows(df_valves=current_df_valves, df_shortest_routes=df_shortest_routes, remaining_minutes=remaining_minutes, current_valve_id=current_valve_id)
   
  df_valves_with_remaining_potential = current_df_valves[current_df_valves["remaining_potential_value"] > 0].copy()
  
  if len(df_valves_with_remaining_potential) > 0 :

    df_valves_with_remaining_potential = df_valves_with_remaining_potential.sort_values(by="remaining_potential_value", ascending=False)

    list_indices = df_valves_with_remaining_potential.index.tolist()
    
    # Overwrite list to only look at first value
    # if it is better than all other options combined
    top_remaining_potential = df_valves_with_remaining_potential.iloc[0]["remaining_potential_value"]
    if top_remaining_potential >= (df_valves_with_remaining_potential["remaining_potential_value"].sum() - top_remaining_potential) :
      list_indices = [list_indices[0]]
      
    best_flow = 0
    df_best_approach = None
    
    for index in list_indices :
      potential_df_valves = current_df_valves.copy()

      row = df_valves_with_remaining_potential.loc[index]

      current_remaining_minutes = remaining_minutes - row["minutes_to_activate"] 

      potential_df_valves.loc[index, "status"] = True
      potential_df_valves.loc[index, "minute_activated"] = total_minutes - current_remaining_minutes 
      potential_df_valves["flow"] = potential_df_valves.apply(lambda x: calculate_flow(total_minutes=total_minutes, flow_rate=x["flow_rate"], minute_activated=x["minute_activated"]), axis=1)

      potential_df_valves = determine_best_valve_order(df_valves=potential_df_valves, df_shortest_routes=df_shortest_routes, total_minutes=total_minutes, current_valve_id=row["id"], remaining_minutes=current_remaining_minutes)
      if potential_df_valves["flow"].sum() > best_flow :
        best_flow = potential_df_valves["flow"].sum()
        df_best_approach = potential_df_valves.copy()
    current_df_valves = df_best_approach.copy()

  return current_df_valves

def retrieve_df_remaining_potential_indices(df_valves_with_remaining_potential: pandas.DataFrame, remaining_potential_value_columns: list) :
  list_remaining_potential_indices = []
  for remaining_potential_value_column in remaining_potential_value_columns :
    current_remaining_potential_indices = {
        "agent_id": remaining_potential_value_column.split("_")[-1]
      , "indices": df_valves_with_remaining_potential.sort_values(by=remaining_potential_value_column, ascending=False).index.tolist()
      , "values": df_valves_with_remaining_potential.sort_values(by=remaining_potential_value_column, ascending=False)[remaining_potential_value_column].tolist()
    }
    list_remaining_potential_indices.append(current_remaining_potential_indices)

  df_remaining_potential_indices = pandas.DataFrame(data=list_remaining_potential_indices)

  return df_remaining_potential_indices

def retrieve_df_remaining_potential_indices_pivotted(df_remaining_potential_indices: pandas.DataFrame) :

  # Pivot dataframe to expand lists
  indices = df_remaining_potential_indices["indices"].apply(pandas.Series).reset_index().melt(id_vars='index').dropna()[['index', 'value']].set_index('index')

  df_remaining_potential_indices_pivotted = pandas.merge(
      df_remaining_potential_indices
    , indices
    , left_index=True
    , right_index=True
  ).rename(columns={'value': 'remaining_potential_index'})

  df_remaining_potential_indices_pivotted["remaining_potential_value"] = df_remaining_potential_indices_pivotted.apply(lambda x : x["values"][x["indices"].index(x["remaining_potential_index"])], axis=1)

  df_remaining_potential_indices_pivotted["agent_rank"] = df_remaining_potential_indices_pivotted.groupby(by="agent_id")["remaining_potential_value"].rank(method="first", ascending=False).astype(int)
  df_remaining_potential_indices_pivotted["index_rank"] = df_remaining_potential_indices_pivotted.groupby(by="remaining_potential_index")["remaining_potential_value"].rank(method="first", ascending=False).astype(int)
  df_remaining_potential_indices_pivotted["global_rank"] = df_remaining_potential_indices_pivotted["remaining_potential_value"].rank(method="dense", ascending=False).astype(int)

  return df_remaining_potential_indices_pivotted[df_remaining_potential_indices_pivotted["remaining_potential_value"] > 0][["agent_id", "remaining_potential_index", "remaining_potential_value", "agent_rank", "index_rank", "global_rank"]]

def retrieve_df_remaining_potential_index_combinations(df_remaining_potential_indices_pivotted: pandas.DataFrame) :

  df_remaining_potential_index_combinations = None
  remaining_potential_index_columns = []
  remaining_potential_value_columns = []
  leveraged_agent_ids = []
  # print("|||||||||||||||||")
  df_remaining_potential_indices_pivotted.reset_index(drop=True, inplace=True)
  # print("Agents list:")
  # print(df_remaining_potential_indices_pivotted["agent_id"].unique().tolist())
  for agent_id in df_remaining_potential_indices_pivotted["agent_id"].unique().tolist() :
    # print(f"agent_id: {agent_id}")
    remaining_potential_index_columns.append(f"remaining_potential_index_{agent_id}")
    remaining_potential_value_columns.append(f"remaining_potential_value_{agent_id}")
    leveraged_agent_ids.append(agent_id)
    if df_remaining_potential_index_combinations is None :
      # print("New pivotted df")
      df_remaining_potential_index_combinations = df_remaining_potential_indices_pivotted[df_remaining_potential_indices_pivotted["agent_id"] == agent_id].add_suffix(f"_{agent_id}")[[f"agent_rank_{agent_id}", f"remaining_potential_index_{agent_id}", f"remaining_potential_value_{agent_id}"]]
      # print("df_remaining_potential_index_combinations")
      # print(df_remaining_potential_index_combinations)
    else :
      # print("Adding to existing df")
      # Using more performant cross join from stackoverflow
      current_df_remaining_potential_index_combinations_columns = df_remaining_potential_index_combinations.columns.tolist()
      # print("current_df_remaining_potential_index_combinations_columns")
      # print(current_df_remaining_potential_index_combinations_columns)
      df_remaining_potential_index_combinations = cartesian_product_multi(*[df_remaining_potential_index_combinations, df_remaining_potential_indices_pivotted[df_remaining_potential_indices_pivotted["agent_id"] == agent_id].add_suffix(f"_{agent_id}")[[f"agent_rank_{agent_id}", f"remaining_potential_index_{agent_id}", f"remaining_potential_value_{agent_id}"]]])
      # print("df_remaining_potential_index_combinations")
      # print(df_remaining_potential_index_combinations)
      # print("Renaming columns to :")
      # print(current_df_remaining_potential_index_combinations_columns + [f"agent_rank_{agent_id}", f"remaining_potential_index_{agent_id}", f"remaining_potential_value_{agent_id}"])
      df_remaining_potential_index_combinations.columns = current_df_remaining_potential_index_combinations_columns + [f"agent_rank_{agent_id}", f"remaining_potential_index_{agent_id}", f"remaining_potential_value_{agent_id}"]
      # print("df_remaining_potential_index_combinations")
      # print(df_remaining_potential_index_combinations)  

      # My original cross join
      # df_remaining_potential_index_combinations = df_remaining_potential_index_combinations.merge(
      #     df_remaining_potential_indices_pivotted[df_remaining_potential_indices_pivotted["agent_id"] == agent_id].add_suffix(f"_{agent_id}")[[f"agent_rank_{agent_id}", f"remaining_potential_index_{agent_id}", f"remaining_potential_value_{agent_id}"]]
      #   , how="cross"
      # )

  # print("||||||||")
  # print("remaining_potential_index_columns")
  # print(remaining_potential_index_columns)
  # print(f"index column count: {df_remaining_potential_index_combinations[remaining_potential_index_columns].count(axis=1)}")
  # print(f"index column unique count: {df_remaining_potential_index_combinations[remaining_potential_index_columns].nunique(axis=1)}")
  
  # Remove attempts to access the same index
  df_remaining_potential_index_combinations = df_remaining_potential_index_combinations[
    df_remaining_potential_index_combinations[remaining_potential_index_columns].count(axis=1)
    ==
    df_remaining_potential_index_combinations[remaining_potential_index_columns].nunique(axis=1)
  ]
  # print("df_remaining_potential_index_combinations")
  # print(df_remaining_potential_index_combinations)

  # Just take first agent if no matches found after dupe removal.
  # This would break for more than 2 agents but is fine
  # for our current requirement of 2 agents
  if len(df_remaining_potential_index_combinations) == 0 :
    # print("|||||")
    # print("Reverting to earlier combinations")
    agent_id = df_remaining_potential_indices_pivotted["agent_id"].unique().tolist()[0]
    remaining_potential_index_columns = [f"remaining_potential_index_{agent_id}"]
    remaining_potential_value_columns = [f"remaining_potential_value_{agent_id}"]
    leveraged_agent_ids = [agent_id]
    # print(f"agent_id: {agent_id}")
    df_remaining_potential_index_combinations = df_remaining_potential_indices_pivotted[df_remaining_potential_indices_pivotted["agent_id"] == agent_id].add_suffix(f"_{agent_id}")[[f"agent_rank_{agent_id}", f"remaining_potential_index_{agent_id}", f"remaining_potential_value_{agent_id}"]]

  df_remaining_potential_index_combinations["distinct_combinations"] = df_remaining_potential_index_combinations\
    .apply(lambda x: sorted([[x[index_col], x[value_col]] for [index_col, value_col] in [list(cols) for cols in zip(remaining_potential_index_columns, remaining_potential_value_columns)]]), axis=1)

  # print("||||||||---1")
  # print("df_remaining_potential_index_combinations")
  # print(df_remaining_potential_index_combinations)

  df_remaining_potential_index_combinations.drop_duplicates(subset='distinct_combinations', keep="first", inplace=True)

  df_remaining_potential_index_combinations["remaining_potential_value_total"] = df_remaining_potential_index_combinations[remaining_potential_value_columns].sum(axis=1)
  df_remaining_potential_index_combinations["combination_id"] = df_remaining_potential_index_combinations.index
  # print("||||||||---2")
  # print("df_remaining_potential_index_combinations")
  # print(df_remaining_potential_index_combinations)

  df_working_merge = df_remaining_potential_index_combinations.merge(df_remaining_potential_indices_pivotted[df_remaining_potential_indices_pivotted["index_rank"]==1][["remaining_potential_index", "remaining_potential_value"]], how="cross")
  df_working_merge["valid_flag"] = df_working_merge.apply(lambda x: x["remaining_potential_index"] not in [x[remaining_potential_index_column] for remaining_potential_index_column in remaining_potential_index_columns], axis=1)
  
  # print("||||||||---3")
  # print("df_working_merge")
  # print(df_working_merge)
  df_working_merge_aggregations = df_working_merge[df_working_merge["valid_flag"] == True].groupby(by="combination_id")["remaining_potential_value"].sum().reset_index(name="total_potential_from_other_indices")
  # print("df_working_merge_aggregations")
  # print(df_working_merge_aggregations)
  df_remaining_potential_index_combinations = df_remaining_potential_index_combinations.merge(df_working_merge_aggregations, how="left", on="combination_id")

  # print("df_remaining_potential_index_combinations")
  # print(df_remaining_potential_index_combinations)

  if len(df_remaining_potential_index_combinations[df_remaining_potential_index_combinations["remaining_potential_value_total"] >= df_remaining_potential_index_combinations["total_potential_from_other_indices"]]) > 0 :
    df_remaining_potential_index_combinations = df_remaining_potential_index_combinations[df_remaining_potential_index_combinations["remaining_potential_value_total"] >= df_remaining_potential_index_combinations["total_potential_from_other_indices"]]

  df_remaining_potential_index_combinations.drop(columns=["distinct_combinations", "combination_id", "total_potential_from_other_indices"], inplace=True)

  return df_remaining_potential_index_combinations, remaining_potential_index_columns, leveraged_agent_ids

def determine_best_valve_order_with_multiple_agents(df_valves: pandas.DataFrame, df_shortest_routes: pandas.DataFrame, df_agents: pandas.DataFrame, total_minutes: int = 26, remaining_minutes: int = 26, depth: int = 0) :

  # print("----------------------")
  # print(f"total_minutes: {total_minutes}")
  # print(f"remaining_minutes: {remaining_minutes}")

  current_df_agents = df_agents.copy()
  # print("current_df_agents")
  # print(current_df_agents)

  df_active_agents = current_df_agents[current_df_agents["minutes_until_active"] == 0].copy()
  
  # Tick over minutes where no action can be taken
  while len(df_active_agents) == 0 :
    remaining_minutes = remaining_minutes - 1
    current_df_agents["minutes_until_active"] = current_df_agents["minutes_until_active"] - 1
    df_active_agents = current_df_agents[current_df_agents["minutes_until_active"] == 0]
    # print("----------")
    # print(f"remaining_minutes: {remaining_minutes}")
    # print("current_df_agents")
    # print(current_df_agents)

  current_df_valves = df_valves.copy()
  current_df_valves["flow"] = current_df_valves.apply(lambda x: calculate_flow(total_minutes=total_minutes, flow_rate=x["flow_rate"], minute_activated=x["minute_activated"]), axis=1)

  incremental_columns = ["id", "flow_rate", "adjacent_valves", "status", "minute_activated", "flow"]
  current_df_valves = current_df_valves[incremental_columns]
  remaining_potential_value_columns = []
  remaining_potential_index_columns = []
  agent_rank_columns = []
  # print("++++++++++++++")
  # print("current_df_valves")
  # print(current_df_valves)
  for index, agent in df_active_agents.iterrows():
    # print("+++")
    # print("current_df_valves")
    # print(current_df_valves)
    identifier = agent["id"]
    current_valve_id = agent["current_valve_id"]
    agent_available = (agent["minutes_until_active"] == 0)
    agent_columns = [f"current_valve_id_{identifier}", f"minutes_to_activate_{identifier}", f"remaining_potential_value_{identifier}"]
    remaining_potential_value_columns.append(f"remaining_potential_value_{identifier}")
    remaining_potential_index_columns.append(f"remaining_potential_index_{identifier}")
    agent_rank_columns.append(f"agent_rank_{identifier}")
    df_current_agent_valves = determine_remaining_potential_flows(df_valves=current_df_valves.copy(), df_shortest_routes=df_shortest_routes, remaining_minutes=remaining_minutes, current_valve_id=current_valve_id, identifier=f"_{identifier}", agent_available=agent_available)[["id"] + agent_columns]
    incremental_columns.extend(agent_columns)
    # print("df_current_agent_valves")
    # print(df_current_agent_valves)
    # print("incremental_columns")
    # print(incremental_columns)
    current_df_valves = current_df_valves.merge(df_current_agent_valves, how="inner", left_on="id", right_on=f"id")[incremental_columns]
  
  # print("current_df_valves")
  # print(current_df_valves)

  # If rows exist with remaining potential for active agents
  if current_df_valves[remaining_potential_value_columns].max().max() > 0 :
    # print("==============")
    # print("current_df_valves")
    # print(current_df_valves)
    
    df_valves_with_remaining_potential = current_df_valves[current_df_valves[remaining_potential_value_columns].max(axis=1) > 0].copy()
    # print("df_valves_with_remaining_potential")
    # print(df_valves_with_remaining_potential)

    df_remaining_potential_indices = retrieve_df_remaining_potential_indices(df_valves_with_remaining_potential=df_valves_with_remaining_potential.copy(), remaining_potential_value_columns=remaining_potential_value_columns)
    # print("df_remaining_potential_indices")
    # print(df_remaining_potential_indices)
    
    df_remaining_potential_indices_pivotted = retrieve_df_remaining_potential_indices_pivotted(df_remaining_potential_indices=df_remaining_potential_indices)
    # print("df_remaining_potential_indices_pivotted")
    # print(df_remaining_potential_indices_pivotted)
    
    df_remaining_potential_index_combinations, remaining_potential_index_columns, leveraged_agent_ids = retrieve_df_remaining_potential_index_combinations(df_remaining_potential_indices_pivotted=df_remaining_potential_indices_pivotted)
    # print("df_remaining_potential_index_combinations")
    # print(df_remaining_potential_index_combinations)

    if depth == 1 :
      print("df_remaining_potential_index_combinations")
      print(df_remaining_potential_index_combinations)
      total_combinations_to_check = len(df_remaining_potential_index_combinations)
      print(f"Combinations to check: {total_combinations_to_check}")
      combination_counter = 0
      
    # print("df_remaining_potential_index_combinations")
    # print(df_remaining_potential_index_combinations)
    
    best_flow = 0
    df_best_approach = None
    
    for combination_index, combination_row in df_remaining_potential_index_combinations.iterrows() :
      if depth == 1 :
        combination_counter += 1
        print(f"Best flow so far: {int(best_flow)}")
        print(f"Checking combination: {combination_counter} / {total_combinations_to_check}")
      potential_df_valves = current_df_valves.copy()
      potential_df_agents = current_df_agents.copy()
      # print("***********")
      # print(f"best_flow: {best_flow}")
      # print("combination_row:")
      # print(combination_row)
      # print("current_df_valves")
      # print(current_df_valves)
      # print("potential_df_valves")
      # print(potential_df_valves)
      for agent_id in leveraged_agent_ids:
        # print(agent_id)
        valves_index = combination_row[f"remaining_potential_index_{agent_id}"]
        potential_valves_row = df_valves_with_remaining_potential.loc[valves_index]
        potential_df_valves.loc[valves_index, "status"] = True
        potential_df_valves.loc[valves_index, "minute_activated"] = total_minutes - remaining_minutes + potential_valves_row[f"minutes_to_activate_{agent_id}"]
        potential_df_agents.loc[agent_id, "minutes_until_active"] = potential_valves_row[f"minutes_to_activate_{agent_id}"]
        potential_df_agents.loc[agent_id, "current_valve_id"] = potential_valves_row[f"id"]

      potential_df_valves["flow"] = potential_df_valves.apply(lambda x: calculate_flow(total_minutes=total_minutes, flow_rate=x["flow_rate"], minute_activated=x["minute_activated"]), axis=1)
      # print("potential_df_valves")
      # print(potential_df_valves)
      potential_df_valves = determine_best_valve_order_with_multiple_agents(df_valves=potential_df_valves, df_shortest_routes=df_shortest_routes, df_agents=potential_df_agents, total_minutes=total_minutes, remaining_minutes=remaining_minutes)
      if potential_df_valves["flow"].sum() > best_flow :
        best_flow = potential_df_valves["flow"].sum()
        df_best_approach = potential_df_valves.copy()
    current_df_valves = df_best_approach.copy()
  
    if depth == 1 :
      print(f"Best flow so far: {int(best_flow)}")

  return current_df_valves

######################
## Part 1

def part_1(input_file: str) :

  df_input = parse_input(input_file=input_file)
  df_valves = build_df_valves(df_input=df_input)
  df_shortest_routes = determine_df_shortest_routes(df_valves=df_valves)
  
  df_best_valve_order = determine_best_valve_order(df_valves=df_valves, df_shortest_routes=df_shortest_routes)
  
  result = int(df_best_valve_order["flow"].sum())

  return result

part_1(input_file="16/sample_input.txt")
# part_1_result = part_1(input_file="16/input.txt")

######################
## Part 2

def part_2(input_file: str, agent_count: int = 2, shortest_routes_file: str = "", shortest_routes_read_from_file: bool = False) :

  df_input = parse_input(input_file=input_file)
  print("df_input")
  print(df_input)
  df_valves = build_df_valves(df_input=df_input)
  print("df_valves")
  print(df_valves)

  if shortest_routes_read_from_file == True and len(shortest_routes_file) > 0 :
    df_shortest_routes = pandas.read_csv(shortest_routes_file, sep="|", header=0)
  else :
    df_shortest_routes = determine_df_shortest_routes(df_valves=df_valves)
    if len(shortest_routes_file) > 0 :
      df_shortest_routes.to_csv(shortest_routes_file, sep="|", header=True, index=False)

  print("df_shortest_routes")
  print(df_shortest_routes)

  df_agents = retrieve_df_agents(agent_count=agent_count)
  print("df_agents")
  print(df_agents)
  total_minutes = 30 - 4 * (len(df_agents) - 1)
  print(f"total_minutes: {total_minutes}")
  remaining_minutes = total_minutes
  print(f"remaining_minutes: {remaining_minutes}")

  df_best_valve_order = determine_best_valve_order_with_multiple_agents(df_valves=df_valves, df_shortest_routes=df_shortest_routes, df_agents=df_agents, total_minutes=total_minutes, remaining_minutes=remaining_minutes, depth=1)
  print("@@@@@@@@@@")
  print("df_best_valve_order")
  print(df_best_valve_order)
  result = int(df_best_valve_order["flow"].sum())

  return result

part_2(input_file="16/sample_input.txt", agent_count=2)
part_2_result = part_2(input_file="16/input.txt", agent_count=2, shortest_routes_file="16/shortest_routes.txt", shortest_routes_read_from_file=True)
