# -*- coding: utf-8 -*-
import bustoken
import logging
import cfgtools
import os

from systools import sys_log_error
from msgbus import MBEasyContext, MBException, FM_PARAM, TK_SYS_ACK
from sysactions import action, show_listbox, show_keyboard, show_info_message, show_confirmation, show_messagebox, get_model, get_custom
from userhelper import UserHelper

mbcontext = None  # type: MBEasyContext
logger = logging.getLogger("manager.users")

config = cfgtools.read(os.environ["LOADERCFG"])
users_with_blocked_changes = config.find_values("UsersManager.BlockedChanges")

# noinspection PyUnusedLocal


@action
def changepass(posid, *args):
    model = get_model(posid)
    authorization_level = get_custom(model, 'Authorization Level', None)
    with UserHelper(mbcontext) as user_helper:
        user_session = _info_user_session(posid)
        # lista de usuarios
        users = user_helper.get_users_by_level("0")
        # lista de supervisores
        users.update(user_helper.get_users_by_level("20"))
        users.update(user_helper.get_users_by_level("29"))
        users_formatted = ["{0} - {1} - {2}".format(i, users.get(i)[0], "DIGITAL" if users.get(i)[1] == '1' else "") for i in users]
        index = show_listbox(posid, users_formatted, message="Usuários", buttons="$OK|$CANCEL")
        if index is None:
            return

        user_alter = user_helper.get_level_user(users.keys()[index])

        if users.keys()[index] in users_with_blocked_changes:
            show_info_message(posid, "Não é permitido alterar a senha desse usuário!", msgtype="error")
            return

        if int(authorization_level) < int(user_alter.get('level')):
            show_messagebox(posid, "Não é permitido alterar a senha desse usuário!", "$INFORMATION")
            return

        options = ("SENHA", "DIGITAL")
        type_box = show_messagebox(posid, "Escolha o tipo de autenticação", "$INFORMATION", buttons="|".join(options))

        bt_pressed = options[type_box]

        if bt_pressed == "SENHA":
            valid = False
            passwd1 = None
            while not valid:
                passwd1 = show_keyboard(posid, "Digite a nova senha", title="Nova Senha", mask="INTEGER", is_password=True, numpad=True)

                if passwd1 is None:
                    return

                if passwd1 in (None, "", "."):
                    show_info_message(posid, "Senha inválida", msgtype="error")
                    continue

                passwd2 = show_keyboard(posid, "Repita a senha", title="Repetir Senha", mask="INTEGER", is_password=True, numpad=True)

                if passwd2 is None:
                    return

                if passwd1 == passwd2:
                    valid = True
                else:
                    show_info_message(posid, "Senhas não conferem. Repita a operação", msgtype="error")

            try:
                sucesso = user_helper.change_pass(users.keys()[index], passwd1)
            except Exception as ex:
                sys_log_error("Exceção ao alterar a senha - Exception: " + str(ex))
                logger.exception("Exceção ao alterar a senha")
                show_info_message(posid, "Ocorreu um erro ao alterar a senha!", msgtype="error")
                return

            if sucesso:
                show_info_message(posid, "Senha alterada com sucesso", msgtype="info")
            else:
                show_info_message(posid, "Ocorreu um erro ao alterar a senha!", msgtype="error")

        elif bt_pressed == "DIGITAL":
            # Checa se temos um leitor de impressao digital
            try:
                ret = mbcontext.MB_EasySendMessage("FingerPrintReader{0}".format(posid), bustoken.TK_FPR_OK)
                if ret.token == TK_SYS_ACK:
                    # Temos o leitor e ele esta operacional, vamos pedir as impressoes do usuario
                    ret = mbcontext.MB_EasySendMessage("FingerPrintReader{0}".format(posid), bustoken.TK_FPR_RE_ENROLL_USER, format=FM_PARAM, data="%s;%s" % (users.keys()[int(index)], posid))
                    if ret.token == bustoken.TK_FPR_FINGER_PRINT_ALREADY_REGISTERED:
                        show_info_message(posid, "Impressão digital já cadastrada para outro usuário", msgtype="error")
                        return
                    elif ret.token != TK_SYS_ACK:
                        # Erro cadastrando impressao digital
                        show_info_message(posid, "Erro cadastrando impressao digital. Tente novamente.", msgtype="error")
                        return
                    else:
                        show_info_message(posid, "Impressão alterada com sucesso.", msgtype="info")
                else:
                    show_info_message(posid, "Leitor não encontrado!", msgtype="error")
            except MBException as e:
                if e.errorcode == 2:  # NOT_FOUND, servico de FingerPrint nao disponivel
                    show_info_message(posid, "Leitor não encontrado!", msgtype="error")
                else:
                    show_info_message(posid, "Erro verificando leitor!", msgtype="error")


