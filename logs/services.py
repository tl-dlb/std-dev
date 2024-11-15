from .models import Log


def create_log(type, comment, user):
    log = Log.objects.create(
        type=type,
        comment=comment,
        created_by=user,
    )
    log.full_clean()
    log.save()
    return log
