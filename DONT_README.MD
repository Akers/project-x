# My Project-X:  Some useful light weight tools projects
# Project-X: 一些实用小工具项目

## shell-create.py: 启动脚本生成工具
shell-create.py 根据制定脚本以及可运行文件生成其linux启动脚本的工具

使用方法：

```shell
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
	--regx 可运行文件过滤表达式，如提供此参数则只会扫描满足该正则表达式的文件
	--template 指定生成脚本时使用的模板文件，模板文件语法详见（http://jinja.pocoo.org/docs/2.10/templates/）
```


例子：
```shell
python shell-create.py springboot --path=C:\projects --template=C:\files\project\python\project-x\shell_templates\springboot_restart.tpl --pattern=*.jar --prefixpath=/tpsys/applications/projects --output=C:\files\shells
```