@action
def createuser(posid, *args):
    with UserHelper(mbcontext) as user_helper:
        userid = show_keyboard(posid, "Digite o Id para novo usuário (máx. 8 dígitos)", mask="INTEGER", title="ID", numpad=True)
        if not userid:
            return
        if len(userid) > 8:
            show_info_message(posid, "Id inválido", msgtype="error")
            return

        user = user_helper.get_user_by_id(userid)
        if user:
            show_info_message(posid, "Id de usuário já existente", msgtype="error")
            return

        username = show_keyboard(posid, "Digite o nome do novo usuário", title="Nome")
        username = str.strip(username) if username else ""
        if username in "":
            show_info_message(posid, "Digite um nome", msgtype="error")
            return

        matching = [s for s in ['|', '-', '+', '[', ']', ';', '/', ',', '.', '!', '@', '#', '^', '$', '%', '&', '*', '(', ')', '_', '=', '{', '}', ':', '?', '<', '>'] if s in username]
        if matching:
            show_info_message(posid, "Nome inválido. Caracteres proibidos: %s" % str(matching), msgtype="error")
            return

        valid = False
        passwd1 = None
        while not valid:
            passwd1 = show_keyboard(posid, "Digite a senha", title="Senha", mask="INTEGER", is_password=True, numpad=True)
            if passwd1 in (None, "", "."):
                show_info_message(posid, "Senha inválida", msgtype="error")
                return
            passwd2 = show_keyboard(posid, "Repita a senha", title="Repetir Senha", mask="INTEGER", is_password=True, numpad=True)
            if passwd1 == passwd2:
                valid = True
            else:
                show_info_message(posid, "Senhas não conferem. Repita a operação", msgtype="error")

        admin = show_confirmation(posid, message="Tornar o usuário supervisor?", buttons="Sim|Não")

        # Checa se temos um leitor de impressao digital
        fmd_data = None
        # noinspection PyBroadException
        try:
            ret = mbcontext.MB_EasySendMessage("FingerPrintReader{0}".format(posid), bustoken.TK_FPR_OK)
            if ret.token == TK_SYS_ACK:
                # Temos o leitor e ele esta operacional, vamos pedir as impressoes do usuario
                ret = mbcontext.MB_EasySendMessage("FingerPrintReader{0}".format(posid), bustoken.TK_FPR_ENROLL_USER, format=FM_PARAM, data="%s;%s" % (userid, posid))

                if ret.token == bustoken.TK_FPR_FINGER_PRINT_ALREADY_REGISTERED:
                    show_info_message(posid, "Impressão digital já cadastrada para outro usuário", msgtype="error")
                    return
                elif ret.token != TK_SYS_ACK:
                    # Erro cadastrando impressao digital
                    show_info_message(posid, "Erro cadastrando impressão digital. Tente novamente.", msgtype="error")
                    return
                else:
                    fmd_data = ret.data
        except MBException as e:
            if e.errorcode == 2:  # NOT_FOUND, servico de FingerPrint nao disponivel
                pass
            else:
                pass
        except Exception as ex:
            sys_log_error("Exceção ao cadastrar digital - Exception: " + str(ex))
            logger.exception("Exceção ao cadastrar digital")
            show_info_message(posid, "Erro cadastrando impressão digital. Tente novamente.", msgtype="error")

        # noinspection PyBroadException
        try:
            sucesso = user_helper.add_user(userid, username, passwd1, admin, fmd_data)
        except Exception as ex:
            sys_log_error("Exceção ao cadastrar usuário - Exception: " + str(ex))
            logger.exception("Exceção ao cadastrar usuário")
            show_info_message(posid, "Ocorreu um erro ao cadastrar usuário!", msgtype="error")
            return

        if sucesso:
            show_info_message(posid, "Usuário cadastrado com sucesso", msgtype="info")
        else:
            show_info_message(posid, "Ocorreu um erro ao cadastrar usuário!", msgtype="error")


