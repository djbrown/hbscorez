from typing import Optional


def parse_spectators(table) -> Optional[int]:
    specs: str = table['data'][4][2]['text']
    if specs == 'k.A.':
        return None

    return int(specs)
