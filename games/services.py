from random import shuffle

from .models import HuntingOfSnarkCategory
from .models import HuntingOfSnarkCriteria


def get_random_hunting_of_snark_criteria(total_points):
    categories_hash = {
        category.id: list(category.criteria.values_list('public_id', flat=True))
        for category in
        HuntingOfSnarkCategory.objects.all().prefetch_related('criteria')
    }
    selected_criteria_ids = []
    points_counter = 0
    while points_counter < total_points:
        category_keys = list(categories_hash.keys())
        shuffle(category_keys)
        for category_key in category_keys:
            if points_counter >= total_points:
                break

            shuffle(categories_hash[category_key])
            criteria_id = categories_hash[category_key].pop(0)
            selected_criteria_ids.append(criteria_id)
            points_counter += 1

            if len(categories_hash[category_key]) == 0:
                del categories_hash[category_key]

    return HuntingOfSnarkCriteria.objects.filter(
        public_id__in=selected_criteria_ids
    ).all()
