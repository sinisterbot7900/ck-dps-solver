"""Talent trees and the game's rules for spending talent points (from the wiki's Skills page, citing the Explorer's Guide):

- A skill gives a talent point every 5 levels, and 5 more at level 100 (25 at the most).
- A talent takes up to 5 points.
- Talents are in tiers of 1, 2, 3 and 2 talents, joined by links: each talent links to two talents of the tier below
  (the outer tier-3 talents to one), and a talent opens once a talent linked above it has all 5 points (user, from the
  game's tree):
      tier 1 -> tier 2: the talent -> both
      tier 2 -> tier 3: left -> left, middle; right -> middle, right
      tier 3 -> tier 4: left -> left; middle -> both; right -> right

Points are lists in talent tree order (the order of points in saves and in defaults.perk_trees).
"""
from ck_dps_solver.model.item_stats import wiki_data

MAX_POINTS = 5
MAX_LEVEL_BONUS = 5 # Extra points at the skill's maximum level
# Links from each tier's talents (by position, left to right) to the positions in the tier below
LINKS = [{0: [0, 1]}, {0: [0, 1], 1: [1, 2]}, {0: [0], 1: [0, 1], 2: [1]}]


def tree(skill):
    """[[(index, talent name), ...] per tier, from tier 1] for a skill"""
    names = wiki_data()['skills'][skill]['talents']
    talents = wiki_data()['talents']
    tiers = {}
    for i, name in enumerate(names):
        tiers.setdefault(int(talents.get(name, {}).get('tier', 1)), []).append((i, name))
    return [tiers[t] for t in sorted(tiers)]


def available(skill, level):
    """Talent points a skill level gives"""
    max_level = wiki_data()['skills'][skill].get('maxLevel', 100)
    return int(level) // 5 + (MAX_LEVEL_BONUS if level >= max_level else 0)


def links(skill):
    """[(talent index above, talent index below)] for a skill's tree"""
    tiers = tree(skill)
    found = []
    for t, (upper, lower) in enumerate(zip(tiers, tiers[1:])):
        for position, (i, _) in enumerate(upper):
            for below in LINKS[t].get(position, []):
                if below < len(lower):
                    found.append((i, lower[below][0]))
    return found


def parents(skill, index):
    return [a for a, b in links(skill) if b == index]


def unlocked(skill, points):
    """Talents you can spend points in: tier 1, and talents linked below a talent with 5 points that is itself open"""
    tiers = tree(skill)
    opened = {i for i, _ in tiers[0]}
    for tier in tiers[1:]:
        for i, _ in tier:
            if any(p in opened and points[p] >= MAX_POINTS for p in parents(skill, i)):
                opened.add(i)
    return opened


def is_legal(skill, level, points):
    if sum(points) > available(skill, level) or any(p < 0 or p > MAX_POINTS for p in points):
        return False
    opened = unlocked(skill, points)
    return all(p == 0 or i in opened for i, p in enumerate(points))


def why_not_add(skill, level, points, index):
    """None if a point can go into the talent, else the reason"""
    if points[index] >= MAX_POINTS:
        return 'Already at 5 points'
    if sum(points) >= available(skill, level):
        return 'No talent points left (a point every 5 levels, 5 more at level 100)'
    if index not in unlocked(skill, points):
        names = wiki_data()['skills'][skill]['talents']
        return 'Needs 5 points in ' + ' or '.join(names[p] for p in parents(skill, index))
    return None


def why_not_remove(skill, level, points, index):
    """None if a point can come out of the talent, else the reason"""
    if points[index] <= 0:
        return 'No points to remove'
    after = list(points)
    after[index] -= 1
    if not is_legal(skill, level, after):
        return 'Talents linked below depend on this one having 5 points'
    return None


def fit_to_level(skill, level, points):
    """Points made legal for a (lower) level: points come off the bottom of the tree first (the last talent, then the one
    before, up to the top) until they fit; talents whose link above closes lose theirs"""
    points = [max(0, min(MAX_POINTS, int(p))) for p in points]
    if is_legal(skill, level, points):
        return points
    tiers = tree(skill)
    order = [i for tier in reversed(tiers) for i, _ in reversed(tier)] # Deepest tier, last talent first
    while True:
        opened = unlocked(skill, points)
        closed = [i for i, p in enumerate(points) if p and i not in opened]
        for i in closed:
            points[i] = 0
        if sum(points) <= available(skill, level):
            return points
        i = next(i for i in order if points[i] > 0)
        points[i] -= 1
