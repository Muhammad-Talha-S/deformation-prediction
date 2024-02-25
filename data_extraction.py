"""
- data_extraction.py
    - Muhammad Talha Saleem <talhasheikh878@gmail.com>
"""
import re
from pathlib import Path
import pandas as pd


class CreateDataFrame:

    def __init__(self):
        """
        Initializes the Model class.
        This constructor method initializes the instance variables of the Model class,
        including dictionaries for training set data, node coordinates, displacement data,
        and a list for output displacement values.
        """
        self.training_set_dict = dict()
        self.node_dict = dict()
        self.load = str()
        self.displacement_dict = dict()
        self.output_data_set = []

    def extract_data(self, input_folder: Path):
        """
        Extracts and processes data from input files in the specified folder.

        Args:
        input_folder (str): The path to the input folder containing variant subfolders.

        This function reads input files (inp, dat, and log) for each variant,
        extracts node coordinates, loads, and displacement values, and populates
        class dictionaries for further analysis.

        Note:
        - Requires the input_folder to be organized with subfolders for each variant.
        - Assumes specific file naming conventions and content structures within input files.

        """
        keyword_pattern = re.compile(r"\*\w*\s?[+%]?")
        counter = 0
        for variant_folder in input_folder.iterdir():
            if variant_folder.is_dir() and variant_folder.stem.startswith("Varient"):
                counter += 1
                inp_filepath = [
                    file for file in variant_folder.iterdir() if file.suffix == ".inp"
                ][0]
                dat_filepath = [
                    file for file in variant_folder.iterdir() if file.suffix == ".dat"
                ][0]
                log_filepath = [
                    file for file in variant_folder.iterdir() if file.suffix == ".log"
                ][0]
                displacement_values = []
                inp_file = open(inp_filepath, "r")
                dat_file = open(dat_filepath, "r")
                log_file = open(log_filepath, "r")
                isCompleted = (
                    True
                    if log_file.readlines()[-1].split()[-1] == "COMPLETED"
                    else False
                )
                if isCompleted:
                    for line in inp_file:
                        if re.match(keyword_pattern, line):
                            keyword = line
                        elif keyword.startswith("**"):
                            continue
                        else:
                            if keyword.startswith("*NODE"):
                                if "PRINT" in keyword:
                                    continue
                                line_data = line.split(",")
                                node_id = line_data[0].strip()
                                x_cord = float(line_data[1].strip())
                                y_cord = float(line_data[2].strip())
                                z_cord = float(line_data[3].strip())
                                cordinates = [x_cord, y_cord, z_cord]
                                self.node_dict.update({node_id: cordinates})
                            elif keyword.startswith("*CLOAD"):
                                self.load = line.split(",")[-1].strip()
                                self.load = float(self.load)
                    for line in dat_file:
                        if "THE FOLLOWING TABLE IS PRINTED FOR ALL NODES" in line:
                            line = next(dat_file)
                            line = next(dat_file)
                            line = next(dat_file)
                            for line in dat_file:
                                if "MAXIMUM" in line:
                                    break
                                data = line.split()
                                if len(data) > 1:
                                    node_id = data[0]
                                    U1 = float(data[1])
                                    U2 = float(data[2])
                                    U3 = float(data[3])
                                    displacement = [U1, U2, U3]
                                    displacement_values.extend(displacement)
                        cordinates = []
                        for _, values in self.node_dict.items():
                            cordinates.extend(values)
                        cordinates.append(self.load)
                        self.training_set_dict[counter] = cordinates
                    self.output_data_set.append(displacement_values)

    def create_dataFrame(self, input_param_excel: Path, output_param_excel: Path):
        """
        Creates and exports data frames from internal dictionaries to Excel files.
        This function converts data stored in the class's internal dictionaries
        into Pandas DataFrames, formats them appropriately, and exports them to
        Excel files named 'input.xlsx' and 'output.xlsx'.
        The data frames include information about node coordinates, forces, and displacement values.
        Note:
        - Requires prior data extraction and processing using the `extract_data` method.
        - Uses the Pandas library for data frame creation.
        - Generates Excel files in the current working directory.
        """
        data_set = []
        for _, value in self.training_set_dict.items():
            data_set.append(value)
        input_columns = [
            "X1", "Y1", "Z1",
            "X2", "Y2", "Z2",
            "X3", "Y3", "Z3",
            "X4", "Y4", "Z4",
            "X5", "Y5", "Z5",
            "X6", "Y6", "Z6",
            "X7", "Y7", "Z7",
            "X8", "Y8", "Z8",
            "X9", "Y9", "Z9",
            "Force",
        ]
        input_dataFrame = pd.DataFrame(data_set, columns=input_columns)
        output_columns = [
            "DX2", "DY2", "DZ2",
            "DX3", "DY3", "DZ3",
            "DX4", "DY4", "DZ4",
            "DX5", "DY5", "DZ5",
            "DX7", "DY7", "DZ7",
            "DX9", "DY9", "DZ9",
        ]
        output_dataFrame = pd.DataFrame(self.output_data_set, columns=output_columns)
        with pd.ExcelWriter(input_param_excel, engine="xlsxwriter") as writer:
            input_dataFrame.to_excel(writer, sheet_name="NodeCoordinates", index=False)
        with pd.ExcelWriter(output_param_excel, engine="xlsxwriter") as writer:
            output_dataFrame.to_excel(
                writer, sheet_name="Displacement values ", index=False
            )

if __name__ == '__main__':
    #
    working_dir = Path.cwd()
    geometry_data_folder = working_dir / "brake_pad_geometry_variants"
    input_param_excel = working_dir / "training_data_excel" / 'input_param.xlsx'
    output_param_excel = working_dir / "training_data_excel" / 'output_param.xlsx'
    #
    brake_pad_data = CreateDataFrame()
    brake_pad_data.extract_data(geometry_data_folder)
    brake_pad_data.create_dataFrame(input_param_excel, output_param_excel)
    #
