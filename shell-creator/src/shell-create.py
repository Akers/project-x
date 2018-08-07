#!/usr/bin/env python3
# -*- coding:utf8 -*-
# @Date    : 2018-03-03
# @Author  : ${author} (${email})
# @Link    : ${link}
# @Version : $Id$

import os
import fire
import re
from fnmatch import fnmatch
from jinja2 import Template


class MainEntry(object):
    """启动脚本生成工具"""

    def __init__(self):
        super(MainEntry, self).__init__()
        self.generator = ShellFileGenerator()

    def springboot(self, path, template, output, shellprefix='restart_', shellsuffix='.sh', prefixpath=None, splitor='/', pattern=None, regx=None, regrouping=None):
        """生成SpringBoot启动脚本"""
        self.generator.path = path
        self.generator.templatePath = template.strip()
        self.generator.shellSuffix = shellsuffix
        self.generator.shellPrefix = shellprefix
        self.generator.output = output
        self.generator.regrouping = regrouping
        return self.generator.springboot(prefixpath, splitor, pattern, regx, regrouping)

    def allshell(self, path):
        """生成全部运行脚本"""
        return ""

    def help(self):
        """帮助文档"""
        man_str = """
            欢迎使用启动脚本生成工具
            使用方法：
            python shell-create method --path= --output= [--shellprefix] [--shellsuffix] [--prefixpath=] [--splitor=] [--pattern=] [--suffix=] --template=
                --method 运行方法： help | springboot | allshell
                          - help 帮助
                          - springboot 生成springboot的启动脚本
                          - allshell 生成all.sh
                --path 工作路径，本工具将扫描此目录下的所有文件，为扫描到的每个文件创建启动脚本
                --output 脚本生成输出目录
                --shellprefix 生成文件的后缀，默认是.sh
                --shellsuffix 生成文件的前缀，默认是restart_
                --prefixpath 可执行文件的前缀路径
                --splitor 文件路径分隔符，可选，默认转换为linux使用的"/"
                --pattern 使用通配符过滤文件名，如*.jar
                --regrouping 重新分组的文件，如jar名字中包含给定的关键字，则生成的脚本输出到regrouping目录中
                --regx 可运行文件过滤表达式，如提供此参数则只会扫描满足该正则表达式的文件
                --template 指定生成脚本时使用的模板文件，模板文件语法详见（http://jinja.pocoo.org/docs/2.10/templates/）
        """
        return man_str


class ShellFileGenerator(object):
    """ShellFileGenerator： 生成脚本的方法"""

    def __init__(self, path=None, templatePath=None):
        super(ShellFileGenerator, self).__init__()
        self.path = path
        self.templatePath = templatePath

    def springboot(self, prefixpath=None, splitor='/', pattern=None, regx=None, regrouping=None):
        filePaths = read_file_list(
            self.path, prefixpath, splitor, pattern, regx)
        datas = generate_springboot_shells(
            filePaths, self.templatePath, prefixpath,
            self.shellPrefix, self.shellSuffix, regrouping)
        generate_shell_file(datas, self.output)


def render_template(templatePath, params):
    """渲染模板
    Args:
        templatePath: 模板路径
        params: 模板参数
    """
    # 根据模板路径分析模板
    with open(templatePath, 'rt', encoding='utf8') as f:
        template = Template(f.read())

    return template.render(params)


def generate_springboot_shells(runnableJarPaths, template, prefixpath=None, shellPrefix='restart_', shellSuffix='.sh', regrouping=None):
    """创建springboot脚本数据
    Args:
        runnableJarPaths: 可执行文件路径列表
        template: 模板路径
        prefixpath: 可运行文件的路径前缀，当部位None时，用于去除脚本路径中的文件路径
        shellPrefix: 脚本文件名前缀
        shellSuffix： 脚本文件名后缀
    Return:
        返回一个包括了脚本文件路径及文件内容的数组：
        [{
            'filename':'脚本路径',
            'content':'脚本文件内容'
        }...]

    """
    tplParams = {}
    outputFiles = []  # 记录生成的文件 [[fileName, content],...]
    for idx, p in enumerate(runnableJarPaths):
        tplParams['exe_file_path'] = p
        tplParams['idx'] = idx
        filename = p
        if prefixpath:
            filename = filename.replace(prefixpath, '')
        if filename.startswith('/'):
            filename = filename[1:]
        # 如果文件名是cart-service-1.0.jar格式的话，只取前面的cart-service
        if re.match('.*?-\d+\.*', filename):
            filename = filename[0:filename.rindex('-')]

        tplParams['server_name'] = filename[filename.rfind("/") + 1:]

        if regrouping and regrouping in filename:
            print("regrouping filename: ", filename)
            filename = '%s/%s%s'%(regrouping,shellPrefix,filename[filename.rfind("/") + 1:])
        else:
            filename = filename[:filename.rfind("/")] + '/' + shellPrefix + filename[filename.rfind("/") + 1:]

        tplParams['base_path'] = filename[0:filename.find('/')]
        
        outputFiles.append(
            {
                'filename': (filename.replace('.', '').replace('-', '_') + shellSuffix).lower(),
                'content': render_template(template, tplParams)
            }
        )
    return outputFiles


def generate_shell_file(shellDatas, output, splitor='/'):
    """创建脚本文件
    Args:
        shellDatas: 脚本文件路径及文件内容的数组：
        [{
            'filename':'脚本路径',
            'content':'脚本文件内容'
        }...]
        output: 输出目录
    """
    for d in shellDatas:
        if not d['filename'].startswith('/'):
            d['filename'] = '/' + d['filename']
        filePath = output + d['filename']
        if not os.path.exists(filePath[:filePath.rfind('/')]):
            os.makedirs(filePath[:filePath.rfind('/')])

        # with open(filePath, 'wt', encoding='utf8') as f:
        with open(filePath, 'wb+') as f:
            f.write(bytes(d['content'], "utf8"))
            print('已生成脚本:{}'.format(filePath))


def generate_all_sh(rootPath, shellPattern='*.sh', shellName='all.sh'):
    """遍历rootPath下的所有文件夹，如该子文件夹中包含了启动脚本，则生成all.sh并将所有启动脚本加入all.sh中
    Args:
        rootPath: 根目录：
        shellName: 可选，生成的脚本名成
    """


def read_file_list(path, prefixpath=None, splitor='/', pattern=None, regx=None):
    """读取指定路径下的文件路径
    Args:
        path: 文件路径
        pattern: 可执行文件的后缀正则
    """

    # 获取目录下的所有文件
    dirlist = []
    for dirpath, dirname, filename in os.walk(path):
        # print('{0},{1},{2}'.format(dirpath,dirname,filename))
        for i in filename:
            if (not pattern or fnmatch(i, pattern)) and (not regx or re.match(regx, i)):
                dirpath = (prefixpath if prefixpath else "") + dirpath.replace(path, '')
                dirlist.append(os.path.join(dirpath, i).replace('\\', splitor))

    print("已获取所有文件")
    for name in dirlist:
        print(name)

    return dirlist


if __name__ == '__main__':
    fire.Fire(MainEntry)
