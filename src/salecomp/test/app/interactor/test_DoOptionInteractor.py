import pytest
from builder import LineBuilder
from builder._OrderBuilder import OrderBuilder
from salecomp.interactor import DoOptionInteractor
from salecomp.model import Order, Line, ProductPart, DefaultOption, State, OrderType
from salecomp.model.exception import OrderNotFound, LineNotFound, ParentNotFoundException, \
    InvalidItemId, InvalidMenu, ParentIsNotAnOption, \
    NotValidSolution, OptionMaxQuantityExceeded
from salecomp.repository import ProductRepository
from testdouble import OrderRepositorySpy, OrderRepositoryStub
from testdoubleutil import SpyCall

pos_id = 1
order_id = 10
line_number = 2
item_id = "1.1050.820000.270001"
quantity = 1


class TestDoOptionInteractor(object):
    class TestDoOptionValidations(object):
        def setup_method(self, method):
            self.must_not_sell = True
            self.order_repository = None

        def teardown_method(self, method):
            if self.must_not_sell:
                assert not self.order_repository.add_line_call.called
                assert not self.order_repository.update_line_call.called

        def test_whenOrderDoesNotExist_ExceptionIsRaised(self):
            self.order_repository = OrderRepositorySpy(get_order_response=None)
            interactor = a_do_option_interactor() \
                .with_order_repository(self.order_repository) \
                .build()

            with pytest.raises(OrderNotFound):
                interactor.execute(pos_id, order_id, line_number, item_id, quantity)

            assert self.order_repository.get_order_call.args[0] == pos_id
            assert self.order_repository.get_order_call.args[1] == order_id

        def test_whenOrderDoesNotHaveLineNumber_ExceptionIsRaised(self):
            order = OrderBuilder().add_line(LineBuilder().with_line_number(1)).build()
            self.order_repository = OrderRepositorySpy(get_order_response=order)
            interactor = a_do_option_interactor() \
                .with_order_repository(self.order_repository) \
                .build()

            with pytest.raises(LineNotFound):
                interactor.execute(pos_id, order_id, line_number, item_id, quantity, )
            assert self.order_repository.get_order_call.args[0] == pos_id
            assert self.order_repository.get_order_call.args[1] == order_id

        def test_whenItemIdHasLessThanFourParts_ExceptionIsRaised(self):
            self.order_repository = OrderRepositorySpy(get_order_response=None)
            interactor = a_do_option_interactor()\
                .with_order_repository(self.order_repository)\
                .build()

            with pytest.raises(InvalidItemId):
                interactor.execute(pos_id, order_id, line_number, "", 1)
            with pytest.raises(InvalidItemId):
                interactor.execute(pos_id, order_id, line_number, "1", 1)
            with pytest.raises(InvalidItemId):
                interactor.execute(pos_id, order_id, line_number, "1.1050", 1)
            with pytest.raises(InvalidItemId):
                interactor.execute(pos_id, order_id, line_number, "1.1050.8200000", 1)

        def test_whenTheMenuIsNotValid_ExceptionIsRaised(self):
            order = an_order_with_two_whoppers()
            self.order_repository = OrderRepositorySpy(get_order_response=order)
            product_repository = ProductRepositoryStub(is_menu_valid_response=False)
            interactor = a_do_option_interactor() \
                .with_product_repository(product_repository) \
                .with_order_repository(self.order_repository) \
                .build()

            with pytest.raises(InvalidMenu):
                interactor.execute(pos_id, order_id, line_number, "2.1050.820000.270001", 1)

        def test_whenParentIsNotFound_ExceptionIsRaised(self):
            order = an_order_with_two_whoppers()
            self.order_repository = OrderRepositorySpy(get_order_response=order)
            product_repository = ProductRepositoryStub(is_menu_valid_response=True)
            interactor = a_do_option_interactor() \
                .with_product_repository(product_repository) \
                .with_order_repository(self.order_repository) \
                .build()

            with pytest.raises(ParentNotFoundException):
                interactor.execute(pos_id, order_id, line_number, "1.1052.820000.270001", quantity)

            order = OrderBuilder() \
                .add_line(LineBuilder()
                          .with_line_number(1)
                          .with_item_id("1")
                          .with_part_code(1051)
                          .add_line(LineBuilder()
                                    .with_line_number(1)
                                    .with_item_id("1.1051")
                                    .with_part_code(1050))) \
                .build()

            self.order_repository = OrderRepositorySpy(get_order_response=order)
            product_repository = ProductRepositoryStub(is_menu_valid_response=True)
            interactor = a_do_option_interactor() \
                .with_product_repository(product_repository) \
                .with_order_repository(self.order_repository) \
                .build()

            with pytest.raises(ParentNotFoundException):
                interactor.execute(pos_id, order_id, 1, "1.1051.1052.820000.270001", 1)

        def test_whenLastParentIsNotAnOption_ExceptionIsRaised(self):
            order = an_order_with_two_whoppers()
            self.order_repository = OrderRepositorySpy(get_order_response=order)
            product_repository = ProductRepositorySpy(is_menu_valid_response=True, is_option_response=False)
            interactor = a_do_option_interactor() \
                .with_product_repository(product_repository) \
                .with_order_repository(self.order_repository) \
                .build()

            with pytest.raises(ParentIsNotAnOption) as exc_info:
                interactor.execute(pos_id, order_id, line_number, item_id, quantity, )

            assert product_repository.is_option_call.args[0] == 820000
            assert exc_info.value.part_code == 820000

        def test_whenSolutionIsNotAValidSonOfTheOption_ExceptionIsRaised(self):
            order = an_order_with_two_whoppers()
            self.order_repository = OrderRepositorySpy(get_order_response=order)
            product_repository = ProductRepositorySpy(is_menu_valid_response=True,
                                                      is_option_response=True,
                                                      is_valid_solution_response=False)
            interactor = a_do_option_interactor() \
                .with_product_repository(product_repository) \
                .with_order_repository(self.order_repository) \
                .build()

            with pytest.raises(NotValidSolution) as exc_info:
                interactor.execute(pos_id, order_id, line_number, item_id, quantity, )

            assert product_repository.is_valid_solution_call.args[0] == 820000
            assert product_repository.is_valid_solution_call.args[1] == 270001
            assert exc_info.value.option_part_code == 820000
            assert exc_info.value.part_code == 270001

        def test_whenNewQuanitySentIsHigherThanMaxQuantity_ExceptionIsRaised(self):
            order = an_order_with_two_whoppers()
            self.order_repository = OrderRepositorySpy(get_order_response=order)
            product_repository = ProductRepositorySpy(is_menu_valid_response=True,
                                                      is_option_response=True,
                                                      is_valid_solution_response=True,
                                                      get_max_quantity_response=1)
            interactor = a_do_option_interactor()\
                .with_product_repository(product_repository)\
                .with_order_repository(self.order_repository)\
                .build()

            with pytest.raises(OptionMaxQuantityExceeded) as exc_info:
                interactor.execute(pos_id, order_id, line_number, item_id, 5)

            assert product_repository.get_max_quantity_call.args[0] == 1050
            assert product_repository.get_max_quantity_call.args[1] == 820000
            assert exc_info.value.parent_part_code == 1050
            assert exc_info.value.option_part_code == 820000
            assert exc_info.value.max_quantity == 1
            assert exc_info.value.tried_quantity == 5

        def test_whenNewQuantityAddedWithOptionQuantityWouldExceedMaxQuantity_ExceptionIsRaised(self):
            order = an_order_with_two_whoppers_with_ingredients()
            self.order_repository = OrderRepositorySpy(get_order_response=order)
            product_repository = ProductRepositorySpy(is_menu_valid_response=True,
                                                      is_option_response=True,
                                                      is_valid_solution_response=True,
                                                      get_max_quantity_response=5)
            interactor = a_do_option_interactor() \
                .with_product_repository(product_repository) \
                .with_order_repository(self.order_repository) \
                .build()

            with pytest.raises(OptionMaxQuantityExceeded) as exc_info:
                interactor.execute(pos_id, order_id, line_number, item_id, 3)

            assert product_repository.get_max_quantity_call.args[0] == 1050
            assert product_repository.get_max_quantity_call.args[1] == 820000
            assert exc_info.value.parent_part_code == 1050
            assert exc_info.value.option_part_code == 820000
            assert exc_info.value.max_quantity == 5
            assert exc_info.value.tried_quantity == 6

        def test_whenChangedQuantityWillNotExceedMaxQuantityBecauseOfTheUpdate_changeSolutionQuantity(self):
            self.must_not_sell = False
            order = an_order_with_two_whoppers_with_ingredients()
            self.order_repository = OrderRepositorySpy(get_order_response=order)
            product_repository = ProductRepositorySpy(is_menu_valid_response=True,
                                                      is_option_response=True,
                                                      is_valid_solution_response=True,
                                                      get_max_quantity_response=5)
            interactor = a_do_option_interactor() \
                .with_product_repository(product_repository) \
                .with_order_repository(self.order_repository) \
                .build()

            interactor.execute(pos_id, order_id, line_number, "1.1050.820000.270003", 3)

            line = self.order_repository.update_line_call.all_args[0][0]  # type: Line
            assert line.part_code == 270003
            assert line.quantity == 3
            assert line.line_number == 2
            assert line.item_id == "1.1050.820000"

            line = self.order_repository.update_line_call.all_args[1][0]  # type: Line
            assert line.part_code == 820000
            assert line.quantity == 4
            assert line.line_number == 2
            assert line.item_id == "1.1050"

            assert not self.order_repository.delete_sons_call.called

    class TestDoOptionWithoutDefaultOptionAndWithoutParts(object):
        def test_whenOptionAlreadyExistsAndSolutionDoesNot_addSolutionWhenOptionAlreadyExists(self):
            order = an_order_with_two_whoppers_with_ingredients()
            order_repository = OrderRepositorySpy(get_order_response=order)
            product_repository = ProductRepositorySpy(is_menu_valid_response=True,
                                                      is_option_response=True,
                                                      is_valid_solution_response=True,
                                                      get_max_quantity_response=100)
            interactor = a_do_option_interactor() \
                .with_product_repository(product_repository) \
                .with_order_repository(order_repository) \
                .build()

            interactor.execute(pos_id, order_id, line_number, item_id, 3)

            line = order_repository.add_line_call.args[0]  # type: Line
            assert line.part_code == 270001
            assert line.quantity == 3
            assert line.line_number == 2
            assert line.item_id == "1.1050.820000"

            line = order_repository.update_line_call.args[0]  # type: Line
            assert line.part_code == 820000
            assert line.quantity == 6
            assert line.line_number == 2
            assert line.item_id == "1.1050"

        def test_whenOptionAndSolutionAlreadyExists_changeSolutionQuantity(self):
            order = an_order_with_two_whoppers_with_ingredients()
            order_repository = OrderRepositorySpy(get_order_response=order)
            product_repository = ProductRepositorySpy(is_menu_valid_response=True,
                                                      is_option_response=True,
                                                      is_valid_solution_response=True,
                                                      get_max_quantity_response=100)
            interactor = a_do_option_interactor() \
                .with_product_repository(product_repository) \
                .with_order_repository(order_repository) \
                .build()

            interactor.execute(pos_id, order_id, line_number, "1.1050.820000.270002", 3)

            line = order_repository.update_line_call.all_args[0][0]  # type: Line
            assert line.part_code == 270002
            assert line.quantity == 3
            assert line.line_number == 2
            assert line.item_id == "1.1050.820000"

            line = order_repository.update_line_call.all_args[1][0]  # type: Line
            assert line.part_code == 820000
            assert line.quantity == 5
            assert line.line_number == 2
            assert line.item_id == "1.1050"

            assert not order_repository.delete_sons_call.called

        def test_whenOptionAndSolutionDoesNotExist_addOptionAndSolution(self):
            order = an_order_with_two_whoppers()
            order_repository = OrderRepositorySpy(get_order_response=order)
            product_repository = ProductRepositorySpy(is_menu_valid_response=True,
                                                      is_option_response=True,
                                                      is_valid_solution_response=True,
                                                      get_max_quantity_response=100)
            interactor = a_do_option_interactor() \
                .with_product_repository(product_repository) \
                .with_order_repository(order_repository) \
                .build()

            interactor.execute(pos_id, order_id, line_number, item_id, 1)

            line = order_repository.add_line_call.all_args[0][0]  # type: Line
            assert line.part_code == 820000
            assert line.quantity == 1
            assert line.line_number == 2
            assert line.item_id == "1.1050"
            assert len(line.lines) == 0

            line = order_repository.add_line_call.all_args[1][0]  # type: Line
            assert line.part_code == 270001
            assert line.quantity == 1
            assert line.line_number == 2
            assert line.item_id == "1.1050.820000"
            assert len(line.lines) == 0

    class TestDoOptionWithoutDefaultOptionAndWithParts(object):
        def test_whenSolutionHasParts_thePartsAreAlsoSolded(self):
            order = an_order_with_a_whopper_combo()
            order_repository = OrderRepositorySpy(get_order_response=order)
            product_repository = ProductRepositorySpy(is_menu_valid_response=True,
                                                      is_option_response=True,
                                                      is_valid_solution_response=True,
                                                      get_max_quantity_response=100,
                                                      get_parts_response=[
                                                          ProductPart(6060, 50801, 1, 1, 1),
                                                          ProductPart(6060, 50802, 1, 10, 2)
                                                      ])
            interactor = a_do_option_interactor() \
                .with_product_repository(product_repository) \
                .with_order_repository(order_repository) \
                .build()

            interactor.execute(pos_id, order_id, line_number, "1.1051.730000.6060", 3)

            assert product_repository.get_parts_call.args[0] == 6060

            line = order_repository.add_line_call.all_args[0][0]  # type: Line
            assert line.part_code == 730000
            assert line.quantity == 3
            assert line.line_number == 2
            assert line.item_id == "1.1051"
            assert len(line.lines) == 0

            line = order_repository.add_line_call.all_args[1][0]  # type: Line
            assert line.part_code == 6060
            assert line.quantity == 3
            assert line.line_number == 2
            assert line.item_id == "1.1051.730000"
            assert len(line.lines) == 0

            line = order_repository.add_line_call.all_args[2][0]  # type: Line
            assert line.part_code == 50801
            assert line.quantity == 1
            assert line.line_number == 2
            assert line.item_id == "1.1051.730000.6060"
            assert len(line.lines) == 0

            line = order_repository.add_line_call.all_args[3][0]  # type: Line
            assert line.part_code == 50802
            assert line.quantity == 2
            assert line.line_number == 2
            assert line.item_id == "1.1051.730000.6060"
            assert len(line.lines) == 0

        def test_whenOldSolutionHasParts_theSonsOfTheSolutionAreRemoved(self):
            order = an_order_with_a_whopper_combo_with_supreme_fries_already_sold()
            order_repository = OrderRepositorySpy(get_order_response=order)
            product_repository = ProductRepositorySpy(is_menu_valid_response=True,
                                                      is_option_response=True,
                                                      is_valid_solution_response=True,
                                                      get_max_quantity_response=100,
                                                      get_parts_response=[
                                                          ProductPart(6060, 50801, 1, 1, 1),
                                                          ProductPart(6060, 50802, 1, 10, 2)
                                                      ])
            interactor = a_do_option_interactor() \
                .with_product_repository(product_repository) \
                .with_order_repository(order_repository) \
                .build()

            interactor.execute(pos_id, order_id, line_number, "1.1051.730000.6060", 0)

            line = order_repository.update_line_call.all_args[0][0]  # type: Line
            assert line.part_code == 6060
            assert line.quantity == 0
            assert line.line_number == 2
            assert line.item_id == "1.1051.730000"

            line = order_repository.update_line_call.all_args[1][0]  # type: Line
            assert line.part_code == 730000
            assert line.quantity == 0
            assert line.line_number == 2
            assert line.item_id == "1.1051"

            line = order_repository.delete_sons_call.args[0]  # type: Line
            assert line.part_code == 6060
            assert line.quantity == 0
            assert line.line_number == 2
            assert line.item_id == "1.1051.730000"

    class TestDoOptionWithDefaultOption(object):
        def test_whenTheSolutionHasADefaultOption_theDefaultOptionsIsAlsoSold(self):
            order = an_order_with_a_whopper_combo()
            order_repository = OrderRepositorySpy(get_order_response=order)
            product_repository = ProductRepositorySpy(is_menu_valid_response=True,
                                                      is_option_response=True,
                                                      is_valid_solution_response=True,
                                                      get_max_quantity_response=100,
                                                      get_default_options_response={
                                                          7070: [
                                                              DefaultOption(18000, [2345]),
                                                              DefaultOption(19000, [1111, 2222])
                                                          ]
                                                      })
            interactor = a_do_option_interactor() \
                .with_product_repository(product_repository) \
                .with_order_repository(order_repository) \
                .build()

            interactor.execute(pos_id, order_id, line_number, "1.1051.730000.7070", 1)

            assert product_repository.get_default_options_call.all_args[0][0] == 7070
            assert product_repository.get_default_options_call.all_args[1][0] == 2345
            assert product_repository.get_default_options_call.all_args[2][0] == 1111
            assert product_repository.get_default_options_call.all_args[3][0] == 2222

            line = order_repository.add_line_call.all_args[0][0]  # type: Line
            assert line.part_code == 730000
            assert line.quantity == 1
            assert line.line_number == 2
            assert line.item_id == "1.1051"
            assert len(line.lines) == 0

            line = order_repository.add_line_call.all_args[1][0]  # type: Line
            assert line.part_code == 7070
            assert line.quantity == 1
            assert line.line_number == 2
            assert line.item_id == "1.1051.730000"
            assert len(line.lines) == 0

            line = order_repository.add_line_call.all_args[2][0]  # type: Line
            assert line.part_code == 18000
            assert line.quantity == 1
            assert line.line_number == 2
            assert line.item_id == "1.1051.730000.7070"
            assert len(line.lines) == 0

            line = order_repository.add_line_call.all_args[3][0]  # type: Line
            assert line.part_code == 2345
            assert line.quantity == 1
            assert line.line_number == 2
            assert line.item_id == "1.1051.730000.7070.18000"
            assert len(line.lines) == 0

            line = order_repository.add_line_call.all_args[4][0]  # type: Line
            assert line.part_code == 19000
            assert line.quantity == 2
            assert line.line_number == 2
            assert line.item_id == "1.1051.730000.7070"
            assert len(line.lines) == 0

            line = order_repository.add_line_call.all_args[5][0]  # type: Line
            assert line.part_code == 1111
            assert line.quantity == 1
            assert line.line_number == 2
            assert line.item_id == "1.1051.730000.7070.19000"
            assert len(line.lines) == 0

            line = order_repository.add_line_call.all_args[6][0]  # type: Line
            assert line.part_code == 2222
            assert line.quantity == 1
            assert line.line_number == 2
            assert line.item_id == "1.1051.730000.7070.19000"
            assert len(line.lines) == 0

        def test_whenTheSolutionHasADefaultOptionAndTheDefaultOptionHasParts_theDefaultOptionsIsSoldWithParts(self):
            order = an_order_with_a_whopper_combo()
            order_repository = OrderRepositorySpy(get_order_response=order)
            product_repository = ProductRepositorySpy(is_menu_valid_response=True,
                                                      is_option_response=True,
                                                      is_valid_solution_response=True,
                                                      get_max_quantity_response=100,
                                                      get_default_options_response={
                                                          7070: [
                                                              DefaultOption(18000, [2345])
                                                          ]
                                                      },
                                                      get_parts_response={2345: [
                                                          ProductPart(2345, 5555, 1, 1, 1),
                                                          ProductPart(2345, 6666, 1, 10, 2),
                                                          ProductPart(2345, 7777, 0, 1, 1)
                                                      ]})
            interactor = a_do_option_interactor() \
                .with_product_repository(product_repository) \
                .with_order_repository(order_repository) \
                .build()

            interactor.execute(pos_id, order_id, line_number, "1.1051.730000.7070", 1)

            assert product_repository.get_default_options_call.all_args[0][0] == 7070
            assert product_repository.get_default_options_call.all_args[1][0] == 2345

            line = order_repository.add_line_call.all_args[0][0]  # type: Line
            assert line.part_code == 730000
            assert line.quantity == 1
            assert line.line_number == 2
            assert line.item_id == "1.1051"
            assert len(line.lines) == 0

            line = order_repository.add_line_call.all_args[1][0]  # type: Line
            assert line.part_code == 7070
            assert line.quantity == 1
            assert line.line_number == 2
            assert line.item_id == "1.1051.730000"
            assert len(line.lines) == 0

            line = order_repository.add_line_call.all_args[2][0]  # type: Line
            assert line.part_code == 18000
            assert line.quantity == 1
            assert line.line_number == 2
            assert line.item_id == "1.1051.730000.7070"
            assert len(line.lines) == 0

            line = order_repository.add_line_call.all_args[3][0]  # type: Line
            assert line.part_code == 2345
            assert line.quantity == 1
            assert line.line_number == 2
            assert line.item_id == "1.1051.730000.7070.18000"
            assert len(line.lines) == 0

            line = order_repository.add_line_call.all_args[4][0]  # type: Line
            assert line.part_code == 5555
            assert line.quantity == 1
            assert line.line_number == 2
            assert line.item_id == "1.1051.730000.7070.18000.2345"
            assert len(line.lines) == 0

            line = order_repository.add_line_call.all_args[5][0]  # type: Line
            assert line.part_code == 6666
            assert line.quantity == 2
            assert line.line_number == 2
            assert line.item_id == "1.1051.730000.7070.18000.2345"
            assert len(line.lines) == 0

            line = order_repository.add_line_call.all_args[6][0]  # type: Line
            assert line.part_code == 7777
            assert line.quantity == 1
            assert line.line_number == 2
            assert line.item_id == "1.1051.730000.7070.18000.2345"
            assert len(line.lines) == 0


