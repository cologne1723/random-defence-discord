from discord import User


def isAdmin(user: User):
    return any(x.name.lower() == 'admin' for x in user.roles)