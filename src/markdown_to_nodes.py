from textnode import TextNode, TextType
import re
from enum import Enum
from htmlnode import *

class BlockType(Enum):
    PARAGRAPH = ""
    HEADING = "#"
    CODE = "`"
    QUOTE = ">"
    UNORDERED_LIST = "*"
    ORDERED_LIST = "1"



def split_nodes_delimiter(old_nodes, delimiter, text_type):
    """list of "old nodes" in, new list where we've split on the delimiter
    and encoded with appropriate text_type out"""
    # You have to be careful about using this with certain delimiters, e.g.
    # '*' for italics. Order matters!
    new_nodes = []
    for node in old_nodes:
        pieces = node.text.split(delimiter)
        # The even-indexed pieces are "outside" the delimiter, while odd-indexed
        # pieces are "inside" the delimiter.
        for index, piece in enumerate(pieces):
            if index % 2 and len(piece) > 0:
                new_nodes.append(TextNode(piece, node.text_types + [text_type]))
            elif len(piece) > 0:
                new_nodes.append(TextNode(piece, node.text_types, node.url))
    return new_nodes

def extract_markdown_images(text):
    # Markdown in, list of tuples out.
    # Each tuple contains alt text and URL for each image.
    matches = re.findall(r"!\[(.*?)\]\((.*?)\)", text)
    return matches

def extract_markdown_links(text):
    # Markdown in, list of tuples out.
    # Each tuple contains anchor text and URL for each link.
    matches = re.findall(r"(?<!!)\[(.*?)\]\((.*?)\)", text)
    return matches

def split_nodes_image(old_nodes):
    """list of nodes in, new list where we've separated images out"""
    new_nodes = []
    for node in old_nodes:
        images = list(re.finditer(r"!\[(.*?)\]\((.*?)\)", node.text))
        idx = 0
        starting_idx = 0
        while idx < len(images):
            text_piece = node.text[starting_idx:images[idx].span()[0]]
            if len(text_piece) > 0:
                new_nodes.append(TextNode(text_piece, node.text_types, node.url))
            img = extract_markdown_images(images[idx].group())[0]
            new_nodes.append(TextNode(img[0], node.text_types + [TextType.IMAGE], img[1]))
            starting_idx = images[idx].span()[1]
            idx += 1
        text_piece = node.text[starting_idx:]
        if len(text_piece) > 0:
            new_nodes.append(TextNode(text_piece, node.text_types, node.url))
    return new_nodes

def split_nodes_link(old_nodes):
    """list of nodes in, new list where we've separated links out"""
    new_nodes = []
    for node in old_nodes:
        links = list(re.finditer(r"(?<!!)\[(.*?)\]\((.*?)\)", node.text))
        idx = 0
        starting_idx = 0
        while idx < len(links):
            text_piece = node.text[starting_idx:links[idx].span()[0]]
            if len(text_piece) > 0:
                new_nodes.append(TextNode(text_piece, node.text_types, node.url))
            lnk = extract_markdown_links(links[idx].group())[0]
            new_nodes.append(TextNode(lnk[0], node.text_types + [TextType.LINK], lnk[1]))
            starting_idx = links[idx].span()[1]
            idx += 1
        text_piece = node.text[starting_idx:]
        if len(text_piece) > 0:
            new_nodes.append(TextNode(text_piece, node.text_types, node.url))
    return new_nodes

def text_to_textnodes(text):
    nodes = [TextNode(text, [], None)]
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "~~", TextType.STRIKETHROUGH)
    nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes

def markdown_to_blocks(text):
    return list(filter(lambda s : len(s) > 0, map(lambda s : s.strip(), text.split("\n\n"))))

def block_to_block_type(text):
    if is_code(text):
        return BlockType.CODE
    if is_heading(text):
        return BlockType.HEADING
    if is_quote(text):
        return BlockType.QUOTE
    if is_unordered_list(text):
        return BlockType.UNORDERED_LIST
    if is_ordered_list(text):
        return BlockType.ORDERED_LIST
    return BlockType.PARAGRAPH

def is_code(text):
    return len(text) >= 6 and text[:3] == "```" and text[-3:] == "```"

def is_heading(text):
    lines = text.split("\n")
    if len(lines) > 1:
        return False
    return bool(re.match(r"#{1,6} ", lines[0]))

def is_quote(text):
    lines = text.split("\n")
    return all(map(lambda s : re.match(r">", s), lines))

def is_unordered_list(text):
    lines = text.split("\n")
    return all(map(lambda s : re.match(r"[-*] ", s), lines))

def is_ordered_list(text):
    lines = text.split("\n")
    return all(map(lambda s : re.match(r"[0-9]*[.)] ", s), lines))

def markdown_to_html_node(text):
    md_blocks = markdown_to_blocks(text)
    # Each block becomes a parent node
    nodes = map(block_to_parent_node, md_blocks)
    # And then we do a single uber-parent
    return ParentNode("div", nodes)

def block_to_parent_node(block):
    # Each block is a wall of text right now.
    block_type = block_to_block_type(block)
    return create_typed_parent_node(block, block_type)

def create_typed_parent_node(block, block_type):
    if block_type == BlockType.PARAGRAPH:
        return create_para_parent_node(block)
    if block_type == BlockType.HEADING:
        return create_header_parent_node(block)
    if block_type == BlockType.QUOTE:
        return create_quote_parent_node(block)
    if block_type == BlockType.CODE:
        return create_code_parent_node(block)
    if block_type == BlockType.UNORDERED_LIST:
        return create_unordered_parent_node(block)
    if block_type == BlockType.ORDERED_LIST:
        return create_ordered_parent_node(block)
    
def create_para_parent_node(block):
    block = block.replace("\n", " ")
    return ParentNode("p", list(map(lambda n : n.to_html_node(), text_to_textnodes(block))))

def create_header_parent_node(block):
    header_depth = block.find(" ")
    return ParentNode("h" + str(header_depth), list(map(lambda n : n.to_html_node(), text_to_textnodes(block[header_depth + 1:]))))

def create_quote_parent_node(block):
    block = block.replace("\n> ", "\n")
    block = block.replace("\n>", "\n")
    block = block[1:]
    children = []
    for line in block.split("\n"):
        subchildren = list(map(lambda n : n.to_html_node(), text_to_textnodes(line + "\n")))
        children.append(ParentNode("p", subchildren))
    return ParentNode("blockquote", children)

def create_code_parent_node(block):
    return ParentNode("pre", [LeafNode("code", block[4:-3])])

def create_unordered_parent_node(block):
    children = []
    for line in block.split("\n"):
        subchildren = list(map(lambda n : n.to_html_node(), text_to_textnodes(line[2:])))
        children.append(ParentNode("li", subchildren))
    return ParentNode("ul", children)

def create_ordered_parent_node(block):
    children = []
    for line in block.split("\n"):
        subchildren = list(map(lambda n : n.to_html_node(), text_to_textnodes(line[line.find(" ") + 1:])))
        children.append(ParentNode("li", subchildren))
    return ParentNode("ol", children)

