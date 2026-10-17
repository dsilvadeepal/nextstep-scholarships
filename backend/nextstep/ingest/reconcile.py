"""Conservative source reconciliation: conflicting rules stay visible, never silently selected."""

import hashlib
import json
import re


def normalized(value):
    return re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()


def bind_program_ids(records, source):
    bindings = {normalized(k): v for k, v in source.program_bindings.items()}
    for record in records:
        identity = normalized(source.sponsor) + "|" + normalized(record.name)
        record.id = bindings.get(
            normalized(record.name),
            "program-" + hashlib.sha256(identity.encode()).hexdigest()[:16],
        )
    return records


def reconcile_records(records):
    merged = {}
    duplicates = 0
    conflict_ids = []
    for raw in records:
        record = raw.model_copy(deep=True)
        # Model-generated IDs can collide across independently extracted pages.
        remap = {}

        def canonical(ref, remap=remap):
            original = ref.id
            ref.id = hashlib.sha256(
                json.dumps(
                    [
                        ref.source_id,
                        ref.document_version,
                        ref.section_id,
                        ref.start,
                        ref.end,
                        ref.quote,
                    ]
                ).encode()
            ).hexdigest()[:24]
            remap[original] = ref.id

        for ref in record.evidence:
            canonical(ref)

        def condition(c):
            for ref in c.evidence:
                canonical(ref)
            for child in c.children:
                condition(child)

        for c in record.conditions:
            condition(c)
        record.field_evidence = {
            key: [remap.get(i, i) for i in ids]
            for key, ids in record.field_evidence.items()
        }
        if record.id not in merged:
            merged[record.id] = record
            continue
        duplicates += 1
        target = merged[record.id]
        if target.corpus_version != record.corpus_version:
            raise ValueError("Cannot reconcile different corpus versions")
        for field in [
            "deadline",
            "opens",
            "cycle",
            "timezone",
            "scope",
            "date_precision",
        ]:
            left, right = getattr(target, field), getattr(record, field)
            if field in target.conflicts:
                if right is not None and str(right) not in target.conflicts[field]:
                    target.conflicts[field].append(str(right))
            elif left is not None and right is not None and left != right:
                target.conflicts[field] = [str(left), str(right)]
                setattr(target, field, None)
            elif left is None:
                setattr(target, field, right)
        existing = {
            (c.kind, c.operator, json.dumps(c.value, sort_keys=True)): c
            for c in target.conditions
        }
        for c in record.conditions:
            key = (c.kind, c.operator, json.dumps(c.value, sort_keys=True))
            # Groups include their children in identity; retain complete alternatives/exclusions.
            if c.children:
                key = (
                    c.kind,
                    c.operator,
                    c.model_dump_json(exclude={"id", "evidence"}),
                )
            if key in existing:
                existing[key].evidence.extend(
                    e for e in c.evidence if e not in existing[key].evidence
                )
            else:
                if any(
                    old.kind == c.kind
                    and old.operator == c.operator
                    and old.value != c.value
                    for old in target.conditions
                ):
                    target.conflicts.setdefault("conditions", []).append(
                        c.model_dump(mode="json")
                    )
                c.id = c.id + "-" + hashlib.sha256(str(key).encode()).hexdigest()[:8]
                target.conditions.append(c)
        target.evidence.extend(e for e in record.evidence if e not in target.evidence)
        target.materials = list(dict.fromkeys([*target.materials, *record.materials]))
        for field, ids in record.field_evidence.items():
            target.field_evidence[field] = list(
                dict.fromkeys([*target.field_evidence.get(field, []), *ids])
            )
        if target.conflicts or record.information_status == "conflicting":
            target.information_status = "conflicting"
        elif record.information_status in ["incomplete", "historical"]:
            target.information_status = record.information_status
        elif (
            target.information_status == "source_checked"
            and record.information_status != "source_checked"
        ):
            target.information_status = "automatically_extracted"
    conflict_ids = [
        id for id, r in merged.items() if r.information_status == "conflicting"
    ]
    return list(merged.values()), {
        "duplicates_merged": duplicates,
        "conflicts": conflict_ids,
    }
