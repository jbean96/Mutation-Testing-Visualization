import unittest
from my_class import MyClass

class MyClassTest(unittest.TestCase):
    def test_double(self):
        c1 = MyClass(2)
        self.assertEqual(c1.double_me(), 4)

    def test_add10(self):
        c1 = MyClass(1)
        self.assertEqual(c1.add10(), 11)

if __name__ == '__main__':
    unittest.main()
