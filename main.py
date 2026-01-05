import os
import glob
import markdown
import frontmatter
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

POSTS_DIR = "posts"

def load_posts():
    posts = []
    if not os.path.exists(POSTS_DIR):
        return []
    
    files = glob.glob(os.path.join(POSTS_DIR, "*.md"))
    for file_path in files:
        with open(file_path, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)
            # Create slug from filename
            filename = os.path.basename(file_path)
            slug = os.path.splitext(filename)[0]
            
            posts.append({
                "slug": slug,
                "title": post.get("title", "Untitled"),
                "date": post.get("date", "1970-01-01"),
                "content": markdown.markdown(post.content, extensions=['fenced_code', 'codehilite'])
            })
    
    # Sort posts by date descending
    posts.sort(key=lambda x: str(x["date"]), reverse=True)
    return posts

def get_post(slug):
    file_path = os.path.join(POSTS_DIR, f"{slug}.md")
    if not os.path.exists(file_path):
        return None
    
    with open(file_path, "r", encoding="utf-8") as f:
        post = frontmatter.load(f)
        return {
            "slug": slug,
            "title": post.get("title", "Untitled"),
            "date": post.get("date", "1970-01-01"),
            "content": markdown.markdown(post.content, extensions=['fenced_code', 'codehilite'])
        }

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    posts = load_posts()
    return templates.TemplateResponse("index.html", {"request": request, "posts": posts})

@app.get("/blog/{slug}", response_class=HTMLResponse)
async def read_post(request: Request, slug: str):
    post = get_post(slug)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return templates.TemplateResponse("post.html", {"request": request, "post": post})
