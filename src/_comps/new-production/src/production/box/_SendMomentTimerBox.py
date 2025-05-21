from production.box._OrderChangerProductionBox import OrderChangerProductionBox


class SendMomentTimerBox(OrderChangerProductionBox):
    def change_order(self, order):
        send_moment_list = []
        self.find_recursive_send_moment(order, send_moment_list)

        if len(send_moment_list) > 0:
            min_send_moment = min(send_moment_list)
            order.display_time = min_send_moment.isoformat()

        return order

    def find_recursive_send_moment(self, order, send_moment_list):
        for item in order.items:
            if item.is_product():
                if not item.has_tag("dont-need-cook") and not item.has_tag("wait-prep-time") and item.send_moment:
                    send_moment_list.append(item.send_moment)
            elif len(item.items) > 0:
                self.find_recursive_send_moment(item, send_moment_list)
