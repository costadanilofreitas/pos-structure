from sqliteutil import DefaultDdlExecutor


class OrderPumpDdlExecutor(DefaultDdlExecutor):
    def __init__(self):
        super(OrderPumpDdlExecutor, self).__init__(create_db_query)


create_db_query = """
CREATE TABLE LastOrderSent (
    OrderId	INTEGER NOT NULL,
    PRIMARY KEY(OrderId)
);

INSERT INTO LastOrderSent (OrderId) VALUES (0);

CREATE TABLE OrderWithError (
    OrderId	INTEGER NOT NULL,
    Enabled	BOOLEAN NOT NULL,
    RetryCount	INTEGER NOT NULL,
    NextRetry	DATETIME NOT NULL,
    Sent BOOLEAN NOT NULL,
    PRIMARY KEY(OrderId)
);

CREATE INDEX IDX_OrderWithError_Sent_Enabled_NextRetry ON OrderWithError (
    Sent, Enabled, NextRetry
);
"""