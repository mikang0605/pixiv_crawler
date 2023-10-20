import yaml


def get_config(n):
    with open("config.yaml", "r") as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
        try:
            # 判断传入的n是否在存在
            if n in data.keys():
                return data[n]
            else:
                print(f"n：{n}不存在")
        except Exception as e:
            print(e)
