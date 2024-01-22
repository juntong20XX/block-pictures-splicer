# -*- coding: utf-8 -*-
"""
Created on Sun Feb 13 18:02:08 2022

@author: juntong

config: {"{image name}": {"file size": ({x}, {y}),
                         ({new_size_x}, {new_size_y}): ["new image path"],
                        }
        }
"""

from PIL import Image, ImageTk

import json
import time
import datetime
import tkinter as tk

try:
    from . import config_maker
except ImportError:
    import config_maker


def get_best_size(x, y, config):
    """根据所给比例(x: y)判断 config 中图片最合适的像素点数量。"""
    # 懒得动脑子，二分法穷举吧
    it = tuple(i['file size'] for i in config.values())
    hi = min(min(size) for size in it)
    lo = 1
    while hi - lo > 2:
        m = (hi + lo) // 2
        ls = [(px - m * x, py - m * y) for px, py in it]
        if any(x < 0 or y < 0 for x, y in ls):  # m is too big
            hi = m
        elif any(x == 0 or y == 0 for x, y in ls):
            return m
        else:  # m maybe too small
            lo = m
    else:
        return lo


def get_proportion(size):
    m = max(size)
    n = min(size)
    r = m % n
    while r != 0:
        m = n
        n = r
        r = m % n
    return size[0] // n, size[1] // n


