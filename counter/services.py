from .models import Counter


def increment_counter_last_number(type):
    counter = Counter.objects.filter(type=type).first()
    counter.last_number = counter.last_number + 1
    counter.full_clean()
    counter.save()
    return counter
    