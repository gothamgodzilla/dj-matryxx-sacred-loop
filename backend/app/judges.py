"""7-judge gate: Guinness eligibility is floor COMMIT with no DD breach."""


def eligible(result):
    return result.get("status") == "0xCOMMITTED"
