
class HTMLNode():
    def __init__(self, tag = None, value = None, children = None, props = None):
        self.tag = tag
        self.value = value
        self.children = children
        self.properties = props
    
    def to_html(self):
        raise NotImplementedError()
    
    def props_to_html(self):
        if self.properties == None:
            return ""
        return " ".join(f"{key}=\"{val}\"" for (key, val) in self.properties.items())
    
    def __repr__(self):
        return f"HTMLNode(tag = {repr(self.tag)}, value = {repr(self.value)}, children = {repr(self.children)}, props = {repr(self.properties)})"

class LeafNode(HTMLNode):
    def __init__(self, tag = None, value = "", props = None):
        super().__init__(tag, value, None, props)

    def to_html(self):
        if self.tag == None:
            return f"{self.value}"
        return f"<{self.tag}{(' ' + self.props_to_html()) * (self.properties != None)}>{self.value}</{self.tag}>"
    
    def __repr__(self):
        return f"LeafNode(tag = {repr(self.tag)}, value = {repr(self.value)}, props = {repr(self.properties)})"
    
class ParentNode(HTMLNode):
    def __init__(self, tag, children, props = None):
        super().__init__(tag, None, children, props)
    
    def to_html(self):
        return f"<{self.tag}{(' ' + self.props_to_html()) * (self.properties != None)}>{''.join((child.to_html() for child in self.children))}</{self.tag}>"
    
    def __repr__(self):
        return f"ParentNode(tag = {repr(self.tag)}, children = {repr(self.children)}, props = {repr(self.properties)})"