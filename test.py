""" Basic tests for 'tuna' package.
"""

# pylint: disable=missing-function-docstring

import sys
import os.path
sys.path.append(
    os.path.realpath(os.path.dirname(os.path.dirname(__file__)))
)
import tuna


def main():
    main_test("itunes.xml")

def main_test(path):
    AClass = tuna.itresume.ItResume
    public_class_vars = [
        k for k in AClass.__dict__
        if not k.startswith('_') and not callable(getattr(AClass, k))
    ]
    assert public_class_vars, "No public var?"
    print("Reading xml:", path)
    tunes = tuna.itresume.ItResume(xml_path=path)
    assert len(tunes.alist) == 100, "Expected 100 elements"
    da_show(tunes)
    return True

def da_show(tunes):
    for num, item in enumerate(tunes.alist, 1):
        print(f"{num:<4}", item)


main()
