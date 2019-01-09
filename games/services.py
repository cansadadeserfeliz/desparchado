from random import shuffle

from .models import HuntingOfSnarkCategory


def get_random_hunting_of_snark_criteria(total_points):
    criteria_list = []

    original_categories = list(
        HuntingOfSnarkCategory.objects.all()
        .prefetch_related('criteria')
    )
    categories = []
    points_counter = 0
    while points_counter < total_points:
        if not len(categories):
            shuffle(original_categories)
            categories = original_categories.copy()

        category = categories.pop(0)
        possible_criteria = list(category.criteria.all())
        shuffle(possible_criteria)
        criteria = possible_criteria[0]

        if criteria in criteria_list:
            continue
        else:
            criteria_list.append(criteria)
            points_counter += 1
    return criteria_list
