from enum import Enum
from htmlnode import LeafNode, ParentNode

class TextType(Enum):
    PARAGRAPH = None
    BOLD = "b"
    ITALIC = "i"
    CODE = "code"
    LINK = "a"
    IMAGE = "img"
    STRIKETHROUGH = "s"

class TextNode:
    def __init__(self, text, text_types, url = None):
        self.text = text
        self.text_types = text_types
        self.url = url
    
    def __eq__(self, other):
        if self.text != other.text:
            return False
        if self.text_types != other.text_types:
            return False
        if self.url != other.url:
            return False
        return True
    
    def __repr__(self):
        return f"TextNode(\"{self.text}\", {self.text_types}, {self.url})"
    
    def to_html_node(self):
        types = self.text_types
        node = LeafNode(None, self.text)
        while types != []:
            current_type = types.pop()
            if current_type == TextType.LINK:
                node = ParentNode("a", [node], {"href": self.url})
            elif current_type == TextType.IMAGE:
                node = ParentNode("img", [node], {"src": self.url, "alt": ""})
            else:
                node = ParentNode(current_type.value, [node])
        return node

