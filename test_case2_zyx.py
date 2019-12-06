from rankengine import Cell
from rankengine import RankEngine

class MyCell(Cell):
    def __init__(self, join_attribute2value, table_attribute2value, l, weight):
        super().__init__(join_attribute2value, table_attribute2value, l, weight)
        self.lexicographic_order = ["z", "y", "x"]

    def __lt__(self, other):
        for attr in self.lexicographic_order:
            if attr not in self.join_attribute2value.keys():
                continue
            if self.join_attribute2value[attr] != other.join_attribute2value[attr]:
                return self.join_attribute2value[attr] < other.join_attribute2value[attr]
        return False

    def __gt__(self, other):
        pass

    def __eq__(self, other):
        pass

if __name__ == "__main__":
    print ("########  test case2_zyx  ########")

    engine = RankEngine(MyCell, "case2_zyx.json")
    engine.preprocess()

    with open("output_case2_zyx.txt", 'w') as output_file:    
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