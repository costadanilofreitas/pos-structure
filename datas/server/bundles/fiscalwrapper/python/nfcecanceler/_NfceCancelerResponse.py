class NfceCancelerResponse(object):
    Canceled = "135"
    AlreadyCanceled = "573"

    def __init__(self, c_stat, x_motivo, n_prot):
        self.c_stat = c_stat
        self.x_motivo = x_motivo
        self.n_prot = n_prot
