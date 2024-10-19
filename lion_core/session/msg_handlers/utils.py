import re

from lionfuncs import to_dict


def extract_action_blocks(text: str) -> list[dict]:
    # Regular expression to match JSON blocks
    pattern = r"```json\s*(.*?)\s*```"
    pattern2 = r"```python\s*(.*?)\s*```"

    # Find all matches in the text
    matches = re.findall(pattern, text, re.DOTALL)
    if not matches:
        matches = re.findall(pattern2, text, re.DOTALL)

    # Parse each match as JSON and collect in a list
    json_blocks = [
        to_dict(match, fuzzy_parse=True, suppress=True) for match in matches
    ]

    json_blocks = [i for i in json_blocks if i]

    out = []
    for i in json_blocks:
        j = {}
        for k, v in i.items():
            k = (
                k.replace("action_", "")
                .replace("recipient_", "")
                .replace("s", "")
            )
            if k in ["name", "function", "recipient"]:
                j["function"] = v
            elif k in ["parameter", "argument", "arg"]:
                j["arguments"] = to_dict(
                    v, str_type="json", fuzzy_parse=True, suppress=True
                )
        if (
            j
            and all(key in j for key in ["function", "arguments"])
            and j["arguments"]
        ):
            out.append(j)

    return out
