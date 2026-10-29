import os
import tempfile
import unittest

from generate_page import extract_title, generate_page, generate_pages_recursive


class TestGeneratePage(unittest.TestCase):
    def test_basepath_rewrites_template_links_and_content(self):
        for basepath in ("/", "/test-repo/"):
            with self.subTest(basepath=basepath), tempfile.TemporaryDirectory() as tmp:
                source = os.path.join(tmp, "index.md")
                template = os.path.join(tmp, "template.html")
                dest = os.path.join(tmp, "docs", "index.html")
                with open(source, "w") as f:
                    f.write(
                        "# Home\n\n[Post](/blog/post)\n\n"
                        "![Image](/images/example.png)\n\n"
                        "[External](https://example.com)\n\n[Relative](other.html)"
                    )
                with open(template, "w") as f:
                    f.write(
                        '<title>{{ Title }}</title><link href="/index.css">'
                        "{{ Content }}"
                    )

                generate_page(source, template, dest, basepath)

                with open(dest) as f:
                    page = f.read()
                self.assertIn("<title>Home</title>", page)
                self.assertIn(f'href="{basepath}index.css"', page)
                self.assertIn(f'href="{basepath}blog/post"', page)
                self.assertIn(f'src="{basepath}images/example.png"', page)
                self.assertIn('href="https://example.com"', page)
                self.assertIn('href="other.html"', page)
                self.assertNotIn("{{ Content }}", page)


class TestGeneratePagesRecursive(unittest.TestCase):
    def test_basepath_propagates_to_nested_pages(self):
        with tempfile.TemporaryDirectory() as tmp:
            content = os.path.join(tmp, "content")
            os.makedirs(os.path.join(content, "blog", "post"))
            for path in ("index.md", os.path.join("blog", "post", "index.md")):
                with open(os.path.join(content, path), "w") as f:
                    f.write("# Page\n\n[Home](/)")
            template = os.path.join(tmp, "template.html")
            with open(template, "w") as f:
                f.write("{{ Content }}")
            dest = os.path.join(tmp, "docs")

            generate_pages_recursive(content, template, dest, "/test-repo/")

            for path in ("index.html", os.path.join("blog", "post", "index.html")):
                with open(os.path.join(dest, path)) as f:
                    self.assertIn('href="/test-repo/"', f.read())

    def test_nested_structure(self):
        with tempfile.TemporaryDirectory() as tmp:
            content = os.path.join(tmp, "content")
            os.makedirs(os.path.join(content, "blog", "post"))
            with open(os.path.join(content, "index.md"), "w") as f:
                f.write("# Home\n\nhello")
            with open(os.path.join(content, "blog", "post", "index.md"), "w") as f:
                f.write("# Post\n\nbody")
            with open(os.path.join(content, "notes.txt"), "w") as f:
                f.write("ignored")
            template = os.path.join(tmp, "template.html")
            with open(template, "w") as f:
                f.write("<title>{{ Title }}</title>{{ Content }}")
            dest = os.path.join(tmp, "docs")

            generate_pages_recursive(content, template, dest)

            with open(os.path.join(dest, "index.html")) as f:
                self.assertEqual(
                    f.read(), "<title>Home</title><div><h1>Home</h1><p>hello</p></div>"
                )
            with open(os.path.join(dest, "blog", "post", "index.html")) as f:
                self.assertEqual(
                    f.read(), "<title>Post</title><div><h1>Post</h1><p>body</p></div>"
                )
            self.assertFalse(os.path.exists(os.path.join(dest, "notes.html")))


class TestExtractTitle(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(extract_title("# Hello"), "Hello")

    def test_strips_whitespace(self):
        self.assertEqual(extract_title("#   Hello world  "), "Hello world")

    def test_title_not_first_line(self):
        self.assertEqual(extract_title("intro\n\n# Title\n\nbody"), "Title")

    def test_ignores_h2(self):
        self.assertEqual(extract_title("## Sub\n\n# Main"), "Main")

    def test_no_h1_raises(self):
        with self.assertRaises(Exception):
            extract_title("## only h2\n\ntext")

    def test_empty_raises(self):
        with self.assertRaises(Exception):
            extract_title("")


if __name__ == "__main__":
    unittest.main()