@action
def removeuser(posid, *args):
    with UserHelper(mbcontext) as user_helper:
        # lista de usuarios
        users = user_helper.get_users_by_level("0")
        # lista de supervisores
        users.update(user_helper.get_users_by_level("20"))

        users_formatted = ["%s - %s" % (i, users.get(i)) for i in users]
        index = show_listbox(posid, users_formatted, message="Usuários", buttons="OK")

        if users.keys()[index] in users_with_blocked_changes:
            show_info_message(posid, "Esse usuário não pode ser removido!", msgtype="error")
            return

        confirm = show_confirmation(posid, message="Tem certeza que deseja excluir o usuário?", buttons="Sim|Não")

        if confirm:
            # noinspection PyBroadException
            try:
                sucesso = user_helper.remove_user(users.keys()[index])
            except Exception as ex:
                sys_log_error("Exceção removendo usuário - Exception: " + str(ex))
                logger.exception("Exceção removendo usuário")
                show_info_message(posid, "Ocorreu um erro ao excluir usuário!", msgtype="error")
                return

            if sucesso:
                show_info_message(posid, "Usuário excluído com sucesso", msgtype="info")
            else:
                show_info_message(posid, "Ocorreu um erro ao excluir usuário!", msgtype="error")
        else:
            show_info_message(posid, "Operação cancelada. Usuário não removido", msgtype="error")


@action
def inactivateuser(posid, *args):
    with UserHelper(mbcontext) as user_helper:
        # lista de usuarios
        users = user_helper.get_users_by_level("0")
        # lista de supervisores
        users.update(user_helper.get_users_by_level("20"))
        users_formatted = ["%s - %s" % (i, users.get(i)) for i in users]
        index = show_listbox(posid, users_formatted, message="Usuários", buttons="$OK|$CANCEL")
        if index is None:
            return

        if users.keys()[index] in users_with_blocked_changes:
            show_info_message(posid, "Este usuário não pode ser desativado!", msgtype="error")
            return

        confirm = show_confirmation(posid, message="Tem certeza que deseja desativar o usuário?", buttons="Sim|Não")

        if confirm:
            # noinspection PyBroadException
            try:
                sucesso = user_helper.activate_user(users.keys()[index], op=1)
            except Exception as ex:
                sys_log_error("Exceção ativando usuário - Exception: " + str(ex))
                logger.exception("Exceção ativando usuário")
                show_info_message(posid, "Ocorreu um erro ao desativar usuário!", msgtype="error")
                return

            if sucesso:
                show_info_message(posid, "Usuário desativado com sucesso", msgtype="info")
            else:
                show_info_message(posid, "Ocorreu um erro ao desativar usuário!", msgtype="error")
        else:
            show_info_message(posid, "Operação cancelada. Usuário não desativado", msgtype="error")

@action
def changeperfil(posid, *args):
    with UserHelper(mbcontext) as user_helper:
        options = ("OPERADOR", "SUPERVISOR")
        type_box = show_messagebox(posid, "Escolha o tipo de perfil", "$INFORMATION", buttons="|".join(options))

        level = "20" if type_box else "0"
        level_intended = "0" if "20" == level else "20"
        users = user_helper.get_users_by_level(level)
        list_users = ["%s - %s" % (i, users.get(i)) for i in users]
        index = show_listbox(posid, list_users, message="Usuários", buttons="$OK|$CANCEL")

        if index is None:
            return

        if users.keys()[index] in users_with_blocked_changes:
            show_info_message(posid, "Este usuário não pode ser alterado!", msgtype="error")
            return

        text_level = {"20": "Tem certeza que deseja alterar o perfil de operador para supervisor?",
                      "0": "Tem certeza que deseja alterar o perfil de supervisor para operador?"}

        confirm = show_confirmation(posid, message= text_level[level_intended], buttons="Sim|Não")

        if confirm:
            try:
                sucesso = user_helper.change_level_user(users.keys()[index], level_intended)
            except Exception as ex:
                sys_log_error("Exceção ativando usuário - Exception: " + str(ex))
                logger.exception("Exceção ao alterar o perfil do usuário")
                show_info_message(posid, "Ocorreu um erro ao alterar o perfil do usuário!", msgtype="error")
                return

            if sucesso:
                show_info_message(posid, "Perfil do usuário alterado com sucesso", msgtype="info")
            else:
                show_info_message(posid, "Ocorreu um erro ao alterar o perfil do usuário!", msgtype="error")
        else:
            show_info_message(posid, "Operação cancelada.", msgtype="error")


def _info_user_session(posid):
    level, info = None, dict()
    with UserHelper(mbcontext) as user_helper:
        user_session = user_helper.get_user_session(posid)
        try:
            for i in user_session:
                level = {'level': int(user_session[i])}
                info = {x.split('=')[0]:x.split('=')[1] for x in i.split(",")}
            return dict(info, **level)
        except MBException as ex:
            return
