import os
import shutil
import sys
from jinja2 import Environment, FileSystemLoader

# Add parent directory to path to import from main.py if needed,
# but we will just reimplement the necessary parts to avoid FastAPI/Request deps
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Try importing logic from main to ensure consistency
    from main import load_posts, POSTS_DIR
except ImportError:
    # Fallback if imports fail (e.g. deps missing in current env)
    print("Could not import from main, ensure dependencies are installed.")
    sys.exit(1)

OUTPUT_DIR = "_site"
STATIC_DIR = "static"
TEMPLATES_DIR = "templates"


def build():
    # 1. Clean and create output directory
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)

    # 2. Copy static files
    output_static = os.path.join(OUTPUT_DIR, "static")
    if os.path.exists(STATIC_DIR):
        shutil.copytree(STATIC_DIR, output_static)

    # 3. Setup Jinja2
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

    # 4. Generate Index
    posts = load_posts()
    index_template = env.get_template("index.html")
    # Mocking request object as None or expected dict since templates might use it
    # Looking at index.html, usually url_for is used.
    # We need to provide a custom url_for or ensure templates handle static logic.
    # Because we are moving to static, `url_for` in templates will fail if we don't provide it
    # or if we don't pass a mock request.
    # Use a simple url_for helper.

    def url_for(name, **path_params):
        if name == "static":
            return f"/static/{path_params['path']}"
        if name == "read_post":
            return f"/blog/{path_params['slug']}.html"
        return "/"

    # Jinja globals to replace FastAPI's standard context
    env.globals["url_for"] = url_for
    # Some templates might access request.url_for, need to check templates usage
    # If templates strictly use {{ url_for(...) }}, env.globals works.
    # If they use {{ request.url_for(...) }}, we need a mock request.

    class MockRequest:
        def __init__(self):
            pass

        def url_for(self, name, **path_params):
            return url_for(name, **path_params)

    mock_request = MockRequest()

    index_html = index_template.render(request=mock_request, posts=posts)
    with open(os.path.join(OUTPUT_DIR, "index.html"), "w") as f:
        f.write(index_html)

    # 5. Generate Posts
    # Create blog directory
    blog_output_dir = os.path.join(OUTPUT_DIR, "blog")
    os.makedirs(blog_output_dir, exist_ok=True)

    post_template = env.get_template("post.html")

    for post in posts:
        slug = post["slug"]
        post_html = post_template.render(request=mock_request, post=post)

        # Determine output path. matching /blog/{slug} route
        # Using {slug}.html
        post_path = os.path.join(blog_output_dir, f"{slug}.html")
        with open(post_path, "w") as f:
            f.write(post_html)

    print(f"Build complete. Site generated in {OUTPUT_DIR}")


if __name__ == "__main__":
    build()
