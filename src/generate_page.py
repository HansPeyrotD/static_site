import os

from block_markdown import markdown_to_html_node


def extract_title(markdown: str) -> str:
    for line in markdown.split("\n"):
        if line.startswith("# "):
            return line[2:].strip()
    raise Exception("no h1 header found")


def generate_page(
    from_path: str, template_path: str, dest_path: str, basepath: str = "/"
) -> None:
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    with open(from_path) as f:
        markdown = f.read()
    with open(template_path) as f:
        template = f.read()

    html = markdown_to_html_node(markdown).to_html()
    title = extract_title(markdown)
    page = template.replace("{{ Title }}", title).replace("{{ Content }}", html)
    page = page.replace('href="/', f'href="{basepath}')
    page = page.replace('src="/', f'src="{basepath}')

    dest_dir = os.path.dirname(dest_path)
    if dest_dir:
        os.makedirs(dest_dir, exist_ok=True)
    with open(dest_path, "w") as f:
        f.write(page)


def generate_pages_recursive(
    dir_path_content: str, template_path: str, dest_dir_path: str, basepath: str = "/"
) -> None:
    for name in os.listdir(dir_path_content):
        source_path = os.path.join(dir_path_content, name)
        if os.path.isfile(source_path):
            if name.endswith(".md"):
                dest_path = os.path.join(dest_dir_path, name[:-3] + ".html")
                generate_page(source_path, template_path, dest_path, basepath)
        else:
            generate_pages_recursive(
                source_path, template_path, os.path.join(dest_dir_path, name), basepath
            )
