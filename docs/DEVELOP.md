## 开发说明文档



#### 编译及安装

- 编译

  本模块支持python3.7以上版本，是否支持3.6取决于setup.py中的install_requires所描述的依赖安装包是否支持。

  ```shell
  python setup.py sdist
  ```

- 安装

  在编译完成后，当前目录会多一个**dist**文件夹，该文件夹下会产生一个**automotive-1.0.0.tar.gz**文件，其中1.0.0为版本号，在src/automotive文件夹下的version.py文件中定义。

  ```shell
  pip install automotive-1.0.0.tar.gz
  ```

  

- 卸载

  可以通过pip方式直接卸载

  ```shell
  pip uninstall automotive
  ```

  



#### PIP源更新

建议使用清华源替代当前源

```shell
pip install pip -U
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```





#### 文档创建



文档创建使用的是**sphinx** 方式自动生成的文件

##### 创建步骤

1. 首先执行命令， 其中所有选项都选择默认配置

   ```shell
   sphinx-quickstart
   ```

2. 安装依赖包

   ```shell
   pip install sphinx  
   pip install sphinx_rtd_theme
   ```

3. 修改的是doc下面的config.py和index.rst两个文件

- **config文件的修改**

  ```python
  # Configuration file for the Sphinx documentation builder.
  #
  # This file only contains a selection of the most common options. For a full
  # list see the documentation:
  # https://www.sphinx-doc.org/en/master/usage/configuration.html
  
  # -- Path setup --------------------------------------------------------------
  
  # If extensions (or modules to document with autodoc) are in another directory,
  # add these directories to sys.path here. If the directory is relative to the
  # documentation root, use os.path.abspath to make it absolute, like shown here.
  #
  # 这三行配置源码所在路径
  import os
  import sys
  sys.path.insert(0, os.path.abspath('../../src'))
  
  
  # -- Project information -----------------------------------------------------
  
  project = 'automotive'
  copyright = '2020, bdstar_qa'
  author = 'bdstar_qa'
  
  # The full version, including alpha/beta/rc tags
  release = '1.0.0'
  
  
  # -- General configuration ---------------------------------------------------
  
  # Add any Sphinx extension module names here, as strings. They can be
  # extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
  # ones.
  # 配置源码自动生成
  extensions = [
      'sphinx.ext.autodoc',
      'sphinx.ext.todo',
      'sphinx.ext.viewcode'
  ]
  
  # Add any paths that contain templates here, relative to this directory.
  templates_path = ['_templates']
  
  # The language for content autogenerated by Sphinx. Refer to documentation
  # for a list of supported languages.
  #
  # This is also used if you do content translation via gettext catalogs.
  # Usually you set "language" from the command line for these cases.
  language = 'zh_cn'
  
  # List of patterns, relative to source directory, that match files and
  # directories to ignore when looking for source files.
  # This pattern also affects html_static_path and html_extra_path.
  exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
  
  
  # -- Options for HTML output -------------------------------------------------
  
  # The theme to use for HTML and HTML Help pages.  See the documentation for
  # a list of builtin themes.
  #
  # 修改sphinx的模式
  html_theme = 'sphinx_rtd_theme'
  
  # Add any paths that contain custom static files (such as style sheets) here,
  # relative to this directory. They are copied after the builtin static files,
  # so a file named "default.css" will overwrite the builtin "default.css".
  html_static_path = ['_static']
  ```



- index.rst文件的修改

  ```rst
  .. automotive documentation master file, created by
  
  本文档主要列举了automotive模块及子模块的一些方法说明
  
  automotive模块文档说明
  ======================================
  
  
  .. toctree::
     :maxdepth: 2
     :caption: Contents:
  
  基础tools工具
  ======================================
  .. automodule:: automotive.tools
     :members:
  
  
  IT6831和Konstanter电源
  ======================================
  .. automodule:: automotive.tools.battery
     :members:
  
  摄像头
  ======================================
  .. automodule:: automotive.tools.camera
     :members:
  
  
  图片处理
  ======================================
  .. automodule:: automotive.tools.images
     :members:
  
  邮件发送接收（未完成)
  ======================================
  .. automodule:: automotive.tools.mail
     :members:
  
  电源变动测试
  ======================================
  .. automodule:: automotive.tools.onoff
     :members:
  
  Serial串口
  ======================================
  .. automodule:: automotive.tools.serial_port
     :members:
  
  SSH操作（未完成)
  ======================================
  .. automodule:: automotive.tools.ssh
     :members:
  
  USB继电器
  ======================================
  .. automodule:: automotive.tools.usbrelay
     :members:
  
  CAN盒
  ======================================
  .. automodule:: automotive.can
     :members:
  
  Android Appium
  ======================================
  .. automodule:: automotive.android
     :members:
  
  索引和表
  ==================
  
  * :ref:`genindex`
  * :ref:`modindex`
  * :ref:`search`
  
  ```

  其中这部分是新增的模块

  ```rst
  CAN盒
  ======================================
  .. automodule:: automotive.can
     :members:
  ```

  

#####  **文档生成**

直接执行`make html`命令可以生成HTML文档，生成的文档在**_build/html**下面，直接双击**index.html**即可打开文档文件



