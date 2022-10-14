from dataclasses import dataclass, field, Field
@dataclass
class Record:
    item_ids: list[int]

Record([1,2,3])
Record(['A','B'])

