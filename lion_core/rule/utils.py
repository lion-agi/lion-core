from lion_core.generic.note import note


def validate_rules_info(rules):
    _r = note(**rules)
    _r_info = note()
    for k, v in _r.items():
        if isinstance(v, dict) and v.get("rule"):
            _r_info[k] = {
                "rule": v.get("rule"),
                "base_config": v.get("base_config", v["rule"].base_config),
                "rule_info": v.get("info", {}),
            }
    return _r_info
