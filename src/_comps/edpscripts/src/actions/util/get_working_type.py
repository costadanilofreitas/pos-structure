from sysactions import get_model


def get_working_type(pos_id):
    model = get_model(pos_id)
    return model.find('.//WorkingMode').get('usrCtrlType')
