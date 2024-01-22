"""
实现命令行指令阅读功能
"""

import re
import sys

try:
    from . import config_maker, cut_gui, stitch
except ImportError:
    import cut_gui
    import config_maker
    import stitch


def print_help():
    """显示帮助文档，并退出程序"""
    print("StitchImage can stitch images into one image.")
    print("Use `size {SIZE YOU CHOOSE} {NUMBERS OF PHOTOS IN X AXLE},{NUMBERS OF PHOTOS IN Y AXLE}` to stitch the "
          "new photo.")
    print("")
    sys.exit()


def read_cut_command(cmd, cmds):
    """读取并执行剪裁指令"""
    name = re.match(r"cut(?:\[(.*)])?", cmd).group(1)
    names = config_maker.get_work_config_name(".")
    name = config_maker.match_name(names, name)
    config = config_maker.get_work_config(".", name)
    x, how, y = re.match(r"([0-9]+)([xX:])([0-9]+)", cmds[0]).groups()
    x = int(x)
    y = int(y)
    if how == ":":
        base = cut_gui.get_best_size(x, y, config)
        x *= base
        y *= base
    cut_gui.PhotoCutter(x, y, name).mainloop()


commands = sys.argv[1:]

if not commands:
    print_help()

first_cmd = commands.pop(0)


def read_stitch_cmd(cmd, cmds):
    """读取并执行拼接指令"""
    # load config
    cfg_file_name = re.match(r"stitch(?:\[(.*)])?", cmd).group(1)
    all_cfg_file_names = config_maker.get_work_config_name(".")
    cfg_file_name = config_maker.match_name(all_cfg_file_names, cfg_file_name)
    config: dict = config_maker.get_work_config(".", cfg_file_name)

    # update data
    all_sizes: dict[tuple[int, int], dict[str, list[str]]] = {}
    file_name: str
    info: dict
    for file_name, info in config.items():
        for i, file_names_of_this_size in info.items():
            match_return = re.match(r"(\d+)x(\d+)", i)
            if match_return is not None:
                size = (int(match_return.group(1)), int(match_return.group(2)))  # (Int, Int)
                all_sizes.setdefault(size, {}).setdefault(file_name, []).extend(file_names_of_this_size)

    if len(cmds) == 0 or cmds[0] == "sizes":
        # 缺少参数 或 sizes 指令 显示可用的尺寸
        print("Available sizes:")
        for i in sorted(all_sizes):
            print("  - {}x{} :".format(*i), "with %d files." % len(all_sizes[i]))
        print()
    elif cmds[0] == "size":
        # "size DDxDD"
        match_return = re.match(r"(\d+)[xX](\d+)", cmds[1])
        size = (int(match_return.group(1)), int(match_return.group(2)))
        if len(cmds) == 2:
            # 显示该尺寸的信信息
            print("Files with size", cmds[1])
            for i, (file_name, files) in enumerate(all_sizes[size].items(), 1):
                print("  %2d. " % i, file_name, ":", len(files), "available files")
        else:
            # 拼接
            match_return = re.match(r"(\d+),(\d+)", cmds[2])
            rectangular_shape = (int(match_return.group(1)), int(match_return.group(2)))
            photos = []

            for files in all_sizes[size].values():
                if len(files) == 1:
                    photos.append(files[0])
                else:
                    print("Choose file from:")
                    for i, n in enumerate(files):
                        print("[%d]" % i, n)
                    i = input("Entre the number:")
                    photos.append(files[int(i)])

            img = stitch.stitch_images(photos, rectangular_shape)
            try:
                file_name = cmds[3]
            except IndexError:
                file_name = "stitch %s to %s.jpg" % (cmds[1], cmds[2])
            print("end of stitch, save photo to", file_name)
            img.save(file_name)
    else:
        print("Unknown command", cmds[0])
        print("Try command `sizes` and `size`")
        print("Use `size {SIZE YOU CHOOSE} {NUMBERS OF PHOTOS IN X AXLE},{NUMBERS OF PHOTOS IN Y AXLE}` to stitch the "
              "new photo.")


if first_cmd.startswith("-"):
    if first_cmd == "--help" or first_cmd == "-h":
        # 执行帮助
        print_help()
elif first_cmd == "init":
    # 创建配置文件
    config_file_name = commands[0] if commands else None
    config_maker.init_work_config("", config_file_name)
elif m := re.match(r"add(?:\[(.*)])?", first_cmd):
    config_maker.add_image_to_work_config(".", commands, m.group(1))
elif m := re.match(r"pop(?:\[(.*)])?", first_cmd):
    config_maker.pop_image_from_work_config(".", commands, m.group(1))
elif first_cmd.startswith("cut"):
    read_cut_command(first_cmd, commands)
elif first_cmd.startswith("stitch"):
    read_stitch_cmd(first_cmd, commands)
else:
    print_help()
