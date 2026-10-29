import re
from enum import Enum

from htmlnode import HTMLNode
from inline_markdown import text_to_textnodes
from parentnode import ParentNode
from textnode import TextNode, TextType, text_node_to_html_node


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


def markdown_to_blocks(markdown: str) -> list[str]:
    blocks = []
    for block in markdown.split("\n\n"):
        block = block.strip()
        if block:
            blocks.append(block)
    return blocks


def block_to_block_type(block: str) -> BlockType:
    lines = block.split("\n")

    if re.match(r"#{1,6} ", block):
        return BlockType.HEADING
    if block.startswith("```\n") and block.endswith("```") and len(block) >= 7:
        return BlockType.CODE
    if all(line.startswith(">") for line in lines):
        return BlockType.QUOTE
    if all(line.startswith("- ") for line in lines):
        return BlockType.UNORDERED_LIST
    if all(line.startswith(f"{i}. ") for i, line in enumerate(lines, start=1)):
        return BlockType.ORDERED_LIST
    return BlockType.PARAGRAPH


def text_to_children(text: str) -> list[HTMLNode]:
    return [text_node_to_html_node(node) for node in text_to_textnodes(text)]


def paragraph_to_html_node(block: str) -> HTMLNode:
    text = " ".join(block.split("\n"))
    return ParentNode("p", text_to_children(text))


def heading_to_html_node(block: str) -> HTMLNode:
    level = len(block) - len(block.lstrip("#"))
    text = block[level + 1 :]
    return ParentNode(f"h{level}", text_to_children(text))


def code_to_html_node(block: str) -> HTMLNode:
    text = block[4:-3]
    code = text_node_to_html_node(TextNode(text, TextType.CODE))
    return ParentNode("pre", [code])


def quote_to_html_node(block: str) -> HTMLNode:
    lines = [line.lstrip(">").strip() for line in block.split("\n")]
    return ParentNode("blockquote", text_to_children(" ".join(lines)))


def unordered_list_to_html_node(block: str) -> HTMLNode:
    items = [
        ParentNode("li", text_to_children(line[2:])) for line in block.split("\n")
    ]
    return ParentNode("ul", items)


def ordered_list_to_html_node(block: str) -> HTMLNode:
    items = [
        ParentNode("li", text_to_children(line.split(". ", 1)[1]))
        for line in block.split("\n")
    ]
    return ParentNode("ol", items)


def block_to_html_node(block: str) -> HTMLNode:
    block_type = block_to_block_type(block)
    if block_type == BlockType.HEADING:
        return heading_to_html_node(block)
    if block_type == BlockType.CODE:
        return code_to_html_node(block)
    if block_type == BlockType.QUOTE:
        return quote_to_html_node(block)
    if block_type == BlockType.UNORDERED_LIST:
        return unordered_list_to_html_node(block)
    if block_type == BlockType.ORDERED_LIST:
        return ordered_list_to_html_node(block)
    return paragraph_to_html_node(block)


def markdown_to_html_node(markdown: str) -> HTMLNode:
    children = [block_to_html_node(block) for block in markdown_to_blocks(markdown)]
    return ParentNode("div", children)
