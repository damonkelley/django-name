from django.core.exceptions import ValidationError


def follow_merged_with(name):
    """A generator to get the merged_with relationship
    of a Name object.

    This will return a Name object until it reaches a Name that
    does not have a merged_with relationship.
    """
    while name:
        merged_into = name.merged_with
        if merged_into:
            yield merged_into
        name = merged_into


def validate_merged_with(name):
    """Validator for the merged_with ForeignKey field.

    This will prevent two scenarios from occurring.
    1. Merging with a nonexistent Name object.

    2. Creating a loop of foreign key relationships.
        For example:
            Name 1 -> Name 2 -> Name 3 -> Name 1

        We need to prevent this because navigating to a name that has
        been merged with another, will redirect you to the Name it has
        been merged with. If a loop is created, we will also create
        the opportunity for an HTTP redirect loop.
    """
    try:
        merge_target = name.__class__.objects.get(id=name.merged_with_id)
    except name.__class__.DoesNotExist:
        raise ValidationError(
            dict(merged_with=u'The merge target must exist.'))

    if name.merged_with_id == name.id:
        raise ValidationError(
            dict(merged_with=u'Unable to merge a Name with itself.'))

    # Iterate through the generator and keep track of the return names.
    # We will find a loop if the return name is already in
    # merged_list. If this happens we will raise a validation error.
    # If we don't find duplicates, then no loop has been created and
    # the generator will raise it's own StopIteration and we will
    # implicitly return.
    merge_sequence = [name]
    for name in follow_merged_with(merge_target):
        if name in merge_sequence:
            msg = (u'The specified merge action completes a merge loop. '
                   'Unable to complete merge.')
            raise ValidationError(dict(merged_with=msg))
        merge_sequence.append(name)
