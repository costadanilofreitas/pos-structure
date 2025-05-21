class NfceDisablerResponse(object):
    Disabled = "102"
    OneOfTheRangeAlreadyDisabled = "256"
    AlreadyDisabled = "206"
    EqualRequest = "563"  # Rejeicao: Ja existe pedido de Inutilizacao com a mesma faixa de inutilizacao
    AlreadyUsedFiscalNumber = "241"  # Rejeicao: Um numero da faixa ja foi utilizado

    def __init__(self, c_stat, x_motivo, n_prot):
        self.c_stat = c_stat
        self.x_motivo = x_motivo
        self.n_prot = n_prot
