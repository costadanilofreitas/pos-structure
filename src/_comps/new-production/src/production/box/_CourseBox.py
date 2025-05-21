from logging import Logger
from datetime import datetime, timedelta

from production.box import ProductionBox
from production.model import Item
from typing import List, Dict, Union, Any

from ._OrderChangerProductionBox import OrderChangerProductionBox


class CourseBox(OrderChangerProductionBox):
    def __init__(self, name, sons, courses, publish_scheduler, logger=None):
        # type: (str, Union[ProductionBox, List[ProductionBox]], List[CourseConfiguration], Any, Logger) -> None  # noqa
        super(CourseBox, self).__init__(name, sons, logger)
        self.courses = courses
        self.publish_scheduler = publish_scheduler
        self.course_dict = {}
        self.course_name_dict = {}
        for course_index in range(0, len(self.courses)):
            for part_code in courses[course_index].products:
                self.course_dict[part_code] = course_index
                self.course_name_dict[courses[course_index].name] = course_index

    def change_order(self, order):
        if len(self.courses) == 0 or order.skip_course:
            return order

        courses = self.separate_product_in_courses(order)
        course = self.get_first_not_ready_course(courses)
        if course is None:
            return order

        if course.is_first:
            order.items = course.products
            return order

        now = datetime.now()
        last_done_time = self.get_last_done_time_of_course(courses[course.index - 1])
        if last_done_time is None or self.has_elapsed_course_interval(now, courses[course.index - 1], last_done_time):
            order.items = course.products
            if last_done_time is not None:
                order.display_time = self.get_display_time(courses[course.index - 1], last_done_time).isoformat()
        else:
            wait_time = self.calculate_wait_time(now, courses[course.index - 1], last_done_time)
            if wait_time > 0:
                self.publish_scheduler.schedule_publish(order.order_id, wait_time)
            order.items = []

        return order

    @staticmethod
    def get_first_not_ready_course(courses):
        for course in courses:
            if not course.ready:
                return course
        return None
        
    def separate_product_in_courses(self, order):
        course_ready = []  # type: List[bool]
        course_products = {}  # type: Dict[int, List[Item]]
        courses = []

        for course_index in range(0, len(self.courses)):
            course_ready.append(True)
            course_products[course_index] = []

        for item in order.items:
            if order.sale_type == "DELIVERY":
                course_index = 0
            else:
                course_index = self.get_course_index(item)
            course_products[course_index].append(item)
            if item.multiplied_qty > 0 and not item.is_served():
                course_ready[course_index] = False

        self._send_fire_items_to_first_available_course(course_products)

        for index in range(0, len(course_ready)):
            courses.append(CourseBox.Course(
                course_products[index],
                course_ready[index],
                index,
                index == 0,
                index == len(course_ready) - 1))

        for index in range(0, len(courses)):
            all_course_items_canceled = True
            for product in courses[index].products:
                if product.qty > 0:
                    all_course_items_canceled = True
                    break

            if all_course_items_canceled and index < len(courses) - 1:
                for product in courses[index].products:
                    courses[index + 1].products.append(product)

        return courses

    def _send_fire_items_to_first_available_course(self, course_products):
        course_qty, first_course_with_products = self._count_courses(course_products)
        self._move_fire_products(course_products, course_qty, first_course_with_products)

    @staticmethod
    def _move_fire_products(course_products, course_qty, first_course_with_products):
        if course_qty > 1:
            for index in range(first_course_with_products + 1, len(course_products)):
                for item in course_products[index][:]:
                    if "fire" in item.properties:
                        course_products[first_course_with_products].append(item)
                        course_products[index].remove(item)

    @staticmethod
    def _count_courses(course_products):
        course_qty = 0
        first_course_with_products = None
        for course_index in course_products:
            if len(course_products[course_index]) > 0:
                course_qty += 1
                if first_course_with_products is None:
                    first_course_with_products = course_index
        return course_qty, first_course_with_products

    def get_course_index(self, item):
        if self.item_has_course_set(item):
            course_index = self.get_course_index_from_set_course(item)
        elif item.part_code in self.course_dict:
            course_index = self.course_dict[item.part_code]
        else:
            course_index = 0
        return course_index

    def item_has_course_set(self, item):
        return item.properties is not None and \
               "course" in item.properties and item.properties["course"] in self.course_name_dict

    def get_course_index_from_set_course(self, item):
        return self.course_name_dict[item.properties["course"]]

    def has_elapsed_course_interval(self, now, course, last_done_time):
        next_course_ready = last_done_time + timedelta(seconds=self.courses[course.index].next_course_wait_time)
        return int((now - next_course_ready).total_seconds()) >= 0

    def get_display_time(self, course, last_done_time):
        course_wait = self.courses[course.index].next_course_wait_time
        return last_done_time + timedelta(seconds=course_wait)

    def calculate_wait_time(self, now, course, last_done_time):
        return int(((last_done_time + timedelta(seconds=self.courses[course.index].next_course_wait_time)) - now)
                   .total_seconds())

    @staticmethod
    def get_last_done_time_of_course(course):
        last_done_time = None
        for item in course.products:
            done_time = item.get_last_tag_time("served")
            if done_time is not None and (last_done_time is None or last_done_time < done_time):
                last_done_time = done_time
        return last_done_time

    class CourseConfiguration(object):
        def __init__(self, name, products, next_course_wait_time):
            self.name = name
            self.products = products
            self.next_course_wait_time = next_course_wait_time

    class Course(object):
        def __init__(self, products, ready, index, is_first, is_last):
            self.products = products
            self.ready = ready
            self.index = index
            self.is_first = is_first
            self.is_last = is_last
