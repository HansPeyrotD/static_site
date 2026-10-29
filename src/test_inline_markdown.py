import unittest

from inline_markdown import (
    extract_markdown_images,
    extract_markdown_links,
    split_nodes_delimiter,
    split_nodes_image,
    split_nodes_link,
    text_to_textnodes,
)
from textnode import TextNode, TextType


class TestSplitNodesDelimiter(unittest.TestCase):
    def test_code_delimiter(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        actual = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" word", TextType.TEXT),
        ]
        self.assertEqual(actual, expected)

    def test_bold_delimiter(self):
        node = TextNode("This has **bold** text", TextType.TEXT)
        actual = split_nodes_delimiter([node], "**", TextType.BOLD)
        expected = [
            TextNode("This has ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertEqual(actual, expected)

    def test_italic_delimiter(self):
        node = TextNode("This has _italic_ text", TextType.TEXT)
        actual = split_nodes_delimiter([node], "_", TextType.ITALIC)
        expected = [
            TextNode("This has ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertEqual(actual, expected)

    def test_non_text_nodes_are_unchanged(self):
        node = TextNode("already bold", TextType.BOLD)
        actual = split_nodes_delimiter([node], "**", TextType.BOLD)
        expected = [TextNode("already bold", TextType.BOLD)]
        self.assertEqual(actual, expected)

    def test_multiple_nodes(self):
        nodes = [
            TextNode("This has `code`", TextType.TEXT),
            TextNode("plain", TextType.BOLD),
            TextNode(" and `more`", TextType.TEXT),
        ]
        actual = split_nodes_delimiter(nodes, "`", TextType.CODE)
        expected = [
            TextNode("This has ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode("plain", TextType.BOLD),
            TextNode(" and ", TextType.TEXT),
            TextNode("more", TextType.CODE),
        ]
        self.assertEqual(actual, expected)

    def test_missing_closing_delimiter_raises(self):
        node = TextNode("This has `broken text", TextType.TEXT)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "`", TextType.CODE)


class TestExtractMarkdown(unittest.TestCase):
    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_multiple_images(self):
        text = "![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        self.assertListEqual(
            [
                ("rick roll", "https://i.imgur.com/aKaOqIh.gif"),
                ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg"),
            ],
            extract_markdown_images(text),
        )

    def test_extract_markdown_links(self):
        text = "a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        self.assertListEqual(
            [
                ("to boot dev", "https://www.boot.dev"),
                ("to youtube", "https://www.youtube.com/@bootdotdev"),
            ],
            extract_markdown_links(text),
        )

    def test_links_ignore_images(self):
        text = "![image](https://a.com/i.png) and [link](https://a.com)"
        self.assertListEqual([("link", "https://a.com")], extract_markdown_links(text))

    def test_images_ignore_links(self):
        text = "![image](https://a.com/i.png) and [link](https://a.com)"
        self.assertListEqual(
            [("image", "https://a.com/i.png")], extract_markdown_images(text)
        )

    def test_no_matches(self):
        self.assertListEqual([], extract_markdown_images("plain text"))
        self.assertListEqual([], extract_markdown_links("plain text"))


class TestSplitNodesImageLink(unittest.TestCase):
    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            split_nodes_image([node]),
        )

    def test_split_links(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )
        self.assertListEqual(
            [
                TextNode("This is text with a link ", TextType.TEXT),
                TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
                TextNode(" and ", TextType.TEXT),
                TextNode(
                    "to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"
                ),
            ],
            split_nodes_link([node]),
        )

    def test_split_image_at_start_and_trailing_text(self):
        node = TextNode("![a](u1) tail", TextType.TEXT)
        self.assertListEqual(
            [TextNode("a", TextType.IMAGE, "u1"), TextNode(" tail", TextType.TEXT)],
            split_nodes_image([node]),
        )

    def test_split_no_matches(self):
        node = TextNode("just text", TextType.TEXT)
        self.assertListEqual([node], split_nodes_image([node]))
        self.assertListEqual([node], split_nodes_link([node]))

    def test_split_non_text_nodes_unchanged(self):
        node = TextNode("[x](y)", TextType.CODE)
        self.assertListEqual([node], split_nodes_link([node]))

    def test_split_links_leaves_images(self):
        node = TextNode("![img](u1) and [link](u2)", TextType.TEXT)
        self.assertListEqual(
            [
                TextNode("![img](u1) and ", TextType.TEXT),
                TextNode("link", TextType.LINK, "u2"),
            ],
            split_nodes_link([node]),
        )


class TestTextToTextNodes(unittest.TestCase):
    def test_full_text(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode(
                    "obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"
                ),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            text_to_textnodes(text),
        )

    def test_plain_text(self):
        self.assertListEqual(
            [TextNode("hello", TextType.TEXT)], text_to_textnodes("hello")
        )


if __name__ == "__main__":
    unittest.main()
