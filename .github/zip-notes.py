# Discord zip post for both games: new README titles of D1 and D2, grouped by README section,
# tagged "(D1 only)" / "(D2 only)" when only one game has them, after a "New Dxx-Models-Textures" section
# for each game whose model/texture pack changed in this push. Run by zip-notify.yml.
# usage: zip-notes.py <d1 repo> <d2 repo> <d1 zip url> <d2 zip url> <d1 models url> <d2 models url>
import difflib, re, subprocess, sys

GROUPS = {'Multiplayer': 'SLikeNet & Network', 'Running several copies on one PC': 'SLikeNet & Network',
          'Observers': 'Features & Options', 'Demos': 'Features & Options', 'HUD and options': 'Features & Options',
          'BugFixes': 'Bug Fixes'}
ORDER = ['SLikeNet & Network', 'Features & Options', 'Bug Fixes']
ZIP = {0: 'download/D1x-Redux-SLikeNet.zip', 1: 'download/D2x-Redux-SLikeNet.zip'}
MODELS = {0: 'download/D1x-Models-Textures.zip', 1: 'download/D2x-Models-Textures.zip'}

def git(repo, *a):
    return subprocess.run(['git', '-C', repo] + list(a), capture_output=True, text=True, encoding='utf-8').stdout

def title(line):
    return re.sub(r'[.:]+$', '', re.match(r'- \*\*([^*]+)\*\*', line).group(1)).strip()

def sections(repo, rev):
    # README title -> the "## " section it sits in
    section, where = None, {}
    for l in git(repo, 'show', rev + ':README.md').splitlines():
        if l.startswith('## '): section = l[3:].strip()
        elif l.startswith('- **'): where.setdefault(title(l), section)
    return where

def new_titles(repo, prev, cur):
    # Titles added between two commits. An added title that nearly matches a removed one in the same
    # section is a fixed typo, so it is not new; an entry moved to another section is listed again.
    removed, added = [], []
    for l in git(repo, 'diff', prev, cur, '--', 'README.md').splitlines():
        if l.startswith('-- **'): removed.append(title(l[1:]))
        elif l.startswith('+- **'): added.append(title(l[1:]))
    if not added: return []
    was, where = sections(repo, prev), sections(repo, cur)
    for t in list(added):
        old = next((r for r in removed if was.get(r) == where.get(t) and
                    difflib.SequenceMatcher(None, r.lower(), t.lower()).ratio() >= 0.8), None)
        if old is not None:
            removed.remove(old)
            added.remove(t)
    if not added: return []
    return [(GROUPS.get(where.get(t), where.get(t) or 'Other'), t) for t in dict.fromkeys(added)]

repos, urls, model_urls = sys.argv[1:3], sys.argv[3:5], sys.argv[5:7]
zips = [git(r, 'log', '-n', '10', '--format=%H', '--', ZIP[i]).split() for i, r in enumerate(repos)]
# Newest zip pushes first; with no new titles, walk both games back to the last pair that had some.
found = [[], []]
for k in range(1, 10):
    for i, r in enumerate(repos):
        found[i] = new_titles(r, zips[i][k], 'HEAD' if k == 1 else zips[i][k - 1]) if len(zips[i]) > k else []
    if found[0] or found[1]: break

key = lambda t: re.sub(r'[^a-z0-9]', '', t.lower())
k1, k2 = {key(t) for _, t in found[0]}, {key(t) for _, t in found[1]}
rows = [(g, t + ('' if key(t) in k2 else ' *(D1 only)*')) for g, t in found[0]]
rows += [(g, t + ' *(D2 only)*') for g, t in found[1] if key(t) not in k1]

# A game's model/texture pack is listed when its repo's newest commit changed it (F7 commits it with the game zip)
models = [i for i, r in enumerate(repos) if git(r, 'diff', '--name-only', 'HEAD~1', 'HEAD', '--', MODELS[i]).strip()]
# A push of only the packs (the D2 game zip unchanged) posts just the links, not the Update History again
if models and not git(repos[1], 'diff', '--name-only', 'HEAD~1', 'HEAD', '--', ZIP[1]).strip():
    rows = []
lines = []
if models:
    lines.append('## New **Dxx-Models-Textures** ' + '/'.join(('D1', 'D2')[i] for i in models))
    for i in models:
        lines += ['- **%s DXA Files**' % ('D1', 'D2')[i], model_urls[i]]
lines += ['## New **D1x-SLikeNet**', urls[0], '## New **D2x-SLikeNet**', urls[1]]
if rows:
    lines.append('## Update History:')
msg = '\n'.join(lines)
for g in ORDER + sorted({g for g, _ in rows} - set(ORDER)):
    items = [t for gg, t in rows if gg == g]
    if not items: continue
    block = '\n**%s**' % g + ''.join('\n- ' + t for t in items)
    if len(msg) + len(block) > 1900:
        msg += '\n- ...and more in the README'
        break
    msg += block
print(msg)
