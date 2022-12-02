
# Import modules
import numpy
import pandas
from io import StringIO

# Determine input file location
input_file = "02\input.txt"

# Ingest file into dataframe
df_strategy_guide = pandas.read_csv(input_file, header=None, names=["opponent", "player"], sep=" ")

# Investigate dataframe
print(df_strategy_guide)
df_strategy_guide.head(15)

# Configure game mapping
game_mapping_text = '''
A|Rock|Scissors|Paper|1
B|Paper|Rock|Scissors|2
C|Scissors|Paper|Rock|3
X|Rock|Scissors|Paper|1
Y|Paper|Rock|Scissors|2
Z|Scissors|Paper|Rock|3
'''

df_game_mapping = pandas.read_csv(StringIO(game_mapping_text), names=["shape_id", "shape", "defeats", "loses_to", "score"], sep="|")

# Investigate dataframe
df_game_mapping.head(15)

# Combine mapping with strategy guide
df_strategy_guide_enhanced = df_strategy_guide.merge(df_game_mapping.add_prefix("opponent_"), how="left", left_on="opponent", right_on="opponent_shape_id")\
  .merge(df_game_mapping.add_prefix("player_"), how="left", left_on="player", right_on="player_shape_id")\
  [["opponent", "player", "opponent_shape", "player_shape", "player_defeats", "player_score"]]

# Investigate dataframe
print(df_strategy_guide_enhanced)
df_strategy_guide_enhanced.head(15)

df_strategy_guide_enhanced["result_score"] = numpy.where(
    df_strategy_guide_enhanced["player_shape"] == df_strategy_guide_enhanced["opponent_shape"]
  , 3
  , numpy.where(
      df_strategy_guide_enhanced["player_defeats"] == df_strategy_guide_enhanced["opponent_shape"]
    , 6
    , 0
  )
)

df_strategy_guide_enhanced["total_score"] = df_strategy_guide_enhanced["player_score"] + df_strategy_guide_enhanced["result_score"]

# Investigate dataframe
print(df_strategy_guide_enhanced)
df_strategy_guide_enhanced.head(15)

# Total Score
df_strategy_guide_enhanced["total_score"].sum()

#############
# Part 2

# Configure shape mapping
shape_mapping_text = '''
A|Rock|Scissors|Paper|1
B|Paper|Rock|Scissors|2
C|Scissors|Paper|Rock|3
'''

df_shape_mapping = pandas.read_csv(StringIO(shape_mapping_text), names=["shape_id", "shape", "defeats", "loses_to", "score"], sep="|")

# Configure result mapping
result_mapping_text = '''
X|Lose|0
Y|Draw|3
Z|Win|6
'''

df_result_mapping = pandas.read_csv(StringIO(result_mapping_text), names=["player", "player_strategy", "result_score"], sep="|")

# Investigate dataframe
print(df_result_mapping)
df_result_mapping.head(15)

# Combine mapping with strategy guide
df_strategy_guide_2 = df_strategy_guide.merge(df_shape_mapping.add_prefix("opponent_"), how="left", left_on="opponent", right_on="opponent_shape_id")\
  .merge(df_result_mapping, how="left", on="player")\
  [["opponent", "player", "opponent_shape", "opponent_defeats", "opponent_loses_to", "player_strategy", "result_score"]]

# Investigate dataframe
print(df_strategy_guide_2)
df_strategy_guide_2.head(15)

# Determine player result
df_strategy_guide_2["player_shape"] = numpy.where(
    df_strategy_guide_2["player_strategy"] == "Lose"
  , df_strategy_guide_2["opponent_defeats"]
  , numpy.where(
      df_strategy_guide_2["player_strategy"] == "Draw"
    , df_strategy_guide_2["opponent_shape"]
    , df_strategy_guide_2["opponent_loses_to"]
  )
)

# Determine scores
df_strategy_guide_2_scores = df_strategy_guide_2.merge(df_shape_mapping.add_prefix("player_"), how="left", on="player_shape")\
  [["opponent", "player", "opponent_shape", "player_strategy", "player_shape", "player_score", "result_score"]]

# Investigate dataframe
print(df_strategy_guide_2_scores)
df_strategy_guide_2_scores.head(15)

# Total Score
df_strategy_guide_2_scores["total_score"] = df_strategy_guide_2_scores["player_score"] + df_strategy_guide_2_scores["result_score"]
df_strategy_guide_2_scores["total_score"].sum()