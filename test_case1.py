from rankengine import Cell
from rankengine import RankEngine

class MyCell(Cell):
    def __init__(self, join_attribute2value, table_attribute2value, l, weight):
        super().__init__(join_attribute2value, table_attribute2value, l, weight)

    def __lt__(self, other):
        return self.weight < other.weight

    def __gt__(self, other):
        pass

    def __eq__(self, other):
        pass

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