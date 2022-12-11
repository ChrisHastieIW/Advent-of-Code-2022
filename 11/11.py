
######################
## Imports

import numpy
import pandas

######################
## Functions

def clean_input(monkey_dict: dict) :
  clean_monkey_dict = {
        "id" : int(monkey_dict["id"])
      , "items" : [int(item) for item in monkey_dict["Starting items"].split(", ")]
      , "operation" : " ".join(monkey_dict["Operation"].split(" ")[-3:])
      , "divisible_test_number" : int(monkey_dict["Test"].split(" ")[-1])
      , "true_target" : int(monkey_dict["If true"].split(" ")[-1])
      , "false_target" : int(monkey_dict["If false"].split(" ")[-1])
      , "items_inspected" : 0
    }
  return clean_monkey_dict
  
def parse_input(input_file: str) :
  
  # Ingest file into list
  with open(input_file, 'r') as f:
    input_list = f.read().splitlines()

  monkeys = []
  current_monkey_id = 0
  current_monkey_dict = {}
  for input in input_list :
    if len(input) == 0 :
      clean_monkey_dict = clean_input(current_monkey_dict)
      monkeys.append(clean_monkey_dict)
    elif input[:6] == "Monkey" :
      current_monkey_id = input[-2]
      current_monkey_dict = {"id" : current_monkey_id}
    elif input[3] != " " :
      current_input = input[2:].split(": ")
      current_monkey_dict[current_input[0]] = current_input[1]
    elif input[4:6] == "If" :
      current_input = input[4:].split(": ")
      current_monkey_dict[current_input[0]] = current_input[1]
    else :
      print(input)
  clean_monkey_dict = clean_input(current_monkey_dict)
  monkeys.append(clean_monkey_dict)

  return monkeys

def monkey_turn_1(monkey_id: int, monkeys: list) :
  for item_index in range(len(monkeys[monkey_id]["items"])) :
    old = monkeys[monkey_id]["items"].pop(0)
    new = eval(monkeys[monkey_id]["operation"])
    item_worry = int(new / 3)
    if item_worry % monkeys[monkey_id]["divisible_test_number"] == 0 :
      target = monkeys[monkey_id]["true_target"]
    else :
      target = monkeys[monkey_id]["false_target"]
    monkeys[target]["items"].append(item_worry)
    monkeys[monkey_id]["items_inspected"] = monkeys[monkey_id]["items_inspected"] + 1   

  return monkeys

def monkey_turn_2(monkey_id: int, monkeys: list, divisible_test_product: int, item_worry_modifier: bool = True) :
  for item_index in range(len(monkeys[monkey_id]["items"])) :
    old = monkeys[monkey_id]["items"].pop(0)
    new = eval(monkeys[monkey_id]["operation"])
    if item_worry_modifier :
      item_worry = int(new / 3) % divisible_test_product
    else :
      item_worry = int(new) % divisible_test_product
    if item_worry % monkeys[monkey_id]["divisible_test_number"] == 0 :
      target = monkeys[monkey_id]["true_target"]
    else :
      target = monkeys[monkey_id]["false_target"]
    monkeys[target]["items"].append(item_worry)
    monkeys[monkey_id]["items_inspected"] = monkeys[monkey_id]["items_inspected"] + 1   

  return monkeys

def monkey_round_1(monkeys: list) :
  for monkey_dict in monkeys :
    monkeys = monkey_turn_1(monkey_dict["id"], monkeys)
    
  return monkeys


def monkey_round_2(monkeys: list, divisible_test_product: int, item_worry_modifier: bool = True) :
  for monkey_dict in monkeys :
    monkeys = monkey_turn_2(monkey_dict["id"], monkeys, divisible_test_product, item_worry_modifier)

  return monkeys

######################
## Part 1

def part_1(input_file: str) :

  monkeys = parse_input(input_file)
  monkey_round_results = [monkeys]
  for x in range(20) :
    monkey_round_results.append(monkey_round_1(monkey_round_results[x]))

  monkey_business_round_20 = pandas.DataFrame(data=monkey_round_results[-1]).sort_values(by="items_inspected", ascending=False)[:2]["items_inspected"].product()
  return monkey_business_round_20

part_1(input_file="11/sample_input.txt")
part_1(input_file="11/input.txt")

######################
## Part 2

def part_2(input_file: str, round_count: int) :

  monkeys = parse_input(input_file)
  unique_divisible_test_numbers = pandas.DataFrame(data=monkeys)["divisible_test_number"].unique()
  divisible_test_product = unique_divisible_test_numbers.prod()

  for x in range(round_count) :
    monkeys = monkey_round_2(monkeys, divisible_test_product=divisible_test_product, item_worry_modifier=False)

  print(pandas.DataFrame(data=monkeys)[["id", "items_inspected"]])

  monkey_business = pandas.DataFrame(data=monkeys).sort_values(by="items_inspected", ascending=False)[:2]["items_inspected"].product()
  return monkey_business

part_2(input_file="11/sample_input.txt", round_count=20)
part_2(input_file="11/sample_input.txt", round_count=1000)
part_2(input_file="11/input.txt", round_count=10000)