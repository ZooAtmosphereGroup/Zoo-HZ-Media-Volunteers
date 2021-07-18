# -*- coding: utf-8 -*-
import os
import time
import argparse

from Crypto.Cipher import AES

_path_project = os.path.dirname(os.path.abspath(__file__))
_path_static = os.path.join(_path_project, 'static')
_path_files = os.path.join(_path_project, '_files')
_path_images = os.path.join(_path_static, 'images')
_path_raw = os.path.join(_path_images, 'raw')
_path_temp = os.path.join(_path_images, 'temp')


class HelloEncrypt(object):
    # 已加密文件头部特征
    header_encrypt = 'encrypted:'
    bin_header_encrypt = bytes(header_encrypt.encode('utf-8'))
    len_header_encrypt = len(bin_header_encrypt)

    def __init__(self, psw_aes, psw_stream):
        # AES密钥
        self.psw_aes = psw_aes
        self.bin_psw_aes = bytearray(psw_aes.encode('utf-8'))
        # 流密钥
        self.psw_stream = psw_stream
        self.bin_psw_stream = bytearray(psw_stream.encode('utf-8'))
        # 加密/解密
        self.do_encrypt = True

    def encrypt_by_str(self, _path_in, _header):
        # 流加密, 对称
        print('encrypt_by_str')
        with open(_path_in, 'rb') as f:
            raw = f.read()

        length_key = len(self.psw_stream)
        encrypt = bytearray()
        encrypt += _header
        k = 0
        for _i in raw:
            _j = self.bin_psw_stream[k % length_key]
            encrypt.append(_i ^ _j)
            k += 1
        try:
            with open(_path_in, 'wb') as f:
                f.write(encrypt)
        except Exception as e:
            print('pass', _path_in, e)

    def decrypt_by_str(self, _path_in, _len_header):
        # 流解密, 对称
        print('decrypt_by_str')
        with open(_path_in, 'rb') as f:
            _raw = f.read()
            raw = _raw[_len_header:]

        length_key = len(self.psw_stream)
        decrypt = bytearray()
        k = 0
        for _i in raw:
            _j = self.bin_psw_stream[k % length_key]
            decrypt.append(_i ^ _j)
            k += 1
        try:
            with open(_path_in, 'wb') as f:
                f.write(decrypt)
        except Exception as e:
            print('pass', _path_in, e)

    def encrypt_by_aes(self, _path_in):
        # AES加密, 对称
        print('encrypt_by_aes')
        with open(_path_in, 'rb') as f:
            cipher = AES.new(self.bin_psw_aes, AES.MODE_EAX)
            cipher_text, tag = cipher.encrypt_and_digest(f.read())

        try:
            with open(_path_in, 'wb') as f:
                [f.write(x) for x in (cipher.nonce, tag, cipher_text)]
        except Exception as e:
            print('pass', _path_in, e)

    def decrypt_by_aes(self, _path_in):
        # AES解密, 对称
        print('decrypt_by_aes')
        with open(_path_in, 'rb') as f:
            nonce, tag, cipher_text = [f.read(x) for x in (16, 16, -1)]
            cipher = AES.new(self.bin_psw_aes, AES.MODE_EAX, nonce)
            text = cipher.decrypt_and_verify(cipher_text, tag)
        try:
            with open(_path_in, 'wb') as f:
                f.write(text)
        except Exception as e:
            print('pass', _path_in, e)

    def encrypt_file(self, _path_in):
        # 文件加解密
        print('do_encrypt:', self.do_encrypt)
        print('path_in:', _path_in)
        ts = time.time()
        count = 0
        for root, dirs, files in os.walk(_path_in):
            for file in files:
                _file = os.path.join(root, file)
                with open(_file, 'rb') as f:
                    line = f.readline()

                # 文件已加密
                if line.startswith(self.bin_header_encrypt):
                    # 正在进行加密
                    if self.do_encrypt:
                        # 忽略
                        continue
                    # 正在进行解密
                    # 流解密
                    self.decrypt_by_str(_file, self.len_header_encrypt)
                    # AES解密
                    self.decrypt_by_aes(_file)
                    count += 1
                    continue
                # 文件未加密
                # 正在进行加密
                if self.do_encrypt:
                    # AES加密
                    self.encrypt_by_aes(_file)
                    # 流加密
                    self.encrypt_by_str(_file, self.bin_header_encrypt)
                    count += 1
                    continue
                # 正在进行解密
                pass

        print('\nend encrypt_file, cost:', time.time() - ts, ' file count:', count)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--do_encrypt', help='encrypt or decrypt', default=False, action='store_true')
    parser.add_argument('--psw_aes', help='password for aes', type=str)
    parser.add_argument('--psw_stream', help='password for stream', type=str)

    args = parser.parse_args()

    if len(args.psw_aes) != 16:
        raise ValueError('len(psw_aes) must be 16')

    path_target = _path_raw

    he = HelloEncrypt(args.psw_aes, args.psw_stream)
    he.do_encrypt = True
    he.encrypt_file(_path_raw)