class PhotoCutter(tk.Tk):
    canvas_width = 908
    canvas_hight = 908
    photo_max_length = 900

    def __init__(self, photo_want_width, photo_want_height,
                 photos_config_path, photo_filter=lambda ls: True):
        """photo_filter : callable object
                        传入参数为list，对应 config值的"file size"项，
                        若返回 True, 则将该图片加入编辑
                        默认全部返回True
        """
        super().__init__()
        self.photo_want_width: int = photo_want_width
        self.photo_want_height: int = photo_want_height
        self.photos_config_path = photos_config_path
        with open(photos_config_path, encoding="utf-8") as fp:
            cfg = json.load(fp)
        self.setupUI()

        self.photos_iter = (path for path, value in cfg.items()
                            if photo_filter(value['file size']))
        self.show_photo(next(self.photos_iter))

        self.quick_veiw_iter = self._update_quick_view_gen()

    def _update_photo(self, scale_back=True):
        self.photo_widget = ImageTk.PhotoImage(self.photo_image,
                                               master=self.canvas)
        self.photo_id = self.canvas.create_image(0, 0, anchor="nw",
                                                 image=self.photo_widget)
        x = self.photo_image.size[0]
        y = self.photo_image.size[1]
        if scale_back:
            self.x_scale.set(self.photo_want_width)
            self.y_scale.set(self.photo_want_height)
        else:
            self.x_scale.set(int(self.x_scale.get() / self.x_scale["to"] * x))
            self.y_scale.set(int(self.y_scale.get() / self.y_scale["to"] * y))
        self.x_scale.config(length=x, to=x)
        self.y_scale.config(length=y, to=y)

        self.canvas.delete(self.line_x_small)
        self.canvas.delete(self.line_x_large)
        self.canvas.delete(self.line_y_small)
        self.canvas.delete(self.line_y_large)
        x_number = self.x_scale.get()
        y_number = self.y_scale.get()
        x = x_number - self.photo_want_width
        self.line_x_small = self.canvas.create_line(
            x, 0, x, self.canvas_hight, width=4, fill="gray")
        self.line_x_large = self.canvas.create_line(
            x_number, 0, x_number, self.canvas_hight, width=4, fill="gray")
        y = y_number - self.photo_want_height
        self.line_y_small = self.canvas.create_line(
            0, y, self.canvas_width, y, width=4, fill="gray")
        self.line_y_large = self.canvas.create_line(
            0, y_number, self.canvas_width, y_number, width=4, fill="gray")

    def show_photo(self, path):
        # “戴帽子”
        self._is_updating_photo = True

        self.photo_path = path
        self.photo_image = self.resize_photo(Image.open(path))
        self.photo_first = self.photo_image
        self._update_photo()
        # 设置缩放
        dx = self.photo_want_width / self.photo_first.size[0]
        dy = self.photo_want_height / self.photo_first.size[1]
        self.zoom_scale.set(100)
        self.zoom_scale.config(to=int(max(dx, dy) * 100))
        # “摘帽子”
        self._is_updating_photo = False

    def zoom_scale_changed(self, number):
        if not self._is_updating_photo:
            self.zoom_photo(float(number) / 100)
        next(self.quick_veiw_iter)

    def zoom_photo(self, x):
        """缩放 self.photo_image 并刷新ui"""
        self._is_updating_photo = True
        size = (int(self.photo_first.size[0] * x),
                int(self.photo_first.size[1] * x))
        self.photo_image = self.photo_first.resize(size)
        self.canvas.delete(self.photo_id)
        self._update_photo(False)

        self._is_updating_photo = False

    def setupUI(self):
        self.x_scale = tk.Scale(self, bg="white", fg="black",
                                sliderlength=10, width=6,
                                orient="horizontal",
                                command=self.x_scale_changed)
        self.y_scale = tk.Scale(self, bg="white", fg="black",
                                sliderlength=10, width=6,
                                orient="vertical",
                                command=self.y_scale_changed)

        self.canvas = tk.Canvas(self, width=903, height=903)
        line_x_small_end = (0, self.canvas_hight)
        line_x_large_sta = (self.photo_want_width, 0)
        line_x_large_end = (self.photo_want_width, self.canvas_hight)
        line_y_small_end = (self.canvas_width, 0)
        line_y_large_sta = (0, self.photo_want_height)
        line_y_large_end = (self.canvas_width, self.photo_want_height)
        self.line_x_small = self.canvas.create_line(0, 0,
                                                    *line_x_small_end,
                                                    width=4, fill="gray")
        self.line_x_large = self.canvas.create_line(*line_x_large_sta,
                                                    *line_x_large_end,
                                                    width=4, fill="gray")
        self.line_y_small = self.canvas.create_line(0, 0,
                                                    *line_y_small_end,
                                                    width=4, fill="gray")
        self.line_y_large = self.canvas.create_line(*line_y_large_sta,
                                                    *line_y_large_end,
                                                    width=4, fill="gray")

        self.quick_veiw_canvas = tk.Canvas(self,
                                           width=self.photo_want_width + 3,
                                           height=self.photo_want_height + 3)

        self.control_frame = self.control_frame_maker()

        self.x_scale.grid(sticky="nw", column=1, row=0)
        self.y_scale.grid(sticky="nw", column=0, row=1)
        self.canvas.grid(column=1, row=1)
        self.quick_veiw_canvas.grid(sticky="n",
                                    column=2, row=1, rowspan=2)
        self.control_frame.grid(sticky="ns",
                                column=3, row=1, rowspan=2)

        self.set_shortcut_keys()

    def control_frame_maker(self):
        frame = tk.Frame(self)
        self.info_box = tk.Label(frame, relief="ridge",
                                 width=20, height=2)
        select_left_button = tk.Button(frame, text="⇦", font=("", 15),
                                       repeatdelay=150, repeatinterval=20,
                                       command=self.select_left_command)
        select_right_button = tk.Button(frame, text="⇨", font=("", 15),
                                        repeatdelay=150,
                                        repeatinterval=20,
                                        command=self.select_right_command)
        select_up_button = tk.Button(frame, text="⇧", font=("", 15),
                                     repeatdelay=150, repeatinterval=20,
                                     command=self.select_up_command)
        select_down_button = tk.Button(frame, text="⇩", font=("", 15),
                                       repeatdelay=150, repeatinterval=20,
                                       command=self.select_down_command)
        self._horizontal_axis_call_time = self._vertical_axis_call_time = 0
        self.zoom_scale = tk.Scale(frame, bg="white", fg="black",
                                   from_=100, length=100,
                                   tickinterval=25, showvalue=False,
                                   orient="vertical",
                                   command=self.zoom_scale_changed)
        photo_pass_button = tk.Button(frame, bg="lightgray", text="PASS",
                                      font=("", 10),
                                      command=self.photo_pass)
        next_button = tk.Button(frame, bg="red", text="NEXT",
                                font=("", 10),
                                command=self.next_photo)
        fast_next_button = tk.Button(frame, bg="lightblue",
                                     text="NEXT with ZOOM",
                                     font=("", 10),
                                     command=self.fast_next_photo)

        self.info_box.grid(column=0, row=0, columnspan=3)
        select_left_button.grid(column=0, row=1, pady=4, rowspan=2)
        select_right_button.grid(column=2, row=1, pady=4, rowspan=2)
        select_up_button.grid(column=1, row=1, padx=1)
        select_down_button.grid(column=1, row=2, padx=1)
        self.zoom_scale.grid(column=0, row=3)
        photo_pass_button.grid(column=1, row=4, sticky="w", pady=5)
        fast_next_button.grid(column=1, row=5, sticky="we")
        next_button.grid(column=2, row=5, sticky="we")

        return frame

    def set_shortcut_keys(self):
        self.bind("<KeyPress-a>", self.select_left_command)
        self.bind("<KeyPress-e>", self.select_right_command)
        self.bind("<KeyPress-o>", self.select_down_command)
        self.bind("<KeyPress-,>", self.select_up_command)
        self.bind("<MouseWheel>", self.zoom_from_mouse)
        self.bind("<KeyPress-b>", self.next_photo)

    def photo_pass(self):
        """显示下一站图片"""
        try:
            self.show_photo(next(self.photos_iter))
        except StopIteration:
            self.destroy()

    def fast_next_photo(self):
        """直接缩放图片"""
        save_name = self.get_save_name()
        need_size = (self.photo_want_width, self.photo_want_height)
        Image.open(self.photo_path).resize(need_size).save(save_name)
        self._photo_next(save_name)

    def get_cut_photo(self):
        right = self.x_scale.get()
        left = right - self.photo_want_width
        lower = self.y_scale.get()
        upper = lower - self.photo_want_height
        return self.photo_image.crop((left, upper, right, lower))

    def _photo_next(self, save_name):
        size = self.photo_want_width, self.photo_want_height
        config_maker.add_cut_image(self.photos_config_path,
                                   save_name, self.photo_path, size)
        self.photo_pass()

    def next_photo(self, key_event=None):
        save_name = self.get_save_name()
        self.get_cut_photo().save(save_name)
        self._photo_next(save_name)

    def get_save_name(self):
        """返回保存图片时使用的图片名，可覆盖"""
        base_name, ext = self.photo_path.rsplit(".", 1)
        add = format(datetime.datetime.now(), " %h%d_%H-%M-%S.")
        return base_name + add + ext

    def select_left_command(self, key_event=None):  # XXX: PID 调速
        number = self.x_scale.get()
        t = time.time()
        if self.photo_want_width < number:
            if t - self._horizontal_axis_call_time < 0.03:
                self.x_scale.set(number - 2)
            else:
                self.x_scale.set(number - 1)
        else:  # 显示警告
            pass
        self._horizontal_axis_call_time = t

    def select_right_command(self, key_event=None):
        number = self.x_scale.get()
        t = time.time()
        if number < self.x_scale["to"]:
            if t - self._horizontal_axis_call_time < 0.03:
                self.x_scale.set(number + 2)
            else:
                self.x_scale.set(number + 1)
        else:  # 显示警告
            pass
        self._horizontal_axis_call_time = t

    def select_down_command(self, key_event=None):
        number = self.y_scale.get()
        t = time.time()
        if number < self.y_scale["to"]:
            if t - self._vertical_axis_call_time < 0.03:
                self.y_scale.set(number + 2)
            else:
                self.y_scale.set(number + 1)
        else:  # 显示警告
            pass
        self._vertical_axis_call_time = t

    def select_up_command(self, key_event=None):
        number = self.y_scale.get()
        t = time.time()
        if number < self.y_scale["to"]:
            if t - self._vertical_axis_call_time < 0.03:
                self.y_scale.set(number - 2)
            else:
                self.y_scale.set(number - 1)
        else:  # 显示警告
            pass
        self._vertical_axis_call_time = t

    def x_scale_changed(self, number):
        number = int(number)
        if number < self.photo_want_width:
            self.x_scale.set(self.photo_want_width)
            # TODO: 显示警告文字
        elif not self._is_updating_photo:
            self.canvas.delete(self.line_x_small)
            self.canvas.delete(self.line_x_large)
            x = number - self.photo_want_width
            self.line_x_small = self.canvas.create_line(x, 0,
                                                        x, self.canvas_hight,
                                                        width=4,
                                                        fill="gray")
            self.line_x_large = self.canvas.create_line(number, 0,
                                                        number,
                                                        self.canvas_hight,
                                                        width=4,
                                                        fill="gray")
        next(self.quick_veiw_iter)

    def y_scale_changed(self, number):
        number = int(number)
        if number < self.photo_want_height:
            self.y_scale.set(self.photo_want_height)
            # TODO: 显示警告文字
        elif not self._is_updating_photo:
            self.canvas.delete(self.line_y_small)
            self.canvas.delete(self.line_y_large)
            y = number - self.photo_want_height
            self.line_y_small = self.canvas.create_line(0, y,
                                                        self.canvas_width, y,
                                                        width=4,
                                                        fill="gray")
            self.line_y_large = self.canvas.create_line(0, number,
                                                        self.canvas_width,
                                                        number,
                                                        width=4,
                                                        fill="gray")
        next(self.quick_veiw_iter)

    def zoom_from_mouse(self, mouse_event):
        delta = 1 if mouse_event.delta > 0 else -1
        self.zoom_scale.set(self.zoom_scale.get() + delta)

    def resize_photo(self, photo):
        """将 photo 修改为合适放映的大小
        即 尽可能等比例缩小至最大<= self.photo_max_length 的长宽"""
        mul = self.photo_max_length / max(photo.size)
        new_size = int(photo.size[0] * mul), int(photo.size[1] * mul)
        return photo.resize(new_size)

    def _update_quick_view_gen(self):
        while 1:
            widge = ImageTk.PhotoImage(self.get_cut_photo(),
                                       master=self.quick_veiw_canvas)
            photo_id = self.quick_veiw_canvas.create_image(0, 0, anchor="nw",
                                                           image=widge)
            yield
            self.quick_veiw_canvas.delete(photo_id)

# base_size = get_best_size(2, 3)  # 94
# # base_size = 94
# p = PhotoCutter(2 * base_size, 3 * base_size, "config.json")
# p.mainloop()
