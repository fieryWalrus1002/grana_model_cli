from typing import Any, Iterator
import pandas as pd
import random
from math import pi
import numpy as np
import pickle
import os


class ObjectData:
    """This data structure"""

    def __init__(
        self,
        pos_csv_filename: str,
        spawn_seed=0,
        res_path: str = "src/grana_model/res/",
    ):
        self.__object_colors_dict = {
            "LHCII": (0, 51, 0, 255),  # darkest green
            "LHCII_monomer": (0, 75, 0, 255),  # darkest green
            "C2S2M2": (0, 102, 0, 255),
            "C2S2M": (0, 153, 0, 255),
            "C2S2": (102, 204, 0, 255),
            "C2": (128, 255, 0, 255),
            "C1": (178, 255, 102, 255),  # lightest green
            "CP43": (178, 255, 103, 255),  # same coordinates as C1, same color
            "cytb6f": (51, 153, 255, 255),  # light blue
        }
        self.res_path = res_path
        self.type_dict = {
            obj_type: self.__generate_object_dict(obj_type)
            for obj_type in self.__object_colors_dict.keys()
        }

        self.pos_list = self.__import_pos_data(
            f"{self.res_path}/grana_coordinates/{pos_csv_filename}"
        )

        self.object_list = self.__generate_object_list(spawn_seed=spawn_seed,)

    def __generate_object_dict(self, obj_type: str):
        obj_dict = {
            "obj_type": obj_type,
            "shapes_compound": self.__load_compound_shapes(obj_type),
            "shapes_simple": self.__load_simple_shapes(obj_type),
            # "sprite": image.load(f"{self.res_path}/sprites/{obj_type}.png"),
            "sprite": f"{obj_type.lower()}.png",
            "color": self.__object_colors_dict[obj_type],
        }
        return obj_dict

    def __import_pos_data(self, file_path):
        """Imports the (x, y) positions from the csv data file provided in filename"""
        imported_csv = pd.read_csv(file_path)
        return pd.DataFrame(imported_csv, columns=["x", "y"]).values.tolist()

    def __load_simple_shapes(self, obj_type):
        with open(f"{self.res_path}shapes/{obj_type}_simple.pickle", "rb") as f:
            return pickle.load(f)

    def __load_compound_shapes(self, obj_type):
        with open(f"{self.res_path}shapes/{obj_type}.pickle", "rb") as f:
            return pickle.load(f)

    # def generate_secondary_object_list(
    #     self,
    #     type_dict: dict[Any, Any],
    #     spawn_seed=0,
    # ) -> Iterator[Any]:
    #     '''
    #     Generates a list of dicts, each containing the data needed to create a
    #     PSII secondary structure, in this format:
    #     {
    #     "obj_type": str,  # ex. "C2S2M2"
    #     "pos_xy": list,  # [x, y] coordinates
    #     "angle": float, # angle in radians
    #     "sprite": ImageData object, a spirte for the object type
    #     "color": (0,0,0,255) RGBA color tuple
    #     "shapes_simple": simple shape coordinate list
    #     "shapes_compound": list of shape coordinate pairs, one for each of the
    #     various compound shapes that are needed to create the PSII structure
    #     }
    #     The list will be an iterator object that you can use the next() function
    #      on to get the next item
    #     '''
    #     obj_list = []

    #     for num in  in zip(pos_list, obj_types):
    #         obj_entry = {
    #             "obj_type": obj_type,
    #             "pos": pos,
    #             "angle": (2 * pi * random()),
    #             "sprite": type_dict[obj_type]["sprite"],
    #             "color": type_dict[obj_type]["color"],
    #             "shapes_simple": type_dict[obj_type]["shapes_simple"],
    #             "shapes_compound": type_dict[obj_type]["shapes_compound"],
    #         }

    #         obj_list.append(obj_entry)

    #     return iter(obj_list)

    # def convert_shape_csv_to_shape_list(self, obj_dict):
    # ''' used to turn csv files into a list of shape lists'''
    #     return [
    #         pd.read_csv(file).values.tolist()
    #         for file in obj_dict["shapes_simple"]
    #     ]

    def __generate_object_list(self, spawn_seed=0,) -> Iterator[Any]:
        """
        Generates a list of dicts, each containing the data needed to create a
        PSII structure, in this format:
        {
        "obj_type": str,  # ex. "C2S2M2"
        "pos_xy": list,  # [x, y] coordinates
        "angle": float, # angle in radians
        "sprite": ImageData object, a spirte for the object type
        "color": (0,0,0,255) RGBA color tuple
        "shapes_simple": simple shape coordinate list
        "shapes_compound": list of shape coordinate pairs, one for each of the
        various compound shapes that are needed to create the PSII structure
        }
        The list will be an iterator object that you can use the next() function
         on to get the next item
        """
        obj_list = []
        structure_types = ["C2S2M2", "C2S2M", "C2S2", "C2", "C1", "CP43"]
        structure_p = [0.57, 0.17, 0.12, 0.09, 0.03, 0.02]

        if spawn_seed == 0:
            rng = np.random.default_rng()
        else:
            rng = np.random.default_rng(spawn_seed)

        obj_types = rng.choice(
            structure_types, len(self.pos_list), replace=True, p=structure_p
        )
        random_pos_list = random.sample(self.pos_list, len(self.pos_list))
        # print(len(random_pos_list))

        for pos, obj_type in zip(random_pos_list, obj_types):
            obj_entry = {
                "obj_type": obj_type,
                "pos": pos,
                "angle": (2 * pi * random.random()),
                "sprite": self.type_dict[obj_type]["sprite"],
                "color": self.type_dict[obj_type]["color"],
                "shapes_simple": self.type_dict[obj_type]["shapes_simple"],
                "shapes_compound": self.type_dict[obj_type]["shapes_compound"],
            }

            obj_list.append(obj_entry)

        return iter(obj_list)

    # def convert_shape_csv_to_shape_list(self, obj_dict):
    # ''' used to turn csv files into a list of shape lists'''
    #     return [
    #         pd.read_csv(file).values.tolist()
    #         for file in obj_dict["shapes_simple"]
    #     ]


