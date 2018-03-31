def set_place(items: list, field: str):
    """
    Adds 'place' to all items according to their order.
    If the value of the specified field on any given item matches the value on the field of the previous item,
    then the item gets the same place as its predecessor.

    :param items: an already sorted list of items, ordered by `field`
    :param field: the field of the items to compare
    """
    for index, item in enumerate(items):
        item.place = index + 1
        if index > 0:
            previous = items[index - 1]
            if getattr(previous, field) == getattr(item, field):
                item.place = previous.place
