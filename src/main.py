from textnode import TextNode, TextType
from markdown_to_nodes import markdown_to_html_node
import os, shutil, os.path, re
import sys

from markdown_to_nodes import create_quote_parent_node

def migrate(source, target):
    # Migrates all contents from the source directory to the target directory.
    # NB: This deletes everything in target! Be careful with it!
    if os.path.exists(target):
        shutil.rmtree(target)
    os.mkdir(target)
    for item in os.listdir(source):
        if os.path.isdir(os.path.join(source, item)):
            migrate(os.path.join(source, item), os.path.join(target, item))
        elif os.path.isfile(os.path.join(source, item)):
            shutil.copy(os.path.join(source, item), os.path.join(target, item))

def extract_title(markdown):
    # Pulls the (first) h1 header from markdown.
    # Raises an exception if there's no h1 header.
    lines = markdown.split("\n")
    for line in lines:
        if re.match(r"# ", line):
            return line[2:]
    raise Exception("No header found!")

def generate_page(from_path, template_path, dest_path, basepath):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    if not os.path.exists(from_path) or not os.path.isfile(from_path):
        raise Exception(f"No file exists at {from_path}")
    if not os.path.exists(template_path) or not os.path.isfile(template_path):
        raise Exception(f"No file exists at {template_path}")
    with open(from_path, "r") as f:
        md = f.read()
    with open(template_path, "r") as f:
        template = f.read()
    html = markdown_to_html_node(md).to_html()
    title = extract_title(md)
    template = template.replace("{{ Title }}", title)
    template = template.replace("{{ Content }}", html)
    template = template.replace("href=\"/", f"href=\"{basepath}")
    template = template.replace("src=\"/", f"src=\"{basepath}")
    # We need to do some funny nonsense with dest_path to make sure
    # that all of the intermediate directories exist.
    split_dest_path = dest_path.split("/")
    partial_path = ""
    for directory in split_dest_path[:-1]:
        partial_path = os.path.join(partial_path, directory)
        if not os.path.isdir(partial_path):
            os.mkdir(partial_path)
    with open(dest_path, "w") as f:
        f.write(template)

def generate_pages_recursive(from_path, template_path, dest_path, basepath):
    if os.path.isfile(from_path) and from_path[-3:] == ".md":
        if dest_path[-3:] == ".md":
            dest_path = dest_path[:-3] + ".html"
        generate_page(from_path, template_path, dest_path, basepath)
        return
    for item in os.listdir(from_path):
        generate_pages_recursive(os.path.join(from_path, item), template_path, os.path.join(dest_path, item), basepath)
    return



def main(basepath):
    migrate('static', 'docs')
    generate_pages_recursive("content", "template.html", "docs", basepath)

if __name__ == "__main__":
    args = sys.argv
    if len(args) > 1:
        basepath = args[1]
    else:
        basepath = "/"
    main(basepath)