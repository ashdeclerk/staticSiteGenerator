from textnode import TextNode, TextType
import re
from enum import Enum
from htmlnode import *
from string import ascii_lowercase, ascii_uppercase

class BlockType(Enum):
    PARAGRAPH = ""
    HEADING = "#"
    CODE = "`"
    QUOTE = ">"
    LIST = "*"



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
    if is_list(text):
        return BlockType.LIST
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
    return re.match(r">", lines[0]) and all(map(lambda s : re.match(r"\s*>", s), lines))

def is_list(text):
    lines = text.split("\n")
    return all(map(lambda s : re.match(r"([\s]*[-*] )|([\s]*[0-9a-zA-Z]*[.)] )", s), lines))

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
    if block_type == BlockType.LIST:
        return create_list_parent_node(block)
    
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

def create_list_parent_node(block):
    # I have decided that it's worth dealing with nested list nonsense,
    # which means this becomes much more complicated than the original version.
    # In particular, we need to deal with stuff based on the starting whitespace,
    # along with figuring out whether we have an ordered or unordered list on the fly,
    # *and* dealing with list values for each ordered list item if it's not what we expect.
    # So, complicated.
    lines = block.split("\n")
    # We're just shoving this to a helper function.
    return create_list_from_lines(lines)

def create_list_from_lines(lines, depth = 0):
    # Indentation makes things *weird*. I don't *want* to allow sublists before
    # the first list item, because I think it's useless, but... Who knows.
    # I'm going to do something that feels kinda hacky, but it should work.
    # Step 1: Find the longest common prefix of all the lines.
    base_prefix = re.match(r"\s*", lines[0]).group()
    for line in lines:
        if not line.startswith(base_prefix):
            new_base_prefix_candidate = re.match(r"\s*", line).group()
            if base_prefix.startswith(new_base_prefix_candidate):
                base_prefix = new_base_prefix_candidate
            else:
                base_prefix = longest_common_prefix(base_prefix, new_base_prefix_candidate)
    # Step 2: Tidy all of the lines.
    for idx, line in enumerate(lines):
        lines[idx] = line.removeprefix(base_prefix)
    # Step 3: Make a child node for each main list line, and for each sublist.
    children = []
    idx = 0
    while idx < len(lines):
        current_line = lines[idx]
        prefix = re.match(r"\s*", current_line).group()
        if prefix:
            # Uh-oh, we have a sublist!
            sublist = [current_line]
            idx += 1
            while idx < len(lines) and re.match(r"\s+", lines[idx]):
                sublist.append(lines[idx])
                idx += 1
            children.append(create_list_from_lines(sublist, depth = depth + 1))
        else:
            # Yay, we're in the main list!
            text_start = re.match(r"([0-9a-zA-Z]*[.)] )|([-*] )", current_line).end()
            subchildren = list(map(lambda n : n.to_html_node(), text_to_textnodes(current_line[text_start:])))
            if is_unordered_list_item(current_line):
                children.append(ParentNode("li", subchildren, {"style": "list-style-type:" + ("disc" if depth == 0 else "circle" if depth == 1 else "square")}))
            else:
                # Step 1: Figure out style. We only need decimal, lower-alpha, or upper-alpha.
                if current_line[0].islower():
                    style = "lower-alpha"
                elif current_line[0].isupper():
                    style = "upper-alpha"
                else:
                    style = "decimal"
                # Step 2: Figure out value. This is a pain in the butt for either alpha.
                if style == "lower-alpha":
                    value = 0
                    value_string = re.match(r"[a-z]*", current_line).group()
                    for sub_idx, let in enumerate(reversed(value_string)):
                        value += (ascii_lowercase.find(let) + 1) * 26 ** sub_idx
                    print(value_string, value)
                elif style == "lower-alpha":
                    value = 0
                    value_string = re.match(r"[A-Z]*", current_line).group()
                    for sub_idx, let in enumerate(reversed(value_string)):
                        value += (ascii_uppercase.find(let) + 1) * 26 ** sub_idx
                else:
                    value = int(re.match(r"[0-9]*", current_line).group())
                children.append(ParentNode("li", subchildren, {"style": "list-style-type:" + style, "value": value}))
            idx += 1
    return ParentNode("ol", children)

def is_unordered_list_item(string):
    return bool(re.match(r"[\s]*[*-] ", string))

def is_ordered_list_item(string):
    return bool(re.match(r"[\s]*[0-9a-zA-Z] ", string))

def longest_common_prefix(string1, string2):
    p = ''
    for idx, let in enumerate(string1):
        if string2[idx] == let:
            p += let
        else:
            break
    return p
