from django.core.exceptions import ObjectDoesNotExist, PermissionDenied


def get_profile_or_403(request):
    try:
        return request.user.profile
    except ObjectDoesNotExist: 
        raise PermissionDenied('User does not have profile.')