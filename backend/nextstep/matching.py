"""Three-valued, bounded rules; missing facts never count as satisfied."""
from datetime import date
from nextstep.models import Condition, ConditionResult, StudentProfile, Scholarship, MatchResult

def evaluate_condition(condition: Condition, profile: StudentProfile, as_of: date) -> ConditionResult:
    c = condition
    def result(status, reason):
        return ConditionResult(condition_id=c.id, status=status, reason=reason)
    unknown = result('unknown', c.reason or f'Please confirm {c.kind}: {c.value}')
    if c.kind == 'group':
        statuses = [evaluate_condition(child, profile, as_of).status for child in c.children]
        if not statuses:
            return unknown
        if c.operator == 'and':
            status = 'unmet' if 'unmet' in statuses else 'unknown' if 'unknown' in statuses else 'met'
        elif c.operator == 'or':
            status = 'met' if 'met' in statuses else 'unknown' if 'unknown' in statuses else 'unmet'
        elif c.operator == 'not' and len(statuses) == 1:
            status = {'met':'unmet','unmet':'met','unknown':'unknown'}[statuses[0]]
        else:
            return unknown
        return result(status, f'{c.operator.upper()} condition: {status}')
    value = None
    expected = c.value
    if c.kind == 'gpa':
        gpa = profile.gpa
        if not gpa or not isinstance(expected,dict):
            return unknown
        if gpa.type == 'unknown' or not gpa.scale or gpa.type != expected.get('type') or gpa.scale != expected.get('scale'):
            return unknown
        value, expected = gpa.value, expected.get('value')
    elif c.kind == 'grade':
        value = profile.grade
    elif c.kind == 'graduation_year':
        value = profile.graduation_year
    elif c.kind in ('state','county','city'):
        value = profile.residence.get(c.kind)
    elif c.kind == 'college' and c.operator in ('accepted','enrolled'):
        entries = profile.context.get(c.operator + '_colleges')
        if entries is None:
            return unknown
        return result('met' if expected in entries else 'unmet', f'{c.operator.title()} college requirement: {expected}')
    elif c.kind in ('membership','employer','utility','citizenship','financial_need'):
        value = profile.context.get(c.kind)
    elif c.kind == 'interest':
        value = profile.interests or None
    else:
        return unknown
    if value is None or expected is None:
        return unknown
    try:
        if c.operator == 'eq':
            met = expected in value if isinstance(value,list) else value == expected
        elif c.operator == 'in' and isinstance(expected,list):
            met = value in expected
        elif c.operator == 'gte' and isinstance(value,(int,float)) and isinstance(expected,(int,float)):
            met = value >= expected
        elif c.operator == 'lte' and isinstance(value,(int,float)) and isinstance(expected,(int,float)):
            met = value <= expected
        else:
            return unknown
    except (TypeError, ValueError):
        return unknown
    return result('met' if met else 'unmet', f'{c.kind}: {c.operator} {expected}')

def match_catalog(records: list[Scholarship], profile: StudentProfile, as_of: date) -> list[MatchResult]:
    results = []
    for record in records:
        evaluated = [evaluate_condition(c,profile,as_of) for c in record.conditions]
        mandatory = [r for c,r in zip(record.conditions,evaluated) if c.required]
        unresolved = [r for r in mandatory if r.status == 'unknown']
        unmet = [r for r in mandatory if r.status == 'unmet']
        senior_rule = any(c.required and c.kind == 'grade' and c.operator == 'eq' and c.value == 12 for c in record.conditions)
        group = 'unmet' if unmet else 'matches'
        fit = 'Condition unmet' if unmet else 'Missing profile information' if unresolved else 'Potential match'
        if profile.grade == 11 and senior_rule:
            group, fit = 'prepare', 'Conditional senior-year preparation; future rules must be checked'
        if record.information_status in ('incomplete','conflicting','historical'):
            group = 'prepare' if group == 'prepare' and record.information_status == 'historical' else 'explore'
        timing = 'unknown'
        if record.deadline and record.deadline < as_of:
            timing = 'closed'
        elif record.opens and record.opens > as_of:
            timing = 'upcoming'
        elif record.opens and record.deadline and record.opens <= as_of <= record.deadline:
            timing = 'open'
        preferences = sum(r.status == 'met' for c,r in zip(record.conditions,evaluated) if not c.required)
        results.append(MatchResult(scholarship_id=record.id,conditions=evaluated,group=group,fit=fit,timing=timing,evidence_label=record.information_status,followups=[r.reason for r in unresolved],sort_key=(len(unresolved),-preferences,record.name.casefold(),record.id)))
    return sorted(results,key=lambda r:r.sort_key)