class ObjectDataExistingData(ObjectData):
    """This data structure"""

    def __init__(self, pos_csv_filename: str, spawn_seed=0):
        self.__object_colors_dict = {
            "LHCII": (0, 51, 0, 255),  # darkest green
            "LHCII_monomer": (0, 75, 0, 255),  # darkest green
            "C2S2M2": (0, 102, 0, 255),
            "C2S2M": (0, 153, 0, 255),
            "C2S2": (102, 204, 0, 255),
            "C2": (128, 255, 0, 255),
            "C1": (178, 255, 102, 255),  # lightest green
            "CP43": (178, 255, 103, 255),  # same coordinates as C1, same color
            "cytb6f": (51, 153, 255, 255),  # light blue
        }
        self.res_path = "src/grana_model/res/"
        self.type_dict = {
            obj_type: self.__generate_object_dict(obj_type)
            for obj_type in self.__object_colors_dict.keys()
        }

        self.pos_list = self.__import_pos_data(
            f"{self.res_path}/grana_coordinates/{pos_csv_filename}"
        )

        self.object_list = self.__generate_object_list(spawn_seed=spawn_seed,)

    def __generate_object_dict(self, obj_type: str):
        obj_dict = {
            "obj_type": obj_type,
            "shapes_compound": self.__load_compound_shapes(obj_type),
            "shapes_simple": self.__load_simple_shapes(obj_type),
            # "sprite": image.load(f"{self.res_path}/sprites/{obj_type}.png"),
            "sprite": os.path.join(self.res_path, f"sprites/{obj_type}.png"),
            "color": self.__object_colors_dict[obj_type],
        }
        return obj_dict

    def __import_pos_data(self, file_path):
        """Imports the (x, y) positions from the csv data file provided in filename"""
        imported_csv = pd.read_csv(file_path)
        return pd.DataFrame(
            imported_csv, columns=["type", "x", "y", "angle"]
        ).values.tolist()

    def __load_simple_shapes(self, obj_type):
        with open(f"{self.res_path}shapes/{obj_type}_simple.pickle", "rb") as f:
            return pickle.load(f)

    def __load_compound_shapes(self, obj_type):
        with open(f"{self.res_path}shapes/{obj_type}.pickle", "rb") as f:
            return pickle.load(f)

    def __generate_object_list(self, spawn_seed=0,) -> Iterator[Any]:
        """
        Generates a list of dicts, each containing the data needed to create a
        PSII structure, in this format:
        {
        "obj_type": str,  # ex. "C2S2M2"
        "pos_xy": list,  # [x, y] coordinates
        "angle": float, # angle in radians
        "sprite": ImageData object, a spirte for the object type
        "color": (0,0,0,255) RGBA color tuple
        "shapes_simple": simple shape coordinate list
        "shapes_compound": list of shape coordinate pairs, one for each of the
        various compound shapes that are needed to create the PSII structure
        }
        The list will be an iterator object that you can use the next() function
         on to get the next item
        """
        obj_list = [
            {
                "obj_type": obj_type,
                "pos": (x, y),
                "angle": angle,
                "sprite": self.type_dict[obj_type]["sprite"],
                "color": self.type_dict[obj_type]["color"],
                "shapes_simple": self.type_dict[obj_type]["shapes_simple"],
                "shapes_compound": self.type_dict[obj_type]["shapes_compound"],
            }
            for obj_type, x, y, angle in self.pos_list
        ]

        return iter(obj_list)

    # def convert_shape_csv_to_shape_list(self, obj_dict):
    # ''' used to turn csv files into a list of shape lists'''
    #     return [
    #         pd.read_csv(file).values.tolist()
    #         for file in obj_dict["shapes_simple"]
    #     ]


if __name__ == "__main__":
    pass
