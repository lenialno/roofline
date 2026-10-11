#!/usr/bin/env python3
"""Repository checks for Roofline. Stdlib only. Exit 1 on any failure.

- skills: SKILL.md frontmatter parses, name equals the directory, description 1..1024 chars,
  English skills do not reference -ru skills, the set of EN and RU skills matches
- typography in prose (outside code fences): no em or en dash, no arrows, no curly quotes
- relative links in Markdown resolve to existing files
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
errors = []


def frontmatter(path):
    text = open(path, encoding="utf-8").read()
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    fields = {}
    for line in m.group(1).splitlines():
        km = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if not km:
            continue
        key, value = km.group(1), km.group(2).strip()
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
        elif ": " in value:
            errors.append("%s: frontmatter %s has ': ' and is not quoted (strict YAML parsers reject it)" % (path, key))
        fields[key] = value
    return fields


skills = sorted(glob.glob("skills/*/SKILL.md"))
names = set()
for path in skills:
    d = os.path.basename(os.path.dirname(path))
    fm = frontmatter(path)
    if fm is None:
        errors.append("%s: no frontmatter" % path)
        continue
    name, desc = fm.get("name", ""), fm.get("description", "")
    names.add(name)
    if name != d:
        errors.append("%s: name %r differs from directory %r" % (path, name, d))
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name or ""):
        errors.append("%s: name %r breaks the Agent Skills naming rule" % (path, name))
    if not 1 <= len(desc) <= 1024:
        errors.append("%s: description is %d chars, must be 1..1024" % (path, len(desc)))
    if not d.endswith("-ru") and d != "roofline-toolbox":
        body = open(path, encoding="utf-8").read()
        for m in re.finditer(r"`(roofline[a-z-]*-ru)`", body):
            errors.append("%s: English skill references Russian skill %s" % (path, m.group(1)))

en = {n for n in names if not n.endswith("-ru") and n != "roofline-toolbox"}
ru = {n[:-3] if n != "roofline-ru" else "roofline" for n in names if n.endswith("-ru")}
if en != ru:
    errors.append("EN and RU skill sets differ: only EN %s, only RU %s" % (sorted(en - ru), sorted(ru - en)))
print("skills: %d found" % len(names))

prose_files = sorted(set(
    glob.glob("skills/*/SKILL.md") + glob.glob("skills/*/references/*.md") + glob.glob("skills/*/profiles/README.md")
    + glob.glob("agents/*.md") + glob.glob("docs/roadmap-ru/*.md") + ["README.md", "README.ru.md"]
))
for path in prose_files:
    text = open(path, encoding="utf-8").read()
    prose = re.sub(r"```.*?```", "", text, flags=re.S)
    prose = re.sub(r"`[^`\n]*`", "", prose)
    prose = re.sub(r"<!--.*?-->", "", prose, flags=re.S)
    prose = re.sub(r"\]\([^)]*\)", "]()", prose)
    for pat, label in (("—", "em dash"), ("–", "en dash"), ("→", "arrow"), ("[«»“”]", "curly quotes")):
        for m in re.finditer(pat, prose):
            line = prose[: m.start()].count("\n") + 1
            errors.append("%s:%d: %s in prose" % (path, line, label))
    for m in re.finditer(r"(?<![\w-])(->|=>)(?![\w>])", prose):
        line = prose[: m.start()].count("\n") + 1
        errors.append("%s:%d: ascii arrow in prose" % (path, line))
    for m in re.finditer(r"\]\(([^)#\s]+)(#[^)]*)?\)", text):
        target = m.group(1)
        if target.startswith(("http://", "https://", "mailto:")) or "${" in target:
            continue
        if not os.path.exists(os.path.normpath(os.path.join(os.path.dirname(path), target))):
            errors.append("%s: broken link %s" % (path, target))
print("prose files: %d checked" % len(prose_files))

for e in errors:
    print("FAIL " + e)
print("result: %s" % ("OK" if not errors else "%d problem(s)" % len(errors)))
sys.exit(1 if errors else 0)
