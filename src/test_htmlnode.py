import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode


class TestHTMLNode(unittest.TestCase):
    def test_repr(self):
        node = HTMLNode(tag = "tag", value = "val", children = ["kids"], props = {"p1": "prop 1", "p2": "prop 2"})
        assert repr(node) == "HTMLNode(tag = \'tag\', value = \'val\', children = [\'kids\'], props = {\'p1\': \'prop 1\', \'p2\': \'prop 2\'})"

    def test_props_to_html(self):
        node = HTMLNode(props = {"href": "https://www.google.com", "target": "_blank"})
        assert node.props_to_html() == "href=\"https://www.google.com\" target=\"_blank\""

class TestLeafNode(unittest.TestCase):
    def test_repr(self):
        node = LeafNode(tag = "tag", value = "val", props = {"p1": "prop 1", "p2": "prop 2"})
        assert repr(node) == "LeafNode(tag = \'tag\', value = \'val\', props = {\'p1\': \'prop 1\', \'p2\': \'prop 2\'})"
    
    def test_to_html(self):
        node = LeafNode(tag = "p", value = "This is a paragraph of text.")
        assert node.to_html() == "<p>This is a paragraph of text.</p>"

    def test_to_html_with_props(self):
        node = LeafNode(tag = "a", value = "Click me!", props = {"href": "https://www.google.com"})
        assert node.to_html() == "<a href=\"https://www.google.com\">Click me!</a>"
    
class TestParentNode(unittest.TestCase):
    def test_repr(self):
        node = ParentNode(tag = "tag", children = ["kids"], props = {"p1": "prop 1", "p2": "prop 2"})
        assert repr(node) == "ParentNode(tag = \'tag\', children = [\'kids\'], props = {\'p1\': \'prop 1\', \'p2\': \'prop 2\'})"

    def test_to_html1(self):
        node = ParentNode(
            "p",
            [
                LeafNode("b", "Bold text"),
                LeafNode(None, "Normal text"),
                LeafNode("i", "italic text"),
                LeafNode(None, "Normal text"),
            ],
        )
        assert node.to_html() == "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>"

    def test_to_html2(self):
        leaf = LeafNode("b", "Bold text")
        parent1 = ParentNode("i", [leaf])
        parent2 = ParentNode("u", [parent1])
        assert parent2.to_html() == "<u><i><b>Bold text</b></i></u>"
