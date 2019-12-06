from os import system

cmds = ["python3 test_case1.py",\
        "python3 test_case2_xzy.py",\
        "python3 test_case2_zyx.py"]

def test_all():
    for cmd in cmds:
        system(cmd)

if __name__ == "__main__":
    test_all()