def an_order_with_two_whoppers():
    return OrderBuilder() \
        .add_line(LineBuilder().with_line_number(1).with_item_id("1").with_part_code(1050)) \
        .add_line(LineBuilder().with_line_number(2).with_item_id("1").with_part_code(1050)) \
        .build()


def an_order_with_two_whoppers_with_ingredients():
    return OrderBuilder() \
        .add_line(LineBuilder().with_line_number(1).with_item_id("1").with_part_code(1050)) \
        .add_line(LineBuilder().with_line_number(2).with_item_id("1").with_part_code(1050)
                  .add_line(LineBuilder()
                            .with_line_number(2)
                            .with_item_id("1.1050")
                            .with_part_code(820000)
                            .with_quantity(3)
                            .add_line(LineBuilder()
                                      .with_line_number(2)
                                      .with_item_id("1.1050.820000")
                                      .with_part_code(270002)
                                      .with_quantity(1))
                            .add_line(LineBuilder()
                                      .with_line_number(2)
                                      .with_item_id("1.1050.820000")
                                      .with_part_code(270003)
                                      .with_quantity(2))
                            )
                  )\
        .build()


def an_order_with_a_whopper_combo():
    return OrderBuilder() \
        .add_line(LineBuilder().with_line_number(1).with_item_id("1").with_part_code(1051)) \
        .add_line(LineBuilder().with_line_number(2).with_item_id("1").with_part_code(1051)
                  .add_line(LineBuilder().with_line_number(2).with_item_id("1.1051").with_part_code(1050))
                  ) \
        .build()


