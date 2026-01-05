import os
import argparse
import re
from datetime import datetime


def slugify(title):
    slug = title.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug


def main():
    parser = argparse.ArgumentParser(description="Create a new blog post.")
    parser.add_argument("title", help="Title of the post")
    args = parser.parse_args()

    title = args.title
    slug = slugify(title)

    posts_dir = "posts"
    images_dir = os.path.join("static", "images", slug)
    post_path = os.path.join(posts_dir, f"{slug}.md")

    # Create images directory
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
        print(f"Created directory: {images_dir}")
    else:
        print(f"Directory already exists: {images_dir}")

    # Create post file
    if os.path.exists(post_path):
        print(f"Post already exists: {post_path}")
        return

    content = f"""---
title: "{title}"
date: {datetime.now().strftime("%Y-%m-%d")}
---

# {title}

Add your content here.
"""

    with open(post_path, "w") as f:
        f.write(content)

    print(f"Created post: {post_path}")


if __name__ == "__main__":
    main()
