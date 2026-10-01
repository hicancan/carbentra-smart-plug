"""Compare native solids across OCC versions without relying on BRep text order.

The 1e-6 mm bounding-box tolerance is one nanometre. The 1e-3 mm3
symmetric-difference limit is absolute, never a percentage of a large assembly.
Manufacturing clearance, insulation and release gates are evaluated separately.
"""
import re

def bounds(shape):
    return tuple(getattr(shape.BoundBox, key) for key in
                 ('XMin', 'YMin', 'ZMin', 'XMax', 'YMax', 'ZMax'))

def compare_shapes(left, right):
    bbox_delta = max(abs(a-b) for a, b in zip(bounds(left), bounds(right)))
    volume_delta = abs(left.Volume-right.Volume)
    area_delta = abs(left.Area-right.Area)
    valid = left.isValid() and right.isValid()
    topology = len(left.Solids) == len(right.Solids) and bool(left.Solids)
    # Run exact OCC Boolean differences; a matching box/volume alone is not proof.
    symmetric_difference = left.cut(right).Volume + right.cut(left).Volume
    return {'passed': valid and topology and bbox_delta <= 1e-6 and
            volume_delta <= 1e-3 and area_delta <= 1e-3 and symmetric_difference <= 1e-3,
            'valid_solids': valid, 'solid_count_equal': topology,
            'bbox_max_difference_mm': bbox_delta, 'volume_difference_mm3': volume_delta,
            'area_difference_mm2': area_delta,
            'symmetric_difference_mm3': symmetric_difference}

def grouped_shapes(document):
    groups = {}
    for obj in document.Objects:
        if hasattr(obj, 'Shape') and not obj.Shape.isNull():
            # Duplicate pin numbers receive different automatic names as KiCad
            # changes pad iteration order. Match the exact component's tail multiset.
            key = re.sub(r'_Tail.*$', '_Tail', obj.Name)
            groups.setdefault(key, []).append((obj.Name, obj.Shape))
    for objects in groups.values():
        objects.sort(key=lambda item: bounds(item[1]))
    return groups

def negative_controls(Part, Vector):
    cube = Part.makeBox(2, 2, 2)
    moved = cube.copy(); moved.translate(Vector(.001, 0, 0))
    bored = cube.cut(Part.makeCylinder(.1, 2, Vector(1, 1, 0)))
    result = {'identical_passes': compare_shapes(cube, cube.copy())['passed'],
              'one_micrometre_shift_rejected': not compare_shapes(cube, moved)['passed'],
              'removed_material_rejected': not compare_shapes(cube, bored)['passed']}
    assert all(result.values()), result
    return result