def an_order_with_a_whopper_combo_with_supreme_fries_already_sold():
    return OrderBuilder() \
        .add_line(LineBuilder().with_line_number(1).with_item_id("1").with_part_code(1051)) \
        .add_line(LineBuilder().with_line_number(2).with_item_id("1").with_part_code(1051)
                  .add_line(LineBuilder().with_line_number(2).with_item_id("1.1051").with_part_code(1050))
                  .add_line(LineBuilder()
                            .with_line_number(2)
                            .with_item_id("1.1051")
                            .with_part_code(730000)
                            .with_quantity(1)
                            .add_line(LineBuilder()
                                      .with_line_number(2)
                                      .with_item_id("1.1051.730000")
                                      .with_part_code(6060)
                                      .with_quantity(1)
                                      .add_line(LineBuilder()
                                                .with_line_number(2)
                                                .with_item_id("1.1051.730000.6060")
                                                .with_part_code(50801)
                                                .with_quantity(1))
                                      .add_line(LineBuilder()
                                                .with_line_number(2)
                                                .with_item_id("1.1051.730000.6060")
                                                .with_part_code(50802)
                                                .with_quantity(1))
                                      )
                            )
                  ) \
        .build()


def a_do_option_interactor():
    return DoOptionInteractorBuilder()


