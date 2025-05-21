from typing import List
from _BaseStructureBuilder import BaseStructureBuilder
from _BasePythonBuilder import BasePythonBuilder
from _PersistNormalBuilder import PersistNormalBuilder


class MWPosBuilder(object):
    CompBase = u"CompBase"
    CompBasePython = u"CompBasePython"
    CompPersistenceNormal = u"CompPersistenceNormal"

    CompDependencies = {
        CompBase: [],
        CompBasePython: [CompBase],
        CompPersistenceNormal: [CompBasePython]
    }

    CompBuilders = {
        CompBase: BaseStructureBuilder,
        CompBasePython: BasePythonBuilder,
        CompPersistenceNormal: PersistNormalBuilder
    }

    def __init__(self, source_pos_directory, dest_pos_directory):
        self.source_pos_directory = source_pos_directory
        self.dest_pos_directory = dest_pos_directory

    def build_with_components(self, components):
        # type: (List[unicode]) -> None
        built_components = []

        for component in components:
            self._build_component_with_dependencies(component, built_components)

    def _build_component_with_dependencies(self, component, built_components):
        # type: (unicode, List[unicode]) -> None
        dependencies = self.CompDependencies[component]
        for dependency in dependencies:
            if dependency not in built_components:
                self._build_component_with_dependencies(dependency, built_components)

        builder_class = self.CompBuilders[component]
        builder_instance = builder_class(self.source_pos_directory, self.dest_pos_directory)
        builder_instance.build()

        built_components.append(component)
