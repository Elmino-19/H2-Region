#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
تجسم‌سازی سه‌بعدی فضای ستاره‌ای و ناحیه H II

این برنامه یک تجسم‌سازی سه‌بعدی واقعی‌تر از فضای ستاره‌ای و ناحیه H II ارائه می‌دهد
که شبیه به انیمیشن‌های نجومی است.

نویسنده: عرفان محمدنیا
"""

import numpy as np
import pyvista as pv
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import time
import random
from scipy.spatial.transform import Rotation as R


class StellarSpaceVisualization:
    """
    کلاس تجسم‌سازی سه‌بعدی فضای ستاره‌ای
    
    این کلاس یک تجسم‌سازی سه‌بعدی واقعی‌تر از فضای ستاره‌ای و ناحیه H II ارائه می‌دهد.
    """
    
    def __init__(self, universe_radius=100.0, hii_radius=20.0, n_stars=5000, n_dust=2000, n_nebula_points=50000):
        """
        مقداردهی اولیه کلاس StellarSpaceVisualization
        
        پارامترها:
            universe_radius (float): شعاع کلی فضای شبیه‌سازی شده
            hii_radius (float): شعاع ناحیه H II
            n_stars (int): تعداد ستارگان پس‌زمینه
            n_dust (int): تعداد ذرات غبار
            n_nebula_points (int): تعداد نقاط برای نمایش سحابی
        """
        self.universe_radius = universe_radius
        self.hii_radius = hii_radius
        self.n_stars = n_stars
        self.n_dust = n_dust
        self.n_nebula_points = n_nebula_points
        
        # ایجاد پلاتر PyVista
        self.plotter = pv.Plotter(window_size=[1200, 900], lighting='light_kit')
        self.plotter.background_color = 'black'
        
        # تنظیم دوربین
        self.plotter.camera.position = (0, -2.5 * self.hii_radius, 0)
        self.plotter.camera.focal_point = (0, 0, 0)
        self.plotter.camera.up = (0, 0, 1)
        self.plotter.camera.view_angle = 60
        
        # ایجاد اجزای صحنه
        self._create_stars()
        self._create_central_star()
        self._create_hii_region()
        self._create_dust()
        self._create_nebula()
        
        # اضافه کردن نور به صحنه
        self._add_lights()
        
        # تنظیم راهنما
        self._add_instructions()
    
    def _create_stars(self):
        """
        ایجاد ستارگان پس‌زمینه
        """
        # ایجاد موقعیت‌های تصادفی برای ستارگان
        np.random.seed(42)  # برای تکرارپذیری
        
        # موقعیت‌های تصادفی در فضای کروی
        theta = np.random.uniform(0, 2*np.pi, self.n_stars)
        phi = np.random.uniform(0, np.pi, self.n_stars)
        r = np.random.uniform(self.hii_radius*1.5, self.universe_radius, self.n_stars)
        
        # تبدیل به مختصات کارتزین
        x = r * np.sin(phi) * np.cos(theta)
        y = r * np.sin(phi) * np.sin(theta)
        z = r * np.cos(phi)
        
        # ایجاد نقاط برای ستارگان
        star_points = np.column_stack((x, y, z))
        background_stars = pv.PolyData(star_points)
        
        # اندازه‌های متفاوت برای ستارگان
        sizes = np.random.uniform(0.5, 3.0, self.n_stars)
        
        # رنگ‌های متفاوت برای ستارگان
        # ایجاد طیف رنگی از آبی تا سفید تا قرمز (برای نمایش دمای ستارگان)
        colors = np.zeros((self.n_stars, 3))
        
        # ستارگان آبی (داغ)
        blue_stars = np.random.choice(self.n_stars, size=int(self.n_stars*0.3), replace=False)
        colors[blue_stars] = np.array([0.6, 0.8, 1.0])  # آبی روشن
        
        # ستارگان سفید (متوسط)
        white_stars = np.random.choice(list(set(range(self.n_stars)) - set(blue_stars)), 
                                      size=int(self.n_stars*0.4), replace=False)
        colors[white_stars] = np.array([1.0, 1.0, 1.0])  # سفید
        
        # ستارگان قرمز (سرد)
        remaining_stars = list(set(range(self.n_stars)) - set(blue_stars) - set(white_stars))
        colors[remaining_stars] = np.array([1.0, 0.6, 0.4])  # قرمز-نارنجی
        
        # اضافه کردن رنگ‌ها به داده‌های ستارگان
        background_stars['colors'] = colors
        
        # اضافه کردن ستارگان به صحنه با جلوه درخشندگی
        self.plotter.add_points(background_stars, scalars='colors', rgb=True, 
                               render_points_as_spheres=True, point_size=sizes*2)
    
    def _create_central_star(self):
        """
        ایجاد ستاره مرکزی با جلوه‌های ویژه
        """
        # ستاره اصلی
        central_star = pv.Sphere(radius=self.hii_radius/20, center=(0, 0, 0))
        self.plotter.add_mesh(central_star, color="white", ambient=0.8, specular=1.0, 
                             specular_power=15, smooth_shading=True)
        
        # جلوه نورانی اطراف ستاره (هاله)
        glow = pv.Sphere(radius=self.hii_radius/15, center=(0, 0, 0))
        self.plotter.add_mesh(glow, color="yellow", opacity=0.3, ambient=0.9, 
                             emissive=True, smooth_shading=True)
        
        # اشعه‌های نور از ستاره
        self._add_star_rays()
    
    def _add_star_rays(self):
        """
        اضافه کردن اشعه‌های نور از ستاره مرکزی
        """
        # تعداد اشعه‌ها
        n_rays = 12
        
        # طول اشعه‌ها
        ray_length = self.hii_radius / 5
        
        # ایجاد اشعه‌ها در جهت‌های مختلف
        for i in range(n_rays):
            # زاویه در صفحه XY
            angle = i * (2 * np.pi / n_rays)
            
            # جهت اشعه
            direction = np.array([np.cos(angle), np.sin(angle), 0])
            
            # نقطه شروع (کمی بیرون از ستاره)
            start_point = direction * (self.hii_radius/20 * 1.1)
            
            # نقطه پایان
            end_point = direction * ray_length
            
            # ایجاد خط برای اشعه
            ray_line = pv.Line(start_point, end_point)
            
            # اضافه کردن اشعه به صحنه
            self.plotter.add_mesh(ray_line, color="yellow", opacity=0.5, line_width=3)
    
    def _create_hii_region(self):
        """
        ایجاد ناحیه H II با جلوه‌های واقعی‌تر
        """
        # ایجاد یک کره برای نمایش مرز تقریبی ناحیه H II
        hii_boundary = pv.Sphere(radius=self.hii_radius, center=(0, 0, 0))
        
        # اضافه کردن بافت ابری به سطح کره
        texture = self._create_cloud_texture(512, 512)
        
        # اضافه کردن ناحیه H II به صحنه
        self.plotter.add_mesh(hii_boundary, opacity=0.3, color="cyan", 
                             smooth_shading=True, specular=0.5, ambient=0.5,
                             texture=texture)
        
        # اضافه کردن ساختارهای داخلی ناحیه H II
        self._add_internal_structures()
    
    def _create_cloud_texture(self, width, height):
        """
        ایجاد بافت ابری برای ناحیه H II
        
        پارامترها:
            width (int): عرض تصویر بافت
            height (int): ارتفاع تصویر بافت
            
        برگشت:
            pv.Texture: بافت ایجاد شده
        """
        # ایجاد یک تصویر خالی
        img = np.zeros((height, width, 4), dtype=np.uint8)
        
        # ایجاد نویز پرلین برای بافت ابری
        scale = 10.0
        octaves = 6
        persistence = 0.5
        lacunarity = 2.0
        
        # ایجاد نویز برای هر پیکسل
        for y in range(height):
            for x in range(width):
                # مقدار نویز در این پیکسل
                noise_val = 0
                amplitude = 1.0
                frequency = 1.0
                
                for i in range(octaves):
                    nx = x / width * scale * frequency
                    ny = y / height * scale * frequency
                    
                    # استفاده از نویز ساده به جای نویز پرلین
                    noise_val += amplitude * (0.5 + 0.5 * np.sin(nx) * np.cos(ny))
                    
                    amplitude *= persistence
                    frequency *= lacunarity
                
                # نرمال‌سازی مقدار نویز
                noise_val = max(0, min(1, noise_val))
                
                # تنظیم رنگ و شفافیت بر اساس مقدار نویز
                color_val = int(255 * noise_val)
                alpha_val = int(200 * noise_val)
                
                # تنظیم رنگ آبی-سبز برای ناحیه H II
                img[y, x, 0] = int(color_val * 0.2)  # R
                img[y, x, 1] = int(color_val * 0.8)  # G
                img[y, x, 2] = int(color_val * 1.0)  # B
                img[y, x, 3] = alpha_val  # A
        
        # ایجاد بافت از تصویر
        texture = pv.Texture(img)
        
        return texture
    
    def _add_internal_structures(self):
        """
        اضافه کردن ساختارهای داخلی به ناحیه H II
        """
        # تعداد ساختارهای داخلی
        n_structures = 5
        
        # ایجاد ساختارهای ابری داخلی
        for i in range(n_structures):
            # موقعیت تصادفی درون ناحیه H II
            r = np.random.uniform(0, self.hii_radius * 0.8)
            theta = np.random.uniform(0, 2*np.pi)
            phi = np.random.uniform(0, np.pi)
            
            x = r * np.sin(phi) * np.cos(theta)
            y = r * np.sin(phi) * np.sin(theta)
            z = r * np.cos(phi)
            
            # اندازه تصادفی
            size = np.random.uniform(self.hii_radius/10, self.hii_radius/5)
            
            # ایجاد یک ساختار ابری (استفاده از بیضی‌گون)
            structure = pv.Ellipsoid(x_radius=size, y_radius=size*1.5, z_radius=size,
                                    center=(x, y, z))
            
            # چرخش تصادفی
            rotation = R.random()
            structure.rotate_y(rotation.as_euler('xyz', degrees=True)[1])
            structure.rotate_z(rotation.as_euler('xyz', degrees=True)[2])
            
            # اضافه کردن ساختار به صحنه
            opacity = np.random.uniform(0.1, 0.3)
            color = np.random.choice(['cyan', 'lightblue', 'turquoise'])
            
            self.plotter.add_mesh(structure, opacity=opacity, color=color, 
                                 smooth_shading=True, ambient=0.7)
    
    def _create_dust(self):
        """
        ایجاد ذرات غبار در اطراف ناحیه H II
        """
        # ایجاد موقعیت‌های تصادفی برای ذرات غبار
        np.random.seed(123)  # برای تکرارپذیری
        
        # موقعیت‌های تصادفی در فضای کروی
        theta = np.random.uniform(0, 2*np.pi, self.n_dust)
        phi = np.random.uniform(0, np.pi, self.n_dust)
        r = np.random.uniform(self.hii_radius*0.9, self.hii_radius*1.3, self.n_dust)
        
        # تبدیل به مختصات کارتزین
        x = r * np.sin(phi) * np.cos(theta)
        y = r * np.sin(phi) * np.sin(theta)
        z = r * np.cos(phi)
        
        # ایجاد نقاط برای ذرات غبار
        dust_points = np.column_stack((x, y, z))
        dust_cloud = pv.PolyData(dust_points)
        
        # اندازه‌های متفاوت برای ذرات غبار
        sizes = np.random.uniform(0.5, 2.0, self.n_dust)
        
        # اضافه کردن ذرات غبار به صحنه
        self.plotter.add_points(dust_cloud, scalars=sizes, render_points_as_spheres=True, 
                               point_size=sizes, color='gray', opacity=0.6)
    
    def _create_nebula(self):
        """
        ایجاد سحابی در اطراف ناحیه H II
        """
        # ایجاد نقاط تصادفی برای سحابی
        np.random.seed(456)  # برای تکرارپذیری
        
        # ایجاد نقاط در یک حلقه اطراف ناحیه H II
        theta = np.random.uniform(0, 2*np.pi, self.n_nebula_points)
        phi = np.random.uniform(0, np.pi, self.n_nebula_points)
        
        # توزیع شعاعی با تمرکز بیشتر در لبه‌های ناحیه H II
        r_base = np.random.beta(2, 2, self.n_nebula_points)  # توزیع بتا برای تمرکز در میانه
        r = self.hii_radius * (0.8 + 0.6 * r_base)  # مقیاس‌بندی به محدوده مورد نظر
        
        # تبدیل به مختصات کارتزین
        x = r * np.sin(phi) * np.cos(theta)
        y = r * np.sin(phi) * np.sin(theta)
        z = r * np.cos(phi)
        
        # اضافه کردن اغتشاش به موقعیت‌ها برای ایجاد ظاهر ابری
        noise_scale = self.hii_radius * 0.1
        x += np.random.normal(0, noise_scale, self.n_nebula_points)
        y += np.random.normal(0, noise_scale, self.n_nebula_points)
        z += np.random.normal(0, noise_scale, self.n_nebula_points)
        
        # ایجاد نقاط برای سحابی
        nebula_points = np.column_stack((x, y, z))
        nebula_cloud = pv.PolyData(nebula_points)
        
        # رنگ‌های متفاوت برای نقاط سحابی
        colors = np.zeros((self.n_nebula_points, 3))
        
        # ناحیه آبی-سبز (یونیزه)
        blue_region = np.random.choice(self.n_nebula_points, size=int(self.n_nebula_points*0.6), replace=False)
        colors[blue_region] = np.array([0.2, 0.8, 1.0])  # آبی-فیروزه‌ای
        
        # ناحیه قرمز (حرارتی)
        remaining = list(set(range(self.n_nebula_points)) - set(blue_region))
        colors[remaining] = np.array([1.0, 0.4, 0.2])  # قرمز-نارنجی
        
        # اضافه کردن رنگ‌ها به داده‌های سحابی
        nebula_cloud['colors'] = colors
        
        # اندازه‌های متفاوت برای نقاط سحابی
        sizes = np.random.uniform(0.5, 2.0, self.n_nebula_points)
        
        # اضافه کردن سحابی به صحنه
        self.plotter.add_points(nebula_cloud, scalars='colors', rgb=True, 
                               render_points_as_spheres=True, point_size=sizes, opacity=0.3)
    
    def _add_lights(self):
        """
        اضافه کردن نورها به صحنه
        """
        # نور اصلی از ستاره مرکزی
        self.plotter.add_light(pv.Light(position=(0, 0, 0), focal_point=(1, 0, 0), 
                                       color='white', intensity=0.8))
        
        # نورهای محیطی برای روشن کردن کل صحنه
        self.plotter.add_light(pv.Light(position=(0, 0, self.universe_radius), 
                                       focal_point=(0, 0, 0), color='blue', 
                                       intensity=0.2, cone_angle=90))
        
        self.plotter.add_light(pv.Light(position=(0, -self.universe_radius, 0), 
                                       focal_point=(0, 0, 0), color='purple', 
                                       intensity=0.2, cone_angle=90))
    
    def _add_instructions(self):
        """
        اضافه کردن راهنمای کاربری به صحنه
        """
        instructions = (
            "راهنمای کاربری:\n"
            "- چرخش: کلیک چپ و حرکت موس\n"
            "- بزرگنمایی: اسکرول موس\n"
            "- جابجایی: کلیک راست و حرکت موس\n"
            "- خروج: کلید ESC"
        )
        
        self.plotter.add_text(instructions, position='upper_left', font_size=12, color='white')
    
    def animate(self, n_frames=200, orbit=True, save_path=None):
        """
        ایجاد انیمیشن با چرخش دوربین به دور صحنه
        
        پارامترها:
            n_frames (int): تعداد فریم‌های انیمیشن
            orbit (bool): آیا دوربین به دور صحنه بچرخد
            save_path (str): مسیر ذخیره انیمیشن (اگر None باشد، ذخیره نمی‌شود)
        """
        # تنظیم عنوان
        self.plotter.add_title("تجسم‌سازی سه‌بعدی ناحیه H II", font_size=16)
        
        # اگر مسیر ذخیره مشخص شده باشد، تنظیمات ذخیره را انجام می‌دهیم
        if save_path:
            self.plotter.open_gif(save_path)
        
        # شروع انیمیشن
        self.plotter.show(auto_close=False, interactive_update=True)
        
        # زاویه شروع
        start_angle = 0
        
        # حلقه انیمیشن
        for i in range(n_frames):
            # چرخش دوربین به دور صحنه
            if orbit:
                angle = start_angle + i * (360 / n_frames)
                rad = np.radians(angle)
                x = 2.5 * self.hii_radius * np.sin(rad)
                y = 2.5 * self.hii_radius * np.cos(rad)
                z = 0.5 * self.hii_radius * np.sin(rad * 0.5)
                
                self.plotter.camera.position = (x, y, z)
                self.plotter.camera.focal_point = (0, 0, 0)
                self.plotter.camera.up = (0, 0, 1)
            
            # به‌روزرسانی صحنه
            self.plotter.update()
            
            # ذخیره فریم اگر مسیر ذخیره مشخص شده باشد
            if save_path:
                self.plotter.write_frame()
            
            # مکث کوتاه
            time.sleep(0.01)
        
        # بستن پنجره نمایش
        if save_path:
            self.plotter.close()
    
    def show(self):
        """
        نمایش صحنه به صورت تعاملی
        """
        # تنظیم عنوان
        self.plotter.add_title("تجسم‌سازی سه‌بعدی ناحیه H II", font_size=16)
        
        # نمایش صحنه
        self.plotter.show()


def main():
    """
    تابع اصلی برنامه
    """
    print("تجسم‌سازی سه‌بعدی فضای ستاره‌ای و ناحیه H II")
    print("=" * 50)
    
    # ایجاد یک نمونه از کلاس StellarSpaceVisualization
    print("در حال ایجاد تجسم‌سازی سه‌بعدی...")
    
    # نمایش منو
    print("\nگزینه‌های نمایش:")
    print("1. نمایش تعاملی")
    print("2. نمایش انیمیشن")
    print("3. ذخیره انیمیشن")
    print("0. خروج")
    
    while True:
        try:
            choice = int(input("\nلطفاً یک گزینه را انتخاب کنید: "))
            
            if choice == 0:
                print("خروج از برنامه...")
                break
            
            elif choice == 1:
                print("در حال بارگذاری نمایش تعاملی...")
                visualization = StellarSpaceVisualization(
                    universe_radius=100.0,
                    hii_radius=20.0,
                    n_stars=3000,
                    n_dust=1500,
                    n_nebula_points=30000
                )
                visualization.show()
            
            elif choice == 2:
                print("در حال بارگذاری انیمیشن...")
                visualization = StellarSpaceVisualization(
                    universe_radius=100.0,
                    hii_radius=20.0,
                    n_stars=3000,
                    n_dust=1500,
                    n_nebula_points=30000
                )
                visualization.animate(n_frames=200)
            
            elif choice == 3:
                print("در حال ایجاد و ذخیره انیمیشن...")
                save_path = input("مسیر ذخیره فایل GIF را وارد کنید (پیش‌فرض: hii_region_animation.gif): ")
                if not save_path:
                    save_path = "hii_region_animation.gif"
                
                visualization = StellarSpaceVisualization(
                    universe_radius=100.0,
                    hii_radius=20.0,
                    n_stars=1500,  # تعداد کمتر برای سرعت بیشتر در ذخیره
                    n_dust=800,
                    n_nebula_points=15000
                )
                visualization.animate(n_frames=100, save_path=save_path)
                print(f"انیمیشن در مسیر {save_path} ذخیره شد.")
            
            else:
                print("گزینه نامعتبر! لطفاً یک گزینه معتبر وارد کنید.")
        
        except ValueError:
            print("ورودی نامعتبر! لطفاً یک عدد وارد کنید.")
        
        except Exception as e:
            print(f"خطا: {e}")


if __name__ == "__main__":
    main()
