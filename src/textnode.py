from enum import Enum
from htmlnode import LeafNode

class TextType(Enum):
    PARAGRAPH = None
    BOLD = "b"
    ITALIC = "i"
    CODE = "code"
    LINK = "a"
    IMAGE = "img"
    STRIKETHROUGH = "s"

class TextNode:
    def __init__(self, text, text_type, url = None):
        self.text = text
        self.text_type = text_type
        self.url = url
    
    def __eq__(self, other):
        if self.text != other.text:
            return False
        if self.text_type != other.text_type:
            return False
        if self.url != other.url:
            return False
        return True
    
    def __repr__(self):
        return f"TextNode(\"{self.text}\", {self.text_type}, {self.url})"
    
    def to_html_node(self):
        if self.text_type == TextType.LINK:
            return LeafNode("a", self.text, {"href": self.url})
        if self.text_type == TextType.IMAGE:
            return LeafNode("img", self.text, {"src": self.url, "alt": ""})
        if self.text_type == TextType.PARAGRAPH:
            return LeafNode(None, self.text)
        return LeafNode(self.text_type.value, self.text)

