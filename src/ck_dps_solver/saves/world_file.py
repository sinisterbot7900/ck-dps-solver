"""Read containers (chests) and the player's position from a Core Keeper world file.

A world file (<n>.world.gzip) is Brotli-compressed Unity Entities data ("DOTSBIN!"). Layout, as decoded from
a 1.3 world (component type names are stripped, so components are found by their data):
  - A node table near the end of the file lists sections as (data offset, size).
  - Archetype section: type count, stable type hashes, then per archetype (entity count, type count, type indices).
  - Chunk section: 16 KB chunks. Chunk header: archetype index at byte 0, entity count at byte 16.
    Component arrays follow (one entry per entity), e.g. positions as float3 (x, 0, z).
  - Buffer patch section: chunk count, then per chunk a record count and (offset in chunk, size, data) records.
    Item slot buffers bigger than their inline capacity (10 slots) are stored here; chest contents are
    (objectID, amount, variation) slots, 12 bytes each.
"""
from dataclasses import dataclass, field
import math
import struct

import numpy as np

CHUNK_SIZE = 16384
SLOT_BYTES = 12
INLINE_SLOTS = 10
BUFFER_STRIDE = 16 + INLINE_SLOTS * SLOT_BYTES # BufferHeader + inline slots


@dataclass
class Container:
    object_id: int        # The container's own object (e.g. a chest type)
    x: float
    z: float
    slots: list = field(default_factory=list) # (objectID, amount, variation)


@dataclass
class World:
    raw: bytes
    type_hashes: list
    archetypes: list      # [{'entities', 'types'}]
    chunks: list          # [{'archetype', 'count', 'offset'}]
    patches: list         # per chunk: [(offset in chunk, size, data offset in file)]


def decompress(path):
    import brotli
    with open(path, 'rb') as f:
        return brotli.decompress(f.read())


def _sections(raw):
    """(offset, size) of the data sections listed in the node table"""
    node_table = struct.unpack_from('<q', raw, 144)[0]
    sections = set()
    for p in range(node_table, len(raw) - 72, 8):
        if struct.unpack_from('<i', raw, p + 24)[0] != 80:
            continue
        offset, size = struct.unpack_from('<qq', raw, p + 56)
        if 0 < offset < len(raw) and 0 < size and offset + size <= len(raw):
            sections.add((offset, size))
    return sorted(sections)


def _parse_archetypes(raw, offset, size):
    n_types = struct.unpack_from('<i', raw, offset)[0]
    if not 0 < n_types < 10000 or 4 + 8 * n_types + 4 > size:
        return None
    type_hashes = list(struct.unpack_from(f'<{n_types}q', raw, offset + 4))
    p = offset + 4 + 8 * n_types
    n_arch = struct.unpack_from('<i', raw, p)[0]; p += 4
    archetypes = []
    for _ in range(n_arch):
        if p + 8 > offset + size:
            return None
        entities, n = struct.unpack_from('<2i', raw, p); p += 8
        if not 0 <= n <= n_types or p + 4 * n > offset + size:
            return None
        archetypes.append({'entities': entities, 'types': list(struct.unpack_from(f'<{n}i', raw, p))}); p += 4 * n
    return (type_hashes, archetypes) if p == offset + size else None


def read_world(path):
    raw = decompress(path)
    if raw[:8] != b'DOTSBIN!':
        raise ValueError(f'{path} is not a DOTSBIN world file')
    sections = _sections(raw)
    chunk_offset, chunk_size = max((s for s in sections if s[1] % CHUNK_SIZE == 0), key=lambda s: s[1])
    n_chunks = chunk_size // CHUNK_SIZE
    parsed = next((r for r in (_parse_archetypes(raw, o, s) for o, s in sections) if r), None)
    if parsed is None:
        raise ValueError('archetype section not found')
    type_hashes, archetypes = parsed
    chunks = []
    for k in range(n_chunks):
        archetype, _, _, _, count = struct.unpack_from('<5i', raw, chunk_offset + k * CHUNK_SIZE)
        chunks.append({'archetype': archetype, 'count': count, 'offset': chunk_offset + k * CHUNK_SIZE})
    patch_offset, patch_size = next(s for s in sections if struct.unpack_from('<i', raw, s[0])[0] == n_chunks and s[0] > chunk_offset)
    q = patch_offset + 4
    patches = []
    for _ in range(n_chunks):
        n = struct.unpack_from('<i', raw, q)[0]; q += 4
        records = []
        for _ in range(n):
            offset, size = struct.unpack_from('<2i', raw, q); q += 8
            records.append((offset, size, q)); q += size
        patches.append(records)
    if q != patch_offset + patch_size:
        raise ValueError('buffer patch section did not parse cleanly')
    return World(raw, type_hashes, archetypes, chunks, patches)


