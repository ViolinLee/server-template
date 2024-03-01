import hashlib
from base64 import b64encode, b64decode
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes


class AESCipher:
    """ AES加密算法

    结果再经过base64编码
    """
    def __init__(self, password):
        self.password = password.encode()
        self.salt = get_random_bytes(AES.block_size)

        self.private_key = hashlib.scrypt(
            self.password,
            salt=self.salt,
            n=2 ** 14,
            r=8,
            p=1,
            dklen=32  # 密钥长度必须为16（AES-128）、24（AES-192）或 32（AES-256）Bytes长度
        )

    def encrypt(self, message):
        """ AES加密方法

        GCM模式
        :param message:
        :return:
        """
        plain_text = message.encode('utf-8')
        cipher_config = AES.new(self.private_key, AES.MODE_GCM)
        cipher_text, tag = cipher_config.encrypt_and_digest(plain_text)

        encrypted_dict = {
            'cipher_text': b64encode(cipher_text).decode('utf-8'),
            'salt': b64encode(self.salt).decode('utf-8'),
            'nonce': b64encode(cipher_config.nonce).decode('utf-8'),
            'tag': b64encode(tag).decode('utf-8')
        }
        encrypted_string = '*'.join(encrypted_dict.values())

        return encrypted_string

    def decrypt(self, encrypted_string):
        """ AES解密方法会首先解析出salt然后再重新构造出private-key而不是直接使用实例私有秘钥变量

        调用处应用try-catch包裹以捕获异常
        :param encrypted_string:
        :return:
        """
        enc_dict = dict(zip(['cipher_text', 'salt', 'nonce', 'tag'], encrypted_string.split('*')))
        salt = b64decode(enc_dict['salt'])
        cipher_text = b64decode(enc_dict['cipher_text'])
        nonce = b64decode(enc_dict['nonce'])
        tag = b64decode(enc_dict['tag'])

        private_key = hashlib.scrypt(
            self.password,
            salt=salt,
            n=2 ** 14,
            r=8,
            p=1,
            dklen=32
        )

        cipher = AES.new(private_key, AES.MODE_GCM, nonce=nonce)
        decrypted = cipher.decrypt_and_verify(cipher_text, tag)

        return decrypted.decode('utf-8')


if __name__ == '__main__':
    key = "Python-WebServer-Template"
    cipher_a = AESCipher(key)

    text = 'Welcome to AES'
    encrypted = cipher_a.encrypt(text)
    print(encrypted)
    print(cipher_a.decrypt(encrypted))

    # 断言可以通过
    cipher_b = AESCipher(key)
    assert(cipher_a.decrypt(encrypted) == cipher_b.decrypt(encrypted))
