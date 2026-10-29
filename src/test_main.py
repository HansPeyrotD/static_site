import unittest
from unittest.mock import patch

from main import main


class TestMain(unittest.TestCase):
    def test_build_uses_docs_and_cli_basepath(self):
        for args, basepath in (
            (["main.py"], "/"),
            (["main.py", "/test-repo/"], "/test-repo/"),
        ):
            with (
                self.subTest(args=args),
                patch("main.sys.argv", args),
                patch("main.copy_directory") as copy_directory,
                patch("main.generate_pages_recursive") as generate_pages,
            ):
                main()

                copy_directory.assert_called_once_with("static", "docs")
                generate_pages.assert_called_once_with(
                    "content", "template.html", "docs", basepath
                )


if __name__ == "__main__":
    unittest.main()
