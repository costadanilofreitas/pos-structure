from production.box import ProductionBox
from typing import List, Dict, Any

from ._BoxConfiguration import BoxConfiguration
from ._ProductionTree import ProductionTree
from ._TreeConfig import TreeConfig
from ._ViewConfiguration import ViewConfiguration
from .boxfactory import ProductionBoxFactory
from .viewfactory import ViewFactory


class TreeBuilder(object):
    def __init__(self, box_factory, view_factory):
        # type: (ProductionBoxFactory, ViewFactory) -> None
        self.box_factory = box_factory
        self.view_factory = view_factory

    def build_trees(self, tree_configs, branch_configs, view_configs):
        # type: (List[TreeConfig], List[TreeConfig], List[ViewConfiguration]) -> List[ProductionTree]  # noqa
        views = {}
        for view in view_configs:
            views[view.name] = self.view_factory.build(view)
        self.box_factory.set_views(views)

        branches = {}
        for branch in branch_configs:
            branches[branch.name] = branch

        trees = []
        for tree_config in tree_configs:
            trees.append(self.build_tree(tree_config, branches))

        return trees

    def build_tree(self, tree_config, branches=None):
        # type: (TreeConfig, Dict[str, Any]) -> ProductionTree
        boxes = self.build_all_boxes(tree_config.boxes, branches)
        name_box_dict = self.get_name_box_dict(boxes)
        self.set_son_in_every_box(boxes, tree_config.boxes, name_box_dict)
        leaf_boxes = self.get_leaf_boxes(tree_config.boxes, name_box_dict)

        if isinstance(boxes[0], ProductionTree):
            return ProductionTree(tree_config.name, boxes[0].root, leaf_boxes)
        else:
            return ProductionTree(tree_config.name, boxes[0], leaf_boxes)

    def build_all_boxes(self, boxes, branches):
        # type: (List[BoxConfiguration], Dict[str, str]) -> List[ProductionBox]
        ret = []
        for box_config in boxes:
            if box_config.type == "Branch":
                box = self.build_tree(branches[box_config.extra_config["BranchName"]], branches)
                box.name = box_config.name
            else:
                box = self.box_factory.build(box_config)
            ret.append(box)
        return ret

    def get_name_box_dict(self, boxes):
        name_box_dict = {}
        for box in boxes:
            name_box_dict[box.name] = box
        return name_box_dict

    def set_son_in_every_box(self, boxes, box_configs, name_box_dict):
        # type: (List[ProductionBox], List[BoxConfiguration], Dict[str, ProductionBox]) -> None
        used_boxes = {}
        for box_config in box_configs:
            sons = []
            for son_name in box_config.sons:
                if son_name not in name_box_dict:
                    raise Exception("Box referencing invalid son: BoxName: {} - SonName: {}"
                                    .format(box_config.name, son_name))
                son_box = name_box_dict[son_name]
                used_boxes[son_box] = son_box
                if isinstance(son_box, ProductionTree):
                    sons.append(son_box.root)
                else:
                    sons.append(son_box)

            if isinstance(name_box_dict[box_config.name], ProductionTree):
                production_tree = name_box_dict[box_config.name]
                for leaf in production_tree.leaves:
                    leaf.sons = sons
            else:
                name_box_dict[box_config.name].sons = sons

        if len(boxes) == len(used_boxes):
            raise Exception("Tree with cycle (No root node found)")

        if len(boxes) - len(used_boxes) > 1:
            remaining = []
            for box in boxes:
                if box not in used_boxes:
                    remaining.append(box)

            remaining_names = ""
            for box in remaining:
                remaining_names += box.name + ", "
            remaining_names = remaining_names[:-2]
            raise Exception("Tree without single root node. Remaining nodes: {}".format(remaining_names))

    def get_leaf_boxes(self, box_configs, name_box_dict):
        leaf_boxes = []
        for box_config in box_configs:
            if len(box_config.sons) == 0:
                leaf_boxes.append(name_box_dict[box_config.name])

        return leaf_boxes
