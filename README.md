## **Usage**
**This part describes how to invoke ``RankEngine`` in your application.**

Let's go through the process of running experiment-1.

First, prepare the four tables as R0.txt, R1.txt, R2.txt, and R3.txt.
```
x	y	weight_0
1	1	1
2	1	2
```
```
y	z	weight_1
1	1	1
3	1	1
```
```
z	w	weight_2
1	1	1
1	2	4
```
```
z	u	weight_3
1	1	1
1	2	5
```
Next, prepare the json file with all parameters specified.

``table_keys`` is for each bag, the common attributes with its parent bag.

``output_ordered_attributes`` is the attribute order showing in the output file.

``value_num`` is the amount of rows in each table.
```json
{
    "table_files": ["case1/R0.txt", "case1/R1.txt", "case1/R2.txt", "case1/R3.txt"],
    "table_keys": [[], ["y"], ["z"], ["z"]],
    "traverse_order": ["2", "3", "1", "0"],
    "children": {"0": ["1"], "1": ["2", "3"], "2": [], "3": []},
    "output_ordered_attributes": ["weight", "x", "y", "z", "u"],
    "value_num": "2"
}
```
Next, create a python file. In the top of it, remember to import relevant components.
```python
from rankengine import Cell
from rankengine import RankEngine
```
Create a cell class which inherits ``Cell``, and remember to override ``def __lt__(self, other)`` since we need to do customized comparison in the priority queue.
```python
class MyCell(Cell):
    def __init__(self, join_attribute2value, table_attribute2value, l, weight):
        super().__init__(join_attribute2value, table_attribute2value, l, weight)

    def __lt__(self, other):
        return self.weight < other.weight
```
Finally, utilize ``RankEninge`` and specify the format of the output file. Below is an example.
```python
if __name__ == "__main__":
    print ("########  test case1  ########")

    engine = RankEngine(MyCell, "case1.json")
    engine.preprocess()

    with open("output_case1.txt", 'w') as output_file:    
        while engine.Q[0]["root"].size() > 0:
            attributeValue_pairs = engine.enumeration()

            res = []
            for pair in attributeValue_pairs:
                res += [pair[0]]
                res += ['=']
                res += [pair[1]]
                res += [', ']
            res.pop()
            res += ['\n']
            output_file.write("".join(str(elem) for elem in res))
```
We already prepared the setup of experiment-1 and experiment-2 for you. Inside folder ``proj_impl``, just type the related command:
```
python3 test_case1.py
python3 test_case2_xzy.py
python3 test_case2_zyx.py
```
Or, you can test all of them at one time
```
python3 test_all.py
```
Furthermore, you can specify your own ranking function by following the above procedure.
