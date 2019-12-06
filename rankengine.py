# for roadNet

from collections import defaultdict
from heapq import heappush, heappop
from copy import deepcopy
from sys import argv
import re
import json

class Relation:
    def __init__(self):
        self.attributes = []
        self.attribute2values = defaultdict(lambda : [])
        self.value_num = 0
        self.keys = []

class Cell:
    def __init__(self, join_attribute2value, table_attribute2value, l, weight):
        self.join_attribute2value = join_attribute2value
        self.table_attribute2value = table_attribute2value
        self.next_level_cells = l
        self.next_cell = None
        self.weight = weight

    def __lt__(self, other):
        pass

    def __gt__(self, other):
        pass

    def __eq__(self, other):
        pass

class PriorityQueue:
    def __init__(self):
        self.heap = []

    def push(self, elem):
        heappush(self.heap, elem)

    def pop(self):
        return heappop(self.heap)

    def top(self):
        return self.heap[0]

    def size(self):
        return len(self.heap)

class Decoder(json.JSONDecoder):
    def decode(self, s):
        result = super().decode(s)  # result = super(Decoder, self).decode(s) for Python 2.x
        return self._decode(result)

    def _decode(self, o):
        if isinstance(o, str):
            try:
                return int(o)
            except ValueError:
                return o
        elif isinstance(o, dict):
            return {self._decode(k): self._decode(v) for k, v in o.items()}
        elif isinstance(o, list):
            return [self._decode(v) for v in o]
        else:
            return o

