import os
from string import punctuation
import json
from multiprocessing import Process

from PIL import Image

_path_project = os.path.dirname(os.path.abspath(__file__))
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
    file_rendered = os.path.join(_path_files, 'rendered.info')
    file_ink = os.path.join(_path_files, 'ink.png')
    url_home = 'https://zooatmospheregroup.github.io/Zoo-HZ-Media-Volunteers'

    def __init__(self):
        for i in _path_list:
            self.mkdir_if_not_exist(i)
        if os.path.exists(self.file_rendered):
            return
        with open(self.file_rendered, 'w') as f:
            json.dump({}, f)

    @classmethod
    def load_rendered(cls):
        with open(cls.file_rendered, 'r') as f:
            return json.load(f)

    @classmethod
    def dump_rendered(cls, rendered):
        with open(cls.file_rendered, 'w') as f:
            json.dump(rendered, f)

    @classmethod
    def fix_file_name(cls, file_name):
        return ''.join([f.lower() for f in file_name if f == '.' or f not in punctuation])

    @staticmethod
    def mkdir_if_not_exist(path):
        if os.path.exists(path) and os.path.isdir(path):
            return
        os.makedirs(path)

    @classmethod
    def transfer_jpg_to_webp(cls, path_in, path_out):
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
    def resize_with_the_same_ratio(cls, path_in, path_out, size_max=3200):
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
                im.resize((width, height)).save(_path, 'WEBP')
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
    def add_ink(cls, path_in, path_out, path_ink=None, ink_position=''):
        # 添加水印
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
                watermark_high = int(2000.00 / watermark_width * watermark_high)
                watermark_width = 2000
                print(watermark_width, watermark_high)
                watermark = watermark.resize((watermark_width, watermark_high),
                                             resample=Image.ANTIALIAS)
                # 居中
                layer = Image.new('RGBA', im.size, (0, 0, 0, 0))
                layer.paste(watermark, (im_width - watermark_width, im_high - watermark_high))
                out = Image.composite(layer, im, layer)
                _, _f = os.path.split(_path_file)
                _path = os.path.join(path_out, _f)
                out.convert("RGB").save(_path + '.webp', 'WEBP')
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
        path_out_head, tail = os.path.split(path_out)
        cls.mkdir_if_not_exist(path_out_head)

        if not os.path.exists(path_in) or not os.path.isdir(path_in):
            print('path: %s is not exist or is not dir' % path_in)
            return

        md_head = """---
layout: default
---
### render for path: %s

""" % path_in
        md_item = """## {size}, {name}
![{name}]({path})

"""
        md = ''
        md += md_head
        for f in os.listdir(path_in):
            # /home/xxx/static/images/webp/zzz/a.webp
            path_abs_f = os.path.join(path_in, f)
            size = round(os.path.getsize(path_abs_f) / 1024 / 1024, 2)
            size_str = 'size: %sM' % size

            # url_home/static/images/webp/zzz/a.webp
            path = path_abs_f[path_abs_f.find('/static/images/'):]
            item = md_item.format(size=size_str, name=f, path=path)
            md += item

        with open(os.path.join(path_out_head, tail), 'w') as f:
            f.write(md)
        return

    @classmethod
    def render_home_page(cls, path_in):
        pass

    def render_all(self, do_filter=True, do_add_ink=True, do_transfer_jpg_to_webp=True, do_resize=True,
                   do_render_md=True, do_render_home=True, do_dump=True):
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
                    if do_resize:
                        self.resize_with_the_same_ratio(path_webp_day, path_resize_day)
                    if do_add_ink:
                        pass
                        # self.add_ink(path_resize_day, ink_size=32)
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
            do_dump=False
        )

    def just_transfer_and_resize(self):
        self.render_all(
            do_render_md=False,
            do_render_home=False,
            do_dump=False
        )

    def just_render_md(self):
        self.render_all(
            do_transfer_jpg_to_webp=False,
            do_resize=False,
            do_render_md=True,
            do_render_home=False,
            do_dump=False
        )

    def just_render_home_page(self):
        self.render_all(
            do_transfer_jpg_to_webp=False,
            do_resize=False,
            do_render_md=False,
            do_render_home=True,
            do_dump=False
        )


if __name__ == '__main__':
    hp = HelloPhoto()
    # hp.render_all()
    hp.add_ink(
        path_in=r'C:\-C\Zoo-HZ-Media-Volunteers\static\images\raw\202103\20210321zbb',
        path_out=r'C:\-C\Zoo-HZ-Media-Volunteers\static\images\webp\202103\20210321zbb',
        path_ink=r'C:\-C\Zoo-HZ-Media-Volunteers\_files\w1-white.png'
    )
