import sysactions

store_id = None


def get_store_id():
    global store_id
    
    if not store_id:
        store_id = sysactions.get_storewide_config("Store.Id")
        
    return store_id
