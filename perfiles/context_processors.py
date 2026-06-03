from accounts.roles import user_role


def role_context(request):
    return {"user_role": user_role(request.user)}
