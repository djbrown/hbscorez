def parse_spectators(table) -> int | None:
    specs: str = table['data'][4][2]['text']
    if specs == 'k.A.':
        return None

    try:
        return int(specs)
    except ValueError:
        return None
