from django.core.exceptions import PermissionDenied
from .models import Profile

def check_department_and_position(department_name, position_name):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                profile = Profile.objects.get(user=request.user)
                if profile.department and profile.position:
                    if profile.department.name == department_name and profile.position.name == position_name:
                        return view_func(request, *args, **kwargs)
            raise PermissionDenied
        return _wrapped_view
    return decorator
