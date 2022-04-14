import pickle
def serialize(filepath, obj):
    '''
    将模型序列化
    :param filepath:
    :param obj:
    :return:
    '''
    with open(filepath, "wb") as file:
        pickle.dump(obj, file)

def deserialize(filepath):
    '''
    将模型反序列化
    :param filepath:
    :return:
    '''
    with open(filepath, "rb") as file:
        obj = pickle.load(file)
        return obj