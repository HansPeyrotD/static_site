import re

from textnode import TextNode, TextType

IMAGE_PATTERN = r"!\[([^\[\]]*)\]\(([^\(\)]*)\)"
LINK_PATTERN = r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)"


def extract_markdown_images(text: str) -> list[tuple[str, str]]:
    return re.findall(IMAGE_PATTERN, text)


def extract_markdown_links(text: str) -> list[tuple[str, str]]:
    return re.findall(LINK_PATTERN, text)


def split_nodes_delimiter(
    old_nodes: list[TextNode], delimiter: str, text_type: TextType
) -> list[TextNode]:
    new_nodes = []

    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue

        split_text = old_node.text.split(delimiter)
        if len(split_text) % 2 == 0:
            raise ValueError(f"missing closing delimiter: {delimiter}")

        for i, part in enumerate(split_text):
            if part == "":
                continue

            if i % 2 == 0:
                new_nodes.append(TextNode(part, TextType.TEXT))
            else:
                new_nodes.append(TextNode(part, text_type))

    return new_nodes


def _split_nodes_markdown(
    old_nodes: list[TextNode], extract, template: str, text_type: TextType
) -> list[TextNode]:
    new_nodes = []

    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue

        remaining = old_node.text
        for text, url in extract(old_node.text):
            before, remaining = remaining.split(template.format(text, url), 1)
            if before:
                new_nodes.append(TextNode(before, TextType.TEXT))
            new_nodes.append(TextNode(text, text_type, url))

        if remaining:
            new_nodes.append(TextNode(remaining, TextType.TEXT))

    return new_nodes


def split_nodes_image(old_nodes: list[TextNode]) -> list[TextNode]:
    return _split_nodes_markdown(
        old_nodes, extract_markdown_images, "![{}]({})", TextType.IMAGE
    )


def split_nodes_link(old_nodes: list[TextNode]) -> list[TextNode]:
    return _split_nodes_markdown(
        old_nodes, extract_markdown_links, "[{}]({})", TextType.LINK
    )


def text_to_textnodes(text: str) -> list[TextNode]:
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes
