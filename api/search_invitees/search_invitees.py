from model import User

def search_invitees(search_phrase):
    matched_users = User.query.filter(User.email.like(f"%{search_phrase}%") |
                                      User.name.like(f"%{search_phrase}%")).all()

    results = {user.email: user.name for user in matched_users}
    return results