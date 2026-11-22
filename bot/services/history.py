
histories = {}

def get_history(user_id: int):
    return histories.get(user_id, [])

def save_exchange(user_id: int,text_user: str,answer:str):
    history = get_history(user_id)

    history.append({"role":'user', "content": text_user})
    history.append({"role":'assistant', "content": answer})
    histories[user_id] = history[-20:]