class DoOptionInteractorBuilder(object):
    def __init__(self):
        self.product_repository = ProductRepositoryStub()
        self.order_repository = OrderRepositoryStub()

    def with_product_repository(self, product_repository):
        self.product_repository = product_repository
        return self

    def with_order_repository(self, order_repository):
        self.order_repository = order_repository
        return self

    def build(self):
        return DoOptionInteractor(self.order_repository, self.product_repository)


class ProductRepositoryStub(ProductRepository):
    def __init__(self,
                 is_menu_valid_response=True,
                 is_option_response=True,
                 is_valid_solution_response=True,
                 get_max_quantity_response=99,
                 get_parts_response=None,
                 get_default_options_response=None):
        self.is_menu_valid_response = is_menu_valid_response
        self.is_option_response = is_option_response
        self.is_valid_solution_response = is_valid_solution_response
        self.get_max_quantity_response = get_max_quantity_response
        self.get_parts_response = get_parts_response
        self.get_default_options_response = get_default_options_response

    def is_menu_valid(self, menu_id):
        return self.is_menu_valid_response

    def is_option(self, part_code):
        return self.is_option_response

    def is_valid_solution(self, option_part_code, part_code):
        return self.is_valid_solution_response

    def get_max_quantity(self, part_code, son_part_code):
        return self.get_max_quantity_response

    def get_parts(self, part_code):
        if isinstance(self.get_parts_response, dict):
            if part_code in self.get_parts_response:
                return self.get_parts_response[part_code]
            return None
        return self.get_parts_response

    def get_default_options(self, part_code):
        if isinstance(self.get_default_options_response, dict):
            if part_code in self.get_default_options_response:
                return self.get_default_options_response[part_code]
            return None
        return self.get_default_options_response


