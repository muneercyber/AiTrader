user_pairs = {}

def set_selected_pair(user_id, pair):
    user_pairs[user_id] = pair

def get_selected_pair(user_id):
    return user_pairs.get(user_id)
