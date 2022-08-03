# import pyvista as pv
# from pyvista.examples import examples
#
#
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