def _chunk_words(world, k):
    c = world.chunks[k]
    words = np.frombuffer(world.raw[c['offset']:c['offset'] + CHUNK_SIZE], dtype='<i4')
    return words, words.view('<f4')


def _position_array(world, k, whole_tiles=True):
    """Offset and values of a float3 (x, 0, z) array with one position per entity"""
    words, floats = _chunk_words(world, k)
    n = world.chunks[k]['count']
    for offset in range(64, CHUNK_SIZE - 12 * n + 1, 64):
        v = floats[offset // 4: offset // 4 + 3 * n].reshape(n, 3)
        xz = v[:, [0, 2]]
        if not np.all(np.isfinite(v)) or np.any((xz != 0) & (np.abs(xz) < 0.01)) or np.any(np.abs(v[:, 1]) > 1e-3) or np.any(np.abs(xz) > 1e5):
            continue
        if whole_tiles and np.any(np.abs(xz * 2 - np.round(xz * 2)) > 1e-3):
            continue
        if np.count_nonzero(np.any(np.abs(xz) >= 0.5, axis=1)) < max(1, n - 1):
            continue
        if not whole_tiles and np.all(np.isin(np.round(xz, 3), (0., 1.))):
            continue # e.g. a (1, 0, 0) scale/direction vector
        return offset, v
    return None, None


def _object_id_array(world, k, object_ids):
    """Offset and values of an (objectID, amount, variation) array where every entity's id is a known object"""
    words, _ = _chunk_words(world, k)
    n = world.chunks[k]['count']
    for offset in range(64, CHUNK_SIZE - 12 * n + 1, 64):
        v = words[offset // 4: offset // 4 + 3 * n].reshape(n, 3)
        if all(int(i) in object_ids for i in v[:, 0]):
            return offset, v
    return None, None


def _slot_buffer_base(world, k):
    """Start of the item slot buffer array. Buffers stored in patch records have zeroed headers in the chunk;
    the others are inline and must have a valid header (length <= capacity 10)."""
    words, _ = _chunk_words(world, k)
    n = world.chunks[k]['count']
    offsets = [o for o, size, _ in world.patches[k] if size % SLOT_BYTES == 0]
    for base in range(64, CHUNK_SIZE - BUFFER_STRIDE * n + 1, 4):
        if any((o - base) % BUFFER_STRIDE or not 0 <= (o - base) // BUFFER_STRIDE < n for o in offsets):
            continue
        external = {(o - base) // BUFFER_STRIDE for o in offsets}
        ok = True
        for i in range(n):
            if i in external:
                continue
            h = (base + BUFFER_STRIDE * i) // 4
            length, capacity = int(words[h + 2]), int(words[h + 3])
            if capacity not in (0, INLINE_SLOTS) or not 0 <= length <= INLINE_SLOTS:
                ok = False
                break
        if ok:
            return base
    return None


def containers(world, container_object_ids, all_object_ids):
    """Every container entity (e.g. chests): its object, position and slots"""
    found = []
    for k, chunk in enumerate(world.chunks):
        if chunk['count'] == 0 or not any(size % SLOT_BYTES == 0 and size >= SLOT_BYTES * INLINE_SLOTS for _, size, _ in world.patches[k]):
            continue
        _, ids = _object_id_array(world, k, all_object_ids)
        if ids is None or not any(int(i) in container_object_ids for i in ids[:, 0]):
            continue
        _, positions = _position_array(world, k)
        base = _slot_buffer_base(world, k)
        if positions is None or base is None:
            continue
        words, _ = _chunk_words(world, k)
        external = {(o - base) // BUFFER_STRIDE: (size, q) for o, size, q in world.patches[k] if size % SLOT_BYTES == 0}
        for i in range(chunk['count']):
            if int(ids[i, 0]) not in container_object_ids:
                continue
            if i in external:
                size, q = external[i]
                slots = np.frombuffer(world.raw[q:q + size], dtype='<i4').reshape(-1, 3)
            else:
                h = (base + BUFFER_STRIDE * i) // 4
                slots = words[h + 4: h + 4 + 3 * INLINE_SLOTS].reshape(-1, 3)
            found.append(Container(int(ids[i, 0]), float(positions[i, 0]), float(positions[i, 2]),
                                   [(int(a), int(b), int(c)) for a, b, c in slots if a]))
    return found


TALENT_STRIDE = 16 + 16 * 8 # BufferHeader + 16 inline (talent id, points) pairs


def pet_talent_lists(world, talent_ids):
    """Talent slots of every pet in the world: lists of (talent id, points).
    Pets keep their talents on separate entities (not in the chest slot), as a buffer of (talent, points) pairs."""
    found = []
    for k, chunk in enumerate(world.chunks):
        n = chunk['count']
        if n == 0:
            continue
        words, _ = _chunk_words(world, k)
        # Candidate buffer starts: a header with capacity 16 and a plausible length, at offsets 16-byte aligned
        for base in range(64, CHUNK_SIZE - TALENT_STRIDE * n + 1, 16):
            h = base // 4
            if int(words[h + 3]) != 16 or not 1 <= int(words[h + 2]) <= 16:
                continue
            lists = []
            for i in range(n):
                hi = (base + TALENT_STRIDE * i) // 4
                length, capacity = int(words[hi + 2]), int(words[hi + 3])
                pairs = [(int(words[hi + 4 + 2 * j]), int(words[hi + 5 + 2 * j])) for j in range(length)] if capacity == 16 else None
                if pairs is None or not 1 <= length <= 16 or any(t not in talent_ids or p not in (0, 1) for t, p in pairs):
                    lists = None
                    break
                lists.append(pairs)
            if lists:
                found += lists
                break
    return found


def player_position(world, inventory_object_ids):
    """(x, z) of the player whose inventory starts with these object ids, or None"""
    wanted = [i for i in inventory_object_ids[:20]]
    for k, records in enumerate(world.patches):
        for record_offset, size, q in records:
            if size % SLOT_BYTES or size < SLOT_BYTES * len(wanted):
                continue
            slots = np.frombuffer(world.raw[q:q + SLOT_BYTES * len(wanted)], dtype='<i4').reshape(-1, 3)
            if [int(i) for i in slots[:, 0]] != wanted:
                continue
            if world.chunks[k]['count'] > 1:
                # The player shares the chunk with other entities (e.g. pets): find which one owns this inventory
                base = _slot_buffer_base(world, k)
                _, positions = _position_array(world, k, whole_tiles=False)
                if base is not None and positions is not None and (record_offset - base) % BUFFER_STRIDE == 0:
                    i = (record_offset - base) // BUFFER_STRIDE
                    if 0 <= i < len(positions):
                        return float(positions[i, 0]), float(positions[i, 2])
                continue
            if world.chunks[k]['count'] == 1:
                # The player's chunk has several (x, 0, z) arrays (direction, scale, ...); the position is the one
                # farthest from the origin, since the others stay near unit length
                _, floats = _chunk_words(world, k)
                best = None
                for offset in range(64, CHUNK_SIZE - 12 + 1, 64):
                    x, y, z = (float(v) for v in floats[offset // 4: offset // 4 + 3])
                    if all(math.isfinite(v) and abs(v) < 1e5 for v in (x, y, z)) and abs(y) < 1e-3 and (abs(x) >= 0.01 or abs(z) >= 0.01):
                        if best is None or math.hypot(x, z) > math.hypot(*best):
                            best = (x, z)
                return best
    return None
