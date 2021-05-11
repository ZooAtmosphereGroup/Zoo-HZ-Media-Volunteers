# -*- encoding: utf-8 -*-
import os
from string import punctuation
import json

from PIL import Image

_path_project = os.path.dirname(os.path.abspath(__file__))
_path_templates = os.path.join(_path_project, 'templates')
_path_files = os.path.join(_path_project, '_files')
_path_mds = os.path.join(_path_project, 'mds')
_path_mds_resize = os.path.join(_path_mds, 'webp-resize-2000')
_path_static = os.path.join(_path_project, 'static')
_path_images = os.path.join(_path_static, 'images')
_path_images_raw = os.path.join(_path_images, 'raw')
_path_images_webp = os.path.join(_path_images, 'webp')
_path_images_resize = os.path.join(_path_images, 'webp-resize-2000')

_path_list = [
    _path_files,
    _path_mds_resize,
    _path_images_raw,
    _path_images_webp,
    _path_images_resize
]


class HelloPhoto(object):
    # 已渲染信息
    file_rendered = os.path.join(_path_files, 'rendered.info')
    # 志愿者列表
    file_volunteers = os.path.join(_path_files, 'volunteers.info')
    # 流密钥
    file_stream_key = os.path.join(_path_files, 'stream_key.info')
    # 水印
    file_ink = os.path.join(_path_files, 'ink.png')
    # 页面信息
    file_page_info = os.path.join(_path_files, 'page.info')
    # 主页
    file_index = os.path.join(_path_project, 'index.html')
    # 模板div
    file_template_div_page = os.path.join(_path_templates, 'div_page.html')
    # 模板home
    file_template_home = os.path.join(_path_templates, 'home.html')
    # 发布站点地址
    site = 'Zoo-HZ-Media-Volunteers'

    def __init__(self):
        for i in _path_list:
            self.mkdir_if_not_exist(i)
        if os.path.exists(self.file_rendered):
            return
        with open(self.file_rendered, 'w') as f:
            json.dump({}, f)

    @classmethod
    def load_rendered(cls):
        # 加载渲染信息
        print('load_rendered')
        # todo: 适配不同开发节点上的不同路径
        with open(cls.file_rendered, 'r') as f:
            return json.load(f)

    @classmethod
    def dump_rendered(cls, rendered):
        # 保存渲染信息
        print('dump_rendered')
        with open(cls.file_rendered, 'w') as f:
            json.dump(rendered, f, indent=4)

    @classmethod
    def fix_file_name(cls, file_name):
        # 适配文件名
        return ''.join([f.lower() for f in file_name if f == '.' or f not in punctuation])

    @staticmethod
    def mkdir_if_not_exist(path):
        # 如果文件夹不存在， 则创建
        if os.path.exists(path) and os.path.isdir(path):
            return
        os.makedirs(path)

    @classmethod
    def transfer_jpg_to_webp(cls, path_in, path_out):
        # JPG转WEBP
        print('transfer_jpg_to_webp')
        cls.mkdir_if_not_exist(path_out)

        def _do(_path_file):
            print('transfer_jpg_to_webp', _path_file)
            try:
                _p, _f = os.path.split(_path_file)
                _file_fix = cls.fix_file_name(_f)
                _path_fix = os.path.join(_p, _file_fix)
                if _f != _file_fix:
                    os.rename(_path_file, _path_fix)
                _path_dst = os.path.join(path_out, _file_fix)
                if _path_dst[-4:] in ('.jpg', '.mpg', '.png'):
                    _path_dst = _path_dst[:-4]
                if _path_dst.endswith('.mpeg'):
                    _path_dst = _path_dst[:-5]
                Image.open(_path_fix).convert("RGB").save(_path_dst + '.webp', 'WEBP')
            except Exception as e:
                print("cannot convert", _path_file, e)

        # file
        if os.path.isfile(path_in):
            _do(path_in)
            return

        # folder
        if os.path.isdir(path_in):
            for f in os.listdir(path_in):
                _do(os.path.join(path_in, f))
            return

        # link or other
        print('path: %s is a link or other file' % path_in)
        return

    @classmethod
    def create_thumbnail(cls, path_in, path_out, size=(640, 360)):
        # 创建略缩图
        print('create_thumbnail')
        cls.mkdir_if_not_exist(path_out)

        def _do(_path_file):
            print('create_thumbnail', _path_file)
            try:
                im = Image.open(_path_file)
                width, height = im.size

                width_16_9 = width
                height_16_9 = int(width_16_9 / 16.0 * 9.0)
                _size = (
                    0,
                    int((height - height_16_9) / 2),
                    width_16_9,
                    int((height - height_16_9) / 2) + height_16_9
                )
                region = im.crop(_size)
                # region.resize(size)
                region.thumbnail(size)
                _, _f = os.path.split(_path_file)
                _path = os.path.join(path_out, _f)
                region.save(_path + '.webp', 'WEBP')
            except Exception as e:
                print("cannot convert", _path_file, e)

        # file
        if os.path.isfile(path_in):
            _do(path_in)
            return

        # folder
        if os.path.isdir(path_in):
            for f in os.listdir(path_in):
                _do(os.path.join(path_in, f))
            return

        # link or other
        print('path: %s is a link or other file' % path_in)
        return

    @classmethod
    def resize_with_the_same_ratio(cls, path_in, path_out,
                                   size_max=3200, _format=None):
        # 调整尺寸, 保持长宽比
        print('resize_with_the_same_ratio')
        cls.mkdir_if_not_exist(path_out)

        def _do(_path_file):
            print('resize_with_the_same_ratio', _path_file)
            try:
                im = Image.open(_path_file)
                width, height = im.size

                if width >= height:
                    height = int(height / (width / size_max))
                    width = size_max
                else:
                    width = int(width / (height / size_max))
                    height = size_max

                _, _f = os.path.split(_path_file)
                _path = os.path.join(path_out, _f)
                if _format:
                    im.resize((width, height)).save(_path, _format)
                else:
                    im.resize((width, height)).save(_path)
            except Exception as e:
                print("cannot convert", _path_file, e)

        # file
        if os.path.isfile(path_in):
            _do(path_in)
            return

        # folder
        if os.path.isdir(path_in):
            for f in os.listdir(path_in):
                _do(os.path.join(path_in, f))
            return

        # link or other
        print('path: %s is a link or other file' % path_in)
        return

    @classmethod
    def add_ink(cls, path_in, path_out,
                path_ink=None, ink_position=''):
        # 添加水印
        print('add_ink')
        cls.mkdir_if_not_exist(path_out)

        def _do(_path_file):
            print('add_ink', _path_file)
            try:
                im = Image.open(_path_file)
                im_width = im.size[0]
                im_high = im.size[1]

                watermark = Image.open(path_ink)
                watermark_width = watermark.size[0]
                watermark_high = watermark.size[1]

                # 根据水印放大比率调整水印大小
                watermark_high = int(1000.00 / watermark_width * watermark_high)
                watermark_width = 1000
                print(watermark_width, watermark_high)
                watermark = watermark.resize((watermark_width, watermark_high),
                                             resample=Image.ANTIALIAS)
                # 居中
                layer = Image.new('RGBA', im.size, (0, 0, 0, 0))
                layer.paste(watermark, (im_width - watermark_width, im_high - watermark_high))
                out = Image.composite(layer, im, layer)
                _, _f = os.path.split(_path_file)
                _path = os.path.join(path_out, _f)
                out.save(_path)
            except Exception as e:
                print("cannot convert", _path_file, e)

        # file
        if os.path.isfile(path_in):
            _do(path_in)
            return

        # folder
        if os.path.isdir(path_in):
            for f in os.listdir(path_in):
                _do(os.path.join(path_in, f))
            return

    @classmethod
    def render_markdown(cls, path_in, path_out):
        # 渲染页面单个页面
        print('render_markdown')
        folder = path_in.split('/')[-1]

        # 加载页面信息文件
        with open(cls.file_page_info, 'r', encoding='utf-8') as f:
            page_info = json.load(f)

        if folder not in page_info:
            raise KeyError('page info not exist: %s' % path_in)

        info = page_info[folder]

        path_out_head, tail = os.path.split(path_out)
        cls.mkdir_if_not_exist(path_out_head)

        if not os.path.exists(path_in) or not os.path.isdir(path_in):
            print('path: %s is not exist or is not dir' % path_in)
            return

        md_head = """---
layout: default
---
### 摄影: {author}
### 描述: {remark}
### 提交时间: {date}

"""
        md_item = """##### {size}, {photo_description}
![{name}]({path})

"""
        md_tail = """
[返回](/Zoo-HZ-Media-Volunteers)
"""
        photos_description = info['photos_description']
        md = md_head.format(author=info['author'],
                            remark=info['remark'],
                            date=info['date'])

        # 先对文件按照名称排序
        path_in_files = os.listdir(path_in)
        path_in_files.sort()

        for f in path_in_files:
            # /home/xxx/static/images/webp/zzz/a.webp
            path_abs_f = os.path.join(path_in, f)
            size = round(os.path.getsize(path_abs_f) / 1024 / 1024, 2)
            size_str = 'size: %sM' % size

            # url_home/static/images/webp/zzz/a.webp
            path = path_abs_f[path_abs_f.find('static/images/'):]

            # 照片描述
            i_description = photos_description[f] if f in photos_description else ''
            item = md_item.format(
                size=size_str,
                name=f,
                photo_description=i_description,
                path='/' + cls.site + '/' + path)
            md += item

        md += md_tail
        with open(os.path.join(path_out_head, tail), 'w') as f:
            f.write(md)
        return

    @classmethod
    def render_home_page(cls, path_in):
        # 渲染主页面
        print('render_home_page', path_in)

        with open(cls.file_page_info, 'r') as f:
            page_info = json.load(f)

        with open(cls.file_template_div_page, 'r') as f:
            div_page = f.read()

        with open(cls.file_template_home, 'r') as f:
            home = f.read()

        pages = ''
        # 逆序
        for page in sorted(list(page_info.keys()), reverse=True):
            info = page_info[page]
            path_author = info['path_author']
            path_resize = info['path_resize']
            author = info['author']
            remark = info['remark']
            title = info['title']
            date = info['date']
            thumbnail = info['thumbnail']
            path_thumbnail = '/'.join(('static/images', path_resize, path_author, thumbnail))
            path_md = '/'.join(('mds', path_resize, path_author))

            pages += div_page.format(path_md=path_md,
                                     author=author,
                                     title=title,
                                     date=date,
                                     path_thumbnail=path_thumbnail,
                                     remark=remark)
        home = home % pages
        # 写入
        with open(cls.file_index, 'w') as f:
            f.write(home)

    def render_all(self, do_filter=False, do_add_ink=True,
                   do_transfer_jpg_to_webp=False,
                   do_resize=True, do_render_md=True,
                   do_render_home=True, do_dump=True):
        rendered = self.load_rendered()
        raw = os.listdir(_path_images_raw)
        for raw_month in raw:
            # /static/images/raw/202002
            path_raw_month = os.path.join(_path_images_raw, raw_month)

            if not os.path.isdir(path_raw_month):
                print(path_raw_month, 'is not dir')
                continue

            raw_days = os.listdir(path_raw_month)
            path_raw_month = os.path.join(_path_images_raw, raw_month)
            path_webp_month = os.path.join(_path_images_webp, raw_month)
            path_resize_month = os.path.join(_path_images_resize, raw_month)
            path_mds_resize_month = os.path.join(_path_mds_resize, raw_month)

            for raw_day in raw_days:
                # /static/images/raw/202002/20200202xxx
                path_raw_day = os.path.join(path_raw_month, raw_day)

                if do_filter and path_raw_day in rendered:
                    print(path_raw_day, 'has rendered')
                    continue
                if not os.path.isdir(path_raw_day):
                    print(path_raw_day, 'is not dir')
                    continue

                path_webp_day = os.path.join(path_webp_month, raw_day)
                path_resize_day = os.path.join(path_resize_month, raw_day)
                path_mds_resize_day = os.path.join(path_mds_resize_month, raw_day + '.md')
                try:
                    if do_transfer_jpg_to_webp:
                        self.transfer_jpg_to_webp(path_raw_day, path_webp_day)
                        _in = path_webp_day
                    else:
                        _in = path_raw_day
                    if do_resize:
                        self.resize_with_the_same_ratio(_in, path_resize_day)
                        _in = path_resize_day
                    if do_add_ink:
                        self.add_ink(_in, _in, path_ink=r'_files/w1-white.png')
                    if do_render_md:
                        self.render_markdown(path_resize_day, path_mds_resize_day)
                    rendered[path_raw_day] = True
                except Exception as e:
                    print(path_raw_day, e)
                    continue

        if do_dump:
            self.dump_rendered(rendered)

        if do_render_home:
            self.render_home_page(_path_mds_resize)

    def render_all_but_no_dump(self):
        self.render_all(
            do_transfer_jpg_to_webp=True,
            do_resize=True,
            do_render_md=True,
            do_render_home=True,
            do_add_ink=True,
            do_dump=False
        )

    def just_transfer_and_resize(self):
        self.render_all(
            do_transfer_jpg_to_webp=True,
            do_resize=True,
            do_add_ink=False,
            do_render_md=False,
            do_render_home=False,
            do_dump=False
        )

    def just_render_md(self):
        self.render_all(
            do_transfer_jpg_to_webp=False,
            do_resize=False,
            do_add_ink=False,
            do_render_md=True,
            do_render_home=False,
            do_dump=False
        )

    def just_render_home_page(self):
        self.render_all(
            do_transfer_jpg_to_webp=False,
            do_resize=False,
            do_add_ink=False,
            do_render_md=False,
            do_render_home=True,
            do_dump=False
        )

    @classmethod
    def encrypt_raw(cls, path_in):
        # 流加密, 对称
        print('encrypt_raw')
        if not os.path.exists(cls.file_stream_key):
            print('file_stream_key not exist', cls.file_stream_key)
            return

        with open(cls.file_stream_key, 'rb') as f:
            bin_key = f.read()
        length_key = len(bin_key)

        for root, dirs, files in os.walk(path_in):

            for file in files:
                _file = os.path.join(root, file)

                with open(_file, 'rb') as f:
                    bin_raw = f.read()

                bin_encrypt = bytearray()

                k = 0
                for i in bin_raw:
                    j = bin_key[k % length_key]
                    bin_encrypt.append(i ^ j)
                    k += 1

                with open(_file, 'wb') as f:
                    f.write(bin_encrypt)
                print('encrypt_raw', _file)

    @classmethod
    def create_page_info(cls, path_in, ignore_rendered=True):
        # 创建页面信息
        print('create_page_info', path_in)
        # page_info = {
        #     # dir: {'title': title, 'author': author,
        #     #       'date': date, 'description': description
        #     #       'folder': folder
        #     #      }
        # }
        # 页面信息文件不存在, 则创建
        if not os.path.exists(cls.file_page_info):
            with open(cls.file_page_info, 'w', encoding='utf-8') as f:
                json.dump({}, f)

        with open(cls.file_page_info, 'r', encoding='utf-8') as f:
            page_info = json.load(f)

        # 更新页面信息
        for root, dirs, files in os.walk(path_in):
            # 跳过子目录
            if not files:
                continue

            folder = root.split('/')[-1]
            # 跳过已渲染
            if ignore_rendered and folder in page_info:
                continue
            print('create_page_info', folder)
            author = folder[8:]
            date = folder[:8]
            path_author = root.replace(path_in, '')
            page_info[folder] = {
                'thumbnail': '',
                'title': '',
                'author': author,
                'date': date,
                'remark': '',
                'path_resize': 'webp-resize-2000',
                'path_author': path_author,
                'photos_description': {
                }
            }
            page_info[folder]['photos_description'] = dict([(i, i)for i in files])

        # 保存页面信息
        # todo: 按目录名称降序排序
        with open(cls.file_page_info, 'w', encoding='utf-8') as f:
            json.dump(page_info, f, indent=4, ensure_ascii=False, sort_keys=True)


if __name__ == '__main__':
    hp = HelloPhoto()
    # hp.encrypt_raw(path_in=_path_images_raw)
    # hp.create_page_info(_path_images_raw)
    # hp.just_render_md()
    hp.just_render_home_page()
    # hp.render_all()
    # hp.render_all(do_filter=True)
