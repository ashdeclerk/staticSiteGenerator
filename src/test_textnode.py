import unittest

from textnode import TextNode, TextType


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD, "/this/is/a/path")
        node2 = TextNode("This is a text node", TextType.BOLD, "/this/is/a/path")
        self.assertEqual(node, node2)

    def test_repr(self):
        node = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(repr(node), "TextNode(\"This is a text node\", TextType.BOLD, None)")

    def test_type_ineq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.ITALIC)
        self.assertNotEqual(node, node2)

    def test_text_ineq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a different text node", TextType.BOLD)
        self.assertNotEqual(node, node2)

    def test_URL_ineq(self):
        node = TextNode("This is a text node", TextType.BOLD, "/blah")
        node2 = TextNode("This is a text node", TextType.BOLD, "/bleh")
        self.assertNotEqual(node, node2)

    def test_to_html(self):
        node = TextNode("This is a text node", TextType.BOLD)
        html = node.to_html_node()
        self.assertEqual(repr(html), "LeafNode(tag = 'b', value = 'This is a text node', props = None)")

    def test_img_to_html(self):
        node = TextNode("This is an image", TextType.IMAGE, "/wah")
        html = node.to_html_node()
        self.assertEqual(repr(html), "LeafNode(tag = 'img', value = 'This is an image', props = {'src': '/wah', 'alt': ''})")
    
    def test_link_to_html(self):
        node = TextNode("This is a link", TextType.LINK, "/weh")
        html = node.to_html_node()
        self.assertEqual(repr(html), "LeafNode(tag = 'a', value = 'This is a link', props = {'href': '/weh'})")


if __name__ == "__main__":
    unittest.main()