"""Rewrite the ~/recent block in README.md with the repos pushed to most recently."""
import json, os, re, sys, urllib.request

USER = "ArhamAzad2004"
SKIP = {USER, f"{USER}.github.io", "nextjs-test", "test3", "Webscrapping-Test"}
COUNT = 5
START, END = "<!-- recent:start -->", "<!-- recent:end -->"


def fetch():
    req = urllib.request.Request(f"https://api.github.com/users/{USER}/repos?sort=pushed&per_page=50",
                                 headers={"Accept": "application/vnd.github+json"})
    if os.environ.get("GITHUB_TOKEN"):
        req.add_header("Authorization", f"Bearer {os.environ['GITHUB_TOKEN']}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def render(repos):
    rows = [r for r in repos if not r["fork"] and not r["archived"] and r["name"] not in SKIP][:COUNT]
    lines = []
    for r in rows:
        desc = (r.get("description") or "").strip()
        lines.append(f"- `{r['pushed_at'][:10]}` **[{r['name']}]({r['html_url']})**" + (f": {desc}" if desc else ""))
    return "\n".join(lines)


def replace(text, block):
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    if not pattern.search(text):
        sys.exit("recent markers not found in README.md")
    return pattern.sub(lambda _: f"{START}\n{block}\n{END}", text)


assert replace(f"a\n{START}\nold\n{END}\nb", "new") == f"a\n{START}\nnew\n{END}\nb"

if __name__ == "__main__":
    path = os.path.join(os.path.dirname(__file__), "..", "README.md")
    with open(path, encoding="utf-8") as f:
        text = f.read()
    new = replace(text, render(fetch()))
    if new != text:
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(new)
        print("README updated")
    else:
        print("no change")
