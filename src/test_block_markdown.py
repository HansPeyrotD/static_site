import unittest

from block_markdown import (
    BlockType,
    block_to_block_type,
    markdown_to_blocks,
    markdown_to_html_node,
)


class TestMarkdownToBlocks(unittest.TestCase):
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

    def test_excessive_newlines(self):
        md = "one\n\n\n\n\ntwo\n\n\n"
        self.assertEqual(markdown_to_blocks(md), ["one", "two"])

    def test_empty(self):
        self.assertEqual(markdown_to_blocks(""), [])
        self.assertEqual(markdown_to_blocks("\n\n  \n\n"), [])


class TestBlockToBlockType(unittest.TestCase):
    def test_headings(self):
        for level in range(1, 7):
            self.assertEqual(
                block_to_block_type("#" * level + " heading"), BlockType.HEADING
            )

    def test_bad_headings(self):
        self.assertEqual(block_to_block_type("####### heading"), BlockType.PARAGRAPH)
        self.assertEqual(block_to_block_type("#heading"), BlockType.PARAGRAPH)

    def test_code(self):
        self.assertEqual(block_to_block_type("```\ncode\n```"), BlockType.CODE)
        self.assertEqual(block_to_block_type("```\na\nb\n```"), BlockType.CODE)

    def test_bad_code(self):
        self.assertEqual(block_to_block_type("```code```"), BlockType.PARAGRAPH)
        self.assertEqual(block_to_block_type("```\ncode"), BlockType.PARAGRAPH)

    def test_quote(self):
        self.assertEqual(block_to_block_type("> a\n> b"), BlockType.QUOTE)
        self.assertEqual(block_to_block_type(">a\n>b"), BlockType.QUOTE)

    def test_bad_quote(self):
        self.assertEqual(block_to_block_type("> a\nb"), BlockType.PARAGRAPH)

    def test_unordered_list(self):
        self.assertEqual(block_to_block_type("- a\n- b\n- c"), BlockType.UNORDERED_LIST)

    def test_bad_unordered_list(self):
        self.assertEqual(block_to_block_type("- a\n-b"), BlockType.PARAGRAPH)

    def test_ordered_list(self):
        self.assertEqual(block_to_block_type("1. a\n2. b\n3. c"), BlockType.ORDERED_LIST)

    def test_bad_ordered_list(self):
        self.assertEqual(block_to_block_type("1. a\n3. b"), BlockType.PARAGRAPH)
        self.assertEqual(block_to_block_type("2. a\n3. b"), BlockType.PARAGRAPH)

    def test_paragraph(self):
        self.assertEqual(block_to_block_type("just some text"), BlockType.PARAGRAPH)


class TestMarkdownToHtmlNode(unittest.TestCase):
    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""
        html = markdown_to_html_node(md).to_html()
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
        html = markdown_to_html_node(md).to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

    def test_headings(self):
        md = "# one\n\n### three with **bold**"
        html = markdown_to_html_node(md).to_html()
        self.assertEqual(html, "<div><h1>one</h1><h3>three with <b>bold</b></h3></div>")

    def test_quote(self):
        md = "> a quote\n> on two lines"
        html = markdown_to_html_node(md).to_html()
        self.assertEqual(html, "<div><blockquote>a quote on two lines</blockquote></div>")

    def test_unordered_list(self):
        md = "- one\n- two with _italic_"
        html = markdown_to_html_node(md).to_html()
        self.assertEqual(
            html, "<div><ul><li>one</li><li>two with <i>italic</i></li></ul></div>"
        )

    def test_ordered_list(self):
        md = "1. one\n2. two"
        html = markdown_to_html_node(md).to_html()
        self.assertEqual(html, "<div><ol><li>one</li><li>two</li></ol></div>")

    def test_mixed_document(self):
        md = "# Title\n\nText with a [link](https://boot.dev)\n\n- a\n- b"
        html = markdown_to_html_node(md).to_html()
        self.assertEqual(
            html,
            '<div><h1>Title</h1><p>Text with a <a href="https://boot.dev">link</a></p><ul><li>a</li><li>b</li></ul></div>',
        )


if __name__ == "__main__":
    unittest.main()
