import os
import re
import time
from typing import AsyncIterator, Dict, List, TypeVar

T = TypeVar("T")



def parse_int_kv_dict(kv_list: str) -> Dict[str, int]:
    as_list = parse_comma_delimited_list(kv_list)
    split_list = [[y.strip() for y in x.split(":")] for x in as_list]
    cleaned_split = {
        x[0]: int(x[1]) for x in split_list if len(x) == 2 and re.match(r"^\d+$", x[1])
    }
    return cleaned_split


def parse_comma_delimited_list(s: str) -> List[str]:
    return [re.sub("\.$", "", x.strip()) for x in s.split(",")]


async def throttle(
    iterator: AsyncIterator[T], update_frequency_seconds: int = 1
) -> AsyncIterator[T]:
    last = None
    result = None
    async for generated in iterator:
        result = generated
        now = time.time()
        if last is None or (now - last > update_frequency_seconds):
            last = now
            yield result
    if result:
        yield result
