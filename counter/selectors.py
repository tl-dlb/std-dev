from .models import Counter


def get_counter_last_number(type):
    counter = Counter.objects.filter(type=type).first()
    return counter.last_number
    