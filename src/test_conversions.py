import unittest

from markdown_to_nodes import *
from textnode import TextNode, TextType

class Test_split(unittest.TestCase):
    def test_multi(self):
        md = "This is text with a **bolded phrase** in the middle. There is also *an italic section* and `some code`."
        assert text_to_textnodes(md) == [TextNode("This is text with a ", TextType.PARAGRAPH),
                            TextNode("bolded phrase", TextType.BOLD),
                            TextNode(" in the middle. There is also ", TextType.PARAGRAPH),
                            TextNode("an italic section", TextType.ITALIC),
                            TextNode(" and ", TextType.PARAGRAPH),
                            TextNode("some code", TextType.CODE),
                            TextNode(".", TextType.PARAGRAPH)]
    
    def test_single(self):
        md = "This is **text** with **several** bolded phrases. **I fucking hope this works.**"
        node = TextNode(md, TextType.PARAGRAPH)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        assert new_nodes == [TextNode("This is ", TextType.PARAGRAPH),
                             TextNode("text", TextType.BOLD),
                             TextNode(" with ", TextType.PARAGRAPH),
                             TextNode("several", TextType.BOLD),
                             TextNode(" bolded phrases. ", TextType.PARAGRAPH),
                             TextNode("I fucking hope this works.", TextType.BOLD)]
    
    def test_image_finder(self):
        md = "This has ![an image](https://i.imgur.com/)"
        assert extract_markdown_images(md) == [("an image", "https://i.imgur.com/")]
    
    def test_link_finder(self):
        md = "This has [a link](https://i.imgur.com/)"
        assert extract_markdown_links(md) == [("a link", "https://i.imgur.com/")]
    
    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.PARAGRAPH,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.PARAGRAPH),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.PARAGRAPH),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_links(self):
        node = TextNode(
            "This is text with a [link](https://i.imgur.com/zjjcJKZ.png) and another [here](https://i.imgur.com/3elNhQu.png)",
            TextType.PARAGRAPH,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.PARAGRAPH),
                TextNode("link", TextType.LINK, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.PARAGRAPH),
                TextNode(
                    "here", TextType.LINK, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )
    
    def test_multiple_splits(self):
        md = """This is a longer bit of markdown.
There are *italicized pieces* and **bold declarations**!
We have [links to cool websites](www.google.com) and also ![embedded images](https://tenor.com/view/brutal-savage-rekt-gif-9810801).
And, of course, `there's a bit of code`."""
        self.assertListEqual(
            text_to_textnodes(md),
            [
                TextNode("This is a longer bit of markdown.\nThere are ", TextType.PARAGRAPH),
                TextNode("italicized pieces", TextType.ITALIC),
                TextNode(" and ", TextType.PARAGRAPH),
                TextNode("bold declarations", TextType.BOLD),
                TextNode("!\nWe have ", TextType.PARAGRAPH),
                TextNode("links to cool websites", TextType.LINK, "www.google.com"),
                TextNode(" and also ", TextType.PARAGRAPH),
                TextNode("embedded images", TextType.IMAGE, "https://tenor.com/view/brutal-savage-rekt-gif-9810801"),
                TextNode(".\nAnd, of course, ", TextType.PARAGRAPH),
                TextNode("there's a bit of code", TextType.CODE),
                TextNode(".", TextType.PARAGRAPH),
            ]
        )

    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
    """
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_block_to_block_type(self):
        blocks = [
            "# Heading!",
            "```Code 1```",
            """```
            Code 2
            ```""",
            "## Heading 2",
            "> Quote\n> Version\n> 1",
            """> Quote
> Version
> 2""",
            """- Unordered
- List
- With
- Dashes""",
            """* Unordered
* List
* With
* Stars""",
            """1. Ordered
2. List
3. With
4. Dots""",
            """1) Ordered
2) List
3) With
4) Parens""",
            """1. A
2. Very
3. Long
4. Ordered
5. List
6. That
7. I
8. Have
9. To
10. Pad
11. Out""",
            "And others"
        ]
        self.assertListEqual(
            list(map(block_to_block_type, blocks)),
            [
                BlockType.HEADING,
                BlockType.CODE,
                BlockType.CODE,
                BlockType.HEADING,
                BlockType.QUOTE,
                BlockType.QUOTE,
                BlockType.UNORDERED_LIST,
                BlockType.UNORDERED_LIST,
                BlockType.ORDERED_LIST,
                BlockType.ORDERED_LIST,
                BlockType.ORDERED_LIST,
                BlockType.PARAGRAPH
            ]
        )

class Test_html_nodification(unittest.TestCase):
    # TODO: More unit tests here. Specifically for quotes and lists and headers.
    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )
