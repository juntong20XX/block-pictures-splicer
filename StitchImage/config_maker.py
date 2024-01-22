# -*- coding: utf-8 -*-
"""
Created on Mon Feb 14 13:22:31 2022

@author: Jessi
"""

import os
import json
import fnmatch

from PIL import Image

MY_DIRPATH = os.path.dirname(__file__)
MY_CONFIG_PATH = os.path.join(MY_DIRPATH, "stitch_image config.json")
DEFINE_DEFINE_CONFIG_NAME = "stitch_image-config.json"


def self_config(update=None):
    """Get the module config. If given update, update config and return changed
    config. Suggest configs:
    - define config: # the define config name
        (str) "stitch_image-config.json" (define)
    - special config: # save the special 
        (dict) {path: [name_1, ...]} (define)
    """
    if update:
        with open(MY_CONFIG_PATH, "w", encoding="utf-8") as fp:
            json.dump(update, fp)
    else:
        with open(MY_CONFIG_PATH, encoding="utf-8") as fp:
            cfg = json.load(fp)
        return cfg


def config_give_and_save(func):
    def f(*args, **kwargs):
        cfg = self_config()
        cfg = func(cfg, *args, **kwargs)
        if cfg:
            self_config(cfg)

    return f


@config_give_and_save
def set_define_config_name(cfg, new_name):
    cfg["define config"] = new_name
    return cfg


@config_give_and_save
def init_work_config(cfg, dir_path, name=None):
    dir_path = os.path.realpath(dir_path)
    if not name:
        name = cfg["define config"]
    if name != DEFINE_DEFINE_CONFIG_NAME:
        cfg["special config"].setdefault(dir_path, []).append(name)
    file_path = os.path.join(dir_path, name)
    print(f"create {file_path} ...")
    with open(file_path, "w", encoding="utf-8") as fp:
        fp.write("{}")
    return cfg


def get_work_config_name(dir_path) -> list:
    """获取`dir_path`目录下的工作配置文件名列表，若未找到文件，则释放 ValueError
返回列表中仅有文件名，不带路径"""
    cfg = self_config()
    dir_path = os.path.realpath(dir_path)
    _, _, files = next(os.walk(dir_path))
    config_names = {DEFINE_DEFINE_CONFIG_NAME}
    config_names.update(cfg["special config"].get(dir_path, ()))
    config_names.intersection_update(set(files))

    if not config_names:
        raise ValueError("Not working config found.")
    return list(config_names)


@config_give_and_save
def remove_work_config(cfg, dir_path, name=None):
    dir_path = os.path.realpath(dir_path)
    _, _, files = next(os.walk(dir_path))
    get_special = cfg["special config"].get(dir_path, ())
    config_names = {DEFINE_DEFINE_CONFIG_NAME}
    config_names.update(get_special)
    config_names.intersection_update(set(files))

    if not config_names:
        raise ValueError("Not working config found.")

    if len(config_names) > 1:
        if name is None:
            raise ValueError("find more than one working configs, "
                             "give argument `name` as file name for remove",
                             config_names)
        else:
            remove_files = fnmatch.filter(config_names, name)
    else:
        remove_files = config_names

    for name in remove_files:
        print(f"remove {os.path.realpath(name)} ...")
        os.remove(name)
        if name in get_special:
            get_special.remove(name)
    if not get_special and isinstance(get_special, list):
        cfg["special config"].pop(dir_path)

    return cfg


def get_work_config(dir_path, name=None):
    """返回dir_path目录中的配置文件,name 属性用于指定配置文件名。
    当未找到name对应的配置或有不止一个配置需要指定name时释放ValueError"""
    config_names = get_work_config_name(dir_path)

    name = match_name(config_names, name)
    with open(os.path.join(dir_path, name), "r", encoding="utf-8") as fp:
        work_config = json.load(fp)
    return work_config


def match_name(names, name):
    if name is not None:
        f = fnmatch.filter(names, name)
        if name in names:
            return name
        elif not f:
            f = [i for i in names if i.startswith(name)]
        if len(f) > 1:
            raise ValueError("searched many answers,", f)
        elif not f:
            raise ValueError("no config matched, configs are", names)
        name = f[0]

    elif len(names) > 1:
        raise ValueError("find more than one working configs, "
                         "give argument `name` as file name", names)
    else:
        name = names[0]
    return name


def write_work_config(new, dir_path, name=None):
    """将新的内容写入工作配置"""
    config_names = get_work_config_name(dir_path)

    name = match_name(config_names, name)
    with open(os.path.join(dir_path, name), "w", encoding="utf-8") as fp:
        json.dump(new, fp, indent=2)


def add_image_to_work_config(dir_path, file_pats, work_config_name=None):
    work_config = get_work_config(dir_path, work_config_name)
    _, _, files = next(os.walk(dir_path))

    names = []
    for pat in file_pats:
        names.extend(fnmatch.filter(files, pat))

    for name in names:
        name = os.path.relpath(name, dir_path)
        with Image.open(name) as im:
            work_config[name] = {"file size": im.size}
        print(f"Add {name} ...")

    write_work_config(work_config, dir_path)


def pop_image_from_work_config(dir_path, file_pats, work_config_name=None):
    work_config = get_work_config(dir_path, work_config_name)

    names = tuple(work_config)
    remove = []
    for pat in file_pats:
        remove.extend(fnmatch.filter(names, pat))
    for name in remove:
        print(f"Pop {name} ...")
        work_config.pop(name)

    write_work_config(work_config, dir_path, work_config_name)


def add_cut_image(config_path, new_image_path, old_image_path, size=None):
    """将剪切过的图片填入工作配置。cut_gui.PhotoCutter将调用此方法。"""
    with open(config_path, encoding="utf-8") as fp:
        cfg = json.load(fp)
    dir_path = os.path.dirname(config_path)
    new_name = os.path.relpath(new_image_path, dir_path)
    old_name = os.path.relpath(old_image_path, dir_path)
    if size is None:
        with Image.open(new_image_path) as im:
            size = im.size
    cfg[old_name].setdefault("{}x{}".format(*size), []).append(new_name)
    with open(config_path, "w", encoding="utf-8") as fp:
        json.dump(cfg, fp, indent=2)
