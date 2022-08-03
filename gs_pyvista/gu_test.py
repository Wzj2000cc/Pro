import pyvista as pv
import numpy as np
from pyvista.examples import examples


# def CellPlot():
#     """
#     绘制六角梁并突出其中的一个Cell
#     :return: None
#     """
#     mesh = examples.load_hexbeam()
#     # 模型六角梁绘制
#     pl = pv.Plotter()  # 类的实例化(做画图前的准备)
#     pl.add_mesh(mesh, show_edges=True, color='white')
#     pl.add_points(mesh.points, color='red', point_size=20)
#     # 六角梁上描述特定的某一个cell
#     single_cell = mesh.extract_cells(mesh.n_cells - 1)  # 指定哪一个具体的cell
#     pl.add_mesh(single_cell, color='pink', edge_color='blue',
#                 line_width=5, show_edges=True)
#
#     pl.camera_position = [(6.20, 3.00, 7.50),
#                           (0.16, 0.13, 2.65),
#                           (-0.28, 0.94, -0.21)]
#
#     pl.show()
#
#
# CellPlot()

def Grid():
    values = np.linspace(40, 200, 125).reshape((5, 5, 5))
    values.shape

    # Create the spatial reference
    grid = pv.UniformGrid()

    # Set the grid dimensions: shape + 1 because we want to inject our values on
    #   the CELL data
    grid.dimensions = np.array(values.shape) + 1

    # Edit the spatial reference
    grid.origin = (100, 33, 55.6)  # The bottom left corner of the data set
    grid.spacing = (1, 1, 1)  # These are the cell sizes along each axis

    # Add the data values to the cell data
    grid.cell_data["money"] = values.flatten(order="F")  # Flatten the array!

    # Now plot the grid!
    grid.plot(show_edges=True)


Grid()
