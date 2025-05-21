from logging import Logger

from production.box import CourseBox
from production.repository import ProductRepository
from typing import List, Optional, Union, Tuple, Any

from ._ProductionBox import ProductionBox


class CustomParamCourseBox(CourseBox):
    def __init__(self, name, sons, product_repository, publish_scheduler, courses, logger=None):
        # type: (str, Optional[Union[List[ProductionBox]], ProductionBox], ProductRepository, List[Tuple[str, int]], Any, Logger) -> None # noqa
        course_products = product_repository.get_courses_products()
        configs = []
        if len(course_products) > 0:
            for course_config in courses:
                configuration = CourseBox.CourseConfiguration(course_config[0],
                                                              course_products[course_config[0]] if course_config[0] in course_products else {},
                                                              course_config[1])
                configs.append(configuration)

        super(CustomParamCourseBox, self).__init__(name,
                                                   sons,
                                                   configs,
                                                   publish_scheduler,
                                                   logger)
