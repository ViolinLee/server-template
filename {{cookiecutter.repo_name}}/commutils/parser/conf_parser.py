from configparser import ConfigParser


class ConfigAgent(ConfigParser):
    def __init__(self, **kwargs):
        super(ConfigParser, self).__init__(**kwargs)

        self.filename = None

    def read(self, filename, encoding=None):
        assert isinstance(filename, str), 'Only support string type, not iterable filename!'
        filenames_ok = super(ConfigParser, self).read(filename, encoding)

        assert len(filenames_ok) == 1, 'Config file read failed!'
        self.filename = filenames_ok[0]

    def get_sections(self):
        return self.sections()

    def get_options(self, section):
        return self.options(section)

    def get_value(self, section, option):
        return self.get(section, option)

    def get_dict(self, section, digit: bool = True, boolean: bool = True) -> dict:
        """ 将指定section下的所有配置提取到字典

        :param digit: 是否自动解析数字类型
        :param boolean: 是否自动解析布尔类型
        :param section:
        :return:
        """
        return {option: int(value) if (digit and value.isdigit()) else self.convert_boolean(value) if boolean else value
                for option, value in self.items(section)}

    def overwrite(self, section, option, value):
        self.set(section, option, value)
        with open(self.filename, 'w') as fp:
            self.write(fp)

    def print_all(self):
        for section in self.sections():
            for option in self.options(section):
                print(f"{section}.{option} = {self.get(section, option)}")
        print('\n')

    @staticmethod
    def convert_boolean(bool_str):
        if bool_str.lower() in ('true', 'yes', 'on', '1'):
            return True
        elif bool_str.lower() in ('false', 'no', 'off', '0'):
            return False
        else:
            return bool_str


if __name__ == '__main__':
    # ConfigAgent unit-test

    configAgent = ConfigAgent()
    configAgent.read('test_param.ini')
    configAgent.print_all()

    print(configAgent.get_sections())
    print(configAgent.get_options('Section1'))
    print(configAgent.get_value('Section1', 'Option2'))
    print(configAgent.get_dict('Section2'))

    configAgent.overwrite('Section1', 'option2', 'Crocodile')
    configAgent.print_all()
