import numpy as np
import pyvista as pv

# تنظیمات اولیه
np.random.seed(42)  # برای تکرارپذیری نتایج تصادفی

# ایجاد یک ابر سه‌بعدی از نقاط (شبیه‌سازی گاز بین‌ستاره‌ای)
n_points = 5000
cloud = np.random.rand(n_points, 3) * 100  # ابر در مکعب 100x100x100

# ایجاد یک میدان چگالی و یونش تصادفی (برای شبیه‌سازی)
density = np.random.rand(n_points) * 0.5 + 0.1  # چگالی بین 0.1 تا 0.6
ionization = np.random.rand(n_points)  # میزان یونش بین 0 تا 1

# ایجاد یک PyVista Polی می‌کنم. بیایید با محتوای دقیق فایل دوباره تلاش کنیم:yData
point_cloud = pv.PolyData(cloud)

# اضافه کردن داده‌های چگالی و یونش به ابر نقاط
point_cloud["density"] = density
point_cloud["ionization"] = ionization

# ایجاد یک منبع نور ستاره‌ای (منبع یونش)
star_position = np.array([50, 50, 50])  # مرکز منطقه
star = pv.Sphere(radius=5, center=star_position)

# رنگ‌آمیزی ابر بر اساس میزان یونش (با استفاده از colormap)
cmap = "plasma"  # یا "viridis", "magma"

# رسم ابر نقاط
plotter = pv.Plotter()
plotter.add_mesh(
    point_cloud,
    scalars="ionization",
    opacity="density",  # نقاط چگال‌تر مات‌تر دیده می‌شوند
    point_size=3,
    cmap=cmap,
    clim=[0, 1],  # محدوده رنگ‌آمیزی
)
plotter.add_mesh(star, color="yellow")  # ستاره مرکزی

# اضافه کردن برچسب و محورها
plotter.add_title("3D Simulation of H II Region")
plotter.add_axes()

# نمایش پلات
plotter.show()