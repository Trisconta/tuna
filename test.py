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
    print("# Reading xml:", path)
    # Configure to display all tracks played
    tuna.itresume.ItResume.configure_lasts("b")
    tunes = tuna.itresume.ItResume(xml_path=path)
    assert len(tunes.alist) > 0, "Expected at least one element!"
    da_show(tunes)
    return True

def da_show(tunes):
    for num, item in enumerate(tunes.alist, 1):
        print(item)


main()
