# 我是文档

这个是我在 gitee 上的老项目([链接](https://gitee.com/juntong2021/stitch-image)), 密钥丢失, 之后在 github 上更新.

## 介绍
`stitch-image`是一个用于将多个图片拼接为一个图片的项目。虽然命令行操作未完成，但相关api已完成。

## 命令行用法
使用`python -m StitchImage`（python模块名称还没想好）调用本项目。

用`init`指令初始化一个编辑项目（是的没错它是项目模式的工作的…… emmm 我可能之后添加一键指令，或许像 ffmpeg 那样）。此命令会在当前路径下创建配置文件，可以填入可选值编辑改变配置名。

在创建项目后，在配置路径下执行`add XX`指令添加想编辑的图片（好吧我承认我可能最近git用多了）。多个文件用空格隔开，支持正则表达式。如果当前目录有多个配置文件，请通过`add[文件名]`指定配置文件。同理，将"add"替换为`pop`执行移出命令。

添加图片后，执行`cut {SIZE}`将启动UI切割图片，SIZE指想要的大小，有比例和像素两种写法，比例为“长:宽”，像素“长x宽”。比例写法会设置像素为将图片得出满足所有图片最大的。如果当前目录有多个配置文件，请通过`cut[文件名]`指定配置文件。

最后，使用`stitch`指令拼接图片，此指令支持中括号配置文件选择。`stitch sizes` 查看已切分的尺寸，`stitch size {尺寸}`查看详细信息，`stitch size {尺寸} {目标图片横行图片数},{目标图片纵行图片数} {保存文件名}`创建拼接图片（文件名参数可选）。
