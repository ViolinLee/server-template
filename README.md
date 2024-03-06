# Web-API Server Project Template
这是一个Python服务端工程模板（生成工具）。该模板简化了工程构建过程，有利于提高服务端代码开发效率以及代码质量。它具备以下特性：  
- 预定义项目结构 
- 支持命令行交互、可配置
- 内置常用脚本自动导入
- 多环境管理

## 软件工具说明
### Web应用和服务框架
工程模板推荐使用支持异步的FastAPI作为Web应用框架，但用户也可以选择使用Flask或Django等应用框架。由于UWSGI不支持ASGI接口，因此无法顺利启动由FastAPI框架编写的应用程序。      

当使用FastAPI时，推荐使用GUNICORN作用Web服务器（GUNICORN在后来的版本中引入了异步处理支持，可以通过在Gunicorn中配置其工作进程的类型为'uvicorn.workers.UvicornWorker'来实现异步支持）。   
当然，工程模板也提供了UWSGI这一Web服务器的配置示例，此时模板提供的主应用示例脚本使用Flask框架编写。

### 容器化
工程模板使用的构建工具为Docker。在根目录的Dockerfile镜像构建模板中添加了默认的构建配置，主要包括源基础镜像、PIP源安装、Web应用启动。   

## 工程结构说明
为了提高模板生成工程过程的自动化程度，项目的部分配置文件之间可能存在一些依赖。比如部署环境管理的配置项依赖于Dockerfile的容器环境变量配置。
### 配置文件
- "{{cookiecutter.repo_name}}/Dockerfile"包含项目镜像构建、容器环境变量的配置。   
- "{{cookiecutter.repo_name}}/.editorconfig"包含代码样式和格式化规则的配置。   
- "{{cookiecutter.repo_name}}"下的gunicorn.conf.py和uwsgi.ini为Web服务器的配置（uvicorn的配置直接在启动脚本start_uvicorn.sh设置，一般用于本地调试）。
- "{{cookiecutter.app_name}}/configs/envs"包含环境管理的配置，依赖于系统环境变量"MODE"。   
- "{{cookiecutter.app_name}}/settings.py"包含应用的基础配置，会读取"{{cookiecutter.app_name}}/configs/envs"目录下配置文件数据。

### 环境变量
可配置的环境变量在Dockerfile中使用ARG来定义（ARG用于设置构建时的参数，而ENV则设置容器运行时的环境变量）。这些变量可以在docker build命令中通过--build-arg选项，它通常用于在构建过程中传递一些动态参数，比如版本号、密钥等。这样做的好处是当需要构建不同环境的镜像时，只需要变更构建命令而不需要更改配置文件。   

以下是模板工程提供的构建参数：
- `PORT`=`80`
- `HOST`=`0.0.0.0`
- `APP_MODULE`=`<module>.<module>:<fastapi-app-name>`
- `WORKERS_PER_CORE`=`1`

### 脚本说明
项目级（非应用级）的脚本文件一律放置在"{{cookiecutter.repo_name}}/scripts"目录下。
- py2so.py：将机密性高的业务代码转为.so文件（待添加）   
- start.sh：容器入口点执行的Web服务器启动脚本，会根据服务器类型自动选择Web服务器（gunicorn、uwsgi、uvicorn）

### 内置功能模块
除了提供预定义的项目结构和配置外，工程模板的另一重要作用是提供较全面的功能模块支持。这些功能模块一般是对行业主流的解决方案库（通常是第三方库）进行了封装，以类、函数或装饰器的方式提供，追求的效果是稳定、通用、强大。   
目前计划支持的内置功能模块如下：   
- async：异步操作   
- auth：鉴权模块  
- cache：缓存模块
- common：通用工具，如常用的自定义装饰器、ID生成。   
- db：数据库连接池、消息订阅发布   
- encrypt：加密算法   
- logger：日志系统   
- parallel：并行操作   
- parser：解析器，主要是解析配置文件   
- scheduler：调度器   

每个模块下的脚本均对所提供功能进行了详细的注释说明，部分功能提供了使用示例，亦作为测试用例。   

应该指出的是，虽然工程模板提供了较全面的功能模块支持，但用户在正式进入开发过程后很可能需要根据实际情况添加新的功能模块。为了项目结构的清晰性，建议将添加的自定义功能模块也放置utils目录下。  
## 使用说明
### 下载项目
项目使用的工程模板工具为cookiecutter，因此在本地初始化项目时，需要事先完整cookiecutter的安装。可以通过以下命令安装：
```
pip install cookiecutter
```
安装完成后，通过下述命令进行项目初始化：
```
$ cookiecutter https://github.com/ViolinLee/webserver-template.git
```
在初始化过程中，按照提示输入项目的各项信息，例如项目名称、应用名称、作者、Web服务器类型等（后续可能会根据需要修改会拓展可配置项）。   

完成输入后，webserver-template会根据这些信息自动生成一个Python Web项目的基础结构。

### 进入开发
在完成项目模板初始化后，即可开始进入业务代码开发工作。由于业务种类繁多，并且每个人都有自己的开发习惯，故在代码开发阶段不做重点说明，但模板其实提供了一些有利于提高代码质量的推荐配置。   

例如，我们推荐在您的IDE中使用EditorConfig插件。EditorConfig 的目标是使开发者可以在项目中共享和维护代码样式规范。在项目根目录下存在一个名为 .editorconfig 的配置文件，它给出了一些适用于Python项目的默认配置，可以指定特定文件类型的编码风格和格式化规则。
### 构建镜像
在用户完成业务代码开发、需要构建镜像时，可以参照根目录下的Dockerfile文件调整镜像构建命令，根据实际情况修改或补充构建参数。

## TODO LIST
- 支持docker-compose 和 Makefile
- 完善Python功能模块
- 完备的Web服务器配置项说明
- 第三方库及版本依赖说明