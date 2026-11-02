from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect
def admin_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        if not request.user.is_superuser:
            messages.error(request, "Apenas o administrador pode realizar esta operação.")
            return redirect("dashboard")
        return view(request, *args, **kwargs)
    return wrapper