class RankEngine:
    def __init__(self, MyCell, json_file):
        self.MyCell = MyCell

        self.bag = {}
        # self.traverse_order = [1, 0]
        self.traverse_order = []
        # self.children = {0: [1],\
        #                     1: []}
        self.children = {}
        self.output_ordered_attributes = []
        self.value_num = 0

        self.read_json_file(json_file)
        
        self.Q = {}
        for bag_num in self.traverse_order:
            self.Q[bag_num] = defaultdict(lambda : PriorityQueue())

        # additional check
        # self.output_ordered_attributeValuePairs = [['x', None], ['y', None], ['z', None]]

    def read_json_file(self, json_file):
        with open(json_file, 'r') as json_file:
            json_file = json.load(json_file, cls=Decoder)

            self.value_num = json_file["value_num"]
            for bag_num, table_file in enumerate(json_file["table_files"]):
                self.bag[bag_num] = Relation()
                self.read_table_file(table_file, bag_num)
            for bag_num in range(len(self.bag)):
                self.bag[bag_num].keys = json_file["table_keys"][bag_num]
            self.traverse_order = json_file["traverse_order"]
            self.children = json_file["children"]
            self.output_ordered_attributes = json_file["output_ordered_attributes"]
            

    def read_table_file(self, table_file, bag_num):
        print ("read " + table_file)
        with open(table_file, 'r') as table_file:
            for line_iter, line in enumerate(table_file):
                parts = re.split(" |\t|\n", line)
                parts.pop()

                # read attributes
                if line_iter == 0:
                    for attr in parts:
                        self.bag[bag_num].attributes += [attr]
                else:
                    for i, value in enumerate(parts):
                        self.bag[bag_num].attribute2values[self.bag[bag_num].attributes[i]] += [int(value)]

                if line_iter == self.value_num:
                    break
            # additional check
            self.bag[bag_num].value_num = self.value_num
            # self.bag[bag_num].value_num = len(self.bag[bag_num].attribute2values['x'])

            print ("the attributes are ", end='')
            print (self.bag[bag_num].attributes)


    def preprocess(self):
        for bag_num in self.traverse_order:
            for value_iter in range(self.bag[bag_num].value_num):
            
                q_input = None
                if len(self.bag[bag_num].keys) == 0:
                    q_input = "root"
                else:
                    q_input = self.create_q_input(bag_num, value_iter)

                l = []
                weight = self.bag[bag_num].attribute2values["weight_" + str(bag_num)][value_iter]
                go_next_value_iter = False
                for child_num in self.children[bag_num]:
                    child_q_input = self.create_child_q_input(bag_num, value_iter, child_num)
                    if child_q_input not in self.Q[child_num].keys():
                    # for a successful join, keys in all children must have the same valuation
                        go_next_value_iter = True
                        break
                    top = self.Q[child_num][child_q_input].top()
                    l.append(top)
                    weight += top.weight
                if go_next_value_iter == True:
                    continue
            
                table_attribute2value = self.get_table_attribute2value(bag_num, value_iter)
                join_attribute2value = self.get_join_attribute2value(table_attribute2value, l)
                self.Q[bag_num][q_input].push(self.MyCell(join_attribute2value, table_attribute2value, l, weight))

    def create_q_input(self, bag_num, value_iter):
        q_input = []
        for key in self.bag[bag_num].keys:
            q_input += [key]
            q_input += ['=']
            q_input += [self.bag[bag_num].attribute2values[key][value_iter]]
            q_input += [',']
        q_input.pop()
        return "".join(str(x) for x in q_input)

    def create_child_q_input(self, bag_num, value_iter, child_num):
        child_q_input = []
        for key in self.bag[child_num].keys:
            child_q_input += [key]
            child_q_input += ['=']
            child_q_input += [self.bag[bag_num].attribute2values[key][value_iter]]
            child_q_input += [',']
        child_q_input.pop()
        return "".join(str(x) for x in child_q_input)

    def get_table_attribute2value(self, bag_num, value_iter):
        table_attribute2value = {}
        for attribute in self.bag[bag_num].attribute2values.keys():
            table_attribute2value[attribute] = self.bag[bag_num].attribute2values[attribute][value_iter]
        return table_attribute2value

    def get_join_attribute2value(self, table_attribute2value, next_level_cells):
        join_attribute2value = deepcopy(table_attribute2value)
        for next_level_cell in next_level_cells:
            for attr, value in next_level_cell.join_attribute2value.items():
                join_attribute2value[attr] = value
        # print (join_attribute2value.keys())
        return join_attribute2value

    def enumeration(self):
        ret_cell = self.Q[0]["root"].top()
        self.topdown(self.Q[0]["root"].top(), 0)
        # return ret_cell.weight, [(attr, ret_cell.join_attribute2value[attr]) for attr in self.output_ordered_attributes]

        # print (ret_cell.join_attribute2value)

        if self.output_ordered_attributes[0] == "weight":
            ret_cell.join_attribute2value["weight"] = ret_cell.weight

        return [(attr, ret_cell.join_attribute2value[attr]) for attr in self.output_ordered_attributes]
        
        # ret_cell.join_attribute2value

        # self.get_output_ordered_attributeValuePairs(ret_cell)
        # return self.output_ordered_attributeValuePairs, ret_cell.weight

    def topdown(self, cell, bag_num):
        q_input = None
        if len(self.bag[bag_num].keys) == 0:
            q_input = "root"
        else:
            q_input = self.create_q_input_topdown(cell, bag_num)

        if cell.next_cell is None and self.Q[bag_num][q_input].size() > 0:
        # if cell.next_cell is None:  # not connect yet
            self.Q[bag_num][q_input].pop()
            for i, child_num in enumerate(self.children[bag_num]):
                old_next_level_cell_weight = cell.next_level_cells[i].weight
                new_next_level_cell = self.topdown(cell.next_level_cells[i], child_num)
                if new_next_level_cell is not None:
                    l = cell.next_level_cells[:]
                    l[i] = new_next_level_cell
                    new_weight = cell.weight - old_next_level_cell_weight + new_next_level_cell.weight

                    join_attribute2value = self.get_join_attribute2value(cell.table_attribute2value, l)
                    self.Q[bag_num][q_input].push(self.MyCell(join_attribute2value, cell.table_attribute2value, l, new_weight))
            # if q_input != "root" and self.Q[bag_num][q_input].size() > 0:
            if q_input != "root":
                # connect
                if self.Q[bag_num][q_input].size() > 0:
                    cell.next_cell = self.Q[bag_num][q_input].top()

        if self.Q[bag_num][q_input].size() > 0:
            return self.Q[bag_num][q_input].top()
        else:
            return None

    def create_q_input_topdown(self, cell, bag_num):
        child_q_input = []
        for key in self.bag[bag_num].keys:
            child_q_input += [key]
            child_q_input += ['=']
            child_q_input += [cell.table_attribute2value[key]]
            child_q_input += [',']
        child_q_input.pop()
        return "".join(str(x) for x in child_q_input)

if __name__ == "__main__":

    engine = RankEngine()
    # engine.parse()

    # print (engine.bag[0].attributes)
    # print (engine.bag[0].attribute2values['x'])

    engine.preprocess()

    while engine.Q[0]["root"].size() > 0:
        ret = engine.enumeration()
        print (ret)
    