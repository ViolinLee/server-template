""" 密码哈希处理工具

借助第三方库passlib实现的哈希密码模块（版本号1.7.4，旧库不再维护，不太推荐使用）
"""

import re
import math
from passlib.pwd import genword
from passlib.context import CryptContext


class PasswordManager:
    """
    使用"pbkdf2_sha256"算法增加密码安全性:
    即使攻击者获取了存储的哈希密码，也无法通过简单地比较哈希值来推断出原始密码
    """
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

    def hash_password(self, password):
        """ 生成密码哈希

        :param password:
        :return:
        """
        return self.pwd_context.hash(password)

    def verify_password(self, password, hashed_password):
        """ 密码验证

        原理: 验证密码时会从哈希值中提取盐值，并将盐值与输入的密码进行相同的哈希计算，然后将结果与存储的哈希值进行比较来验证密码的正确性
        :param password:
        :param hashed_password:
        :return:
        """
        return self.pwd_context.verify(password, hashed_password)

    @staticmethod
    def random_password(entropy=None, length=None, returns=None, **kwds):
        """ 生成随机密码

        :param entropy:
        :param length:
        :param returns:
        :param kwds:
        :return:
        """
        return genword(entropy, length, returns, **kwds)

    @staticmethod
    def calculate_entropy(password):
        """ 计算密码的熵

        TODO:考虑密码长度的正向作用
        :param password:
        :return:
        """
        symbols = 0
        upper = 0
        lower = 0
        digits = 0
        for char in password:
            if re.match(r"[A-Z]", char):
                upper += 1
            elif re.match(r"[a-z]", char):
                lower += 1
            elif re.match(r"\d", char):
                digits += 1
            else:
                symbols += 1

        # 计算密码的熵
        total_symbols = symbols + upper + lower + digits
        entropy = 0
        if symbols > 0:
            entropy += symbols * math.log2(32)  # 假设有32种特殊字符
        if upper > 0:
            entropy += upper * math.log2(26)  # 26个大写字母
        if lower > 0:
            entropy += lower * math.log2(26)  # 26个小写字母
        if digits > 0:
            entropy += digits * math.log2(10)  # 10个数字

        return entropy / total_symbols if total_symbols > 0 else 0

    def calculate_strength(self, password):
        """ 密码强度的简单评估

        :param password:
        :return:
        """
        entropy = self.calculate_entropy(password)

        strength = "Weak"
        if len(password) < 8 or entropy < 3:
            pass
        elif entropy < 4:
            strength = "Moderate"
        else:
            strength = "Strong"

        return strength

    @staticmethod
    def check_policy(pwd) -> bool:
        """ 密码策略检查

        :param pwd:
        :return:
        """
        # 字符级策略
        if len(pwd) < 8 or not re.search(r"[A-Z]", pwd) or not re.search(r"[a-z]", pwd) or not re.search(r"\d", pwd):
            return False
        return True


if __name__ == '__main__':
    # 计算密码哈希
    pm = PasswordManager()
    pwd = "duolaameng_1314"
    hashed_pwd = pm.hash_password(pwd)
    print("Hashed password:", hashed_pwd)
    print("Second Hashed result:", pm.hash_password(pwd))

    # 密码验证
    input_password = "duolaameng_1314"
    if pm.verify_password(input_password, hashed_pwd):
        print("Password is correct.")
    else:
        print("Password is incorrect.")

    # 生成随机密码
    print(PasswordManager.random_password(length=12))

    # 计算密码的熵/强度评估/策略检查
    print(pm.calculate_entropy("1"))
    print(pm.calculate_entropy("1234"), pm.calculate_strength("1234"), pm.check_policy("1234"), )
    print(pm.calculate_entropy("1234asdf"), pm.calculate_strength("1234asdf"), pm.check_policy("1234asdf"))
    print(pm.calculate_entropy("1234asdfASDF"), pm.calculate_strength("1234asdfASDF"), pm.check_policy("1234asdfASDF"))
    print(pm.calculate_entropy("1234asdfASDF_+{}"), pm.calculate_strength("1234asdfASDF_+{}"), pm.check_policy("1234asdfASDF_+{}"))
