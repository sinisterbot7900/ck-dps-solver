"""Pets as solver items, from the wiki's pet data and the talents a pet has learned.

Buff pets (e.g. Owlux) give their owner their built-in bonuses plus the buff value of each learned talent.
Other pets fight on their own: their damage isn't modeled, but poison or burning they apply to targets counts for
"against poisoned/burning targets" bonuses. A pet's poison counts as keeping targets poisoned (its attack rate isn't
known), but it isn't poison you apply (the Ivy set needs that).
"""
from ck_dps_solver.model import Item

from ck_dps_solver.model.item_stats import CONDITION_ATTRIBUTES, scale_condition, wiki_data

# In-game values that differ from the (older) wiki pet data: talent -> value per learned talent.
# Empty: Triple Trouble's 2% per talent was confirmed in game (2026-10-12).
TALENT_VALUE_OVERRIDES = {}
# Conditions an attacking pet applies to targets that matter for its owner's bonuses
TARGET_EFFECTS = {'ChanceToApplyPoisoned', 'ApplyBurning'}


def pet_type(internal_id):
    return wiki_data()['equipment'][internal_id].get('pet', {}).get('type')


def talents_by_id():
    return {t['id']: (name, t) for name, t in wiki_data()['pets']['talents'].items()}


def pet_item(internal_id, learned_talents=()):
    """Item for a pet. learned_talents: wiki talent ids the pet has learned (an id can repeat)."""
    record = wiki_data()['equipment'][internal_id]
    buff_pet = pet_type(internal_id) == 'Buff'
    attributes = {}

    def add(condition, value):
        attribute = CONDITION_ATTRIBUTES.get(condition)
        if attribute == '%_chance_to_apply_poison' and not buff_pet:
            attribute = '%_pet_poison_chance' # The pet's own attacks poison
        if attribute is not None and value:
            attributes[attribute] = round(attributes.get(attribute, 0) + value, 4)

    for condition in record.get('conditions', []):
        if buff_pet or condition['id'] in TARGET_EFFECTS:
            add(condition['id'], scale_condition(condition['id'], condition['value']))
    talents = talents_by_id()
    for talent_id in learned_talents:
        name, talent = talents.get(talent_id, (None, None))
        if talent is None or not (buff_pet or talent['condition'] in TARGET_EFFECTS):
            continue
        if name in TALENT_VALUE_OVERRIDES:
            value = TALENT_VALUE_OVERRIDES[name]
        else:
            raw = talent.get('buffValue') if buff_pet else talent.get('value')
            value = scale_condition(talent['condition'], raw or 0)
        add(talent['condition'], value)
    return Item(name=record['name'], item_category='Pet', consider_for='Both', attributes=attributes)


def talent_display_name(talent_name, buff_pet=True):
    names = wiki_data()['pets']['talents'][talent_name].get('displayName', {})
    return names.get('buff' if buff_pet else 'melee') or names.get('range') or talent_name


def catalogue_pets(talent_points=5, talents_to_try=None):
    """Every pet that can affect your damage, as if it had learned `talent_points` talents.
    Buff pets: one version per talent that changes a solver attribute, with all points in that talent
    (e.g. "Owlux (5x Triple Trouble)"). talents_to_try: talent names to make versions for (None = every useful one).
    Other pets: their effect on targets (poison, burning) only."""
    pets_data = wiki_data()['pets']
    talents = pets_data['talents']
    found = []
    for internal_id in pets_data['pets']:
        pet = wiki_data()['equipment'][internal_id].get('pet', {})
        if pet.get('type') == 'Buff':
            versions = []
            for talent_name in pet.get('talents', []):
                talent = talents.get(talent_name)
                if talent is None or CONDITION_ATTRIBUTES.get(talent['condition']) is None or (talents_to_try is not None and talent_name not in talents_to_try):
                    continue
                item = pet_item(internal_id, [talent['id']] * talent_points)
                item.name = f"{item.name} ({talent_points}x {talent_display_name(talent_name)})"
                versions.append(item)
            found += versions
        else:
            item = pet_item(internal_id)
            if any(item.attributes.values()):
                found.append(item)
    return found


def species_for_talents(talent_ids):
    """Pets whose talent pool contains every one of these talent ids (a pet rolls its talent slots from its pool)"""
    by_id = talents_by_id()
    names = {by_id[t][0] for t in talent_ids if t in by_id}
    return [internal_id for internal_id in wiki_data()['pets']['pets']
            if names and names <= set(wiki_data()['equipment'][internal_id].get('pet', {}).get('talents', []))]


def learned_talents_from_aux(aux_json):
    """Learned talent ids from a pet's inventory aux data in a character save ({"prefabs": [...]})"""
    import json
    learned = []
    for prefab in (json.loads(aux_json) if aux_json else {}).get('prefabs', []):
        for component in prefab.get('types', []):
            for entry in component.get('data', []):
                try:
                    talent = json.loads(entry)
                except (TypeError, ValueError):
                    continue
                if isinstance(talent, dict) and 'Talent' in talent and talent.get('Points', 0) > 0:
                    learned.append(talent['Talent'])
    return learned
