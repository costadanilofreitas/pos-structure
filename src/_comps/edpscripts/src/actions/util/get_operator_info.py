def get_operator_info(model, operator_id):
    need_logged = True
    session = ''
    for op in model.find('Operators').findall('Operator'):
        if op.get('id') == operator_id and (op.get('state') == 'LOGGEDIN' or op.get('state') == 'PAUSED'):
            if op.get('state') == 'PAUSED':
                need_logged = False
            operator = op
            session = operator.get('sessionId')
            operator_id = operator.get("id")
            break

    return need_logged, operator_id, session
