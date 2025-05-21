from production.box import CustomParamCourseBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class CustomParamCourseBoxBuilder(BoxBuilder):
    def __init__(self, product_repository, publish_scheduler, loggers):
        super(CustomParamCourseBoxBuilder, self).__init__(loggers)
        self.product_repository = product_repository
        self.publish_scheduler = publish_scheduler

    def build(self, config):
        # type: (BoxConfiguration) -> CustomParamCourseBox
        courses = self.get_extra(config, "Courses", None)
        param_courses = []
        for course in courses.keys():
            param_courses.append((course, int(courses[course]["WaitTime"]), int(courses[course]["Order"])))

        param_courses = sorted(param_courses, self.course_comparer)

        return CustomParamCourseBox(config.name,
                                    config.sons,
                                    self.product_repository,
                                    self.publish_scheduler,
                                    param_courses,
                                    self.get_logger(config))

    def course_comparer(self, c1, c2):
        return int(c1[2]) - int(c2[2])