class ProductRepositorySpy(ProductRepositoryStub):
    def __init__(self,
                 is_menu_valid_response=True,
                 is_option_response=False,
                 is_valid_solution_response=True,
                 get_max_quantity_response=99,
                 get_parts_response=None,
                 get_default_options_response=None):
        super(ProductRepositorySpy, self).__init__(is_menu_valid_response,
                                                   is_option_response,
                                                   is_valid_solution_response,
                                                   get_max_quantity_response,
                                                   get_parts_response,
                                                   get_default_options_response)
        self.is_menu_valid_call = SpyCall()
        self.is_option_call = SpyCall()
        self.is_valid_solution_call = SpyCall()
        self.get_max_quantity_call = SpyCall()
        self.get_parts_call = SpyCall()
        self.get_default_options_call = SpyCall()

    def is_menu_valid(self, menu_id):
        self.is_menu_valid_call.register_call(menu_id)
        return super(ProductRepositorySpy, self).is_menu_valid(menu_id)

    def is_option(self, part_code):
        self.is_option_call.register_call(part_code)
        return super(ProductRepositorySpy, self).is_option(part_code)

    def is_valid_solution(self, option_part_code, part_code):
        self.is_valid_solution_call.register_call(option_part_code, part_code)
        return super(ProductRepositorySpy, self).is_valid_solution(option_part_code, part_code)

    def get_max_quantity(self, part_code, son_part_code):
        self.get_max_quantity_call.register_call(part_code, son_part_code)
        return super(ProductRepositorySpy, self).get_max_quantity(part_code, son_part_code)

    def get_parts(self, part_code):
        self.get_parts_call.register_call(part_code)
        return super(ProductRepositorySpy, self).get_parts(part_code)

    def get_default_options(self, part_code):
        self.get_default_options_call.register_call(part_code)
        return super(ProductRepositorySpy, self).get_default_options(part_code)



